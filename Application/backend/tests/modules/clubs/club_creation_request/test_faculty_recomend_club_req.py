from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.admin.club_creation_requests  as club_application_module


def test_recommend_club_request_success(client,auth_headers):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.SUBMITTED,
        review_comments=None,
        reviewed_by=None,
        decided_at=None,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "The proposal is well planned and recommended.",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Club proposal recommended."

    request_data = body["request"]

    assert request_data["id"] == str(club_request.id)
    assert request_data["status"] == ClubRequestStatus.FACULTY_RECOMMENDED.value
    assert request_data["review_comments"] == (
        "The proposal is well planned and recommended."
    )
    assert request_data["reviewed_by"] == faculty.id
    assert request_data["decided_at"] is not None



def test_recommend_club_request_without_review_comments(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={},
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Club proposal recommended."

    request_data = body["request"]

    assert request_data["status"] == ClubRequestStatus.FACULTY_RECOMMENDED.value
    assert request_data["review_comments"] is None
    assert request_data["reviewed_by"] == faculty.id
    assert request_data["decided_at"] is not None



def test_recommend_already_recommended_request(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "Updated recommendation.",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["request"]["status"] == (
        ClubRequestStatus.FACULTY_RECOMMENDED.value
    )

    assert body["request"]["review_comments"] == "Updated recommendation."
    assert body["request"]["reviewed_by"] == faculty.id



def test_recommend_club_request_not_found(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        "/api/club-creation-requests/999999/recommend",
        json={
            "review_comments": "Recommended.",
        },
        headers=headers,
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["message"] == "Request not found"


def test_recommend_club_request_invalid_status(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.APPROVED,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "Recommended.",
        },
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == (
        "Request cannot be recommended in its current state."
    )



def test_recommend_club_request_forbidden_for_unassigned_faculty(
    client,
    auth_headers,
):
    assigned_faculty = UserFactory(
        email="assigned@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    other_faculty = UserFactory(
        email="other@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=assigned_faculty,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(other_faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "Recommended.",
        },
        headers=headers,
    )

    assert response.status_code == 403

    body = response.get_json()

    assert body["message"] == "You are not assigned to this request"



def test_recommend_unassigned_club_request_success(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=None,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "I recommend this proposal.",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["request"]["status"] == (
        ClubRequestStatus.FACULTY_RECOMMENDED.value
    )

    assert body["request"]["reviewed_by"] == faculty.id



def test_recommend_club_request_forbidden_for_student(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(student.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "Recommended.",
        },
        headers=headers,
    )

    assert response.status_code == 403



def test_recommend_club_request_unauthorized(
    client,
):
    response = client.patch(
        "/api/club-creation-requests/1/recommend",
        json={
            "review_comments": "Recommended.",
        },
    )

    assert response.status_code == 401



def test_recommend_club_request_persists_changes(
    client,
    auth_headers,
    db_session,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        faculty_advisor=faculty,
        status=ClubRequestStatus.SUBMITTED,
        review_comments=None,
        reviewed_by=None,
        decided_at=None,
    )

    headers = auth_headers(faculty.email)

    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/recommend",
        json={
            "review_comments": "Excellent proposal.",
        },
        headers=headers,
    )

    assert response.status_code == 200

    db_session.expire_all()

    saved_request = (
        db_session.query(ClubCreationRequest)
        .filter(ClubCreationRequest.id == club_request.id)
        .first()
    )

    assert saved_request is not None
    assert saved_request.status == ClubRequestStatus.FACULTY_RECOMMENDED
    assert saved_request.review_comments == "Excellent proposal."
    assert saved_request.reviewed_by == faculty.id
    assert saved_request.decided_at is not None