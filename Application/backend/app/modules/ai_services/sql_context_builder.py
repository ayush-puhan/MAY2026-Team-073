"""ClubConnect AI Assistant - SQL Context Builder (Phase 3, extended Phase 5B/6).

Implements Gateway stages 3 and 5 from
docs/ClubConnect_AI_Documentation/Architecture/ClubConnect_AI_Architecture_V2.md
Task 7 ("Determine SQL Context" / "Retrieve SQL") for the six
simple/status intents scoped to Phase 3 (see NEXT_PHASE.md):

    Application Status, Attendance, Rewards, Announcements,
    Profile & Account, Support Tickets

Phase 5B/6 adds the two recommendation-intent builders,
``build_club_recommendation_context`` and
``build_event_recommendation_context`` (see recommendation_logic_playbook.md
for the behavioral spec they implement).

Phase 6 (final polish, this revision) adds four more builders that were
previously deferred: ``build_membership_context`` (a user's own
approved club list - previously unhandled, causing Navigation to
answer "which clubs am I a member of" with a bare dashboard redirect
instead of the actual list), ``build_financial_operations_context``
(treasurer/faculty budget+expense figures), ``build_faculty_questions_
context`` (a faculty advisor's advised-club oversight - previously
this intent had *no* SQL builder at all, meaning Gemini had been
answering "which clubs do I advise" from RAG context alone with no
grounding, a hallucination risk flagged during this phase's testing),
and ``build_admin_overview_context`` (platform/university-wide club
status + creation-request oversight for admin-tier roles). Club
Creation & Governance remains RAG-only - see CHANGELOG.md for the
rationale.

Design notes:
    - Every function has the signature ``(db_session, user, **kwargs) ->
      dict`` and returns an already-summarized, JSON-safe dict - never a
      list of ORM objects, never a raw SQL row dump (Architecture V2
      Task 1.5 #4 / assistant_conversation_behavior.md Section 8).
    - Every function is defensive against empty tables: an empty result
      set returns a dict describing "nothing on file" (e.g.
      ``{"applications": []}``), never an exception, per
      NEXT_PHASE.md's verification steps and
      assistant_conversation_behavior.md Section 7 ("state that plainly
      ... do not fabricate placeholder activity").
    - Queries are scoped to the authenticated ``user`` only - this is the
      row-level authorization layer called out in intent_router.py's
      ``authorize_intent`` docstring ("that's enforced later by SQL
      scoping (Phase 3)").
    - The reference database has a known data gap (see
      PROJECT_CONTEXT.md Section 7.5): ``events`` has 0 rows despite
      ``event_registrations`` and ``attendance_records`` holding
      NOT NULL FKs into it. Attendance/registration lookups therefore
      use an outer join and fall back to an ID-based label
      ("Event #<id>") when no matching event row exists, rather than
      raising or silently dropping the record. No DB/ORM change was made
      to accommodate this, per project instructions.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database.enums import (
    AnnouncementAudience,
    ClubMemberRole,
    ClubStatus,
    EventStatus,
    MembershipStatus,
)
from app.database.models.applications import ClubJoinApplication
from app.database.models.auth import User
from app.database.models.academics import StudentProfile
from app.database.models.clubs import Announcement, Club, ClubCreationRequest, ClubMembership
from app.database.models.events import AttendanceRecord, Event, EventRegistration
from app.database.models.finance import Budget, Expense
from app.database.models.interests import ClubInterest, EventInterest, Interest, UserInterest
from app.database.models.rewards import RewardPointsLedger, RewardRedemption, RewardTaskCompletion
from app.database.models.support import SupportTicket, TicketResponse


def _iso(dt) -> Optional[str]:
    """Render a datetime as an ISO-8601 string, or None if absent."""
    return dt.isoformat() if dt is not None else None


def _enum_value(value) -> Optional[str]:
    """Normalize a SQLAlchemy Enum column value (enum member or raw string)."""
    if value is None:
        return None
    return value.value if hasattr(value, "value") else value


def _safe_datetime(raw_value) -> Optional[datetime]:
    """Best-effort parse of a raw (driver-level) datetime value.

    Discovered during Phase 3 testing: every row in the reference DB's
    `attendance_records.checked_in_at` column holds the literal,
    un-evaluated string "CURRENT_TIMESTAMP" instead of an actual
    timestamp (a seed-script bug - the SQL keyword was inserted as a
    string rather than being evaluated at insert time; see
    PROJECT_CONTEXT.md Section 7 for the write-up). SQLAlchemy's ORM
    raises when it tries to coerce that string into a `datetime` via the
    normal typed column path, so this value is fetched with a raw
    textual query (see `build_attendance_context`) and parsed here
    instead - returning None rather than raising or fabricating a time
    when the value isn't parseable. No DB/ORM change was made to
    accommodate this, per project instructions.
    """
    if raw_value is None:
        return None
    if isinstance(raw_value, datetime):
        return raw_value
    try:
        return datetime.fromisoformat(str(raw_value))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Application Status
# ---------------------------------------------------------------------------


def build_application_status_context(db: Session, user: User, **_kwargs) -> dict:
    """Summarize the authenticated user's club-join applications.

    Returns: {"applications": [{"club_name", "status", "applied_at",
    "reviewed_at", "review_comments"}, ...]} - empty list if none.
    """
    rows = (
        db.query(ClubJoinApplication, Club.name)
        .join(Club, ClubJoinApplication.club_id == Club.id)
        .filter(ClubJoinApplication.user_id == user.id)
        .order_by(ClubJoinApplication.applied_at.desc())
        .all()
    )

    applications = [
        {
            "club_name": club_name,
            "status": _enum_value(application.status),
            "applied_at": _iso(application.applied_at),
            "reviewed_at": _iso(application.reviewed_at),
            "review_comments": application.review_comments,
        }
        for application, club_name in rows
    ]

    return {"applications": applications}


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


def _event_label(event_id: int, title: Optional[str]) -> str:
    """Human-readable event label, defensive against the known empty-`events`
    reference-DB gap (PROJECT_CONTEXT.md Section 7.5): falls back to an
    ID-based label rather than surfacing None/blank to the model."""
    return title if title else f"Event #{event_id}"


def build_attendance_context(db: Session, user: User, **_kwargs) -> dict:
    """Summarize the authenticated user's own event registrations and
    check-ins.

    Returns: {"total_registered", "total_attended", "records": [
    {"event_title", "registration_status", "attended", "checked_in_at"}]}
    Outer-joined against `events` so registrations/attendance for a
    missing event row (see module docstring) still surface with an
    ID-based label instead of being dropped or erroring.

    Attendance timestamps are fetched via a raw textual query rather
    than the ORM entity, defensively working around the
    `checked_in_at = "CURRENT_TIMESTAMP"` data corruption discovered in
    the reference DB (see `_safe_datetime`) - presence of a row still
    counts as "attended" even when its timestamp can't be parsed.
    """
    registrations = (
        db.query(EventRegistration, Event.title)
        .outerjoin(Event, EventRegistration.event_id == Event.id)
        .filter(EventRegistration.user_id == user.id)
        .order_by(EventRegistration.registered_at.desc())
        .all()
    )

    attendance_rows = db.execute(
        text("SELECT event_id, checked_in_at FROM attendance_records WHERE user_id = :uid"),
        {"uid": user.id},
    ).all()
    attended_lookup = {event_id: _safe_datetime(checked_in_at) for event_id, checked_in_at in attendance_rows}

    records = []
    for registration, event_title in registrations:
        attended = registration.event_id in attended_lookup
        records.append({
            "event_title": _event_label(registration.event_id, event_title),
            "registration_status": _enum_value(registration.status),
            "attended": attended,
            "checked_in_at": _iso(attended_lookup.get(registration.event_id)) if attended else None,
        })

    return {
        "total_registered": len(records),
        "total_attended": len(attended_lookup),
        "records": records,
    }


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------


def build_rewards_context(db: Session, user: User, recent_limit: int = 5, **_kwargs) -> dict:
    """Summarize the authenticated user's reward points balance and recent
    activity.

    Returns: {"points_balance", "recent_ledger": [{"points", "reason",
    "created_at"}], "recent_redemptions": [{"reward_description",
    "points_spent", "status", "created_at"}]}. Balance is
    SUM(reward_points_ledger.points) - the ledger is append-only, per
    the model docstring - never an updatable running total.
    """
    balance = (
        db.query(func.coalesce(func.sum(RewardPointsLedger.points), 0))
        .filter(RewardPointsLedger.user_id == user.id)
        .scalar()
    )

    recent_ledger_rows = (
        db.query(RewardPointsLedger)
        .filter(RewardPointsLedger.user_id == user.id)
        .order_by(RewardPointsLedger.created_at.desc())
        .limit(recent_limit)
        .all()
    )

    recent_redemption_rows = (
        db.query(RewardRedemption)
        .filter(RewardRedemption.user_id == user.id)
        .order_by(RewardRedemption.created_at.desc())
        .limit(recent_limit)
        .all()
    )

    completed_tasks = (
        db.query(func.count(RewardTaskCompletion.id))
        .filter(RewardTaskCompletion.user_id == user.id)
        .scalar()
    )

    return {
        "points_balance": int(balance),
        "recent_ledger": [
            {
                "points": entry.points,
                "reason": entry.reason,
                "created_at": _iso(entry.created_at),
            }
            for entry in recent_ledger_rows
        ],
        "recent_redemptions": [
            {
                "reward_description": redemption.reward_description,
                "points_spent": redemption.points_spent,
                "status": _enum_value(redemption.status),
                "created_at": _iso(redemption.created_at),
            }
            for redemption in recent_redemption_rows
        ],
        "completed_task_count": int(completed_tasks),
    }


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


def build_announcements_context(db: Session, user: User, recent_limit: int = 10, **_kwargs) -> dict:
    """Summarize announcements visible to the authenticated user: posted by
    a club they belong to (any status of `AnnouncementAudience` for that
    club), plus platform-wide announcements (`SYSTEM_WIDE`/
    `UNIVERSITY_WIDE`, which carry no `club_id`).

    Returns: {"announcements": [{"club_name" (None for platform-wide),
    "title", "posted_at", "audience"}]} - empty list if none apply.
    """
    member_club_ids = [
        row[0]
        for row in db.query(ClubMembership.club_id)
        .filter(
            ClubMembership.user_id == user.id,
            ClubMembership.status == MembershipStatus.APPROVED,
        )
        .all()
    ]

    platform_wide_audiences = (AnnouncementAudience.SYSTEM_WIDE, AnnouncementAudience.UNIVERSITY_WIDE)

    query = db.query(Announcement, Club.name).outerjoin(Club, Announcement.club_id == Club.id)

    if member_club_ids:
        query = query.filter(
            (Announcement.club_id.in_(member_club_ids))
            | (Announcement.target_audience.in_(platform_wide_audiences))
        )
    else:
        query = query.filter(Announcement.target_audience.in_(platform_wide_audiences))

    rows = query.order_by(Announcement.created_at.desc()).limit(recent_limit).all()

    announcements = [
        {
            "club_name": club_name,  # None for platform-wide announcements
            "title": announcement.title,
            "posted_at": _iso(announcement.created_at),
            "audience": _enum_value(announcement.target_audience),
        }
        for announcement, club_name in rows
    ]

    return {"announcements": announcements}


# ---------------------------------------------------------------------------
# Profile & Account
# ---------------------------------------------------------------------------


def build_profile_context(db: Session, user: User, **_kwargs) -> dict:
    """Summarize the authenticated user's own profile/account state.

    Deliberately excludes `password_hash`, `google_id`, and any other
    internal/auth-only field, per assistant_conversation_behavior.md
    Section 10's exposure rules. Returns "student_profile": None for
    non-student roles or students without a profile row yet.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    student_profile = None
    if profile is not None:
        student_profile = {
            "academic_year": profile.academic_year,
            "semester": profile.semester,
            "batch": profile.batch,
            "section": profile.section,
            "is_verified": profile.is_verified,
        }

    return {
        "full_name": user.full_name,
        "email": user.email,
        "role": _enum_value(user.role),
        "phone": user.phone,
        "email_verified": user.email_verified,
        "profile_photo_configured": bool(user.profile_photo_url),
        "accessibility_prefs_configured": bool(user.accessibility_prefs),
        "color_blind_mode": user.color_blind_mode,
        "student_profile": student_profile,
    }


# ---------------------------------------------------------------------------
# Support Tickets
# ---------------------------------------------------------------------------


def build_support_tickets_context(db: Session, user: User, recent_limit: int = 10, **_kwargs) -> dict:
    """Summarize the authenticated user's own support tickets.

    Returns: {"tickets": [{"title", "ticket_type", "priority", "status",
    "created_at", "response_count"}]} - empty list if none on file.
    """
    tickets = (
        db.query(SupportTicket)
        .filter(SupportTicket.raised_by == user.id)
        .order_by(SupportTicket.created_at.desc())
        .limit(recent_limit)
        .all()
    )

    ticket_ids = [ticket.id for ticket in tickets]
    response_counts = {}
    if ticket_ids:
        response_counts = dict(
            db.query(TicketResponse.ticket_id, func.count(TicketResponse.id))
            .filter(TicketResponse.ticket_id.in_(ticket_ids))
            .group_by(TicketResponse.ticket_id)
            .all()
        )

    return {
        "tickets": [
            {
                "title": ticket.title,
                "ticket_type": _enum_value(ticket.ticket_type),
                "priority": _enum_value(ticket.priority),
                "status": _enum_value(ticket.status),
                "created_at": _iso(ticket.created_at),
                "response_count": response_counts.get(ticket.id, 0),
            }
            for ticket in tickets
        ]
    }


# ---------------------------------------------------------------------------
# Membership (Phase 6 final polish)
#
# Distinct from "Membership Process" (RAG-only, explains the general
# apply -> approve flow) and "Application Status" (the user's pending/
# rejected/approved application rows). This intent answers "which clubs
# am I currently a member of" directly from club_memberships, so the
# model has the real club list instead of redirecting to the dashboard
# or - worse - guessing (see assistant_conversation_behavior.md Section
# 7: never infer membership from anything but an APPROVED row).
# ---------------------------------------------------------------------------


def build_membership_context(db: Session, user: User, **_kwargs) -> dict:
    """Summarize the authenticated user's own approved club memberships.

    Only ``status = APPROVED`` rows count as "currently a member" per
    assistant_conversation_behavior.md Section 7 ("never treat a
    club_join_applications row as proof of membership" - the same
    principle applies to non-approved club_memberships rows, e.g.
    pending/withdrawn/rejected).

    Column-projected (club name + role_in_club + status only) rather
    than loading full ClubMembership ORM rows, for the same reason
    ``routes.py``'s ``_resolve_approved_club_roles`` avoids it: some
    reference-DB ``club_memberships.applied_at`` rows hold the literal
    string "CURRENT_TIMESTAMP" instead of a real timestamp, which a
    typed ``DateTime`` column load would choke on. This builder never
    needs that column, so it's never at risk from that corruption.

    Returns: {"memberships": [{"club_name", "role_in_club"}]} - empty
    list if the user holds no approved membership.
    """
    rows = (
        db.query(Club.name, ClubMembership.role_in_club)
        .join(ClubMembership, ClubMembership.club_id == Club.id)
        .filter(
            ClubMembership.user_id == user.id,
            ClubMembership.status == MembershipStatus.APPROVED,
        )
        .order_by(Club.name.asc())
        .all()
    )

    return {
        "memberships": [
            {"club_name": club_name, "role_in_club": _enum_value(role_in_club)}
            for club_name, role_in_club in rows
        ]
    }


# ---------------------------------------------------------------------------
# Financial Operations / Faculty Questions - shared helper (Phase 6 final
# polish)
#
# Both intents summarize the same underlying budgets/expenses data, just
# scoped to a different club set (Financial Operations: clubs the caller
# treasures; Faculty Questions: clubs the caller advises - a faculty
# advisor reaching Financial Operations directly, per
# intent_router.py's ``allowed_platform_roles``, also gets their advised
# clubs' figures here). Column-projected budget/expense loads only pull
# fields this module actually returns - no ORM relationship traversal
# that would pull in unrelated/unauthorized rows.
# ---------------------------------------------------------------------------


def _treasurer_club_ids(db: Session, user_id: int) -> list:
    """Club IDs where the user holds an APPROVED treasurer membership."""
    rows = (
        db.query(ClubMembership.club_id)
        .filter(
            ClubMembership.user_id == user_id,
            ClubMembership.status == MembershipStatus.APPROVED,
            ClubMembership.role_in_club == ClubMemberRole.TREASURER,
        )
        .all()
    )
    return [club_id for (club_id,) in rows]


def _advised_club_ids(db: Session, user_id: int) -> list:
    """Club IDs where the user is the club's ``faculty_advisor_id``."""
    rows = db.query(Club.id).filter(Club.faculty_advisor_id == user_id).all()
    return [club_id for (club_id,) in rows]


def _club_financial_snapshot(db: Session, club_ids: list, recent_expense_limit: int = 5) -> list:
    """Per-club budget/expense summary for the given club IDs.

    Returns a list (one entry per club, only for clubs that actually
    have at least a name resolvable - i.e. every id in ``club_ids``) of:
    {"club_name", "budgets": [{"title", "status", "allocated_amount",
    "period_start", "period_end"}], "total_allocated_amount",
    "expense_approval_breakdown": {"pending", "approved", "rejected"},
    "total_expenses_claimed", "recent_expenses": [{"description",
    "amount", "status", "approval_status", "created_at"}]}

    Never returns raw ORM rows - every figure here is either a scalar
    aggregate or an already-summarized list, per this module's
    docstring contract.
    """
    if not club_ids:
        return []

    club_names = dict(db.query(Club.id, Club.name).filter(Club.id.in_(club_ids)).all())

    budgets_by_club: dict = {cid: [] for cid in club_ids}
    allocated_by_club: dict = {cid: 0 for cid in club_ids}
    budget_ids_by_club: dict = {cid: [] for cid in club_ids}
    for budget in db.query(Budget).filter(Budget.club_id.in_(club_ids)).all():
        budgets_by_club[budget.club_id].append({
            "title": budget.title,
            "status": _enum_value(budget.status),
            "allocated_amount": float(budget.allocated_amount) if budget.allocated_amount is not None else 0.0,
            "period_start": _iso(budget.period_start),
            "period_end": _iso(budget.period_end),
        })
        allocated_by_club[budget.club_id] += float(budget.allocated_amount or 0)
        budget_ids_by_club[budget.club_id].append(budget.id)

    all_budget_ids = [bid for ids in budget_ids_by_club.values() for bid in ids]
    budget_to_club = {bid: cid for cid, ids in budget_ids_by_club.items() for bid in ids}

    expense_breakdown_by_club: dict = {cid: {"pending": 0, "approved": 0, "rejected": 0} for cid in club_ids}
    total_claimed_by_club: dict = {cid: 0.0 for cid in club_ids}
    recent_expenses_by_club: dict = {cid: [] for cid in club_ids}

    if all_budget_ids:
        expense_rows = (
            db.query(Expense)
            .filter(Expense.budget_id.in_(all_budget_ids))
            .order_by(Expense.created_at.desc())
            .all()
        )
        for expense in expense_rows:
            cid = budget_to_club.get(expense.budget_id)
            if cid is None:
                continue
            approval = _enum_value(expense.approval_status) or "pending"
            expense_breakdown_by_club[cid][approval] = expense_breakdown_by_club[cid].get(approval, 0) + 1
            total_claimed_by_club[cid] += float(expense.amount or 0)
            if len(recent_expenses_by_club[cid]) < recent_expense_limit:
                recent_expenses_by_club[cid].append({
                    "description": expense.description,
                    "amount": float(expense.amount) if expense.amount is not None else 0.0,
                    "status": _enum_value(expense.status),
                    "approval_status": approval,
                    "created_at": _iso(expense.created_at),
                })

    snapshot = []
    for cid in club_ids:
        if cid not in club_names:
            continue  # defensive: id somehow doesn't resolve to a club row
        snapshot.append({
            "club_name": club_names[cid],
            "budgets": budgets_by_club[cid],
            "total_allocated_amount": round(allocated_by_club[cid], 2),
            "expense_approval_breakdown": expense_breakdown_by_club[cid],
            "total_expenses_claimed": round(total_claimed_by_club[cid], 2),
            "recent_expenses": recent_expenses_by_club[cid],
        })
    return snapshot


def build_financial_operations_context(db: Session, user: User, **_kwargs) -> dict:
    """Budget/expense summary for the clubs the authenticated user may see
    financial figures for: clubs they hold an APPROVED treasurer
    membership in, plus (for a faculty advisor) clubs they advise.

    RBAC note: this builder is only ever called after
    ``intent_router.authorize_intent`` has already confirmed the caller
    is either a faculty advisor or holds the treasurer club role
    somewhere - but it independently re-derives the *specific* club set
    from the caller's own rows rather than trusting an intent-level
    "yes/no", so a treasurer of Club A can never see Club B's figures
    just because they're a treasurer of *some* club.

    Returns: {"clubs": [...]} (see ``_club_financial_snapshot``) - empty
    list if the caller doesn't currently treasure or advise any club
    (e.g. a faculty advisor with no assigned clubs yet).
    """
    club_ids = set(_treasurer_club_ids(db, user.id))
    if _enum_value(user.role) == "faculty_advisor":
        club_ids.update(_advised_club_ids(db, user.id))

    return {"clubs": _club_financial_snapshot(db, list(club_ids))}


def build_faculty_questions_context(db: Session, user: User, **_kwargs) -> dict:
    """Oversight summary for the clubs the authenticated faculty advisor
    advises: club roster info, events awaiting approval, and a light
    financial snapshot (total allocated + pending-expense count only -
    detailed expense-level figures belong to Financial Operations, not
    this general oversight intent).

    Returns: {"advised_clubs": [{"club_name", "status", "category",
    "member_count_cache"}], "events_pending_approval": [{"event_title",
    "club_name", "start_at"}], "budget_overview": [{"club_name",
    "total_allocated_amount", "pending_expense_count"}]} - every list
    honestly empty if the advisor currently has no advised clubs, per
    this module's "state that plainly" convention.
    """
    club_rows = (
        db.query(Club.id, Club.name, Club.status, Club.category, Club.member_count_cache)
        .filter(Club.faculty_advisor_id == user.id)
        .order_by(Club.name.asc())
        .all()
    )
    club_ids = [club_id for club_id, *_ in club_rows]

    advised_clubs = [
        {
            "club_name": name,
            "status": _enum_value(status),
            "category": category,
            "member_count_cache": member_count_cache,
        }
        for _cid, name, status, category, member_count_cache in club_rows
    ]

    events_pending_approval = []
    if club_ids:
        pending_rows = (
            db.query(Event.title, Club.name, Event.start_at)
            .join(Club, Event.club_id == Club.id)
            .filter(Event.club_id.in_(club_ids), Event.status == EventStatus.PENDING_APPROVAL)
            .order_by(Event.start_at.asc())
            .all()
        )
        events_pending_approval = [
            {"event_title": title, "club_name": club_name, "start_at": _iso(start_at)}
            for title, club_name, start_at in pending_rows
        ]

    budget_overview = [
        {
            "club_name": entry["club_name"],
            "total_allocated_amount": entry["total_allocated_amount"],
            "pending_expense_count": entry["expense_approval_breakdown"].get("pending", 0),
        }
        for entry in _club_financial_snapshot(db, club_ids)
    ]

    return {
        "advised_clubs": advised_clubs,
        "events_pending_approval": events_pending_approval,
        "budget_overview": budget_overview,
    }


# ---------------------------------------------------------------------------
# Admin Questions (Phase 6 final polish)
#
# Platform-wide oversight for Student Affairs Office / Dean of Student
# Welfare / System Admin (per intent_router.py's ``allowed_platform_
# roles``): club status breakdown, inactive-club listing, most-active
# clubs, and club-creation-request throughput. Scoped to the caller's
# own university (multi-tenant, per platform_getting_started.md -
# "every account belongs to one university tenant") whenever the
# caller's ``university_id`` is set; a caller with no university on
# file falls back to platform-wide (no such account should normally
# exist, but this is fail-open on scope only, never on authorization -
# authorize_intent already gated who can reach this builder at all).
# ---------------------------------------------------------------------------


def build_admin_overview_context(
    db: Session, user: User, inactive_limit: int = 20, most_active_limit: int = 5, recent_requests_limit: int = 10, **_kwargs
) -> dict:
    """Platform-wide (or university-scoped) club and proposal oversight.

    Returns: {"total_clubs", "club_status_breakdown": {status: count},
    "inactive_clubs": [{"club_name", "status"}], "most_active_clubs":
    [{"club_name", "category", "member_count_cache"}],
    "club_creation_requests": {"pending_count", "recent": [{
    "proposed_name", "status", "created_at", "requested_by"}]}}

    ``member_count_cache`` is named after the underlying denormalized
    column deliberately (assistant_conversation_behavior.md Section 7:
    present a cached figure as the platform's current display figure,
    not a guaranteed live count) - the model is expected to phrase it
    accordingly rather than as a precise live count.
    """
    club_query = db.query(Club)
    if user.university_id is not None:
        club_query = club_query.filter(Club.university_id == user.university_id)
    clubs = club_query.all()

    total_clubs = len(clubs)
    status_breakdown: dict = {}
    for c in clubs:
        status = _enum_value(c.status) or "unknown"
        status_breakdown[status] = status_breakdown.get(status, 0) + 1

    inactive_clubs = [
        {"club_name": c.name, "status": _enum_value(c.status)}
        for c in clubs
        if c.status != ClubStatus.ACTIVE
    ][:inactive_limit]

    most_active_clubs = [
        {"club_name": c.name, "category": c.category, "member_count_cache": c.member_count_cache}
        for c in sorted(
            (c for c in clubs if c.status == ClubStatus.ACTIVE),
            key=lambda c: c.member_count_cache or 0,
            reverse=True,
        )[:most_active_limit]
    ]

    request_query = db.query(ClubCreationRequest, User.full_name).join(
        User, ClubCreationRequest.requested_by == User.id
    )
    if user.university_id is not None:
        # club_creation_requests has no university_id column of its own;
        # scope via the requester's university instead.
        request_query = request_query.filter(User.university_id == user.university_id)

    all_requests = request_query.order_by(ClubCreationRequest.created_at.desc()).all()
    pending_count = sum(
        1 for request, _name in all_requests if _enum_value(request.status) == "submitted"
    )
    recent_requests = [
        {
            "proposed_name": request.proposed_name,
            "status": _enum_value(request.status),
            "created_at": _iso(request.created_at),
            "requested_by": requester_name,
        }
        for request, requester_name in all_requests[:recent_requests_limit]
    ]

    return {
        "total_clubs": total_clubs,
        "club_status_breakdown": status_breakdown,
        "inactive_clubs": inactive_clubs,
        "most_active_clubs": most_active_clubs,
        "club_creation_requests": {
            "pending_count": pending_count,
            "recent": recent_requests,
        },
    }


# ---------------------------------------------------------------------------
# Club Recommendation / Event Recommendation (Phase 5B/6)
#
# Per recommendation_logic_playbook.md Section 1-2 and NEXT_PHASE.md: these
# builders return a *raw feature summary* only - explicit interests,
# exclusion data (existing memberships/registrations), and behavioral
# history as supporting signals. Ranking and rationale-writing is Gemini's
# job at prompt time; nothing here scores, sorts, or drops a candidate for
# being "weaker" - only for being genuinely inapplicable (already joined,
# already registered, not yet started/active).
#
# Both builders deliberately avoid loading full ClubMembership ORM rows
# (which would touch the corrupted `applied_at` column - see
# routes.py's `_resolve_approved_club_roles` docstring for the same
# finding/workaround) by projecting only the columns actually needed.
# ---------------------------------------------------------------------------


def _user_interest_names(db: Session, user_id: int) -> list:
    """Distinct interest names the user has explicitly stated (`user_interests`)."""
    rows = (
        db.query(Interest.name)
        .join(UserInterest, UserInterest.interest_id == Interest.id)
        .filter(UserInterest.user_id == user_id)
        .order_by(Interest.name)
        .all()
    )
    return [name for (name,) in rows]


def _approved_member_club_ids(db: Session, user_id: int) -> list:
    """Club IDs the user already holds an APPROVED membership in (exclusion
    set) - column-projected to avoid the corrupted `applied_at`/`decided_at`
    values a full `ClubMembership` load would try to coerce."""
    rows = (
        db.query(ClubMembership.club_id)
        .filter(
            ClubMembership.user_id == user_id,
            ClubMembership.status == MembershipStatus.APPROVED,
        )
        .all()
    )
    return [club_id for (club_id,) in rows]


def _academic_year(db: Session, user_id: int) -> Optional[str]:
    """`student_profiles.academic_year` for this user, or None (non-student
    role, or a student without a profile row yet). Contextual color only -
    see recommendation_logic_playbook.md Section 5."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    return profile.academic_year if profile is not None else None


def build_club_recommendation_context(db: Session, user: User, **_kwargs) -> dict:
    """Feature summary for the Club Recommendation intent (playbook Section 3).

    Candidate clubs are those the user is not already an approved member of
    AND that share at least one interest tag with the user's own
    `user_interests` (playbook step 1: identify by interest overlap; step 2:
    exclude existing memberships). For each candidate, also surfaces the
    user's own event registration/attendance counts for that club's events
    as *supporting* behavioral evidence (playbook step 3) - never a
    separate inclusion criterion on its own.

    If the user has no stated interests, ``candidate_clubs`` is honestly
    empty (cold-start per playbook Section 7) - this is a prompting
    concern, not something this builder guesses around with a popularity
    fallback.

    Returns: {"academic_year", "user_interests": [...],
    "current_club_memberships": [...], "candidate_clubs": [{"club_name",
    "category", "matching_interests", "user_event_registration_count",
    "user_event_attendance_count"}]}
    """
    user_interests = _user_interest_names(db, user.id)
    member_club_ids = _approved_member_club_ids(db, user.id)

    current_memberships = []
    if member_club_ids:
        current_memberships = [
            name
            for (name,) in db.query(Club.name).filter(Club.id.in_(member_club_ids)).all()
        ]

    candidate_clubs = []
    if user_interests:
        # Candidate clubs: active, not already joined, sharing >=1 interest
        # tag with the user (playbook step 1). This is filtering, not
        # ranking - Gemini weighs strength of overlap at prompt time.
        candidate_query = (
            db.query(Club.id, Club.name, Club.category, Interest.name)
            .join(ClubInterest, ClubInterest.club_id == Club.id)
            .join(Interest, ClubInterest.interest_id == Interest.id)
            .filter(Club.status == ClubStatus.ACTIVE)
            .filter(Interest.name.in_(user_interests))
        )
        if member_club_ids:
            candidate_query = candidate_query.filter(~Club.id.in_(member_club_ids))

        by_club: dict = {}
        for club_id, club_name, category, interest_name in candidate_query.all():
            entry = by_club.setdefault(
                club_id, {"club_name": club_name, "category": category, "matching_interests": []}
            )
            if interest_name not in entry["matching_interests"]:
                entry["matching_interests"].append(interest_name)

        candidate_ids = list(by_club.keys())

        # Supporting behavioral signal: the user's own registration/
        # attendance counts against each candidate club's events (playbook
        # step 3) - never used to add or drop a candidate by itself.
        registration_counts: dict = {}
        attendance_counts: dict = {}
        if candidate_ids:
            registration_counts = dict(
                db.query(Event.club_id, func.count(EventRegistration.id))
                .join(EventRegistration, EventRegistration.event_id == Event.id)
                .filter(Event.club_id.in_(candidate_ids), EventRegistration.user_id == user.id)
                .group_by(Event.club_id)
                .all()
            )
            attendance_counts = dict(
                db.query(Event.club_id, func.count(AttendanceRecord.id))
                .join(AttendanceRecord, AttendanceRecord.event_id == Event.id)
                .filter(Event.club_id.in_(candidate_ids), AttendanceRecord.user_id == user.id)
                .group_by(Event.club_id)
                .all()
            )

        for club_id, entry in by_club.items():
            entry["user_event_registration_count"] = int(registration_counts.get(club_id, 0))
            entry["user_event_attendance_count"] = int(attendance_counts.get(club_id, 0))
            candidate_clubs.append(entry)

    return {
        "academic_year": _academic_year(db, user.id),
        "user_interests": user_interests,
        "current_club_memberships": current_memberships,
        "candidate_clubs": candidate_clubs,
    }


def build_event_recommendation_context(db: Session, user: User, **_kwargs) -> dict:
    """Feature summary for the Event Recommendation intent (playbook Section 4).

    Candidate events are upcoming (not yet ended), not cancelled/rejected,
    the user is not already registered for, and either (a) share an
    interest tag with the user's `user_interests`, or (b) belong to a club
    the user already holds an approved membership in (playbook step 1).
    Behavioral history (distinct interest tags drawn from the user's own
    past registrations/attendance) is surfaced separately as a supporting
    signal (playbook step 2) - it does not by itself add or remove a
    candidate.

    If there is no overlap and no membership-based match, ``upcoming_
    candidate_events`` is honestly empty (cold-start per playbook Section
    7) rather than falling back to a popularity list.

    Returns: {"user_interests": [...], "member_club_names": [...],
    "attended_event_interest_tags": [...], "registered_event_interest_tags":
    [...], "upcoming_candidate_events": [{"event_title", "club_name",
    "start_at", "matching_interests", "club_membership_match"}]}
    """
    now = datetime.utcnow()
    user_interests = _user_interest_names(db, user.id)
    member_club_ids = _approved_member_club_ids(db, user.id)

    member_club_names = []
    if member_club_ids:
        member_club_names = [
            name
            for (name,) in db.query(Club.name).filter(Club.id.in_(member_club_ids)).all()
        ]

    already_registered_event_ids = {
        event_id
        for (event_id,) in db.query(EventRegistration.event_id)
        .filter(EventRegistration.user_id == user.id)
        .all()
    }

    def _distinct_interest_tags(event_ids) -> list:
        if not event_ids:
            return []
        rows = (
            db.query(Interest.name)
            .join(EventInterest, EventInterest.interest_id == Interest.id)
            .filter(EventInterest.event_id.in_(event_ids))
            .distinct()
            .order_by(Interest.name)
            .all()
        )
        return [name for (name,) in rows]

    attended_event_ids = [
        event_id
        for (event_id,) in db.execute(
            text("SELECT DISTINCT event_id FROM attendance_records WHERE user_id = :uid"),
            {"uid": user.id},
        ).all()
    ]
    attended_event_interest_tags = _distinct_interest_tags(attended_event_ids)
    registered_event_interest_tags = _distinct_interest_tags(list(already_registered_event_ids))

    excluded_statuses = (EventStatus.CANCELLED, EventStatus.REJECTED, EventStatus.COMPLETED)
    upcoming_query = (
        db.query(Event, Club.name)
        .join(Club, Event.club_id == Club.id)
        .filter(Event.start_at >= now)
        .filter(~Event.status.in_(excluded_statuses))
    )
    if already_registered_event_ids:
        upcoming_query = upcoming_query.filter(~Event.id.in_(already_registered_event_ids))

    upcoming_events = upcoming_query.order_by(Event.start_at.asc()).all()

    event_ids = [event.id for event, _ in upcoming_events]
    event_interest_map: dict = {}
    if event_ids:
        for event_id, interest_name in (
            db.query(EventInterest.event_id, Interest.name)
            .join(Interest, EventInterest.interest_id == Interest.id)
            .filter(EventInterest.event_id.in_(event_ids))
            .all()
        ):
            event_interest_map.setdefault(event_id, []).append(interest_name)

    candidate_events = []
    for event, club_name in upcoming_events:
        event_interests = event_interest_map.get(event.id, [])
        matching_interests = [name for name in event_interests if name in user_interests]
        club_membership_match = event.club_id in member_club_ids

        if not matching_interests and not club_membership_match:
            continue  # not identified as a candidate per playbook step 1

        candidate_events.append({
            "event_title": event.title,
            "club_name": club_name,
            "start_at": _iso(event.start_at),
            "matching_interests": matching_interests,
            "club_membership_match": club_membership_match,
        })

    return {
        "user_interests": user_interests,
        "member_club_names": member_club_names,
        "attended_event_interest_tags": attended_event_interest_tags,
        "registered_event_interest_tags": registered_event_interest_tags,
        "upcoming_candidate_events": candidate_events,
    }


# ---------------------------------------------------------------------------
# Intent -> builder dispatch (consumed by routes.py)
# ---------------------------------------------------------------------------

# The six Phase 3 intents, the two Phase 5B/6 recommendation intents, and
# (Phase 6 final polish) Membership plus the three previously-deferred
# role-scoped intents - Financial Operations, Faculty Questions, and
# Admin Questions. Club Creation & Governance remains RAG-only for now
# (process explanation intent; no per-user SQL fact currently requested
# for it - see CHANGELOG.md).
CONTEXT_BUILDERS = {
    "Application Status": build_application_status_context,
    "Attendance": build_attendance_context,
    "Rewards": build_rewards_context,
    "Announcements": build_announcements_context,
    "Profile & Account": build_profile_context,
    "Support Tickets": build_support_tickets_context,
    "Club Recommendation": build_club_recommendation_context,
    "Event Recommendation": build_event_recommendation_context,
    "Membership": build_membership_context,
    "Financial Operations": build_financial_operations_context,
    "Faculty Questions": build_faculty_questions_context,
    "Admin Questions": build_admin_overview_context,
}


def build_sql_context(intent_name: str, db: Session, user: User) -> Optional[dict]:
    """Dispatch to the matching builder for `intent_name`, or None if this
    intent has no Phase 3 SQL context builder (either it's RAG-only, or
    its SQL is deferred to a later phase - see NEXT_PHASE.md)."""
    builder = CONTEXT_BUILDERS.get(intent_name)
    if builder is None:
        return None
    return builder(db, user)
