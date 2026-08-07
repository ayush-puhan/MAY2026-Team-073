from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module

# get all club successfully
def test_get_all_ua_clubs_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    club1 = ClubFactory(
        university=university,
        name="Coding Club",
    )

    club2 = ClubFactory(
        university=university,
        name="Music Club",
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    assert body[0]["id"] == club1.id
    assert body[0]["name"] == club1.name

    assert body[1]["id"] == club2.id
    assert body[1]["name"] == club2.name

# return ordered by name
def test_get_all_ua_clubs_ordered_by_name(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    ClubFactory(
        university=university,
        name="Zoology Club",
    )

    ClubFactory(
        university=university,
        name="Art Club",
    )

    ClubFactory(
        university=university,
        name="Coding Club",
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs",
        headers=headers,
    )

    body = response.get_json()

    names = [club["name"] for club in body]

    assert names == [
        "Art Club",
        "Coding Club",
        "Zoology Club",
    ]

# only university club of that university
def test_get_all_ua_clubs_filters_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    other_university = UniversityFactory()

    university_admin_user.university = university

    own_club = ClubFactory(
        university=university,
    )

    ClubFactory(
        university=other_university,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs",
        headers=headers,
    )

    body = response.get_json()

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["id"] == own_club.id

# No club return if there no club in the university
def test_get_all_ua_clubs_empty(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/clubs",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []

# Authentication
def test_get_all_ua_clubs_unauthorized(
    client,
):
    response = client.get(
        "/api/university-admin/clubs",
    )

    assert response.status_code == 401

# Forbidden
def test_get_all_ua_clubs_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)

    headers = auth_headers(student.email)

    response = client.get(
        "/api/university-admin/clubs",
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