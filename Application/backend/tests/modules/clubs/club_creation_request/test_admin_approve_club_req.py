from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.admin.club_creation_requests  as club_application_module


def test_approve_club_request_success(
    client,
    auth_headers,
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        proposed_name="Robotics Club",
        proposed_category="Technology",
        proposal_description="A robotics and innovation club.",
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Club approved and created."
    assert body["club_id"] is not None

    request_data = body["request"]

    assert request_data["id"] == str(club_request.id)
    assert request_data["status"] == ClubRequestStatus.APPROVED.value
    assert request_data["resulting_club_id"] == body["club_id"]
    assert request_data["reviewed_by"] == dean.id
    assert request_data["decided_at"] is not None



def test_approve_club_request_creates_club_with_correct_data(
    client,
    auth_headers,
    db_session,
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        proposed_name="Photography Club",
        proposed_category="Arts",
        proposal_description="Photography and visual arts.",
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()

    club_id = body["club_id"]

    club = (
        db_session.query(Club)
        .filter(Club.id == club_id)
        .first()
    )

    assert club is not None
    assert club.name == "Photography Club"
    assert club.slug == "photography-club"
    assert club.category == "Arts"
    assert club.description == "Photography and visual arts."
    assert club.faculty_advisor_id == faculty.id
    assert club.university_id == university.id
    assert club.status == ClubStatus.ACTIVE
    assert club.created_at is not None



def test_approve_club_request_updates_request(
    client,
    auth_headers,
    db_session,
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 201

    db_session.expire_all()

    saved_request = (
        db_session.query(ClubCreationRequest)
        .filter(ClubCreationRequest.id == club_request.id)
        .first()
    )

    assert saved_request.status == ClubRequestStatus.APPROVED
    assert saved_request.resulting_club_id is not None
    assert saved_request.reviewed_by == dean.id
    assert saved_request.decided_at is not None

    club = (
        db_session.query(Club)
        .filter(Club.id == saved_request.resulting_club_id)
        .first()
    )

    assert club is not None




def test_club_request_not_found(
    client,
    auth_headers,
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        "/api/club-creation-requests/999999/approve",
        headers=headers,
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["message"] == "Request not found"



def test_approve_club_request_not_recommended(
    client,
    auth_headers,
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Request not recommended."


def test_already_approved_request(
    client,
    auth_headers,
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.APPROVED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Request not recommended."


def test_approve_club_request_generates_unique_slug(
    client,
    auth_headers,
    db_session
):
    university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=university,
    )

    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    # Existing club occupies "robotics-club"
    ClubFactory(
        name="Robotics Club",
        slug="robotics-club",
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        proposed_name="Robotics Club",
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()

    club = (
        db_session.query(Club)
        .filter(Club.id == body["club_id"])
        .first()
    )

    assert club.slug == "robotics-club-2"



def test_approve_club_request_forbidden_for_faculty(
    client,
    auth_headers,
):
    university = UniversityFactory()

    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 403



def test_approve_club_request_forbidden_for_student(
    client,
    auth_headers,
):
    university = UniversityFactory()
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(student.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 403


def test_approve_club_request_unauthorized(
    client,
):
    response = client.patch(
        "/api/club-creation-requests/1/approve",
    )

    assert response.status_code == 401



def test_approve_club_request_uses_dean_university(
    client,
    auth_headers,
    db_session,
):
    dean_university = UniversityFactory()
    other_university = UniversityFactory()

    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
        university=dean_university,
    )

    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=other_university,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
        university=other_university,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        proposed_name="Chess Club",
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(dean.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/approve",
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()

    club = (
        db_session.query(Club)
        .filter(Club.id == body["club_id"])
        .first()
    )

    assert club is not None
    assert club.university_id == dean_university.id