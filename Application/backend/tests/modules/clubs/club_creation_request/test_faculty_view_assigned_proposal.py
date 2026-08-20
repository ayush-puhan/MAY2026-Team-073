from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.admin.club_creation_requests  as club_application_module



def test_get_faculty_club_requests_success(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student1 = UserFactory(
        email="student1@campus.edu",
        role=UserRole.STUDENT,
    )

    student2 = UserFactory(
        email="student2@campus.edu",
        role=UserRole.STUDENT,
    )

    request1 = ClubCreationRequestFactory(
        requester=student1,
        faculty_advisor=faculty,
        proposed_name="Robotics Club",
        status=ClubRequestStatus.SUBMITTED,
    )

    request2 = ClubCreationRequestFactory(
        requester=student2,
        faculty_advisor=faculty,
        proposed_name="Photography Club",
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(faculty.email)

    response = client.get(
        "/api/club-creation-requests/faculty",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    ids = {request["id"] for request in body}

    assert ids == {
        str(request1.id),
        str(request2.id),
    }


def test_get_faculty_club_requests_returns_only_assigned_proposals(
    client,
    auth_headers,
):
    faculty1 = UserFactory(
        email="faculty1@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    faculty2 = UserFactory(
        email="faculty2@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    student1 = UserFactory(
        email="student1@campus.edu",
        role=UserRole.STUDENT,
    )

    student2 = UserFactory(
        email="student2@campus.edu",
        role=UserRole.STUDENT,
    )

    assigned_request = ClubCreationRequestFactory(
        requester=student1,
        faculty_advisor=faculty1,
        proposed_name="Robotics Club",
        status=ClubRequestStatus.SUBMITTED,
    )

    other_request = ClubCreationRequestFactory(
        requester=student2,
        faculty_advisor=faculty2,
        proposed_name="Photography Club",
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(faculty1.email)

    response = client.get(
        "/api/club-creation-requests/faculty",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    assert body[0]["id"] == str(assigned_request.id)
    assert body[0]["id"] != str(other_request.id)


def test_get_faculty_club_requests_invalid_faculty_id(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )

    headers = auth_headers(faculty.email)

    response = client.get(
        "/api/club-creation-requests/faculty"
        "?faculty_advisor_id=invalid",
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Invalid faculty_advisor_id"


def test_get_faculty_club_requests_no_assigned_proposals(
    client,
    auth_headers,
):
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )
    headers = auth_headers(faculty.email)
    response = client.get(
        "/api/club-creation-requests/faculty",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []



def test_get_faculty_club_requests_ordered_by_latest_first(
    client,
    auth_headers,
):
    from datetime import datetime, timedelta
    faculty = UserFactory(
        email="faculty@campus.edu",
        role=UserRole.FACULTY_ADVISOR,
    )
    student1 = UserFactory(
        email="student1@campus.edu",
        role=UserRole.STUDENT,
    )
    student2 = UserFactory(
        email="student2@campus.edu",
        role=UserRole.STUDENT,
    )
    older_request = ClubCreationRequestFactory(
        requester=student1,
        faculty_advisor=faculty,
        proposed_name="Older Club",
        created_at=datetime.utcnow() - timedelta(days=2),
        status=ClubRequestStatus.SUBMITTED,
    )

    newer_request = ClubCreationRequestFactory(
        requester=student2,
        faculty_advisor=faculty,
        proposed_name="Newer Club",
        created_at=datetime.utcnow(),
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(faculty.email)

    response = client.get(
        "/api/club-creation-requests/faculty",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    assert body[0]["id"] == str(newer_request.id)
    assert body[1]["id"] == str(older_request.id)



def test_get_faculty_club_requests_forbidden_for_student(
    client,
    auth_headers,
):
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    headers = auth_headers(student.email)

    response = client.get(
        "/api/club-creation-requests/faculty",
        headers=headers,
    )

    assert response.status_code == 403


def test_get_faculty_club_requests_unauthorized(
    client,
):
    response = client.get(
        "/api/club-creation-requests/faculty",
    )

    assert response.status_code == 401