"""FK enforcement, unique/composite-unique, check constraints, and
CASCADE / SET NULL / RESTRICT delete behaviour."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from database.enums import MembershipStatus, UserRole
from database.models.auth import User
from database.models.clubs import Club, ClubMembership
from database.models.events import AttendanceRecord, Event, EventRegistration
from database.models.finance import Budget, Expense


def _make_user(session, email, role=UserRole.STUDENT):
    user = User(email=email, password_hash="hash", full_name="Test User", role=role)
    session.add(user)
    session.commit()
    return user


def test_foreign_key_enforcement(session):
    membership = ClubMembership(user_id=9999, club_id=9999, status=MembershipStatus.PENDING)
    session.add(membership)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_unique_constraint_on_email(session):
    _make_user(session, "dup@example.com")
    session.add(User(email="dup@example.com", password_hash="x", full_name="Dup"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_composite_unique_constraint_membership(session, sample_university):
    advisor = _make_user(session, "advisor@example.com")
    student = _make_user(session, "student@example.com")
    club = Club(name="Chess Club", slug="chess-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()

    session.add(ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.PENDING))
    session.commit()

    # Same user + club combination again should violate uq_user_club
    session.add(ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.PENDING))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_check_constraint_event_dates(session, sample_university):
    advisor = _make_user(session, "advisor2@example.com")
    club = Club(name="Art Club", slug="art-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()

    bad_event = Event(
        club_id=club.id,
        title="Bad Event",
        start_at=datetime.utcnow(),
        end_at=datetime.utcnow() - timedelta(hours=1),  # end before start -> violates ck_event_dates
        created_by=advisor.id,
    )
    session.add(bad_event)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_check_constraint_expense_amount_positive(session, sample_university):
    advisor = _make_user(session, "advisor3@example.com")
    club = Club(name="Music Club", slug="music-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()

    budget = Budget(
        club_id=club.id, title="Budget", period_start=datetime.utcnow(),
        period_end=datetime.utcnow() + timedelta(days=1), allocated_amount=100, created_by=advisor.id,
    )
    session.add(budget)
    session.commit()

    bad_expense = Expense(budget_id=budget.id, description="Invalid", amount=-5, submitted_by=advisor.id)
    session.add(bad_expense)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_cascade_delete_club_removes_memberships(session, sample_university):
    advisor = _make_user(session, "advisor4@example.com")
    student = _make_user(session, "student4@example.com")
    club = Club(name="Debate Club", slug="debate-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()

    membership = ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED)
    session.add(membership)
    session.commit()
    membership_id = membership.id

    session.delete(club)
    session.commit()

    assert session.get(ClubMembership, membership_id) is None


def test_set_null_on_club_faculty_advisor_delete(session, sample_university):
    advisor = _make_user(session, "advisor5@example.com")
    club = Club(name="Photography Club", slug="photo-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()
    club_id = club.id

    session.delete(advisor)
    session.commit()

    refreshed = session.get(Club, club_id)
    assert refreshed.faculty_advisor_id is None


def test_restrict_on_event_creator_delete(session, sample_university):
    advisor = _make_user(session, "advisor6@example.com")
    club = Club(name="Coding Club", slug="coding-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()

    event = Event(
        club_id=club.id, title="Hackathon", start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=3), created_by=advisor.id,
    )
    session.add(event)
    session.commit()

    # events.created_by is ON DELETE RESTRICT -> deleting the creator must fail
    session.delete(advisor)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_cascade_delete_event_removes_registrations_and_attendance(session, sample_university):
    advisor = _make_user(session, "advisor7@example.com")
    student = _make_user(session, "student7@example.com")
    club = Club(name="Gaming Club", slug="gaming-club-2", faculty_advisor_id=advisor.id,
                university_id=sample_university.id)
    session.add(club)
    session.commit()

    event = Event(
        club_id=club.id, title="LAN Party", start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=4), created_by=advisor.id,
    )
    session.add(event)
    session.commit()

    registration = EventRegistration(event_id=event.id, user_id=student.id)
    attendance = AttendanceRecord(event_id=event.id, user_id=student.id)
    session.add_all([registration, attendance])
    session.commit()
    reg_id, att_id = registration.id, attendance.id

    session.delete(event)
    session.commit()

    assert session.get(EventRegistration, reg_id) is None
    assert session.get(AttendanceRecord, att_id) is None
