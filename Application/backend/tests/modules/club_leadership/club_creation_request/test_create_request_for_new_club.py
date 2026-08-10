from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.club_creation_requests  as club_application_module

def test_create_club_request_success(
    client,
    auth_headers,
):
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )
    faculty_advisor = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    headers = auth_headers(student.email)
    payload = {
        "name": "Robotics Club",
        "category": "Technology",
        "description": "A club for students interested in robotics.",
        "faculty_advisor_id": faculty_advisor.id,
    }
    response = client.post(
        "/api/club-creation-requests",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Club creation request submitted."

    request_data = body["request"]

    assert request_data["proposed_name"] == "Robotics Club"
    assert request_data["proposed_category"] == "Technology"
    assert request_data["proposal_description"] == (
        "A club for students interested in robotics."
    )
    assert request_data["requested_by"] == student.id
    assert request_data["faculty_advisor_id"] == faculty_advisor.id
    assert request_data["status"] == ClubRequestStatus.SUBMITTED.value

    assert request_data["resulting_club_id"] is None
    assert request_data["reviewed_by"] is None
    assert request_data["review_comments"] is None
    assert request_data["created_at"] is not None
    assert request_data["decided_at"] is None



def test_create_club_request_persists_to_database(
    client,
    auth_headers,
    db_session,
):
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    headers = auth_headers(student.email)

    payload = {
        "name": "Photography Club",
        "category": "Arts",
        "description": "Photography and visual arts club.",
    }

    response = client.post(
        "/api/club-creation-requests",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()
    request_id = int(body["request"]["id"])

    saved_request = (
        db_session.query(ClubCreationRequest)
        .filter(ClubCreationRequest.id == request_id)
        .first()
    )

    assert saved_request is not None
    assert saved_request.proposed_name == "Photography Club"
    assert saved_request.proposed_category == "Arts"
    assert saved_request.proposal_description == (
        "Photography and visual arts club."
    )
    assert saved_request.requested_by == student.id
    assert saved_request.faculty_advisor_id is None
    assert saved_request.status == ClubRequestStatus.SUBMITTED


def test_create_club_request_missing_name(
    client,
    auth_headers,
):
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    headers = auth_headers(student.email)

    response = client.post(
        "/api/club-creation-requests",
        json={
            "description": "A robotics club.",
        },
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Missing fields: name"



def test_create_club_request_missing_description(
    client,
    auth_headers,
):
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    headers = auth_headers(student.email)

    response = client.post(
        "/api/club-creation-requests",
        json={
            "name": "Robotics Club",
        },
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Missing fields: description"



def test_create_club_request_forbidden_for_non_student(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    headers = auth_headers(faculty.email)

    response = client.post(
        "/api/club-creation-requests",
        json={
            "name": "Robotics Club",
            "description": "A robotics club.",
        },
        headers=headers,
    )

    assert response.status_code == 403