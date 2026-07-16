"""Focused tests for the academic/interest/application-workflow schema
additions and the JWT session-tracking helpers."""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from database.enums import AuthProvider, Gender, MembershipStatus, UserRole
from database.models.academics import Department, Program, StudentProfile
from database.models.applications import ApplicationInterest, ClubJoinApplication
from database.models.auth import AuthSession, User
from database.models.clubs import Club
from database.models.interests import ClubInterest, EventInterest, Interest, UserInterest
from database.session_manager import (
    ACCESS_TOKEN_EXPIRES,
    cleanup_expired_tokens,
    delete_token,
    generate_and_store_token,
    get_active_token,
    validate_stored_token,
)


def _make_user(session, email="student@example.com", **kwargs):
    user = User(email=email, password_hash="hash", full_name="Test User", **kwargs)
    session.add(user)
    session.commit()
    return user


def _make_department_and_program(session, university):
    dept = Department(name="Computer Science & Engineering", code="CSE", university_id=university.id)
    session.add(dept)
    session.commit()
    program = Program(department_id=dept.id, name="B.Tech Computer Science")
    session.add(program)
    session.commit()
    return dept, program


# ---------- Users: new columns ----------

def test_google_id_uniqueness(session):
    _make_user(session, email="a@example.com", google_id="g-123", auth_provider=AuthProvider.GOOGLE)
    session.add(
        User(email="b@example.com", password_hash="hash", full_name="B", google_id="g-123")
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_auth_provider_and_dob_and_gender(session):
    user = _make_user(
        session,
        auth_provider=AuthProvider.GOOGLE,
        dob=date(2003, 5, 1),
        gender=Gender.FEMALE,
    )
    fetched = session.get(User, user.id)
    assert fetched.auth_provider == AuthProvider.GOOGLE
    assert fetched.dob == date(2003, 5, 1)
    assert fetched.gender == Gender.FEMALE


def test_color_blind_mode_default_and_enabled(session):
    default_user = _make_user(session, email="default@example.com")
    assert session.get(User, default_user.id).color_blind_mode is False

    enabled_user = _make_user(session, email="enabled@example.com", color_blind_mode=True)
    assert session.get(User, enabled_user.id).color_blind_mode is True


# ---------- Departments / Programs / StudentProfile ----------

def test_department_and_program(session, sample_university):
    dept, program = _make_department_and_program(session, sample_university)
    assert program.department_id == dept.id


def test_student_profile_one_to_one(session, sample_university):
    student = _make_user(session)
    _, program = _make_department_and_program(session, sample_university)
    profile = StudentProfile(
        user_id=student.id, program_id=program.id, academic_year=2, semester=4, batch="2024", section="A"
    )
    session.add(profile)
    session.commit()

    assert session.get(User, student.id).student_profile.batch == "2024"

    # A second profile for the same user violates the 1:1 (user_id is the PK).
    session.add(StudentProfile(user_id=student.id, program_id=program.id))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


# ---------- Interests ----------

def test_interest_name_uniqueness(session):
    session.add(Interest(name="Robotics"))
    session.commit()
    session.add(Interest(name="Robotics"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_interest_mapping_and_duplicate_rejected(session):
    user = _make_user(session)
    interest = Interest(name="Photography")
    session.add(interest)
    session.commit()

    session.add(UserInterest(user_id=user.id, interest_id=interest.id))
    session.commit()

    session.add(UserInterest(user_id=user.id, interest_id=interest.id))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_club_interest_mapping(session, sample_university):
    advisor = _make_user(session, email="advisor@example.com", role=UserRole.FACULTY_ADVISOR)
    club = Club(name="Robotics Club", slug="robotics-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    interest = Interest(name="Machine Learning")
    session.add_all([club, interest])
    session.commit()

    session.add(ClubInterest(club_id=club.id, interest_id=interest.id))
    session.commit()
    assert len(club.interest_links) == 1


def test_event_interest_mapping(session, sample_university):
    from database.models.events import Event

    advisor = _make_user(session, email="advisor2@example.com", role=UserRole.FACULTY_ADVISOR)
    club = Club(name="AI Club", slug="ai-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add(club)
    session.commit()

    event = Event(
        club_id=club.id,
        title="AI Talk",
        start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=1),
        created_by=advisor.id,
    )
    interest = Interest(name="Artificial Intelligence")
    session.add_all([event, interest])
    session.commit()

    session.add(EventInterest(event_id=event.id, interest_id=interest.id))
    session.commit()
    assert len(event.interest_links) == 1


# ---------- Club join applications ----------

def test_club_join_application_crud(session, sample_university):
    advisor = _make_user(session, email="advisor3@example.com", role=UserRole.FACULTY_ADVISOR)
    student = _make_user(session, email="applicant@example.com")
    club = Club(name="Debate Club", slug="debate-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add(club)
    session.commit()

    application = ClubJoinApplication(
        user_id=student.id,
        club_id=club.id,
        motivation="Excited to debate.",
        status=MembershipStatus.PENDING,
    )
    session.add(application)
    session.commit()

    fetched = session.get(ClubJoinApplication, application.id)
    assert fetched.status == MembershipStatus.PENDING
    assert fetched.reviewed_at is None


def test_application_reviewer_and_resume_document_relationships(session, sample_university):
    from database.enums import DocumentType
    from database.models.communication import Document

    advisor = _make_user(session, email="advisor4@example.com", role=UserRole.FACULTY_ADVISOR)
    reviewer = _make_user(session, email="reviewer@example.com", role=UserRole.FACULTY_ADVISOR)
    student = _make_user(session, email="applicant2@example.com")
    club = Club(name="Music Club", slug="music-club", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    session.add(club)
    session.commit()

    resume = Document(
        owner_id=student.id, doc_type=DocumentType.GENERAL, file_url="https://x/resume.pdf",
        title="Resume",
    )
    session.add(resume)
    session.commit()

    application = ClubJoinApplication(
        user_id=student.id,
        club_id=club.id,
        resume_document_id=resume.id,
        reviewed_by=reviewer.id,
        status=MembershipStatus.APPROVED,
        reviewed_at=datetime.utcnow(),
    )
    session.add(application)
    session.commit()

    fetched = session.get(ClubJoinApplication, application.id)
    assert fetched.reviewer.email == "reviewer@example.com"
    assert fetched.resume_document.title == "Resume"


def test_application_interests_and_duplicate_rejected(session, sample_university):
    advisor = _make_user(session, email="advisor5@example.com", role=UserRole.FACULTY_ADVISOR)
    student = _make_user(session, email="applicant3@example.com")
    club = Club(name="Entrepreneurship Cell", slug="e-cell", faculty_advisor_id=advisor.id, university_id=sample_university.id)
    interest = Interest(name="Entrepreneurship")
    session.add_all([club, interest])
    session.commit()

    application = ClubJoinApplication(user_id=student.id, club_id=club.id, status=MembershipStatus.PENDING)
    session.add(application)
    session.commit()

    session.add(ApplicationInterest(application_id=application.id, interest_id=interest.id))
    session.commit()

    session.add(ApplicationInterest(application_id=application.id, interest_id=interest.id))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


# ---------- JWT session tracking ----------

def test_generate_and_store_token_returns_real_jwt_matching_stored_row(session):
    user = _make_user(session, email="jwt1@example.com")
    token = generate_and_store_token(user.id, session=session)

    # A real JWT has three dot-separated base64url segments (not a bare id).
    assert token.count(".") == 2

    stored = session.query(AuthSession).filter_by(user_id=user.id).one()
    assert stored.token == token
    assert stored.user_id == user.id

    delta = stored.expires_at - stored.created_at
    assert timedelta(minutes=59) < delta <= ACCESS_TOKEN_EXPIRES + timedelta(seconds=5)


def test_get_active_token_returns_active_session(session):
    user = _make_user(session, email="jwt2@example.com")
    token = generate_and_store_token(user.id, session=session)
    assert get_active_token(user.id, session=session) == token


def test_validate_stored_token_accepts_active_and_rejects_expired(session):
    user = _make_user(session, email="jwt3@example.com")
    token = generate_and_store_token(user.id, session=session)
    assert validate_stored_token(token, session=session) is True

    expired = AuthSession(
        user_id=user.id, token="expired.mock.token",
        expires_at=datetime.utcnow() - timedelta(minutes=1),
    )
    session.add(expired)
    session.commit()
    assert validate_stored_token("expired.mock.token", session=session) is False


def test_delete_token_removes_row_on_logout(session):
    user = _make_user(session, email="jwt4@example.com")
    token = generate_and_store_token(user.id, session=session)

    assert delete_token(token, session=session) is True
    assert session.query(AuthSession).filter_by(token=token).one_or_none() is None
    # Deleting again (already logged out) reports nothing found.
    assert delete_token(token, session=session) is False


def test_cleanup_expired_tokens_preserves_active_sessions(session):
    user = _make_user(session, email="jwt5@example.com")
    active_token = generate_and_store_token(user.id, session=session)

    expired = AuthSession(
        user_id=user.id, token="another.expired.token",
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    session.add(expired)
    session.commit()

    deleted = cleanup_expired_tokens(session=session)
    assert deleted == 1
    remaining = {row.token for row in session.query(AuthSession).all()}
    assert remaining == {active_token}
