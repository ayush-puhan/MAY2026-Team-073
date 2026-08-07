"""ClubConnect AI Assistant - Intent Router + Authorization (Phase 2).

Implements Gateway stages 1-2 from
docs/ClubConnect_AI_Documentation/Architecture/ClubConnect_AI_Architecture_V2.md
(Task 7): Intent Detection and Authorization Check. Nothing past this
point is implemented here - see NEXT_PHASE.md for Phase 3 onward.

Design notes (per NEXT_PHASE.md scope for this phase):
    - The Task 2 intent catalog is encoded as a plain data structure
      (``INTENT_CATALOG``) - no rules engine, no ML classifier training.
    - Classification is a keyword/regex pre-filter only. Architecture V2
      itself allows deferring the Gemini classification fallback when the
      keyword pass is judged sufficient for a phase ("if the keyword pass
      alone is judged sufficient for Phase 2, defer the Gemini dependency
      to Phase 5" - NEXT_PHASE.md). That path is taken here: no Gemini
      call, no new dependency, `requirements.txt` untouched. Messages the
      keyword pass can't confidently resolve fall through to the
      "Ambiguous Request" intent (itself part of the Task 2 catalog),
      which is the correct behavior per the catalog rather than a stand-in
      for a missing classifier - Section 5 of
      assistant_conversation_behavior.md already directs the assistant to
      ask a single clarifying question in exactly this case.
    - Authorization distinguishes ``users.role`` (platform-level) from
      ``club_memberships.role_in_club`` (club-scoped), per
      assistant_conversation_behavior.md Section 1 and NEXT_PHASE.md's
      "Risks" section. Per Architecture V2 Task 1.1 #4, most intents are
      role-orthogonal (any authenticated role may reach them; SQL scoping
      -- Phase 3 -- handles personalization/visibility). Only the handful
      of intents the catalog and NEXT_PHASE.md call out explicitly as
      role-gated ("a student cannot reach 'Admin Questions' or 'Financial
      Operations' as a treasurer-only action for a club they don't hold
      that role in") are restricted here.
"""
import re
from dataclasses import dataclass, field
from typing import Optional

from app.database.enums import ClubMemberRole, UserRole

# ---------------------------------------------------------------------------
# Task 2 intent catalog (subset of fields needed for Phase 2; sql_tables and
# rag_docs are carried now so Phases 3-4 can consume this same catalog
# without re-deriving it from the architecture doc a second time).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntentDefinition:
    name: str
    description: str
    sql_tables: tuple = ()
    rag_docs: tuple = ()
    keywords: tuple = ()
    # None = role-orthogonal (any authenticated platform role may reach it).
    allowed_platform_roles: Optional[frozenset] = None
    # If set, the user must additionally hold this club-scoped role in at
    # least one club (checked alongside allowed_platform_roles, not instead
    # of it - either condition being true grants access).
    requires_club_role: Optional[ClubMemberRole] = None


INTENT_CATALOG: "dict[str, IntentDefinition]" = {}


def _register(intent: IntentDefinition) -> None:
    INTENT_CATALOG[intent.name] = intent


_register(IntentDefinition(
    name="Emergency Reporting",
    description="Harassment/safety/medical reports - never LLM-resolved.",
    sql_tables=("emergency_reports",),
    rag_docs=("helpdesk_support_guide.md",),
    keywords=(
        "harass", "harassment", "assault", "unsafe", "in danger", "emergency",
        "medical emergency", "someone is following", "wheelchair assistance",
        "hurt myself", "hurt someone",
    ),
    allowed_platform_roles=None,  # every role must always be able to reach this
))

_register(IntentDefinition(
    name="Getting Started",
    description="New/returning user orientation, what ClubConnect does.",
    sql_tables=("users", "student_profiles"),
    rag_docs=("platform_getting_started.md",),
    keywords=("what is this app", "how do i start", "just signed up", "new here", "getting started"),
))

_register(IntentDefinition(
    name="Navigation",
    description="Where do I find X, for existing users.",
    sql_tables=("users",),
    rag_docs=("platform_getting_started.md",),
    keywords=("where do i find", "where is", "where can i see", "how do i get to", "navigate to"),
))

_register(IntentDefinition(
    name="Club Discovery",
    description="Browsing/searching clubs by category, name, keyword.",
    sql_tables=("clubs", "club_interests"),
    rag_docs=(),
    keywords=("show me clubs", "find a club", "is there a", "list clubs", "tech clubs", "search clubs"),
))

_register(IntentDefinition(
    name="Club Recommendation",
    description="Personalized club suggestions.",
    sql_tables=("user_interests", "club_interests", "club_memberships", "student_profiles"),
    rag_docs=(),
    keywords=("recommend club", "recommend clubs", "clubs for me", "clubs should i join", "clubs match my interests"),
))

_register(IntentDefinition(
    name="Event Recommendation",
    description="Personalized event suggestions.",
    sql_tables=("events", "event_interests", "event_registrations", "attendance_records", "club_memberships"),
    rag_docs=(),
    keywords=("recommend event", "events should i attend", "events for me", "workshops i'd like"),
))

_register(IntentDefinition(
    name="Membership Process",
    description="Explaining the general apply->approve flow.",
    sql_tables=(),
    rag_docs=("membership_process_guide.md",),
    keywords=("how do i join", "how to join a club", "what happens after i apply", "join a club"),
))

_register(IntentDefinition(
    name="Application Status",
    description="User's specific application state.",
    sql_tables=("club_join_applications",),
    rag_docs=("membership_process_guide.md",),
    keywords=(
        "did i get into", "my application", "application still pending", "application status",
        "applications are pending", "applications pending", "any pending applications",
        "what applications are pending",
    ),
))

_register(IntentDefinition(
    name="Membership",
    description="The user's own current (approved) club memberships - distinct from Membership Process (how joining works) and Application Status (a pending/decided application).",
    sql_tables=("club_memberships",),
    rag_docs=(),
    keywords=(
        "which clubs am i", "what clubs am i", "clubs am i a member",
        "clubs am i currently a member", "my memberships", "my current clubs",
        "clubs i belong to", "clubs i'm in", "clubs i am in", "list my clubs",
    ),
))

_register(IntentDefinition(
    name="Event Registration",
    description="Explaining registration/check-in mechanics.",
    sql_tables=(),
    rag_docs=("event_lifecycle_guide.md",),
    keywords=("how do i register for an event", "how does check-in work", "register for the event"),
))

_register(IntentDefinition(
    name="Attendance",
    description="User's own attendance record.",
    sql_tables=("attendance_records", "event_registrations"),
    rag_docs=("event_lifecycle_guide.md",),
    keywords=(
        "marked present", "was i marked", "my attendance", "did i attend",
        "am i registered", "which events am i registered", "what events am i registered",
        "events am i registered for", "my registrations", "my event registrations",
    ),
))

_register(IntentDefinition(
    name="Rewards",
    description="Points system mechanics + personal balance.",
    sql_tables=("reward_points_ledger", "reward_task_completions", "reward_redemptions"),
    rag_docs=("rewards_system_guide.md",),
    keywords=("reward points", "how many points", "points do i have", "redeem points"),
))

_register(IntentDefinition(
    name="Announcements",
    description="What's new / how announcements work.",
    sql_tables=("announcements",),
    rag_docs=("platform_getting_started.md",),
    keywords=("any new announcements", "announcements", "what's new", "did the club post"),
))

_register(IntentDefinition(
    name="Club Creation & Governance",
    description="Proposing a new club, tracking a proposal.",
    sql_tables=("club_creation_requests",),
    rag_docs=("club_creation_governance_guide.md",),
    keywords=("start a new club", "create a club", "club proposal", "propose a club"),
))

_register(IntentDefinition(
    name="Support Tickets",
    description="Raising/tracking a helpdesk ticket.",
    sql_tables=("support_tickets", "ticket_responses"),
    rag_docs=("helpdesk_support_guide.md",),
    keywords=("report a bug", "helpdesk", "support ticket", "is my ticket resolved", "raise a ticket"),
))

_register(IntentDefinition(
    name="Financial Operations",
    description="Budget/expense process + own club's figures (treasurer/faculty).",
    sql_tables=("budgets", "expenses"),
    rag_docs=("financial_operations_guide.md",),
    keywords=(
        "submit an expense", "budget utilization", "our budget", "reimbursement", "club budget",
        "financial summary", "my finances", "our finances", "expense summary",
        "budgets need approval", "budget approval", "budgets pending approval",
        "what budgets need approval", "pending budgets", "budgets are pending approval",
    ),
    allowed_platform_roles=frozenset({UserRole.FACULTY_ADVISOR}),
    requires_club_role=ClubMemberRole.TREASURER,
))

_register(IntentDefinition(
    name="Faculty Questions",
    description="Oversight of advised clubs.",
    sql_tables=("clubs", "events", "expenses"),
    rag_docs=("event_lifecycle_guide.md", "financial_operations_guide.md"),
    keywords=(
        "waiting on my approval", "events waiting for approval", "advised clubs",
        "clubs do i advise", "clubs i advise", "my advised clubs",
    ),
    allowed_platform_roles=frozenset({UserRole.FACULTY_ADVISOR}),
))

_register(IntentDefinition(
    name="Admin Questions",
    description="Platform-wide oversight, club approvals.",
    sql_tables=("club_creation_requests",),
    rag_docs=("club_creation_governance_guide.md", "platform_getting_started.md"),
    keywords=(
        "summarize this week's", "new club proposals", "platform-wide", "all club proposals",
        "inactive clubs", "active clubs", "most active club", "club statistics",
        "university statistics", "university club statistics", "engagement trends",
        "engagement metrics", "platform-wide engagement",
    ),
    allowed_platform_roles=frozenset({
        UserRole.STUDENT_AFFAIRS_OFFICE,
        UserRole.DEAN_STUDENT_WELFARE,
        UserRole.SYSTEM_ADMIN,
    }),
))

_register(IntentDefinition(
    name="Profile & Account",
    description="Editing profile, verification status, accessibility prefs.",
    sql_tables=("users", "student_profiles"),
    rag_docs=("platform_getting_started.md",),
    keywords=("change my profile", "am i verified", "my profile photo", "my account"),
))

_register(IntentDefinition(
    name="Role Capabilities Q&A",
    description="What can I do as a <role>.",
    sql_tables=("users",),
    # role_permissions_reference.md is the authoritative per-role detail
    # doc (Phase 6 final polish); platform_getting_started.md stays
    # listed too since it still carries the two-role-layer explanation
    # (platform role vs role_in_club) this intent also needs.
    rag_docs=("platform_getting_started.md", "role_permissions_reference.md"),
    keywords=(
        "what can i do as", "my capabilities", "what am i allowed to do",
        "what can a", "what does a", "difference between president and vice president",
        "difference between a president and a vice president",
        "can a student approve", "who approves club creation", "who can manage expenses",
        "what permissions does", "permission matrix", "what permissions",
    ),
))

_register(IntentDefinition(
    name="Ambiguous Request",
    description="Underspecified ask, or nothing else matched confidently.",
    sql_tables=(),
    rag_docs=(),
    keywords=(),  # never matched directly - this is the fallback intent
))

_register(IntentDefinition(
    name="Out-of-Scope",
    description="Off-topic, unauthorized data, homework help, etc.",
    sql_tables=(),
    rag_docs=(),
    keywords=("do my homework", "do my calculus", "write my essay", "phone number of", "another student's"),
))


# ---------------------------------------------------------------------------
# Stage 1: Intent Detection (keyword pre-filter)
# ---------------------------------------------------------------------------

# Checked in this order so higher-priority / more specific intents win over
# broader ones when a message could plausibly match more than one (e.g.
# "emergency" must never lose to "support ticket").
_DETECTION_ORDER = (
    "Emergency Reporting",
    "Out-of-Scope",
    "Club Recommendation",
    "Event Recommendation",
    "Membership",
    "Application Status",
    "Attendance",
    "Rewards",
    "Announcements",
    "Admin Questions",
    "Club Creation & Governance",
    "Support Tickets",
    "Financial Operations",
    "Faculty Questions",
    "Role Capabilities Q&A",
    "Profile & Account",
    "Membership Process",
    "Event Registration",
    "Navigation",
    "Club Discovery",
    "Getting Started",
)


def detect_intent(message: str) -> str:
    """Keyword/regex pre-filter over the Task 2 intent catalog.

    Returns the matched intent name, or "Ambiguous Request" if nothing in
    the catalog matches confidently. No Gemini fallback call is made here
    (see module docstring) - deferred to Phase 5.
    """
    if not message or not message.strip():
        return "Ambiguous Request"

    text = message.lower()

    for intent_name in _DETECTION_ORDER:
        intent = INTENT_CATALOG[intent_name]
        for kw in intent.keywords:
            if kw in text:
                return intent_name

    return "Ambiguous Request"


# ---------------------------------------------------------------------------
# Stage 2: Authorization Check
# ---------------------------------------------------------------------------


def _role_value(role) -> Optional[str]:
    """Normalize a UserRole/ClubMemberRole (enum or raw string) to its value."""
    if role is None:
        return None
    return role.value if hasattr(role, "value") else role


def authorize_intent(intent_name: str, user_role, club_roles=()) -> bool:
    """Authorization Check (Gateway stage 2).

    Args:
        intent_name: an intent name from INTENT_CATALOG (as returned by
            detect_intent, or already known some other way).
        user_role: the authenticated user's platform-level `users.role`
            (UserRole enum or its string value).
        club_roles: an iterable of the user's club-scoped
            `club_memberships.role_in_club` values (across all their club
            memberships), used only for intents with `requires_club_role`.

    Returns:
        True if the user's role(s) permit reaching this intent at all.
        This is *not* row-level authorization - that's enforced later by
        SQL scoping (Phase 3), per assistant_conversation_behavior.md
        Section 10 ("authorization is enforced by the SQL context-builder
        ... before it ever reaches the model").
    """
    intent = INTENT_CATALOG.get(intent_name)
    if intent is None:
        # Unknown intent name - fail closed rather than silently allowing.
        return False

    if intent.allowed_platform_roles is None and intent.requires_club_role is None:
        return True  # role-orthogonal intent, per Architecture V2 Task 1.1 #4

    user_role_value = _role_value(user_role)
    allowed_role_values = None
    if intent.allowed_platform_roles is not None:
        allowed_role_values = {_role_value(r) for r in intent.allowed_platform_roles}
        if user_role_value in allowed_role_values:
            return True

    if intent.requires_club_role is not None:
        required_value = _role_value(intent.requires_club_role)
        club_role_values = {_role_value(r) for r in club_roles}
        if required_value in club_role_values:
            return True

    return False


# ---------------------------------------------------------------------------
# Stage 1 fallback: Gemini classifier (Phase 5A)
#
# Deferred from Phase 2 ("if the keyword pass alone is judged sufficient
# for Phase 2, defer the Gemini dependency to Phase 5" - NEXT_PHASE.md).
# Only ever called by routes.py when detect_intent() has already
# returned "Ambiguous Request" - this is a fallback for the messages the
# keyword pass can't resolve, not a second classification path that
# runs on every message.
# ---------------------------------------------------------------------------


def classify_ambiguous(message: str) -> str:
    """Ask Gemini to pick the best-fitting catalog intent for a message
    the keyword pre-filter couldn't confidently resolve.

    On any failure - missing API key, network/SDK error, or a response
    that isn't a recognized intent name - falls back to "Ambiguous
    Request" rather than raising. An LLM outage must never break the
    chat endpoint (NFR: Reliability/Availability).
    """
    from app.modules.ai_services.gemini_client import (
        GeminiConfigError,
        GeminiRequestError,
        generate_response,
    )

    candidate_names = [name for name in INTENT_CATALOG if name != "Ambiguous Request"]
    catalog_listing = "\n".join(f"- {name}: {INTENT_CATALOG[name].description}" for name in candidate_names)

    prompt = (
        "You are an intent classifier for the ClubConnect Assistant. "
        "Given the user message below, respond with ONLY the single "
        "best-matching intent name from this list, exactly as written, "
        "and nothing else. If none genuinely fit, respond with exactly "
        "\"Ambiguous Request\".\n\n"
        f"{catalog_listing}\n\n"
        f"User message: {message}"
    )

    try:
        raw = generate_response(prompt)
    except (GeminiConfigError, GeminiRequestError):
        return "Ambiguous Request"
    except Exception:
        # Belt-and-suspenders: any other unexpected failure still must
        # not break the endpoint.
        return "Ambiguous Request"

    candidate = raw.strip().strip('"').strip("'")
    return candidate if candidate in INTENT_CATALOG else "Ambiguous Request"
