from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module

# Activate club successfully
def test_activate_club_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
    )

    club = ClubFactory(
        university=university,
        status=ClubStatus.PENDING,
        faculty_advisor=None,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        f"/api/university-admin/clubs/{club.id}/activate",
        headers=headers,
        json={
            "faculty_advisor_id": advisor.id,
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Club activated successfully"
    assert body["club"]["id"] == club.id
    assert body["club"]["status"] == ClubStatus.ACTIVE.value
    assert body["club"]["faculty_advisor_id"] == advisor.id


# Missing faculty id
def test_activate_club_missing_faculty_advisor(
    client,
    auth_headers,
    university_admin_user,
):
    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        "/api/university-admin/clubs/1/activate",
        headers=headers,
        json={},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "faculty_advisor_id is required"

# club not found
def test_activate_club_not_found(
    client,
    auth_headers,
    university_admin_user,
):
    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        "/api/university-admin/clubs/99999/activate",
        headers=headers,
        json={
            "faculty_advisor_id": 1,
        },
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Club not found"


# club belongs to other university
def test_activate_club_different_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    other_university = UniversityFactory()

    university_admin_user.university = university

    club = ClubFactory(
        university=other_university,
        status=ClubStatus.PENDING,
    )

    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        f"/api/university-admin/clubs/{club.id}/activate",
        headers=headers,
        json={
            "faculty_advisor_id": advisor.id,
        },
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Club not found"

# club already active
def test_activate_club_not_pending(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
    )

    club = ClubFactory(
        university=university,
        status=ClubStatus.ACTIVE,
        faculty_advisor=None,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        f"/api/university-admin/clubs/{club.id}/activate",
        headers=headers,
        json={
            "faculty_advisor_id": advisor.id,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Club is not pending activation"


# Faculty advisor not found
def test_activate_club_faculty_advisor_not_found(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    club = ClubFactory(
        university=university,
        status=ClubStatus.PENDING,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        f"/api/university-admin/clubs/{club.id}/activate",
        headers=headers,
        json={
            "faculty_advisor_id": 99999,
        },
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Faculty advisor not found"


# faculty belongs to other university
def test_activate_club_faculty_advisor_other_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    other_university = UniversityFactory()

    university_admin_user.university = university

    club = ClubFactory(
        university=university,
        status=ClubStatus.PENDING,
    )

    advisor = UserFactory(
        university=other_university,
        role=UserRole.FACULTY_ADVISOR,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.patch(
        f"/api/university-admin/clubs/{club.id}/activate",
        headers=headers,
        json={
            "faculty_advisor_id": advisor.id,
        },
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Faculty advisor not found"

# Authentication required
def test_activate_club_unauthorized(client):
    response = client.patch(
        "/api/university-admin/clubs/1/activate",
        json={
            "faculty_advisor_id": 1,
        },
    )

    assert response.status_code == 401


# Forbidden test
def test_activate_club_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    headers = auth_headers(student.email)
    response = client.patch(
        "/api/university-admin/clubs/1/activate",
        headers=headers,
        json={
            "faculty_advisor_id": 1,
        },
    )
    assert response.status_code == 403


# Database error check
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

