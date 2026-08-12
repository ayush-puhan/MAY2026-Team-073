"""Unit tests for app/modules/ai_services/routes.py's club-roles
resolution (Phase 5A follow-up).

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q

Covers `_resolve_approved_club_roles()`, extracted from the `/chat`
endpoint specifically so this data-quality regression can be tested
directly against a hermetic in-memory DB, without needing a full
Flask request/JWT/reference-DB setup (same fixture pattern as
test_sql_context_builder.py - a fresh in-memory SQLite DB per test,
no reliance on, and no mutation of, the real reference database).
"""
from datetime import datetime

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database import models  # noqa: F401 - registers all mapped tables
from app.database.enums import MembershipStatus, UserRole
from app.database.models.auth import User
from app.database.models.clubs import Club, ClubMembership
from app.database.models.university import University
from app.modules.ai_services.routes import _resolve_approved_club_roles


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
        email="member.student@test.edu",
        password_hash="x",
        full_name="Member Student",
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
def second_club(db, university):
    c = Club(name="Debate Society", slug="debate-society", university_id=university.id)
    db.add(c)
    db.commit()
    return c


def test_resolve_club_roles_empty_when_no_memberships(db, student):
    assert _resolve_approved_club_roles(db, student.id) == []


def test_resolve_club_roles_normal_case(db, student, club):
    membership = ClubMembership(
        user_id=student.id,
        club_id=club.id,
        role_in_club="member",
        status=MembershipStatus.APPROVED,
        applied_at=datetime(2026, 1, 1),
    )
    db.add(membership)
    db.commit()

    assert _resolve_approved_club_roles(db, student.id) == ["member"]


def test_resolve_club_roles_excludes_non_approved(db, student, club):
    membership = ClubMembership(
        user_id=student.id,
        club_id=club.id,
        role_in_club="member",
        status=MembershipStatus.PENDING,
        applied_at=datetime(2026, 1, 1),
    )
    db.add(membership)
    db.commit()

    assert _resolve_approved_club_roles(db, student.id) == []


def test_resolve_club_roles_tolerates_current_timestamp_literal_string(db, student, club):
    """Regression test for the crash reported against `/api/ai/chat`:
    `club_memberships.applied_at` holding the literal, un-evaluated
    string "CURRENT_TIMESTAMP" (same class of seed-script bug as
    `attendance_records.checked_in_at` - see
    test_sql_context_builder.py's
    test_attendance_tolerates_current_timestamp_literal_string and
    PROJECT_CONTEXT.md Section 14) must not raise when resolving a
    user's club-scoped roles, since role_in_club is all this query
    needs - applied_at is irrelevant to authorization and should never
    be read at all.

    Inserted via raw SQL, bypassing the ORM's DateTime column type
    (which would reject this at insert time) - this mirrors exactly how
    the bad value reached the reference DB (a raw seed-data insert, not
    an ORM write).
    """
    db.execute(
        text(
            "INSERT INTO club_memberships "
            "(user_id, club_id, role_in_club, status, applied_at) "
            "VALUES (:user_id, :club_id, 'MEMBER', 'APPROVED', 'CURRENT_TIMESTAMP')"
        ),
        {"user_id": student.id, "club_id": club.id},
    )
    db.commit()

    assert _resolve_approved_club_roles(db, student.id) == ["member"]


def test_resolve_club_roles_tolerates_mixed_clean_and_corrupted_rows(db, student, club, second_club):
    """A user with one clean membership and one corrupted one must get
    both roles back, not just the clean one - the corruption in one
    row must not silently drop or crash on sibling rows."""
    clean = ClubMembership(
        user_id=student.id,
        club_id=club.id,
        role_in_club="member",
        status=MembershipStatus.APPROVED,
        applied_at=datetime(2026, 1, 1),
    )
    db.add(clean)
    db.commit()

    db.execute(
        text(
            "INSERT INTO club_memberships "
            "(user_id, club_id, role_in_club, status, applied_at) "
            "VALUES (:user_id, :club_id, 'PRESIDENT', 'APPROVED', 'CURRENT_TIMESTAMP')"
        ),
        {"user_id": student.id, "club_id": second_club.id},
    )
    db.commit()

    assert set(_resolve_approved_club_roles(db, student.id)) == {"member", "president"}
