from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module


def test_get_faculty_advisors_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    advisor1 = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
        full_name="Alice",
        is_active=True,
    )

    advisor2 = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
        full_name="Bob",
        is_active=True,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/faculty-advisors",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2
    assert body[0] == {
        "value": advisor1.id,
        "label": advisor1.full_name,
    }
    assert body[1] == {
        "value": advisor2.id,
        "label": advisor2.full_name,
    }


# faculty not from aother university
def test_get_faculty_advisors_filters_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    other_university = UniversityFactory()

    university_admin_user.university = university

    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
        is_active=True,
    )

    UserFactory(
        university=other_university,
        role=UserRole.FACULTY_ADVISOR,
        is_active=True,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/faculty-advisors",
        headers=headers,
    )

    body = response.get_json()

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["value"] == advisor.id


# not inactive advisor will come
def test_get_faculty_advisors_filters_inactive(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
        is_active=True,
    )

    UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
        is_active=False,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/faculty-advisors",
        headers=headers,
    )

    body = response.get_json()

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["value"] == advisor.id


# Ignore users with other role
def test_get_faculty_advisors_filters_role(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
        is_active=True,
    )

    UserFactory(
        university=university,
        role=UserRole.STUDENT,
        is_active=True,
    )

    UserFactory(
        university=university,
        role=UserRole.SYSTEM_ADMIN,
        is_active=True,
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/faculty-advisors",
        headers=headers,
    )

    body = response.get_json()

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["value"] == advisor.id


# return empty if no advisor in university
def test_get_faculty_advisors_empty(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/faculty-advisors",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []

# private api
def test_get_faculty_advisors_unauthorized(client):
    response = client.get(
        "/api/university-admin/faculty-advisors",
    )

    assert response.status_code == 401

# proper role can access
def test_get_faculty_advisors_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)

    headers = auth_headers(student.email)

    response = client.get(
        "/api/university-admin/faculty-advisors",
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