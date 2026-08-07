"""
----------------------------------------------------
ClubConnect AI Module
Integrated by AI Backend
Module Owner: AI Assistant / RAG Pipeline
----------------------------------------------------

ClubConnect AI Assistant - API routes.

Phase 3 scope: Phase 1/2's wiring, plus the SQL Context Builder (Gateway
stages 3/5 from Architecture V2 Task 7) for the six simple/status
intents scoped to this phase - see sql_context_builder.py and
NEXT_PHASE.md. See intent_router.py for the intent catalog and the
detection/authorization logic.

Phase 4 scope: adds RAG retrieval (Gateway stages 4/6 from Architecture
V2 Task 7) via rag_retriever.py's ``retrieve_rag_context`` for any
authorized intent that has ``rag_docs`` - independent of whether that
intent has a Phase 3 SQL builder yet (some intents, e.g. Financial
Operations, have RAG docs before their SQL builder lands in a later
phase).

Phase 5A scope: adds prompt assembly (prompt_builder.py) and the
Gemini call (gemini_client.py) - Gateway stages 7/8 from Architecture
V2 Task 7 ("Assemble Prompt" / "Call Gemini + Format Response"). Also
wires in the Gemini-fallback intent classifier
(intent_router.classify_ambiguous), deferred from Phase 2, which only
runs when the keyword pre-filter (detect_intent) can't resolve a
message. The /chat endpoint now returns Gemini's answer under
``response`` instead of the bare sql_context/rag_context echo;
sql_context/rag_context are still included for debugging/continuity.

Phase 6A scope: adds a lightweight Redis-backed response cache and
short conversation memory in front of the Gemini call - see
cache.py. For an authorized, cacheable intent (cache.CACHEABLE_INTENTS),
a repeated user+role+intent+normalized-prompt request is served from
Redis instead of calling Gemini again; the last 5 conversation
exchanges are fetched from Redis and passed to the existing Prompt
Builder unchanged. Only successful Gemini responses are cached; a
cache/Redis outage degrades to the pre-Phase-6A behavior (always call
Gemini) rather than failing the request - see cache.py's module
docstring.

Deliberately NOT implemented yet (see NEXT_PHASE.md for the phase that
covers each):
    - Remaining-intent SQL + evaluation suite                -> Phase 7
    - Streaming, provider failover (Groq/OpenRouter)

The /chat endpoint below proves the wiring end-to-end: auth -> DB ->
intent detection (+ Gemini fallback) -> authorization -> SQL context ->
RAG context -> cache check -> prompt assembly (+ history) -> Gemini ->
cache write -> response.

Phase 6B scope: adds four new, non-chat endpoints - AI Report
Generation (report_service.py), Financial/Performance Analytics
(analytics_service.py), and AI Content Generation (content_service.py).
None of these are chat turns: no intent detection, no RAG, no
conversation memory, no response caching - each is a one-shot "compute
+ summarize" request scoped by the caller's own role/club-membership
data, following the exact same authorization-before-data-access
ordering as /chat (see each service module's docstring for its access
rules) and the exact same Gemini-failure handling as /chat
(GeminiConfigError/GeminiRequestError -> 503, never a 500).
"""
import os

from flask import Blueprint, request, current_app
from flask_jwt_extended import get_jwt_identity

from app.database.database import get_session
from app.database.enums import MembershipStatus
from app.database.models.auth import User
from app.database.models.clubs import ClubMembership
from app.middleware.auth_middleware import require_auth
from app.modules.ai_services.analytics_service import (
    build_financial_analytics,
    build_performance_analytics,
    financial_analytics_access,
    interpret_analytics,
)
from app.modules.ai_services.cache import (
    append_conversation_turn,
    get_cached_response,
    get_conversation_history,
    set_cached_response,
)
from app.modules.ai_services.content_service import generate_content
from app.modules.ai_services.gemini_client import (
    GeminiConfigError,
    GeminiRequestError,
    generate_response,
)
from app.modules.ai_services.intent_router import authorize_intent, classify_ambiguous, detect_intent
from app.modules.ai_services.prompt_builder import build_prompt
from app.modules.ai_services.rag_retriever import retrieve_rag_context
from app.modules.ai_services.report_service import REPORT_TYPES, generate_report
from app.modules.ai_services.sql_context_builder import build_sql_context

# Refusal wording per docs/.../System_Documents/assistant_conversation_behavior.md
# Section 4 ("Refusal Policy") - kept in sync with that document's
# template rather than inventing separate copy here.
_UNAUTHORIZED_RESPONSE = (
    "I can't help with that — that's outside what I have access to here. "
    "I can help you with clubs, events, memberships, and other platform "
    "questions instead, if that's useful."
)


def _resolve_approved_club_roles(db, user_id: int) -> list:
    """Return ``role_in_club`` for every club the user belongs to with
    APPROVED status.

    Deliberately selects only the ``role_in_club`` column rather than
    loading full ``ClubMembership`` ORM objects. Data-quality finding
    (see PROJECT_CONTEXT.md Section 14): some reference-DB
    `club_memberships.applied_at` rows hold the literal, un-evaluated
    string "CURRENT_TIMESTAMP" instead of a real timestamp - the same
    class of seed-script bug already documented (and already worked
    around) for `attendance_records.checked_in_at` in
    `sql_context_builder.py`'s `_safe_datetime`/`build_attendance_context`.
    Loading a full `ClubMembership` object makes SQLAlchemy's typed
    `DateTime` column coerce every column on the row, including
    `applied_at`/`decided_at`, which raises on that value. A
    column-projected query never reads those two columns at all, so it
    can't be affected by this corruption - no raw-SQL fallback is
    needed here, unlike the attendance case, because we don't need the
    timestamp value at all for authorization purposes.

    No DB/ORM/schema change was made to accommodate this, per project
    instructions - this only changes which columns this one query asks
    for.
    """
    rows = (
        db.query(ClubMembership.role_in_club)
        .filter(
            ClubMembership.user_id == user_id,
            ClubMembership.status == MembershipStatus.APPROVED,
        )
        .all()
    )
    return [role for (role,) in rows]

ai_bp = Blueprint('ai_services', __name__, url_prefix='/api/ai')


def _list_markdown_files(directory: str):
    """Return sorted .md filenames in directory, or [] if it doesn't exist."""
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith(".md"))


def _knowledge_base_status(kb_dir: str) -> dict:
    """Lightweight existence/count check - not a document loader.

    Confirms the KNOWLEDGE_BASE_DIR config points at a real directory
    containing the expected System and RAG documents. Parsing, chunking,
    and embedding those documents is implemented in the RAG phase.
    """
    return {
        "knowledge_base_dir": kb_dir,
        "system_documents": _list_markdown_files(os.path.join(kb_dir, "system")),
        "rag_documents": _list_markdown_files(os.path.join(kb_dir, "rag")),
    }


@ai_bp.route('/health', methods=['GET'])
def health():
    """Unauthenticated scaffold check: confirms config + knowledge base wiring."""
    kb_dir = current_app.config.get("KNOWLEDGE_BASE_DIR")
    return {
        "status": "ai_services scaffold wired",
        "gemini_model": current_app.config.get("GEMINI_MODEL"),
        "gemini_api_key_configured": bool(current_app.config.get("GEMINI_API_KEY")),
        "knowledge_base": _knowledge_base_status(kb_dir),
    }, 200


@ai_bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    """Authenticated endpoint - Phase 5A: + Prompt Builder + Gemini.

    Proves the full pipeline end-to-end: validates the JWT (via
    require_auth), resolves the authenticated user's own row and
    club-scoped roles, classifies the message against the Task 2 intent
    catalog (keyword pre-filter, falling back to Gemini classification
    only when that pre-filter can't resolve it - see
    intent_router.classify_ambiguous), checks whether the user's role(s)
    may reach that intent at all, and - only when authorized - builds
    the scoped SQL context (Phase 3) and retrieves scoped RAG context
    (Phase 4), assembles the full prompt (Phase 5A - prompt_builder.py),
    and calls Gemini (Phase 5A - gemini_client.py) for the final answer.

    Authorization is unchanged from Phase 2-4: it happens before SQL
    context is built and before RAG retrieval runs, never after - see
    intent_router.authorize_intent and rag_retriever.py's module
    docstring. An unauthorized request never reaches the prompt builder
    or Gemini at all.

    Per the Non-Functional Requirements' Availability/Reliability rules,
    a Gemini/config failure returns a clean error rather than a 500 -
    the rest of the platform (and this endpoint's auth/context wiring)
    keeps working regardless of AI provider health.
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message")

    if not message or not isinstance(message, str) or not message.strip():
        return {"message": "A non-empty 'message' field is required."}, 400

    user_id = get_jwt_identity()
    if not user_id:
        return {"message": "Invalid session identity."}, 401

    with get_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found."}, 404

        club_roles = _resolve_approved_club_roles(db, user.id)

        user_context = {
            "user_id": user.id,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
        }

        detected_intent = detect_intent(message)
        if detected_intent == "Ambiguous Request":
            detected_intent = classify_ambiguous(message)

        authorized = authorize_intent(detected_intent, user.role, club_roles)

        sql_context = build_sql_context(detected_intent, db, user) if authorized else None
        rag_context = (
            retrieve_rag_context(detected_intent, message, user.role, club_roles)
            if authorized
            else []
        )

    if not authorized:
        return {
            "status": "ok",
            "response": _UNAUTHORIZED_RESPONSE,
            "user_context": user_context,
            "detected_intent": detected_intent,
            "authorized": authorized,
            "sql_context": sql_context,
            "rag_context": rag_context,
        }, 200

    # Phase 6A: serve a cache hit (same user, role, intent, and
    # normalized prompt) straight from Redis - never calls Gemini. Only
    # cacheable intents (cache.CACHEABLE_INTENTS) are ever looked up
    # here; everything else always falls through to Gemini below.
    cache_user_id = user_context["user_id"]
    cache_role = user_context["role"]
    cached_response = get_cached_response(cache_user_id, cache_role, detected_intent, message)
    if cached_response is not None:
        return {
            "status": "ok",
            "response": cached_response,
            "user_context": user_context,
            "detected_intent": detected_intent,
            "authorized": authorized,
            "sql_context": sql_context,
            "rag_context": rag_context,
            "cache_hit": True,
        }, 200

    history = get_conversation_history(cache_user_id)
    prompt = build_prompt(user_context, detected_intent, message, sql_context, rag_context, history)

    try:
        response_text = generate_response(prompt)
    except GeminiConfigError:
        return {
            "status": "ai_unavailable",
            "message": "The AI assistant isn't configured right now. Please try again later.",
            "detected_intent": detected_intent,
            "authorized": authorized,
            "sql_context": sql_context,
            "rag_context": rag_context,
        }, 503
    except GeminiRequestError:
        return {
            "status": "ai_unavailable",
            "message": "The AI assistant couldn't process that request. Please try again shortly.",
            "detected_intent": detected_intent,
            "authorized": authorized,
            "sql_context": sql_context,
            "rag_context": rag_context,
        }, 503

    # Only successful Gemini responses are ever cached/remembered -
    # never a failed call (the except branches above return before
    # reaching here).
    set_cached_response(cache_user_id, cache_role, detected_intent, message, response_text)
    append_conversation_turn(cache_user_id, message, response_text)

    return {
        "status": "ok",
        "response": response_text,
        "user_context": user_context,
        "detected_intent": detected_intent,
        "authorized": authorized,
        "sql_context": sql_context,
        "rag_context": rag_context,
        "cache_hit": False,
    }, 200


# ---------------------------------------------------------------------------
# Phase 6B: AI Report Generation, Analytics, Content Generation
# ---------------------------------------------------------------------------


def _gemini_error_body(exc, detected_field_name: str, detected_value):
    """Shared 503 body for a Gemini failure on any Phase 6B endpoint -
    same wording/status convention as /chat's handling above."""
    if isinstance(exc, GeminiConfigError):
        message = "The AI assistant isn't configured right now. Please try again later."
    else:
        message = "The AI assistant couldn't process that request. Please try again shortly."
    return {
        "status": "ai_unavailable",
        "message": message,
        detected_field_name: detected_value,
    }


@ai_bp.route('/reports', methods=['POST'])
@require_auth
def reports():
    """Phase 6B - AI Report Generation.

    Body: {"report_type": "<one of report_service.REPORT_TYPES>"}. See
    report_service.py for the full catalog and each type's access rule.
    """
    data = request.get_json(silent=True) or {}
    report_type = data.get("report_type")
    if not report_type or not isinstance(report_type, str):
        return {"message": "A 'report_type' field is required."}, 400

    user_id = get_jwt_identity()
    if not user_id:
        return {"message": "Invalid session identity."}, 401

    with get_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found."}, 404

        club_roles = _resolve_approved_club_roles(db, user.id)

        try:
            result = generate_report(report_type, db, user, club_roles)
        except (GeminiConfigError, GeminiRequestError) as exc:
            return _gemini_error_body(exc, "report_type", report_type), 503

    if result["label"] is None:
        return {
            "status": "error",
            "message": "Unsupported report type.",
            "supported_report_types": list(REPORT_TYPES.keys()),
        }, 400
    if not result["authorized"]:
        return {
            "status": "ok",
            "report_type": result["report_type"],
            "label": result["label"],
            "authorized": False,
            "message": "You don't have access to this report type.",
        }, 200

    return {
        "status": "ok",
        "report_type": result["report_type"],
        "label": result["label"],
        "authorized": True,
        "summary": result["summary"],
        "data": result["data"],
    }, 200


@ai_bp.route('/analytics/financial', methods=['POST'])
@require_auth
def analytics_financial():
    """Phase 6B - Financial Analytics. Treasurer/Faculty Advisor/Student
    Affairs Office/Dean of Student Welfare/System Admin only."""
    user_id = get_jwt_identity()
    if not user_id:
        return {"message": "Invalid session identity."}, 401

    with get_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found.", "resource": "user"}, 404

        club_roles = _resolve_approved_club_roles(db, user.id)

        if not financial_analytics_access(user, club_roles):
            return {
                "status": "ok",
                "authorized": False,
                "message": "You don't have access to financial analytics.",
            }, 200

        result = build_financial_analytics(db, user)
        try:
            explanation = interpret_analytics(result["analytics"], user, "Financial Analytics")
        except (GeminiConfigError, GeminiRequestError) as exc:
            return _gemini_error_body(exc, "analytics_type", "financial"), 503

    return {
        "status": "ok",
        "authorized": True,
        "summary": explanation,
        "analytics": result["analytics"],
        "chart": result["chart"],
    }, 200


@ai_bp.route('/analytics/performance', methods=['POST'])
@require_auth
def analytics_performance():
    """Phase 6B - Performance Analytics. Role-orthogonal: every
    authenticated role gets a scope-appropriate view (personal, led/
    advised clubs, or platform-wide) - see analytics_service.py."""
    user_id = get_jwt_identity()
    if not user_id:
        return {"message": "Invalid session identity."}, 401

    with get_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found.", "resource": "user"}, 404

        club_roles = _resolve_approved_club_roles(db, user.id)
        result = build_performance_analytics(db, user, club_roles)
        try:
            explanation = interpret_analytics(result["analytics"], user, "Performance Analytics")
        except (GeminiConfigError, GeminiRequestError) as exc:
            return _gemini_error_body(exc, "analytics_type", "performance"), 503

    return {
        "status": "ok",
        "authorized": True,
        "scope": result["scope"],
        "summary": explanation,
        "analytics": result["analytics"],
        "chart": result["chart"],
    }, 200


@ai_bp.route('/content', methods=['POST'])
@require_auth
def content():
    """Phase 6B - AI Content Generation. Body: {"content_type": "<one of
    content_service.CONTENT_TYPES>", "details": "<free text>"}. Every
    authenticated role may use every content type (spec Section 5).
    Never persisted, never emailed - draft text only."""
    data = request.get_json(silent=True) or {}
    content_type = data.get("content_type")
    details = data.get("details", "")
    if not content_type or not isinstance(content_type, str):
        return {"message": "A 'content_type' field is required."}, 400

    user_id = get_jwt_identity()
    if not user_id:
        return {"message": "Invalid session identity."}, 401

    with get_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found."}, 404

        try:
            result = generate_content(content_type, details, user)
        except (GeminiConfigError, GeminiRequestError) as exc:
            return _gemini_error_body(exc, "content_type", content_type), 503

    if result["label"] is None:
        return {"message": f"Unknown content_type: {content_type!r}."}, 400

    return {
        "status": "ok",
        "content_type": result["content_type"],
        "label": result["label"],
        "draft": result["draft"],
    }, 200
