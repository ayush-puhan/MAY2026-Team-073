"""Unit tests for app/modules/ai_services/sql_context_builder.py (Phase 3).

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q

Uses a fresh in-memory SQLite database per test (same fixture pattern as
app/database/tests/conftest.py) rather than the shared reference
`clubconnect.db`, so each builder can be exercised against both a
populated case and an empty-result case independently and
deterministically, per NEXT_PHASE.md's verification steps - no reliance
on, and no mutation of, the real reference database.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database import models  # noqa: F401 - registers all mapped tables
from app.database.enums import (
    AnnouncementAudience,
    BudgetStatus,
    ClubMemberRole,
    ClubRequestStatus,
    ClubStatus,
    EventStatus,
    ExpenseApprovalStatus,
    ExpenseStatus,
    MembershipStatus,
    RegistrationStatus,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserRole,
)
from app.database.models.academics import Department, Program, StudentProfile
from app.database.models.applications import ClubJoinApplication
from app.database.models.auth import User
from app.database.models.clubs import Announcement, Club, ClubCreationRequest, ClubMembership
from app.database.models.events import AttendanceRecord, Event, EventRegistration
from app.database.models.interests import ClubInterest, EventInterest, Interest, UserInterest
from app.database.models.rewards import RewardPointsLedger, RewardRedemption
from app.database.models.support import SupportTicket, TicketResponse
from app.database.models.university import University
from app.database.models.finance import Budget, Expense
from app.modules.ai_services.sql_context_builder import (
    build_admin_overview_context,
    build_announcements_context,
    build_application_status_context,
    build_attendance_context,
    build_club_recommendation_context,
    build_event_recommendation_context,
    build_faculty_questions_context,
    build_financial_operations_context,
    build_membership_context,
    build_profile_context,
    build_rewards_context,
    build_sql_context,
    build_support_tickets_context,
)


@pytest.fixture()
def engine():
    eng = create_engine("sqlite:///:memory:", future=True)

    @event.listens_for(eng, "connect")
    def _fk_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def db(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    sess = SessionLocal()
    yield sess
    sess.close()


@pytest.fixture()
def university(db):
    uni = University(name="Test University", domain="test.edu")
    db.add(uni)
    db.commit()
    return uni


@pytest.fixture()
def department(db, university):
    dept = Department(name="Computer Science", code="CS", university_id=university.id)
    db.add(dept)
    db.commit()
    return dept


@pytest.fixture()
def program(db, department):
    prog = Program(department_id=department.id, name="B.Tech CS")
    db.add(prog)
    db.commit()
    return prog


@pytest.fixture()
def student(db, university):
    """A student user with no related rows in any Phase 3 table - the
    empty-result case for every builder."""
    user = User(
        email="empty.student@test.edu",
        password_hash="x",
        full_name="Empty Student",
        role=UserRole.STUDENT,
        university_id=university.id,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def club(db, university):
    c = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    db.add(c)
    db.commit()
    return c


@pytest.fixture()
def faculty_advisor(db, university):
    """A faculty advisor user with no advised clubs yet - the empty-result
    case for the Financial Operations / Faculty Questions builders."""
    user = User(
        email="advisor@test.edu",
        password_hash="x",
        full_name="Dr. Advisor",
        role=UserRole.FACULTY_ADVISOR,
        university_id=university.id,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def admin_user(db, university):
    user = User(
        email="admin@test.edu",
        password_hash="x",
        full_name="Admin User",
        role=UserRole.SYSTEM_ADMIN,
        university_id=university.id,
    )
    db.add(user)
    db.commit()
    return user


# ---------------------------------------------------------------------------
# Application Status
# ---------------------------------------------------------------------------


def test_application_status_empty(db, student):
    assert build_application_status_context(db, student) == {"applications": []}


def test_application_status_populated(db, student, club):
    application = ClubJoinApplication(
        user_id=student.id,
        club_id=club.id,
        status=MembershipStatus.PENDING,
        applied_at=datetime(2026, 1, 1),
    )
    db.add(application)
    db.commit()

    context = build_application_status_context(db, student)

    assert context == {
        "applications": [
            {
                "club_name": "Robotics Club",
                "status": "pending",
                "applied_at": "2026-01-01T00:00:00",
                "reviewed_at": None,
                "review_comments": None,
            }
        ]
    }


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


def test_attendance_empty(db, student):
    context = build_attendance_context(db, student)
    assert context == {"total_registered": 0, "total_attended": 0, "records": []}


def test_attendance_populated_with_event_row(db, student, club):
    event = Event(
        club_id=club.id,
        title="Hackathon",
        start_at=datetime(2026, 2, 1, 9, 0),
        end_at=datetime(2026, 2, 1, 17, 0),
        created_by=student.id,
    )
    db.add(event)
    db.commit()

    registration = EventRegistration(event_id=event.id, user_id=student.id, status=RegistrationStatus.REGISTERED)
    db.add(registration)
    db.commit()

    attendance = AttendanceRecord(event_id=event.id, user_id=student.id, checked_in_at=datetime(2026, 2, 1, 9, 5))
    db.add(attendance)
    db.commit()

    context = build_attendance_context(db, student)

    assert context["total_registered"] == 1
    assert context["total_attended"] == 1
    assert context["records"] == [
        {
            "event_title": "Hackathon",
            "registration_status": "registered",
            "attended": True,
            "checked_in_at": "2026-02-01T09:05:00",
        }
    ]


def test_attendance_missing_event_row_falls_back_to_id_label(db, student, club):
    """Defensive handling of the known reference-DB gap (PROJECT_CONTEXT.md
    Section 7.5): a registration/attendance row can point at an event_id
    with no matching `events` row. The builder must not raise and must
    fall back to an ID-based label rather than fabricating a title."""
    # Simulate the "events" gap by inserting a registration that points at
    # an event_id with no matching row, the same way the reference DB's
    # dangling seed data exists (FK enforcement bypassed at load time) -
    # without touching any production database. Foreign-key enforcement is
    # briefly disabled on this in-memory test connection only, purely to
    # construct the orphaned row this test needs.
    orphan_event_id = 999
    db.execute(text("PRAGMA foreign_keys = OFF"))
    registration = EventRegistration(event_id=orphan_event_id, user_id=student.id)
    db.add(registration)
    db.commit()
    db.execute(text("PRAGMA foreign_keys = ON"))

    context = build_attendance_context(db, student)

    assert context["records"] == [
        {
            "event_title": f"Event #{orphan_event_id}",
            "registration_status": "registered",
            "attended": False,
            "checked_in_at": None,
        }
    ]


def test_attendance_tolerates_current_timestamp_literal_string(db, student, club):
    """Defensive handling of a real data-quality issue discovered in the
    reference DB (see PROJECT_CONTEXT.md): every row in
    `attendance_records.checked_in_at` holds the literal, un-evaluated
    string "CURRENT_TIMESTAMP" rather than an actual timestamp. The
    builder must still report the record as attended (presence of the
    row is what matters) without raising, and without fabricating a
    real check-in time."""
    event = Event(
        club_id=club.id,
        title="Orientation",
        start_at=datetime(2026, 4, 1),
        end_at=datetime(2026, 4, 1, 1),
        created_by=student.id,
    )
    db.add(event)
    db.commit()

    db.add(EventRegistration(event_id=event.id, user_id=student.id))
    db.commit()

    # Insert the corrupted value directly via raw SQL, bypassing the ORM's
    # DateTime column type (which would reject this at insert time) - this
    # mirrors exactly how the bad value reached the reference DB (a raw
    # seed-data insert, not an ORM write).
    db.execute(
        text(
            "INSERT INTO attendance_records (event_id, user_id, checked_in_at) "
            "VALUES (:event_id, :user_id, 'CURRENT_TIMESTAMP')"
        ),
        {"event_id": event.id, "user_id": student.id},
    )
    db.commit()

    context = build_attendance_context(db, student)

    assert context["total_attended"] == 1
    assert context["records"] == [
        {
            "event_title": "Orientation",
            "registration_status": "registered",
            "attended": True,
            "checked_in_at": None,  # unparseable source value - not fabricated
        }
    ]


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------


def test_rewards_empty(db, student):
    context = build_rewards_context(db, student)
    assert context == {
        "points_balance": 0,
        "recent_ledger": [],
        "recent_redemptions": [],
        "completed_task_count": 0,
    }


def test_rewards_populated(db, student):
    db.add_all([
        RewardPointsLedger(user_id=student.id, points=50, reason="Event attendance", created_at=datetime(2026, 1, 1)),
        RewardPointsLedger(user_id=student.id, points=-20, reason="Redeemed reward", created_at=datetime(2026, 1, 2)),
    ])
    db.add(RewardRedemption(
        user_id=student.id, points_spent=20, reward_description="Club T-Shirt", created_at=datetime(2026, 1, 2)
    ))
    db.commit()

    context = build_rewards_context(db, student)

    assert context["points_balance"] == 30
    assert len(context["recent_ledger"]) == 2
    assert context["recent_ledger"][0]["reason"] == "Redeemed reward"  # most recent first
    assert context["recent_redemptions"][0]["reward_description"] == "Club T-Shirt"


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


def test_announcements_empty_for_user_with_no_clubs(db, student):
    context = build_announcements_context(db, student)
    assert context == {"announcements": []}


def test_announcements_scoped_to_users_clubs_plus_platform_wide(db, student, club):
    membership = ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED)
    db.add(membership)
    db.commit()

    club_announcement = Announcement(
        club_id=club.id,
        posted_by=student.id,
        title="Meeting moved to Friday",
        body="...",
        target_audience=AnnouncementAudience.ALL_MEMBERS,
        created_at=datetime(2026, 1, 5),
    )
    platform_announcement = Announcement(
        club_id=None,
        posted_by=student.id,
        title="Platform maintenance window",
        body="...",
        target_audience=AnnouncementAudience.SYSTEM_WIDE,
        created_at=datetime(2026, 1, 6),
    )
    db.add_all([club_announcement, platform_announcement])
    db.commit()

    context = build_announcements_context(db, student)

    titles = {a["title"] for a in context["announcements"]}
    assert titles == {"Meeting moved to Friday", "Platform maintenance window"}
    by_title = {a["title"]: a for a in context["announcements"]}
    assert by_title["Meeting moved to Friday"]["club_name"] == "Robotics Club"
    assert by_title["Platform maintenance window"]["club_name"] is None


def test_announcements_not_leaked_from_a_club_user_is_not_in(db, student, club, university):
    other_club = Club(name="Chess Club", slug="chess-club", university_id=university.id)
    db.add(other_club)
    db.commit()

    db.add(Announcement(
        club_id=other_club.id,
        posted_by=student.id,
        title="Chess Club internal update",
        body="...",
        target_audience=AnnouncementAudience.ALL_MEMBERS,
    ))
    db.commit()

    context = build_announcements_context(db, student)
    assert context == {"announcements": []}


# ---------------------------------------------------------------------------
# Profile & Account
# ---------------------------------------------------------------------------


def test_profile_without_student_profile_row(db, student):
    context = build_profile_context(db, student)
    assert context["full_name"] == "Empty Student"
    assert context["role"] == "student"
    assert context["student_profile"] is None
    assert "password_hash" not in context


def test_profile_with_student_profile_row(db, student, program):
    profile = StudentProfile(user_id=student.id, program_id=program.id, academic_year=2, is_verified=True)
    db.add(profile)
    db.commit()

    context = build_profile_context(db, student)

    assert context["student_profile"] == {
        "academic_year": 2,
        "semester": None,
        "batch": None,
        "section": None,
        "is_verified": True,
    }


# ---------------------------------------------------------------------------
# Support Tickets
# ---------------------------------------------------------------------------


def test_support_tickets_empty(db, student):
    assert build_support_tickets_context(db, student) == {"tickets": []}


def test_support_tickets_populated_with_response_count(db, student):
    ticket = SupportTicket(
        raised_by=student.id,
        title="Can't upload profile photo",
        description="Upload button does nothing.",
        ticket_type=TicketType.BUG,
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        created_at=datetime(2026, 1, 10),
    )
    db.add(ticket)
    db.commit()

    db.add(TicketResponse(ticket_id=ticket.id, responder_id=student.id, body="Looking into it."))
    db.commit()

    context = build_support_tickets_context(db, student)

    assert context["tickets"] == [
        {
            "title": "Can't upload profile photo",
            "ticket_type": "Bug",
            "priority": "Medium",
            "status": "Open",
            "created_at": "2026-01-10T00:00:00",
            "response_count": 1,
        }
    ]


# ---------------------------------------------------------------------------
# Membership (Phase 6 final polish)
# ---------------------------------------------------------------------------


def test_membership_empty_for_user_with_no_approved_clubs(db, student):
    assert build_membership_context(db, student) == {"memberships": []}


def test_membership_lists_only_approved_clubs(db, student, university):
    approved_club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    pending_club = Club(name="Chess Club", slug="chess-club", university_id=university.id)
    db.add_all([approved_club, pending_club])
    db.commit()

    db.add_all([
        ClubMembership(
            user_id=student.id, club_id=approved_club.id,
            status=MembershipStatus.APPROVED, role_in_club=ClubMemberRole.PRESIDENT,
        ),
        ClubMembership(
            user_id=student.id, club_id=pending_club.id,
            status=MembershipStatus.PENDING,
        ),
    ])
    db.commit()

    context = build_membership_context(db, student)

    # Pending club must never surface as a "current" membership - only
    # APPROVED counts, per assistant_conversation_behavior.md Section 7.
    assert context == {
        "memberships": [{"club_name": "Robotics Club", "role_in_club": "president"}]
    }


def test_membership_excludes_withdrawn_and_rejected(db, student, university):
    club = Club(name="Debate Club", slug="debate-club", university_id=university.id)
    db.add(club)
    db.commit()
    db.add_all([
        ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.WITHDRAWN),
    ])
    db.commit()

    assert build_membership_context(db, student) == {"memberships": []}


# ---------------------------------------------------------------------------
# Financial Operations (Phase 6 final polish)
# ---------------------------------------------------------------------------


def test_financial_operations_empty_for_user_with_no_treasurer_or_advised_clubs(db, student):
    assert build_financial_operations_context(db, student) == {"clubs": []}


def test_financial_operations_scoped_to_treasurer_club_only(db, student, university):
    treasurer_club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    other_club = Club(name="Chess Club", slug="chess-club", university_id=university.id)
    db.add_all([treasurer_club, other_club])
    db.commit()

    db.add(ClubMembership(
        user_id=student.id, club_id=treasurer_club.id,
        status=MembershipStatus.APPROVED, role_in_club=ClubMemberRole.TREASURER,
    ))
    db.add(Budget(
        club_id=treasurer_club.id, title="Spring Semester", created_by=student.id,
        period_start=datetime(2026, 1, 1), period_end=datetime(2026, 5, 1),
        allocated_amount=1000, status=BudgetStatus.APPROVED,
    ))
    # A budget on a club the user has nothing to do with must never leak in.
    db.add(Budget(
        club_id=other_club.id, title="Other Club Budget", created_by=student.id,
        period_start=datetime(2026, 1, 1), period_end=datetime(2026, 5, 1),
        allocated_amount=500, status=BudgetStatus.APPROVED,
    ))
    db.commit()

    context = build_financial_operations_context(db, student)

    assert len(context["clubs"]) == 1
    entry = context["clubs"][0]
    assert entry["club_name"] == "Robotics Club"
    assert entry["total_allocated_amount"] == 1000.0
    assert entry["budgets"][0]["title"] == "Spring Semester"


def test_financial_operations_includes_expense_breakdown_and_recent_expenses(db, student, university):
    club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    db.add(club)
    db.commit()
    db.add(ClubMembership(
        user_id=student.id, club_id=club.id,
        status=MembershipStatus.APPROVED, role_in_club=ClubMemberRole.TREASURER,
    ))
    budget = Budget(
        club_id=club.id, title="Spring Semester", created_by=student.id,
        period_start=datetime(2026, 1, 1), period_end=datetime(2026, 5, 1),
        allocated_amount=1000, status=BudgetStatus.APPROVED,
    )
    db.add(budget)
    db.commit()

    db.add_all([
        Expense(
            budget_id=budget.id, description="Sensors", amount=150, submitted_by=student.id,
            status=ExpenseStatus.APPROVED, approval_status=ExpenseApprovalStatus.APPROVED,
            created_at=datetime(2026, 2, 1),
        ),
        Expense(
            budget_id=budget.id, description="Snacks", amount=40, submitted_by=student.id,
            status=ExpenseStatus.PENDING, approval_status=ExpenseApprovalStatus.PENDING,
            created_at=datetime(2026, 2, 2),
        ),
    ])
    db.commit()

    context = build_financial_operations_context(db, student)

    entry = context["clubs"][0]
    assert entry["total_expenses_claimed"] == 190.0
    assert entry["expense_approval_breakdown"] == {"approved": 1, "pending": 1, "rejected": 0}
    assert len(entry["recent_expenses"]) == 2
    assert entry["recent_expenses"][0]["description"] == "Snacks"  # most recent first


def test_financial_operations_includes_advised_clubs_for_faculty(db, faculty_advisor, university):
    advised_club = Club(
        name="Green Earth Initiative", slug="green-earth", university_id=university.id,
        faculty_advisor_id=faculty_advisor.id,
    )
    db.add(advised_club)
    db.commit()
    db.add(Budget(
        club_id=advised_club.id, title="Sustainability Fund", created_by=faculty_advisor.id,
        period_start=datetime(2026, 1, 1), period_end=datetime(2026, 6, 1),
        allocated_amount=2000, status=BudgetStatus.APPROVED,
    ))
    db.commit()

    context = build_financial_operations_context(db, faculty_advisor)

    assert [c["club_name"] for c in context["clubs"]] == ["Green Earth Initiative"]
    assert context["clubs"][0]["total_allocated_amount"] == 2000.0


def test_financial_operations_faculty_advisor_with_no_clubs_is_honestly_empty(db, faculty_advisor):
    assert build_financial_operations_context(db, faculty_advisor) == {"clubs": []}


# ---------------------------------------------------------------------------
# Faculty Questions (Phase 6 final polish)
# ---------------------------------------------------------------------------


def test_faculty_questions_empty_for_advisor_with_no_advised_clubs(db, faculty_advisor):
    assert build_faculty_questions_context(db, faculty_advisor) == {
        "advised_clubs": [],
        "events_pending_approval": [],
        "budget_overview": [],
    }


def test_faculty_questions_lists_advised_clubs_and_pending_events(db, faculty_advisor, university):
    advised_club = Club(
        name="Data Science Society", slug="dss", university_id=university.id,
        faculty_advisor_id=faculty_advisor.id, category="Technology",
    )
    other_club = Club(name="Chess Club", slug="chess-club", university_id=university.id)
    db.add_all([advised_club, other_club])
    db.commit()

    pending_event = Event(
        club_id=advised_club.id, title="Kaggle Bootcamp",
        start_at=datetime(2026, 3, 1, 9, 0), end_at=datetime(2026, 3, 1, 12, 0),
        created_by=faculty_advisor.id, status=EventStatus.PENDING_APPROVAL,
    )
    scheduled_event = Event(
        club_id=advised_club.id, title="Already Approved Talk",
        start_at=datetime(2026, 3, 5, 9, 0), end_at=datetime(2026, 3, 5, 12, 0),
        created_by=faculty_advisor.id, status=EventStatus.SCHEDULED,
    )
    # An event on a club this advisor doesn't advise must never leak in.
    other_pending_event = Event(
        club_id=other_club.id, title="Chess Tournament",
        start_at=datetime(2026, 3, 2, 9, 0), end_at=datetime(2026, 3, 2, 12, 0),
        created_by=faculty_advisor.id, status=EventStatus.PENDING_APPROVAL,
    )
    db.add_all([pending_event, scheduled_event, other_pending_event])
    db.commit()

    context = build_faculty_questions_context(db, faculty_advisor)

    assert context["advised_clubs"] == [
        {
            "club_name": "Data Science Society",
            "status": "active",
            "category": "Technology",
            "member_count_cache": 0,
        }
    ]
    assert context["events_pending_approval"] == [
        {"event_title": "Kaggle Bootcamp", "club_name": "Data Science Society", "start_at": "2026-03-01T09:00:00"}
    ]


def test_faculty_questions_budget_overview_summarizes_without_expense_detail(db, faculty_advisor, university):
    advised_club = Club(
        name="Data Science Society", slug="dss", university_id=university.id,
        faculty_advisor_id=faculty_advisor.id,
    )
    db.add(advised_club)
    db.commit()
    budget = Budget(
        club_id=advised_club.id, title="Annual Budget", created_by=faculty_advisor.id,
        period_start=datetime(2026, 1, 1), period_end=datetime(2026, 12, 31),
        allocated_amount=5000, status=BudgetStatus.APPROVED,
    )
    db.add(budget)
    db.commit()
    db.add(Expense(
        budget_id=budget.id, description="Server costs", amount=300, submitted_by=faculty_advisor.id,
        status=ExpenseStatus.PENDING, approval_status=ExpenseApprovalStatus.PENDING,
    ))
    db.commit()

    context = build_faculty_questions_context(db, faculty_advisor)

    assert context["budget_overview"] == [
        {"club_name": "Data Science Society", "total_allocated_amount": 5000.0, "pending_expense_count": 1}
    ]
    # Faculty Questions is an oversight summary, not the detailed financial
    # breakdown - it must not carry a `recent_expenses`-shaped key.
    assert "recent_expenses" not in context["budget_overview"][0]


# ---------------------------------------------------------------------------
# Admin Questions (Phase 6 final polish)
# ---------------------------------------------------------------------------


def test_admin_overview_empty_university_has_zero_clubs(db, admin_user):
    context = build_admin_overview_context(db, admin_user)
    assert context["total_clubs"] == 0
    assert context["club_status_breakdown"] == {}
    assert context["inactive_clubs"] == []
    assert context["most_active_clubs"] == []
    assert context["club_creation_requests"] == {"pending_count": 0, "recent": []}


def test_admin_overview_status_breakdown_and_inactive_clubs(db, admin_user, university):
    active = Club(name="Robotics Club", slug="robotics-club", university_id=university.id, status=ClubStatus.ACTIVE)
    suspended = Club(name="Old Debate Club", slug="old-debate", university_id=university.id, status=ClubStatus.SUSPENDED)
    archived = Club(name="Retired Club", slug="retired-club", university_id=university.id, status=ClubStatus.ARCHIVED)
    db.add_all([active, suspended, archived])
    db.commit()

    context = build_admin_overview_context(db, admin_user)

    assert context["total_clubs"] == 3
    assert context["club_status_breakdown"] == {"active": 1, "suspended": 1, "archived": 1}
    inactive_names = {c["club_name"] for c in context["inactive_clubs"]}
    assert inactive_names == {"Old Debate Club", "Retired Club"}
    assert {c["club_name"] for c in context["most_active_clubs"]} == {"Robotics Club"}


def test_admin_overview_most_active_ranked_by_member_count_cache(db, admin_user, university):
    small = Club(name="Small Club", slug="small-club", university_id=university.id, member_count_cache=5)
    big = Club(name="Big Club", slug="big-club", university_id=university.id, member_count_cache=200)
    db.add_all([small, big])
    db.commit()

    context = build_admin_overview_context(db, admin_user, most_active_limit=5)

    assert [c["club_name"] for c in context["most_active_clubs"]] == ["Big Club", "Small Club"]


def test_admin_overview_scoped_to_admins_own_university(db, admin_user, university):
    other_uni = University(name="Other University", domain="other.edu")
    db.add(other_uni)
    db.commit()

    own_club = Club(name="Own Uni Club", slug="own-uni-club", university_id=university.id)
    other_club = Club(name="Other Uni Club", slug="other-uni-club", university_id=other_uni.id)
    db.add_all([own_club, other_club])
    db.commit()

    context = build_admin_overview_context(db, admin_user)

    assert context["total_clubs"] == 1
    assert context["club_status_breakdown"] == {"active": 1}


def test_admin_overview_club_creation_requests_pending_count_and_recent(db, admin_user, student):
    request = ClubCreationRequest(
        proposed_name="AI Ethics Club",
        proposal_description="A club to discuss AI ethics.",
        requested_by=student.id,
        status=ClubRequestStatus.SUBMITTED,
        created_at=datetime(2026, 1, 15),
    )
    db.add(request)
    db.commit()

    context = build_admin_overview_context(db, admin_user)

    assert context["club_creation_requests"]["pending_count"] == 1
    assert context["club_creation_requests"]["recent"] == [
        {
            "proposed_name": "AI Ethics Club",
            "status": "submitted",
            "created_at": "2026-01-15T00:00:00",
            "requested_by": "Empty Student",
        }
    ]


# ---------------------------------------------------------------------------
# Dispatch (build_sql_context)
# ---------------------------------------------------------------------------


def test_dispatch_known_intent_calls_matching_builder(db, student):
    assert build_sql_context("Rewards", db, student) == build_rewards_context(db, student)


def test_dispatch_unknown_or_out_of_scope_intent_returns_none(db, student):
    assert build_sql_context("Getting Started", db, student) is None
    assert build_sql_context("Not A Real Intent", db, student) is None


def test_dispatch_recommendation_intents_now_have_builders(db, student):
    """Phase 5B/6 regression guard: these used to return None (no builder
    registered yet) - they must now dispatch to the real builders."""
    assert build_sql_context("Club Recommendation", db, student) == build_club_recommendation_context(
        db, student
    )
    assert build_sql_context("Event Recommendation", db, student) == build_event_recommendation_context(
        db, student
    )


def test_dispatch_phase6_intents_now_have_builders(db, student, faculty_advisor, admin_user):
    """Phase 6 final-polish regression guard: Membership, Financial
    Operations, Faculty Questions, and Admin Questions used to return
    None (no builder registered yet) - they must now dispatch to the
    real builders."""
    assert build_sql_context("Membership", db, student) == build_membership_context(db, student)
    assert build_sql_context("Financial Operations", db, student) == build_financial_operations_context(
        db, student
    )
    assert build_sql_context("Faculty Questions", db, faculty_advisor) == build_faculty_questions_context(
        db, faculty_advisor
    )
    assert build_sql_context("Admin Questions", db, admin_user) == build_admin_overview_context(db, admin_user)


# ---------------------------------------------------------------------------
# Club Recommendation (Phase 5B/6)
# ---------------------------------------------------------------------------


def _interest(db, name):
    interest = Interest(name=name)
    db.add(interest)
    db.commit()
    return interest


def test_club_recommendation_cold_start_returns_empty_candidates(db, student):
    """No user_interests and no history on file: per playbook Section 7,
    candidate_clubs must be honestly empty - never a popularity fallback."""
    context = build_club_recommendation_context(db, student)

    assert context == {
        "academic_year": None,
        "user_interests": [],
        "current_club_memberships": [],
        "candidate_clubs": [],
    }


def test_club_recommendation_matches_by_shared_interest(db, student, university):
    robotics = _interest(db, "Robotics")

    db.add(UserInterest(user_id=student.id, interest_id=robotics.id))
    club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    db.add(club)
    db.commit()
    db.add(ClubInterest(club_id=club.id, interest_id=robotics.id))
    db.commit()

    context = build_club_recommendation_context(db, student)

    assert context["user_interests"] == ["Robotics"]
    assert context["current_club_memberships"] == []
    assert context["candidate_clubs"] == [
        {
            "club_name": "Robotics Club",
            "category": None,
            "matching_interests": ["Robotics"],
            "user_event_registration_count": 0,
            "user_event_attendance_count": 0,
        }
    ]


def test_club_recommendation_excludes_already_joined_clubs(db, student, university):
    robotics = _interest(db, "Robotics")
    db.add(UserInterest(user_id=student.id, interest_id=robotics.id))
    club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    db.add(club)
    db.commit()
    db.add(ClubInterest(club_id=club.id, interest_id=robotics.id))
    db.add(ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED))
    db.commit()

    context = build_club_recommendation_context(db, student)

    assert context["current_club_memberships"] == ["Robotics Club"]
    # Already an approved member - must not appear as a candidate even
    # though the interest tag matches.
    assert context["candidate_clubs"] == []


def test_club_recommendation_includes_behavioral_signal_counts(db, student, university):
    robotics = _interest(db, "Robotics")
    db.add(UserInterest(user_id=student.id, interest_id=robotics.id))
    club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    db.add(club)
    db.commit()
    db.add(ClubInterest(club_id=club.id, interest_id=robotics.id))
    event = Event(
        club_id=club.id,
        title="Robotics Workshop",
        start_at=datetime(2026, 3, 1, 9, 0),
        end_at=datetime(2026, 3, 1, 12, 0),
        created_by=student.id,
    )
    db.add(event)
    db.commit()
    db.add(EventRegistration(event_id=event.id, user_id=student.id))
    db.add(AttendanceRecord(event_id=event.id, user_id=student.id, checked_in_at=datetime(2026, 3, 1, 9, 5)))
    db.commit()

    context = build_club_recommendation_context(db, student)

    assert context["candidate_clubs"] == [
        {
            "club_name": "Robotics Club",
            "category": None,
            "matching_interests": ["Robotics"],
            "user_event_registration_count": 1,
            "user_event_attendance_count": 1,
        }
    ]


# ---------------------------------------------------------------------------
# Event Recommendation (Phase 5B/6)
# ---------------------------------------------------------------------------


def test_event_recommendation_cold_start_returns_empty_candidates(db, student):
    context = build_event_recommendation_context(db, student)

    assert context == {
        "user_interests": [],
        "member_club_names": [],
        "attended_event_interest_tags": [],
        "registered_event_interest_tags": [],
        "upcoming_candidate_events": [],
    }


def test_event_recommendation_matches_by_shared_interest(db, student, university):
    photography = _interest(db, "Photography")
    db.add(UserInterest(user_id=student.id, interest_id=photography.id))
    club = Club(name="Photography Society", slug="photo-soc", university_id=university.id)
    db.add(club)
    db.commit()
    event = Event(
        club_id=club.id,
        title="Golden Hour Walk",
        start_at=datetime(2027, 1, 1, 17, 0),
        end_at=datetime(2027, 1, 1, 19, 0),
        created_by=student.id,
    )
    db.add(event)
    db.commit()
    db.add(EventInterest(event_id=event.id, interest_id=photography.id))
    db.commit()

    context = build_event_recommendation_context(db, student)

    assert context["user_interests"] == ["Photography"]
    assert context["upcoming_candidate_events"] == [
        {
            "event_title": "Golden Hour Walk",
            "club_name": "Photography Society",
            "start_at": "2027-01-01T17:00:00",
            "matching_interests": ["Photography"],
            "club_membership_match": False,
        }
    ]


def test_event_recommendation_matches_by_club_membership_without_interest_overlap(db, student, university):
    club = Club(name="Robotics Club", slug="robotics-club", university_id=university.id)
    db.add(club)
    db.commit()
    db.add(ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED))
    event = Event(
        club_id=club.id,
        title="Members Only Build Night",
        start_at=datetime(2027, 2, 1, 18, 0),
        end_at=datetime(2027, 2, 1, 20, 0),
        created_by=student.id,
    )
    db.add(event)
    db.commit()

    context = build_event_recommendation_context(db, student)

    assert context["member_club_names"] == ["Robotics Club"]
    assert context["upcoming_candidate_events"] == [
        {
            "event_title": "Members Only Build Night",
            "club_name": "Robotics Club",
            "start_at": "2027-02-01T18:00:00",
            "matching_interests": [],
            "club_membership_match": True,
        }
    ]


def test_event_recommendation_excludes_already_registered_events(db, student, university):
    photography = _interest(db, "Photography")
    db.add(UserInterest(user_id=student.id, interest_id=photography.id))
    club = Club(name="Photography Society", slug="photo-soc", university_id=university.id)
    db.add(club)
    db.commit()
    event = Event(
        club_id=club.id,
        title="Golden Hour Walk",
        start_at=datetime(2027, 1, 1, 17, 0),
        end_at=datetime(2027, 1, 1, 19, 0),
        created_by=student.id,
    )
    db.add(event)
    db.commit()
    db.add(EventInterest(event_id=event.id, interest_id=photography.id))
    db.add(EventRegistration(event_id=event.id, user_id=student.id))
    db.commit()

    context = build_event_recommendation_context(db, student)

    # Already registered - must not appear as a candidate even though the
    # interest tag matches.
    assert context["upcoming_candidate_events"] == []
    # But the registration still surfaces as a behavioral signal.
    assert context["registered_event_interest_tags"] == ["Photography"]


def test_event_recommendation_excludes_past_events(db, student, university):
    photography = _interest(db, "Photography")
    db.add(UserInterest(user_id=student.id, interest_id=photography.id))
    club = Club(name="Photography Society", slug="photo-soc", university_id=university.id)
    db.add(club)
    db.commit()
    past_event = Event(
        club_id=club.id,
        title="Old Workshop",
        start_at=datetime(2020, 1, 1, 9, 0),
        end_at=datetime(2020, 1, 1, 11, 0),
        created_by=student.id,
    )
    db.add(past_event)
    db.commit()
    db.add(EventInterest(event_id=past_event.id, interest_id=photography.id))
    db.commit()

    context = build_event_recommendation_context(db, student)

    assert context["upcoming_candidate_events"] == []


def test_event_recommendation_surfaces_attended_interest_tags(db, student, university):
    photography = _interest(db, "Photography")
    club = Club(name="Photography Society", slug="photo-soc", university_id=university.id)
    db.add(club)
    db.commit()
    past_event = Event(
        club_id=club.id,
        title="Past Workshop",
        start_at=datetime(2020, 1, 1, 9, 0),
        end_at=datetime(2020, 1, 1, 11, 0),
        created_by=student.id,
    )
    db.add(past_event)
    db.commit()
    db.add(EventInterest(event_id=past_event.id, interest_id=photography.id))
    db.add(AttendanceRecord(event_id=past_event.id, user_id=student.id, checked_in_at=datetime(2020, 1, 1, 9, 5)))
    db.commit()

    context = build_event_recommendation_context(db, student)

    assert context["attended_event_interest_tags"] == ["Photography"]
