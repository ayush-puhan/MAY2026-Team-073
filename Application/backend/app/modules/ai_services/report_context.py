"""ClubConnect AI Assistant - Report/Analytics SQL Context (Phase 6B).

Companion to ``sql_context_builder.py`` (Phase 3/5B/6), which is left
untouched per project instructions ("DO NOT MODIFY ... SQL Context
Builders"). This module adds the handful of aggregations Phase 6B's
report/analytics endpoints need that no existing builder already
covers: per-club activity snapshots (for club leadership/faculty/
admin), a personal volunteer-assignment summary, an admin-tier
emergency-report summary, and a platform-wide budget aggregate for
admin-tier roles who aren't themselves a treasurer/advisor.

Same conventions as ``sql_context_builder.py``:
    - Every function returns an already-summarized, JSON-safe dict -
      never raw ORM rows.
    - Defensive against empty tables - "nothing on file" is a normal,
      non-exceptional result.
    - Column-projected / scoped queries only; no unscoped table scans
      exposed to a caller who shouldn't see other users'/clubs' rows.
    - Row-level scope (which clubs, which university) is re-derived
      from the caller's own data here, not trusted from an intent-level
      yes/no - same pattern as ``build_financial_operations_context``.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.database.enums import ClubMemberRole, MembershipStatus, UserRole
from app.database.models.applications import ClubJoinApplication
from app.database.models.auth import User
from app.database.models.clubs import Club, ClubMembership
from app.database.models.events import Event, VolunteerAssignment
from app.database.models.finance import Budget, Expense
from app.database.models.support import EmergencyReport

# Club-scoped roles treated as "club leadership" for report/analytics
# access - everything above a bare MEMBER/APPLICANT. Matches the
# officer-role set implied by club_creation_governance_guide.md and
# mirrors ClubMemberRole's ordering in enums.py.
OFFICER_ROLES = frozenset({
    ClubMemberRole.VOLUNTEER_COORDINATOR,
    ClubMemberRole.EVENT_COORDINATOR,
    ClubMemberRole.SECRETARY,
    ClubMemberRole.TREASURER,
    ClubMemberRole.VICE_PRESIDENT,
    ClubMemberRole.PRESIDENT,
})

ADMIN_TIER_ROLES = frozenset({
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE,
    UserRole.SYSTEM_ADMIN,
})


def _role_value(value) -> Optional[str]:
    if value is None:
        return None
    return value.value if hasattr(value, "value") else value


def _enum_value(value) -> Optional[str]:
    if value is None:
        return None
    return value.value if hasattr(value, "value") else value


def _iso(dt) -> Optional[str]:
    return dt.isoformat() if dt is not None else None


def officer_club_ids(db: Session, user_id: int) -> list:
    """Club IDs where the user holds an APPROVED officer-tier
    ``role_in_club`` (see ``OFFICER_ROLES``)."""
    rows = (
        db.query(ClubMembership.club_id)
        .filter(
            ClubMembership.user_id == user_id,
            ClubMembership.status == MembershipStatus.APPROVED,
            ClubMembership.role_in_club.in_(OFFICER_ROLES),
        )
        .distinct()
        .all()
    )
    return [club_id for (club_id,) in rows]


def advised_club_ids(db: Session, user_id: int) -> list:
    """Club IDs where the user is the club's ``faculty_advisor_id``."""
    rows = db.query(Club.id).filter(Club.faculty_advisor_id == user_id).all()
    return [club_id for (club_id,) in rows]


# ---------------------------------------------------------------------------
# Club Activity Report / club-level Performance Analytics
# ---------------------------------------------------------------------------


def _club_activity_snapshot(db: Session, club_ids: list) -> list:
    """Per-club activity summary for the given club IDs.

    Returns a list of {"club_name", "status", "category",
    "member_count_cache", "event_status_breakdown": {status: count},
    "pending_join_applications_count"} - one entry per club that
    resolves, in the same "already summarized, never raw ORM" style as
    ``sql_context_builder._club_financial_snapshot``.
    """
    if not club_ids:
        return []

    clubs = db.query(Club).filter(Club.id.in_(club_ids)).all()

    event_breakdown_by_club = {cid: {} for cid in club_ids}
    for club_id, status in (
        db.query(Event.club_id, Event.status).filter(Event.club_id.in_(club_ids)).all()
    ):
        status_value = _enum_value(status)
        bucket = event_breakdown_by_club.setdefault(club_id, {})
        bucket[status_value] = bucket.get(status_value, 0) + 1

    pending_apps_by_club = {cid: 0 for cid in club_ids}
    for (club_id,) in (
        db.query(ClubJoinApplication.club_id)
        .filter(
            ClubJoinApplication.club_id.in_(club_ids),
            ClubJoinApplication.status == MembershipStatus.PENDING,
        )
        .all()
    ):
        pending_apps_by_club[club_id] = pending_apps_by_club.get(club_id, 0) + 1

    return [
        {
            "club_name": club.name,
            "status": _enum_value(club.status),
            "category": club.category,
            "member_count_cache": club.member_count_cache,
            "event_status_breakdown": event_breakdown_by_club.get(club.id, {}),
            "pending_join_applications_count": pending_apps_by_club.get(club.id, 0),
        }
        for club in clubs
    ]


def resolve_club_activity_scope(db: Session, user: User) -> tuple:
    """Determine which clubs the caller may see an activity snapshot
    for, and a short label describing why.

    Returns (club_ids, scope_label). Precedence: admin-tier roles see
    every club in their own university (platform-wide oversight,
    university-scoped like ``build_admin_overview_context``); a
    faculty advisor sees their advised clubs; anyone else sees the
    clubs where they hold an officer-tier role. Never a mix of two
    scopes for one caller - the highest-precedence scope that applies
    wins, matching how ``authorize_intent``'s role checks are meant to
    be read (a broader oversight role subsumes a narrower one).
    """
    role_value = _role_value(user.role)

    if role_value in {r.value for r in ADMIN_TIER_ROLES}:
        query = db.query(Club.id)
        if user.university_id is not None:
            query = query.filter(Club.university_id == user.university_id)
        return [cid for (cid,) in query.all()], "platform-wide (your university)"

    if role_value == UserRole.FACULTY_ADVISOR.value:
        return advised_club_ids(db, user.id), "clubs you advise"

    officer_ids = officer_club_ids(db, user.id)
    return officer_ids, "clubs you hold an officer role in"


def build_club_activity_context(db: Session, user: User, **_kwargs) -> dict:
    """Club Activity Report / club-level Performance Analytics context.

    Returns: {"scope", "clubs": [...]} - see ``_club_activity_snapshot``.
    An empty ``clubs`` list is a normal, honest result for a caller with
    no qualifying clubs yet (e.g. an officer of no club, an advisor with
    no assigned clubs).
    """
    club_ids, scope = resolve_club_activity_scope(db, user)
    return {"scope": scope, "clubs": _club_activity_snapshot(db, club_ids)}


# ---------------------------------------------------------------------------
# Volunteer Report (personal)
# ---------------------------------------------------------------------------


def build_volunteer_report_context(db: Session, user: User, recent_limit: int = 20, **_kwargs) -> dict:
    """Summarize the authenticated user's own volunteer assignments
    (across every club membership they hold, not just currently-approved
    ones - a past/withdrawn membership's assignment history is still
    theirs).

    Returns: {"assignments": [{"club_name", "task_description", "status",
    "due_at", "event_title"}]} - empty list if none on file.
    """
    rows = (
        db.query(VolunteerAssignment, Club.name, Event.title)
        .join(ClubMembership, VolunteerAssignment.assignee_membership_id == ClubMembership.id)
        .join(Club, ClubMembership.club_id == Club.id)
        .outerjoin(Event, VolunteerAssignment.event_id == Event.id)
        .filter(ClubMembership.user_id == user.id)
        .order_by(VolunteerAssignment.created_at.desc())
        .limit(recent_limit)
        .all()
    )

    assignments = [
        {
            "club_name": club_name,
            "task_description": assignment.task_description,
            "status": _enum_value(assignment.status),
            "due_at": _iso(assignment.due_at),
            "event_title": event_title if event_title else f"Event #{assignment.event_id}",
        }
        for assignment, club_name, event_title in rows
    ]

    return {"assignments": assignments}


# ---------------------------------------------------------------------------
# Emergency Report Summary (admin-tier only - never a personal report)
# ---------------------------------------------------------------------------


def build_emergency_summary_context(db: Session, user: User, recent_limit: int = 10, **_kwargs) -> dict:
    """Aggregate summary of emergency reports for admin-tier oversight.

    Deliberately an aggregate, not a case-by-case dump: category/status
    counts and a recent list of {"category", "status", "days_open"}
    only - no reporter identity and no free-text description, even
    though the caller is authorized to see emergency reports, because
    a report/analytics summary has no need to carry a reporter's raw
    account of a harassment/medical incident into an LLM prompt, and
    withholding it here costs the summary nothing.

    Scoped to the caller's own university (via the reporting user, when
    known) when ``user.university_id`` is set, platform-wide otherwise -
    same fail-open-on-scope-only convention as
    ``build_admin_overview_context``.
    """
    query = db.query(EmergencyReport)
    if user.university_id is not None:
        query = query.join(User, EmergencyReport.reported_by == User.id, isouter=True).filter(
            (User.university_id == user.university_id) | (EmergencyReport.reported_by.is_(None))
        )
    reports = query.all()

    category_breakdown: dict = {}
    status_breakdown: dict = {}
    recent = []
    now = datetime.utcnow()
    for report in sorted(reports, key=lambda r: r.created_at or now, reverse=True):
        category = _enum_value(report.category)
        status = _enum_value(report.status)
        category_breakdown[category] = category_breakdown.get(category, 0) + 1
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
        if len(recent) < recent_limit:
            days_open = None
            if report.created_at is not None and report.resolved_at is None:
                days_open = (now - report.created_at).days
            recent.append({"category": category, "status": status, "days_open": days_open})

    return {
        "total_reports": len(reports),
        "category_breakdown": category_breakdown,
        "status_breakdown": status_breakdown,
        "recent": recent,
    }


# ---------------------------------------------------------------------------
# Budget Report (platform-wide, admin-tier caller with no club of their
# own to report on - a treasurer/faculty advisor uses the existing
# ``build_financial_operations_context`` instead, see report_service.py)
# ---------------------------------------------------------------------------


def build_budget_platform_context(db: Session, user: User, **_kwargs) -> dict:
    """Platform-wide (university-scoped) budget/expense aggregate for an
    admin-tier caller who isn't personally a treasurer/advisor of any
    club - the same figures ``build_financial_operations_context``
    would show a treasurer, but summed across every club rather than
    the caller's own.

    Returns: {"total_allocated_amount", "total_expenses_claimed",
    "expense_approval_breakdown": {"pending", "approved", "rejected"},
    "budget_status_breakdown": {status: count}}.
    """
    club_query = db.query(Club.id)
    if user.university_id is not None:
        club_query = club_query.filter(Club.university_id == user.university_id)
    club_ids = [cid for (cid,) in club_query.all()]

    if not club_ids:
        return {
            "total_allocated_amount": 0.0,
            "total_expenses_claimed": 0.0,
            "expense_approval_breakdown": {"pending": 0, "approved": 0, "rejected": 0},
            "budget_status_breakdown": {},
        }

    budgets = db.query(Budget).filter(Budget.club_id.in_(club_ids)).all()
    total_allocated = sum(float(b.allocated_amount or 0) for b in budgets)
    budget_status_breakdown: dict = {}
    for b in budgets:
        status = _enum_value(b.status)
        budget_status_breakdown[status] = budget_status_breakdown.get(status, 0) + 1

    budget_ids = [b.id for b in budgets]
    total_claimed = 0.0
    approval_breakdown = {"pending": 0, "approved": 0, "rejected": 0}
    if budget_ids:
        expenses = db.query(Expense).filter(Expense.budget_id.in_(budget_ids)).all()
        for e in expenses:
            total_claimed += float(e.amount or 0)
            approval = _enum_value(e.approval_status) or "pending"
            approval_breakdown[approval] = approval_breakdown.get(approval, 0) + 1

    return {
        "total_allocated_amount": round(total_allocated, 2),
        "total_expenses_claimed": round(total_claimed, 2),
        "expense_approval_breakdown": approval_breakdown,
        "budget_status_breakdown": budget_status_breakdown,
    }
