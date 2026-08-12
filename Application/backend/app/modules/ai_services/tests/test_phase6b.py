"""Unit tests for Phase 6B: report_context.py, report_service.py,
analytics_service.py, content_service.py.

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/test_phase6b.py -q

Same fixture pattern as test_sql_context_builder.py/test_routes.py - a
fresh in-memory SQLite DB per test. Gemini is never called for real:
every test that reaches a *_service.generate_response call point
monkeypatches ``gemini_client.generate_response`` directly, the same
approach test_prompt_builder.py/test_gemini_client.py use for isolating
Gemini from the rest of the pipeline.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database import models  # noqa: F401 - registers all mapped tables
from app.database.enums import (
    ClubMemberRole,
    ClubStatus,
    EmergencyCategory,
    EmergencyStatus,
    EventStatus,
    ExpenseApprovalStatus,
    MembershipStatus,
    UserRole,
    VolunteerTaskStatus,
)
from app.database.models.applications import ClubJoinApplication
from app.database.models.auth import User
from app.database.models.clubs import Club, ClubMembership
from app.database.models.events import Event, VolunteerAssignment
from app.database.models.finance import Budget, Expense
from app.database.models.support import EmergencyReport
from app.database.models.university import University

from app.modules.ai_services import analytics_service, content_service, report_service
from app.modules.ai_services.report_context import (
    build_budget_platform_context,
    build_club_activity_context,
    build_emergency_summary_context,
    build_volunteer_report_context,
    officer_club_ids,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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
def student(db, university):
    user = User(
        email="student@test.edu", password_hash="x", full_name="Student One",
        role=UserRole.STUDENT, university_id=university.id,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def president(db, university, club):
    user = User(
        email="president@test.edu", password_hash="x", full_name="Club President",
        role=UserRole.STUDENT, university_id=university.id,
    )
    db.add(user)
    db.commit()
    db.add(ClubMembership(
        user_id=user.id, club_id=club.id, status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    ))
    db.commit()
    return user


@pytest.fixture()
def treasurer(db, university, club):
    user = User(
        email="treasurer@test.edu", password_hash="x", full_name="Club Treasurer",
        role=UserRole.STUDENT, university_id=university.id,
    )
    db.add(user)
    db.commit()
    db.add(ClubMembership(
        user_id=user.id, club_id=club.id, status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    ))
    db.commit()
    return user


@pytest.fixture()
def faculty_advisor(db, university):
    user = User(
        email="advisor@test.edu", password_hash="x", full_name="Dr. Advisor",
        role=UserRole.FACULTY_ADVISOR, university_id=university.id,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def admin_user(db, university):
    user = User(
        email="admin@test.edu", password_hash="x", full_name="Admin User",
        role=UserRole.SYSTEM_ADMIN, university_id=university.id,
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


def _club_roles(db, user):
    from app.modules.ai_services.routes import _resolve_approved_club_roles
    return _resolve_approved_club_roles(db, user.id)


def _fake_gemini(monkeypatch, module, text="This is a generated summary."):
    monkeypatch.setattr(module, "generate_response", lambda prompt, model_name=None: text)


# ---------------------------------------------------------------------------
# report_context.py
# ---------------------------------------------------------------------------


def test_officer_club_ids_empty_for_plain_member(db, student, club):
    db.add(ClubMembership(
        user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    ))
    db.commit()
    assert officer_club_ids(db, student.id) == []


def test_officer_club_ids_includes_president(db, president, club):
    assert officer_club_ids(db, president.id) == [club.id]


def test_club_activity_context_for_leadership(db, president, club):
    db.add(Event(
        club_id=club.id, title="Kickoff", start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=1), status=EventStatus.SCHEDULED,
        created_by=president.id,
    ))
    db.commit()

    result = build_club_activity_context(db, president)
    assert result["scope"] == "clubs you hold an officer role in"
    assert len(result["clubs"]) == 1
    assert result["clubs"][0]["club_name"] == "Robotics Club"
    assert result["clubs"][0]["event_status_breakdown"] == {"scheduled": 1}


def test_club_activity_context_admin_is_platform_wide(db, admin_user, club):
    result = build_club_activity_context(db, admin_user)
    assert result["scope"] == "platform-wide (your university)"
    assert len(result["clubs"]) == 1


def test_club_activity_context_empty_for_plain_student(db, student):
    result = build_club_activity_context(db, student)
    assert result["clubs"] == []


def test_volunteer_report_context_empty(db, student):
    assert build_volunteer_report_context(db, student) == {"assignments": []}


def test_volunteer_report_context_populated(db, president, club):
    event_row = Event(
        club_id=club.id, title="Fest", start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=2), status=EventStatus.SCHEDULED,
        created_by=president.id,
    )
    db.add(event_row)
    db.commit()

    membership = db.query(ClubMembership).filter_by(user_id=president.id).first()
    db.add(VolunteerAssignment(
        event_id=event_row.id, assignee_membership_id=membership.id, assigned_by=president.id,
        task_description="Set up chairs", status=VolunteerTaskStatus.ASSIGNED,
    ))
    db.commit()

    result = build_volunteer_report_context(db, president)
    assert len(result["assignments"]) == 1
    assert result["assignments"][0]["task_description"] == "Set up chairs"
    assert result["assignments"][0]["club_name"] == "Robotics Club"


def test_emergency_summary_admin_only_aggregate(db, admin_user, student):
    db.add(EmergencyReport(
        reported_by=student.id, category=EmergencyCategory.MEDICAL,
        description="details", status=EmergencyStatus.REPORTED, created_at=datetime.utcnow(),
    ))
    db.commit()

    result = build_emergency_summary_context(db, admin_user)
    assert result["total_reports"] == 1
    assert result["category_breakdown"] == {"medical": 1}
    # No free-text description or reporter identity ever surfaces.
    assert "description" not in result["recent"][0]
    assert "reported_by" not in result["recent"][0]


def test_emergency_summary_empty(db, admin_user):
    result = build_emergency_summary_context(db, admin_user)
    assert result["total_reports"] == 0
    assert result["recent"] == []


def test_budget_platform_context_aggregates_across_clubs(db, admin_user, club):
    budget = Budget(
        club_id=club.id, title="Annual Budget", period_start=datetime.utcnow(),
        period_end=datetime.utcnow() + timedelta(days=30), allocated_amount=1000,
        created_by=admin_user.id,
    )
    db.add(budget)
    db.commit()
    db.add(Expense(
        budget_id=budget.id, description="Snacks", amount=200, submitted_by=admin_user.id,
        approval_status=ExpenseApprovalStatus.APPROVED,
    ))
    db.commit()

    result = build_budget_platform_context(db, admin_user)
    assert result["total_allocated_amount"] == 1000.0
    assert result["total_expenses_claimed"] == 200.0
    assert result["expense_approval_breakdown"]["approved"] == 1


# ---------------------------------------------------------------------------
# report_service.py
# ---------------------------------------------------------------------------


def test_generate_report_unknown_type_is_unauthorized(db, student):
    result = report_service.generate_report("not_a_real_type", db, student, [])
    assert result["label"] is None
    assert result["authorized"] is False
    assert result["summary"] is None


def test_generate_report_personal_type_always_allowed(db, student, monkeypatch):
    _fake_gemini(monkeypatch, report_service)
    result = report_service.generate_report("membership", db, student, [])
    assert result["authorized"] is True
    assert result["summary"] == "This is a generated summary."
    assert result["data"] == {"memberships": []}


def test_generate_report_budget_denied_for_plain_student(db, student):
    result = report_service.generate_report("budget", db, student, [])
    assert result["authorized"] is False
    assert result["label"] == "Budget Report"


def test_generate_report_budget_allowed_for_treasurer(db, treasurer, monkeypatch):
    _fake_gemini(monkeypatch, report_service)
    club_roles = _club_roles(db, treasurer)
    result = report_service.generate_report("budget", db, treasurer, club_roles)
    assert result["authorized"] is True


def test_generate_report_emergency_denied_for_faculty(db, faculty_advisor):
    result = report_service.generate_report("emergency_summary", db, faculty_advisor, [])
    assert result["authorized"] is False


def test_generate_report_emergency_allowed_for_admin(db, admin_user, monkeypatch):
    _fake_gemini(monkeypatch, report_service)
    result = report_service.generate_report("emergency_summary", db, admin_user, [])
    assert result["authorized"] is True


def test_generate_report_student_activity_combines_sources(db, student, monkeypatch):
    _fake_gemini(monkeypatch, report_service)
    result = report_service.generate_report("student_activity", db, student, [])
    assert result["authorized"] is True
    assert set(result["data"].keys()) == {
        "memberships", "attendance", "rewards", "open_support_tickets",
    }


# ---------------------------------------------------------------------------
# analytics_service.py
# ---------------------------------------------------------------------------


def test_financial_analytics_access(db, student, treasurer, faculty_advisor, admin_user):
    assert analytics_service.financial_analytics_access(student, []) is False
    assert analytics_service.financial_analytics_access(treasurer, _club_roles(db, treasurer)) is True
    assert analytics_service.financial_analytics_access(faculty_advisor, []) is True
    assert analytics_service.financial_analytics_access(admin_user, []) is True


def test_build_financial_analytics_computes_utilization(db, treasurer, club):
    budget = Budget(
        club_id=club.id, title="Spring Budget", period_start=datetime.utcnow(),
        period_end=datetime.utcnow() + timedelta(days=30), allocated_amount=500,
        created_by=treasurer.id,
    )
    db.add(budget)
    db.commit()
    db.add(Expense(
        budget_id=budget.id, description="Prizes", amount=250, submitted_by=treasurer.id,
        approval_status=ExpenseApprovalStatus.APPROVED,
    ))
    db.commit()

    result = analytics_service.build_financial_analytics(db, treasurer)
    clubs = result["analytics"]["clubs"]
    assert len(clubs) == 1
    assert clubs[0]["utilization_percent"] == 50.0
    assert result["chart"]["type"] == "bar"


def test_build_performance_analytics_personal_scope_for_plain_student(db, student):
    result = analytics_service.build_performance_analytics(db, student, [])
    assert result["scope"] == "personal"
    assert "club_involvement" in result["analytics"]


def test_build_performance_analytics_led_clubs_scope_for_president(db, president):
    club_roles = _club_roles(db, president)
    result = analytics_service.build_performance_analytics(db, president, club_roles)
    assert result["scope"] == "led_clubs"


def test_build_performance_analytics_platform_scope_for_admin(db, admin_user):
    result = analytics_service.build_performance_analytics(db, admin_user, [])
    assert result["scope"] == "platform"


def test_interpret_analytics_calls_gemini(db, student, monkeypatch):
    _fake_gemini(monkeypatch, analytics_service, text="Explanation text.")
    text = analytics_service.interpret_analytics({"a": 1}, student, "Test Analytics")
    assert text == "Explanation text."


# ---------------------------------------------------------------------------
# content_service.py
# ---------------------------------------------------------------------------


def test_generate_content_unknown_type():
    class Dummy:
        full_name = "Someone"
    result = content_service.generate_content("not_a_type", "details", Dummy())
    assert result["authorized"] is False
    assert result["draft"] is None


def test_generate_content_known_type(db, student, monkeypatch):
    _fake_gemini(monkeypatch, content_service, text="Join us for the event!")
    result = content_service.generate_content("invitation", "Robotics Club open house on Friday", student)
    assert result["authorized"] is True
    assert result["draft"] == "Join us for the event!"
    assert result["label"] == "Invitation Message"


def test_generate_content_every_type_has_label_and_instruction():
    for content_type, (label, instruction) in content_service.CONTENT_TYPES.items():
        assert label and instruction
