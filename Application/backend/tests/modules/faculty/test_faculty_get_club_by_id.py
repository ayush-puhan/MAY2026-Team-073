from app.database.enums import *
from db_factory.factory import *

# -------------------------------------------------------------------
# Test: Successfully retrieve club details
# -------------------------------------------------------------------
def test_get_club_detail_success(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user
    )

    student = UserFactory()

    ClubMembershipFactory(
        club=club,
        user=student,
        status=MembershipStatus.APPROVED,
    )

    CommitteeFactory(
        club=club,
        name="Technical Team",
    )

    BudgetFactory(
        club=club,
        creator=faculty_advisor_user,
        title="Main Budget",
        allocated_amount=100000,
    )

    response = client.get(
        f"/api/faculty/clubs/{club.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["id"] == club.id
    assert body["name"] == club.name
    assert len(body["members"]) == 1
    assert len(body["committees"]) == 1
    assert body["mainBudget"]["title"] == "Main Budget"
    assert body["members"][0]["user_name"] == student.full_name


# -------------------------------------------------------------------
# Test: Club not owned by advisor
# -------------------------------------------------------------------
def test_get_club_detail_forbidden(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    another_advisor = UserFactory(role=UserRole.FACULTY_ADVISOR)
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
        faculty_advisor=another_advisor
    )

    response = client.get(
        f"/api/faculty/clubs/{club.id}",
        headers=headers,
    )

    assert response.status_code == 403
    assert "Not Found" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: Club has no members, committees or budget
# -------------------------------------------------------------------
def test_get_club_detail_empty_relations(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user
    )

    response = client.get(
        f"/api/faculty/clubs/{club.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["members"] == []
    assert body["committees"] == []
    assert body["mainBudget"] is None


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_club_detail_unauthorized(client):

    response = client.get(
        "/api/faculty/clubs/1",
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Wrong role
# -------------------------------------------------------------------
def test_get_club_detail_wrong_role(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)

    response = client.get(
        "/api/faculty/clubs/1",
        headers=headers,
    )

    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_get_club_detail_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    db_error
):
    import app.modules.faculty.routes as faculty_module
    db_error(faculty_module)
    headers = auth_headers(faculty_advisor_user.email)

    response = client.get(
        "/api/faculty/clubs/1",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]