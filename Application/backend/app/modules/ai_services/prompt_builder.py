"""ClubConnect AI Assistant - Prompt Builder (Phase 5A).

Gateway stage 7 from
docs/ClubConnect_AI_Documentation/Architecture/ClubConnect_AI_Architecture_V2.md
Task 7 ("Assemble Prompt"): combines the always-injected System
Documents (knowledge_base/system/*.md -
assistant_conversation_behavior.md, dashboard_redundancy_map.md,
recommendation_logic_playbook.md) with the current turn's
``sql_context`` (Phase 3), ``rag_context`` (Phase 4), optional
conversation history, and the user's message into the single prompt
string sent to Gemini (``gemini_client.py``).

Security note (unchanged from Phase 2-4, not re-decided here):
``routes.py`` only calls this after ``authorize_intent()`` has already
returned True and after ``sql_context``/``rag_context`` have already
been built through the existing authorized-scoped builders
(sql_context_builder.py, rag_retriever.py). This module does not
perform authorization itself and does not fetch any data on its own -
it only formats what it is handed. Nothing unauthorized ever reaches
here to begin with, so nothing unauthorized can leak into the prompt.
"""
import json
import os

from app.modules.ai_services.rag.loader import load_documents

_DEFAULT_KB_SYSTEM_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "knowledge_base", "system"
)

# Process-wide cache: the System Documents are small, static, and
# loaded from disk on every phase's health check already - no need to
# re-read/re-join them on every single chat request.
_system_docs_cache: "str | None" = None


def _resolve_kb_system_dir() -> str:
    """The 'system' subdirectory of the configured KNOWLEDGE_BASE_DIR.

    Falls back to this module's own knowledge_base/system path when
    called outside a Flask app context (e.g. unit tests), matching
    rag_retriever.py's ``_resolve_kb_rag_dir`` convention.
    """
    try:
        from flask import current_app
        base = current_app.config.get("KNOWLEDGE_BASE_DIR")
    except RuntimeError:
        base = None

    return os.path.join(base, "system") if base else _DEFAULT_KB_SYSTEM_DIR


def load_system_documents(kb_system_dir: "str | None" = None) -> str:
    """Load and concatenate every System Document into one block of text.

    Cached per process when called with the default (config-resolved)
    directory; an explicit ``kb_system_dir`` (as tests use) always
    re-reads and is never cached, so tests can point at a fixture
    directory without polluting the shared cache.
    """
    global _system_docs_cache

    if kb_system_dir is None and _system_docs_cache is not None:
        return _system_docs_cache

    directory = kb_system_dir or _resolve_kb_system_dir()
    docs = load_documents(directory)
    combined = "\n\n".join(d.text.strip() for d in docs if d.text.strip())

    if kb_system_dir is None:
        _system_docs_cache = combined
    return combined


def reset_system_documents_cache() -> None:
    """Test helper - clears the process-wide System Documents cache."""
    global _system_docs_cache
    _system_docs_cache = None


def _format_sql_context(sql_context: "dict | None") -> str:
    if not sql_context:
        return "(none for this intent)"
    return json.dumps(sql_context, indent=2, default=str)


def _format_rag_context(rag_context: "list[dict] | None") -> str:
    if not rag_context:
        return "(none retrieved for this turn)"

    parts = []
    for chunk in rag_context:
        doc_id = chunk.get("doc_id", "unknown_document")
        section_title = chunk.get("section_title") or ""
        text = chunk.get("text", "")
        header = f"[{doc_id}" + (f" - {section_title}]" if section_title else "]")
        parts.append(f"{header}\n{text}")
    return "\n\n".join(parts)


def _format_history(history: "list[dict] | None") -> str:
    if not history:
        return "(no prior turns)"

    lines = []
    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def build_prompt(
    user_context: dict,
    intent_name: str,
    message: str,
    sql_context: "dict | None" = None,
    rag_context: "list[dict] | None" = None,
    history: "list[dict] | None" = None,
) -> str:
    """Assemble the full Gemini prompt for one ``/api/ai/chat`` turn.

    ``user_context`` is the already-resolved dict routes.py builds
    (``user_id``/``full_name``/``role``) - included only so the model
    knows who it is addressing in its reply; it grants the model no
    additional data access. The only data the model can actually draw
    on is whatever is already present in ``sql_context``/``rag_context``,
    which the caller must only pass in once authorized.
    """
    system_docs = load_system_documents()

    sql_present = bool(sql_context)
    priority_note = (
        "PRIORITY RULE: SQL context below, when present, is the complete, "
        "authoritative, already-personalized answer for this user and this "
        "turn - it has already been fetched and scoped specifically to "
        "answer this message. Lead your answer with it directly. Use the "
        "knowledge base excerpts only to explain process/mechanics the SQL "
        "context doesn't cover. Do NOT fall back to a generic dashboard "
        "pointer (e.g. 'check your X tab') when the SQL context already "
        "contains the specific fact being asked for - only redirect to the "
        "dashboard per Section 9's rules when no synthesis is being asked "
        "for and the fact is truly just a bare lookup with no context added."
        if sql_present
        else "No SQL context was fetched for this turn (this intent has none, "
        "or none applied) - answer from the knowledge base excerpts and "
        "system documents only; do not invent personalized figures."
    )

    sections = [
        system_docs,
        "---",
        priority_note,
        "",
        f"Authenticated user: {user_context.get('full_name', 'unknown')} "
        f"(role: {user_context.get('role', 'unknown')})",
        f"Detected intent: {intent_name}",
        "",
        "SQL context (already scoped and authorized for this user) - HIGHEST PRIORITY source for this turn:",
        _format_sql_context(sql_context),
        "",
        "Retrieved knowledge base excerpts (already scoped and authorized for this user) - SECONDARY source, for process/mechanics only:",
        _format_rag_context(rag_context),
        "",
        "Conversation history:",
        _format_history(history),
        "",
        f"User message: {message}",
    ]
    return "\n".join(sections)
