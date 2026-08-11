from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.club_creation_requests  as club_application_module


def test_get_club_creation_requests_success(
    client,
    auth_headers,
):
    admin = UserFactory(
        email="admin@campus.edu",
        role=UserRole.STUDENT_AFFAIRS_OFFICE,
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
        proposed_name="Robotics Club",
        proposed_category="Technology",
        proposal_description="Robotics activities",
        status=ClubRequestStatus.SUBMITTED,
    )

    request2 = ClubCreationRequestFactory(
        requester=student2,
        proposed_name="Photography Club",
        proposed_category="Arts",
        proposal_description="Photography activities",
        status=ClubRequestStatus.APPROVED,
    )

    headers = auth_headers(admin.email)

    response = client.get(
        "/api/club-creation-requests/admin",
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



def test_get_club_creation_requests_filter_by_status(
    client,
    auth_headers,
):
    admin = UserFactory(
        email="admin@campus.edu",
        role=UserRole.STUDENT_AFFAIRS_OFFICE,
    )
    student1 = UserFactory(
        email="student1@campus.edu",
        role=UserRole.STUDENT,
    )
    student2 = UserFactory(
        email="student2@campus.edu",
        role=UserRole.STUDENT,
    )
    submitted_request = ClubCreationRequestFactory(
        requester=student1,
        status=ClubRequestStatus.SUBMITTED,
    )

    ClubCreationRequestFactory(
        requester=student2,
        status=ClubRequestStatus.APPROVED,
    )

    headers = auth_headers(admin.email)

    response = client.get(
        "/api/club-creation-requests/admin?status=submitted",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    assert body[0]["id"] == str(submitted_request.id)
    assert body[0]["status"] == ClubRequestStatus.SUBMITTED.value



def test_get_club_creation_requests_invalid_status(
    client,
    auth_headers,
):
    admin = UserFactory(
        email="admin@campus.edu",
        role=UserRole.STUDENT_AFFAIRS_OFFICE,
    )

    headers = auth_headers(admin.email)

    response = client.get(
        "/api/club-creation-requests/admin?status=invalid_status",
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Invalid status"



def test_get_club_creation_requests_empty(
    client,
    auth_headers,
):
    admin = UserFactory(
        email="admin@campus.edu",
        role=UserRole.STUDENT_AFFAIRS_OFFICE,
    )

    headers = auth_headers(admin.email)

    response = client.get(
        "/api/club-creation-requests/admin",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body == []



def test_get_club_creation_requests_ordered_by_latest_first(
    client,
    auth_headers,
):
    from datetime import datetime, timedelta

    admin = UserFactory(
        email="admin@campus.edu",
        role=UserRole.STUDENT_AFFAIRS_OFFICE,
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
        proposed_name="Older Club",
        created_at=datetime.utcnow() - timedelta(days=2),
        status=ClubRequestStatus.SUBMITTED,
    )

    newer_request = ClubCreationRequestFactory(
        requester=student2,
        proposed_name="Newer Club",
        created_at=datetime.utcnow(),
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(admin.email)

    response = client.get(
        "/api/club-creation-requests/admin",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    assert body[0]["id"] == str(newer_request.id)
    assert body[1]["id"] == str(older_request.id)


def test_get_club_creation_requests_for_dean(
    client,
    auth_headers,
):
    dean = UserFactory(
        email="dean@campus.edu",
        role=UserRole.DEAN_STUDENT_WELFARE,
    )

    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    club_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(dean.email)

    response = client.get(
        "/api/club-creation-requests/admin",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == str(club_request.id)


def test_get_club_creation_requests_forbidden_for_student(
    client,
    auth_headers,
):
    student = UserFactory(
        email="student@campus.edu",
        role=UserRole.STUDENT,
    )

    headers = auth_headers(student.email)

    response = client.get(
        "/api/club-creation-requests/admin",
        headers=headers,
    )

    assert response.status_code == 403