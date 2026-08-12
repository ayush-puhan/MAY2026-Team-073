"""ClubConnect AI Assistant - AI Report Generation (Phase 6B).

New feature, not part of the Architecture V2 chat gateway
(``/api/ai/chat``) - a report is a one-shot "generate a summary of X"
request, not a conversational turn, so it doesn't go through
``intent_router``/``prompt_builder``/the RAG pipeline at all. It does,
however, fully reuse:

    - the existing SQL Context Builders (``sql_context_builder.py``,
      unmodified) for the report types they already cover personally
      (attendance, membership, rewards, support tickets, financial
      operations for a treasurer/advisor's own clubs);
    - the new Phase 6B-only aggregations in ``report_context.py`` for
      the report types nothing existing covers (club activity,
      volunteer, emergency summary, platform-wide budget);
    - ``gemini_client.generate_response`` for turning the backend-
      computed context into a short professional report.

Backend computes every figure; Gemini only writes the prose. No
prediction, no forecasting - the same "backend computes, Gemini
explains" rule the Phase 6B spec calls out for analytics applies here
too, since a report is one Gemini call short of an analytics response.

Never fabricates: every report is grounded in a context dict built
the same defensive, "empty is a normal, non-exceptional result" way
as every builder in ``sql_context_builder.py``.
"""
from app.database.enums import ClubMemberRole, UserRole
from app.modules.ai_services.gemini_client import generate_response
from app.modules.ai_services.report_context import (
    ADMIN_TIER_ROLES,
    build_budget_platform_context,
    build_club_activity_context,
    build_emergency_summary_context,
    build_volunteer_report_context,
    officer_club_ids,
)
from app.modules.ai_services.sql_context_builder import (
    build_attendance_context,
    build_financial_operations_context,
    build_membership_context,
    build_rewards_context,
    build_support_tickets_context,
)


def _role_value(value):
    if value is None:
        return None
    return value.value if hasattr(value, "value") else value


def _is_admin_tier(user) -> bool:
    return _role_value(user.role) in {r.value for r in ADMIN_TIER_ROLES}


def _is_faculty(user) -> bool:
    return _role_value(user.role) == UserRole.FACULTY_ADVISOR.value


def _is_treasurer(club_roles) -> bool:
    return ClubMemberRole.TREASURER.value in {_role_value(r) for r in club_roles}


def _is_leadership(club_roles) -> bool:
    officer_values = {_role_value(r) for r in [
        ClubMemberRole.VOLUNTEER_COORDINATOR, ClubMemberRole.EVENT_COORDINATOR,
        ClubMemberRole.SECRETARY, ClubMemberRole.TREASURER,
        ClubMemberRole.VICE_PRESIDENT, ClubMemberRole.PRESIDENT,
    ]}
    return bool(officer_values & {_role_value(r) for r in club_roles})


# ---------------------------------------------------------------------------
# Report catalog: report_type -> (label, context_builder, access_check)
#
# Every access_check takes (user, club_roles) and returns True/False -
# same shape intent_router.authorize_intent uses, kept local to this
# module because reports aren't intents and don't belong in that
# catalog (per "do not modify intent_router.py").
#
# Personal report types (student_activity, attendance, membership,
# reward, support_ticket, volunteer) are role-orthogonal by design -
# every authenticated role may generate a report about their own
# activity, per Phase 6B spec Section 5 ("Students: Personal reports").
# ---------------------------------------------------------------------------


def _always_allowed(_user, _club_roles) -> bool:
    return True


def _club_activity_access(_user, _club_roles) -> bool:
    # Anyone can call this; resolve_club_activity_scope() in
    # report_context.py naturally returns an empty club list (an
    # honest "nothing to report" result, not a 403) for a caller with
    # no officer/advisor/admin-tier standing anywhere. Gating happens
    # at the data-scope layer rather than a hard role allowlist here,
    # matching how build_financial_operations_context re-derives scope
    # from the caller's own rows rather than trusting a yes/no.
    return True


def _budget_access(user, club_roles) -> bool:
    # NOTE (Phase 6B stabilization QA): a user whose *platform* role is
    # "student" can still pass this check if they hold a club-scoped
    # TREASURER role somewhere - that's intentional, not a leak. The
    # report is then scoped to only that person's own treasurer clubs
    # by _budget_context()/build_financial_operations_context(), the
    # same pattern the "Financial Operations" chat intent uses. Flagged
    # during manual API testing as a possible RBAC issue and confirmed
    # correct: verified the student in that test case (`user_id=3`) is
    # the actual TREASURER of record for both clubs in the response.
    return _is_treasurer(club_roles) or _is_faculty(user) or _is_admin_tier(user)


def _emergency_access(user, _club_roles) -> bool:
    return _is_admin_tier(user)


def _student_activity_context(db, user, **_kwargs):
    """Combined personal snapshot: membership + attendance + rewards +
    open support tickets - the "Student Activity Report" from the
    Phase 6B spec. Each piece reuses an existing, unmodified builder;
    this function only concatenates their already-summarized output."""
    return {
        "memberships": build_membership_context(db, user)["memberships"],
        "attendance": build_attendance_context(db, user),
        "rewards": build_rewards_context(db, user),
        "open_support_tickets": [
            t for t in build_support_tickets_context(db, user)["tickets"]
            if t.get("status") not in ("resolved", "closed")
        ],
    }


def _budget_context(db, user, **_kwargs):
    """Treasurer/faculty use their own club(s)' figures (existing
    builder, unmodified); an admin-tier caller with no club of their
    own gets the platform-wide aggregate instead."""
    own_clubs = build_financial_operations_context(db, user)
    if own_clubs.get("clubs"):
        return own_clubs
    return build_budget_platform_context(db, user)


REPORT_TYPES = {
    "student_activity": ("Student Activity Report", _student_activity_context, _always_allowed),
    "attendance": ("Attendance Report", build_attendance_context, _always_allowed),
    "membership": ("Membership Report", build_membership_context, _always_allowed),
    "reward": ("Reward Report", build_rewards_context, _always_allowed),
    "support_ticket": ("Support Ticket Report", build_support_tickets_context, _always_allowed),
    "volunteer": ("Volunteer Report", build_volunteer_report_context, _always_allowed),
    "club_activity": ("Club Activity Report", build_club_activity_context, _club_activity_access),
    "budget": ("Budget Report", _budget_context, _budget_access),
    "emergency_summary": ("Emergency Report Summary", build_emergency_summary_context, _emergency_access),
}


_REPORT_PROMPT_INSTRUCTIONS = (
    "You are writing a concise, professional report for a university club "
    "management platform. Use ONLY the JSON data below - never invent a "
    "figure, name, or event that isn't present in it. If a list is empty, "
    "say so plainly rather than describing placeholder activity. Structure "
    "the report as short paragraphs or bullet points, in plain business "
    "language, no more than a few hundred words. Do not use markdown "
    "headers. Field names describe counts of events for the report's "
    "subject, not counts of people - e.g. 'total_registered' is the number "
    "of events this person registered for, and 'total_attended' is the "
    "number of events they attended; do not phrase these as a number of "
    "registered users or attendees."
)


def generate_report(report_type: str, db, user, club_roles=()) -> dict:
    """Generate one AI report.

    Returns {"report_type", "label", "authorized", "data", "summary"} on
    success. When ``report_type`` is unknown, ``authorized`` is False
    and ``summary``/``data`` are both None - callers (routes.py) map
    that to a 400, not a 404/403, since it's a client input error, not
    an access-control decision.
    """
    entry = REPORT_TYPES.get(report_type)
    if entry is None:
        return {
            "report_type": report_type,
            "label": None,
            "authorized": False,
            "data": None,
            "summary": None,
        }

    label, context_builder, access_check = entry
    authorized = access_check(user, club_roles)
    if not authorized:
        return {
            "report_type": report_type,
            "label": label,
            "authorized": False,
            "data": None,
            "summary": None,
        }

    data = context_builder(db, user)

    prompt = (
        f"{_REPORT_PROMPT_INSTRUCTIONS}\n\n"
        f"Report type: {label}\n"
        f"Prepared for: {user.full_name} (role: {_role_value(user.role)})\n\n"
        f"Data:\n{_json_dumps(data)}"
    )
    summary = generate_response(prompt)

    return {
        "report_type": report_type,
        "label": label,
        "authorized": True,
        "data": data,
        "summary": summary,
    }


def _json_dumps(data) -> str:
    import json
    return json.dumps(data, indent=2, default=str)
