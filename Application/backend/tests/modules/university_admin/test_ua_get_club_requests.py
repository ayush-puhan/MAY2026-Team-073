import bcrypt
from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module


# Get all club requests
def test_get_club_creation_requests_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    student = UserFactory(university=university)

    req1 = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED,
    )

    req2 = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.APPROVED,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/club-requests",
        headers=headers,
    )

    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 2
    assert body[0]["proposed_name"] == req2.proposed_name
    assert body[1]["proposed_name"] == req1.proposed_name
    assert body[0]["requested_by_name"] == student.full_name


# Filter by status
def test_get_club_creation_requests_filter_status(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    student = UserFactory(university=university)

    ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED,
    )

    approved_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.APPROVED,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/club-requests?status=approved",
        headers=headers,
    )

    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["id"] == approved_request.id
    assert body[0]["status"] == ClubRequestStatus.APPROVED.value


# 3. Only request from same university is returned
def test_get_club_creation_requests_same_university_only(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    another_university = UniversityFactory()

    university_admin_user.university = university

    student1 = UserFactory(university=university)
    student2 = UserFactory(university=another_university)

    same_uni_request = ClubCreationRequestFactory(
        requester=student1,
    )

    ClubCreationRequestFactory(
        requester=student2,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/club-requests",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == same_uni_request.id

# 4. No requests found
def test_get_club_creation_requests_empty(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/club-requests",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# 5. Unauthorized
def test_get_club_creation_requests_unauthorized(client):
    response = client.get("/api/university-admin/club-requests")

    assert response.status_code == 401

# 6. Forbidden
def test_get_club_creation_requests_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    headers = auth_headers(student.email)
    response = client.get(
        "/api/university-admin/club-requests",
        headers=headers,
    )
    assert response.status_code == 403

# 7. database error
def test_get_stats_database_error(
    client,
    auth_headers,
    university_admin_user,
    db_error,
):
    db_error(university_admin_module)

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/stats",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]