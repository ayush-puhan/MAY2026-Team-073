"""ClubConnect AI Assistant - Financial & Performance Analytics (Phase 6B).

Same "backend computes, Gemini interprets" split the Phase 6B spec
calls for: every number here (utilization %, breakdowns, chart data)
is computed in this module from data already returned by the existing,
unmodified SQL Context Builders (plus ``report_context.py``'s Phase 6B
additions) - Gemini is only asked to explain what the numbers mean in
plain language. No prediction, no forecasting, no ML.
"""
from app.database.enums import ClubMemberRole, UserRole
from app.modules.ai_services.gemini_client import generate_response
from app.modules.ai_services.report_context import (
    build_club_activity_context,
    resolve_club_activity_scope,
)
from app.modules.ai_services.sql_context_builder import (
    build_admin_overview_context,
    build_attendance_context,
    build_faculty_questions_context,
    build_financial_operations_context,
    build_membership_context,
    build_rewards_context,
)


def _role_value(value):
    if value is None:
        return None
    return value.value if hasattr(value, "value") else value


# ---------------------------------------------------------------------------
# Financial Analytics
# ---------------------------------------------------------------------------

FINANCIAL_ANALYTICS_ROLES = frozenset({
    UserRole.FACULTY_ADVISOR,
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE,
    UserRole.SYSTEM_ADMIN,
})


def financial_analytics_access(user, club_roles) -> bool:
    """Per Phase 6B spec Section 2: Treasurer, Faculty Advisor, Student
    Affairs Office, Dean of Student Welfare, System Admin only."""
    if ClubMemberRole.TREASURER.value in {_role_value(r) for r in club_roles}:
        return True
    return _role_value(user.role) in {r.value for r in FINANCIAL_ANALYTICS_ROLES}


def _budget_utilization_chart(clubs: list) -> dict:
    """Bar chart: allocated vs. claimed per club - computed here, not
    by Gemini, per the "backend computes" rule."""
    labels = [c["club_name"] for c in clubs]
    return {
        "type": "bar",
        "labels": labels,
        "series": [
            {"name": "Allocated", "values": [c["total_allocated_amount"] for c in clubs]},
            {"name": "Claimed", "values": [c["total_expenses_claimed"] for c in clubs]},
        ],
    }


def build_financial_analytics(db, user) -> dict:
    """Budget summary, expense summary, pending approvals, and
    utilization for every club the caller treasurers/advises - reuses
    ``build_financial_operations_context`` (unmodified) for the raw
    figures, and adds a computed utilization percentage plus chart data
    on top.
    """
    context = build_financial_operations_context(db, user)
    clubs = context.get("clubs", [])

    for club in clubs:
        allocated = club.get("total_allocated_amount", 0) or 0
        claimed = club.get("total_expenses_claimed", 0) or 0
        club["utilization_percent"] = round((claimed / allocated) * 100, 1) if allocated else 0.0

    pending_total = sum(c.get("expense_approval_breakdown", {}).get("pending", 0) for c in clubs)

    analytics = {
        "clubs": clubs,
        "total_pending_approvals": pending_total,
    }
    chart = _budget_utilization_chart(clubs) if clubs else None

    return {"analytics": analytics, "chart": chart}


# ---------------------------------------------------------------------------
# Performance Analytics
# ---------------------------------------------------------------------------


def build_performance_analytics(db, user, club_roles=()) -> dict:
    """Role-scoped performance analytics, per Phase 6B spec Section 3.

    - Student (no officer role, not faculty/admin-tier): personal
      attendance/participation/rewards/club-involvement figures.
    - Club leadership or faculty advisor: club health for the clubs
      they lead/advise (plus faculty's pending-approvals view).
    - Admin-tier: platform-wide engagement (reuses
      ``build_admin_overview_context``, unmodified).
    """
    role_value = _role_value(user.role)

    if role_value in {UserRole.STUDENT_AFFAIRS_OFFICE.value, UserRole.DEAN_STUDENT_WELFARE.value,
                       UserRole.SYSTEM_ADMIN.value}:
        overview = build_admin_overview_context(db, user)
        chart = {
            "type": "bar",
            "labels": list(overview.get("club_status_breakdown", {}).keys()),
            "series": [{"name": "Clubs", "values": list(overview.get("club_status_breakdown", {}).values())}],
        }
        return {"scope": "platform", "analytics": overview, "chart": chart}

    if role_value == UserRole.FACULTY_ADVISOR.value:
        faculty = build_faculty_questions_context(db, user)
        club_ids, _ = resolve_club_activity_scope(db, user)
        activity = build_club_activity_context(db, user)
        return {
            "scope": "advised_clubs",
            "analytics": {**faculty, "club_activity": activity["clubs"]},
            "chart": None,
        }

    officer_roles = {ClubMemberRole.VOLUNTEER_COORDINATOR.value, ClubMemberRole.EVENT_COORDINATOR.value,
                      ClubMemberRole.SECRETARY.value, ClubMemberRole.TREASURER.value,
                      ClubMemberRole.VICE_PRESIDENT.value, ClubMemberRole.PRESIDENT.value}
    if officer_roles & {_role_value(r) for r in club_roles}:
        activity = build_club_activity_context(db, user)
        clubs = activity["clubs"]
        chart = {
            "type": "bar",
            "labels": [c["club_name"] for c in clubs],
            "series": [{"name": "Members", "values": [c["member_count_cache"] for c in clubs]}],
        } if clubs else None
        return {"scope": "led_clubs", "analytics": activity, "chart": chart}

    # Default: personal performance (student, or any role with no
    # leadership/advisor/admin standing).
    memberships = build_membership_context(db, user)
    attendance = build_attendance_context(db, user)
    rewards = build_rewards_context(db, user)
    analytics = {
        "club_involvement": memberships["memberships"],
        "attendance": attendance,
        "rewards": rewards,
    }
    chart = {
        "type": "bar",
        "labels": ["Registered", "Attended"],
        "series": [{"name": "Events", "values": [attendance["total_registered"], attendance["total_attended"]]}],
    }
    return {"scope": "personal", "analytics": analytics, "chart": chart}


_ANALYTICS_PROMPT_INSTRUCTIONS = (
    "You are interpreting analytics data for a university club management "
    "platform. The numbers below were computed by the backend - do not "
    "recompute, predict, or forecast anything; only explain what the "
    "figures show, note anything that stands out (e.g. high utilization, "
    "a club with no recent activity), and keep it factual and concise "
    "(a few short paragraphs, plain language, no markdown headers)."
)


def interpret_analytics(analytics: dict, user, label: str) -> str:
    """Backend-computed analytics -> a short Gemini-written explanation."""
    import json
    prompt = (
        f"{_ANALYTICS_PROMPT_INSTRUCTIONS}\n\n"
        f"Analytics type: {label}\n"
        f"Prepared for: {user.full_name} (role: {_role_value(user.role)})\n\n"
        f"Data:\n{json.dumps(analytics, indent=2, default=str)}"
    )
    return generate_response(prompt)
