from app.database.enums import *
from db_factory.factory import *

# -------------------------------------------------------------------
# Test: Successfully retrieve advisor clubs
# -------------------------------------------------------------------
def test_get_faculty_clubs_success(
    client,
    auth_headers,
    faculty_advisor_user
):
    university = UniversityFactory()
    ClubFactory(
        faculty_advisor=faculty_advisor_user,
        university=university,
        name="AI Club",
    )
    ClubFactory(
        faculty_advisor=faculty_advisor_user,
        university=university,
        name="Coding Club",
    )

    headers = auth_headers(faculty_advisor_user.email)
    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/clubs",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.get_json()

    assert len(body) == 2

    assert body[0]["faculty_advisor_id"] == faculty_advisor_user.id
    assert "id" in body[0]
    assert "name" in body[0]
    assert "description" in body[0]
    assert "category" in body[0]
    assert "slug" in body[0]
    assert "status" in body[0]
    assert "member_count_cache" in body[0]


# -------------------------------------------------------------------
# Test: Advisor has no clubs
# -------------------------------------------------------------------
def test_get_faculty_clubs_empty(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)
    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json() == []


# -------------------------------------------------------------------
# Test: Advisor requests another advisor's clubs
# -------------------------------------------------------------------
def test_get_faculty_clubs_wrong_user(
    client,
    auth_headers,
    faculty_advisor_user
):
    another_advisor = UserFactory(role=faculty_advisor_user.role)

    headers = auth_headers(faculty_advisor_user.email)
    response = client.get(
        f"/api/faculty/{another_advisor.id}/clubs",
        headers=headers,
    )

    assert response.status_code == 404
    assert "Forbidden" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_faculty_clubs_unauthorized(client):

    response = client.get(
        "/api/faculty/1/clubs",
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Wrong role (student)
# -------------------------------------------------------------------
def test_get_faculty_clubs_wrong_role(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)

    response = client.get(
        f"/api/faculty/{student_user.id}/clubs",
        headers=headers,
    )

    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_get_faculty_clubs_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    db_error,
):
    import app.modules.faculty.routes as faculty_module
    db_error(faculty_module)
    headers = auth_headers(faculty_advisor_user.email)
    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/clubs",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]