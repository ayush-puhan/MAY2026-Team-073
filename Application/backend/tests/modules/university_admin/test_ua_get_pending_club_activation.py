from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module

#1. Get pending activation clubs successfully
def test_get_pending_activation_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    pending_club = ClubFactory(
        university=university,
        status=ClubStatus.PENDING,
        faculty_advisor=None,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs/pending-activation",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == pending_club.id
    assert body[0]["name"] == pending_club.name
    assert body[0]["status"] == ClubStatus.PENDING.value


# 2. Do not get clubs from other university
def test_get_pending_activation_filters_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    another_university = UniversityFactory()

    university_admin_user.university = university

    own_club = ClubFactory(
        university=university,
        status=ClubStatus.PENDING,
        faculty_advisor=None,
    )

    ClubFactory(
        university=another_university,
        status=ClubStatus.PENDING,
        faculty_advisor=None,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs/pending-activation",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == own_club.id


# 3. Do not get active cklubs
def test_get_pending_activation_filters_status(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    ClubFactory(
        university=university,
        status=ClubStatus.ACTIVE,
        faculty_advisor=None,
    )

    pending = ClubFactory(
        university=university,
        status=ClubStatus.PENDING,
        faculty_advisor=None,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs/pending-activation",
        headers=headers,
    )

    body = response.get_json()

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["id"] == pending.id


# 4. No pending club test
def test_get_pending_activation_empty(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs/pending-activation",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# 5. Unauthenticaed
def test_get_pending_activation_unauthorized(client):
    response = client.get(
        "/api/university-admin/clubs/pending-activation",
    )

    assert response.status_code == 401

# 6. Forbidden
def test_get_pending_activation_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    headers = auth_headers(student.email)
    response = client.get(
        "/api/university-admin/clubs/pending-activation",
        headers=headers,
    )
    assert response.status_code == 403


# 6. Database error
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