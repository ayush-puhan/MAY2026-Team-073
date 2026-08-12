from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.club_creation_requests  as club_application_module

def test_reject_club_request_success_for_faculty(
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
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(faculty.email)
    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/reject",
        json={
            "review_comments": "The proposal needs more details.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "Club request rejected."
    request_data = body["request"]
    assert request_data["id"] == str(club_request.id)
    assert request_data["status"] == ClubRequestStatus.REJECTED.value
    assert request_data["review_comments"] == (
        "The proposal needs more details."
    )
    assert request_data["reviewed_by"] == faculty.id
    assert request_data["decided_at"] is not None


def test_reject_club_request_success_for_dean(
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
        status=ClubRequestStatus.FACULTY_RECOMMENDED,
    )
    headers = auth_headers(dean.email)
    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/reject",
        json={
            "review_comments": "The proposal does not meet the requirements.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "Club request rejected."
    assert body["request"]["status"] == ClubRequestStatus.REJECTED.value
    assert body["request"]["reviewed_by"] == dean.id
    assert body["request"]["review_comments"] == (
        "The proposal does not meet the requirements."
    )
    assert body["request"]["decided_at"] is not None



def test_reject_club_request_forbidden_for_unassigned_faculty(
    client,
    auth_headers,
):
    university = UniversityFactory()
    assigned_faculty = UserFactory(
        email="assigned@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
        university=university,
    )
    other_faculty = UserFactory(
        email="other@campus.edu",
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
        faculty_advisor=assigned_faculty,
        status=ClubRequestStatus.SUBMITTED,
    )
    headers = auth_headers(other_faculty.email)
    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/reject",
        json={
            "review_comments": "Rejecting this proposal.",
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == "You are not assigned to this request"




import pytest
@pytest.mark.parametrize(
    "status",
    [
        ClubRequestStatus.APPROVED,
        ClubRequestStatus.REJECTED,
    ],
)
def test_reject_already_finalized_request(
    client,
    auth_headers,
    status,
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
        status=status,
    )
    headers = auth_headers(dean.email)
    response = client.patch(
        f"/api/club-creation-requests/{club_request.id}/reject",
        json={
            "review_comments": "Reject this request.",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "Request cannot be rejected in its current state."
    )



def test_reject_club_request_not_found(
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
        "/api/club-creation-requests/999999/reject",
        json={
            "review_comments": "Request does not exist.",
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Request not found"