import bcrypt
from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module

# -------------------------------------------------------------------
# Test: Successfully retrieve university statistics
# -------------------------------------------------------------------
def test_get_stats_success(
    client,
    auth_headers,
    university_admin_user
):

    university = UniversityFactory()
    university_admin_user.university = university
    club = ClubFactory(
        university=university,
        status=ClubStatus.ACTIVE,
    )

    student = UserFactory(
        university=university,
    )

    ClubMembershipFactory(
        user=student,
        club=club,
        status=MembershipStatus.APPROVED,
    )

    EventFactory(
        club=club,
        creator=student,
        status=EventStatus.SCHEDULED,
    )

    ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED
    )

    headers = auth_headers(university_admin_user.email)
    response = client.get(
        "/api/university-admin/stats",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["totalClubs"] == 1
    assert body["totalMemberships"] == 1
    assert body["activeEvents"] == 1
    assert body["pendingApprovals"] == 1


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_stats_unauthorized(client):
    response = client.get(
        "/api/university-admin/stats",
    )
    assert response.status_code == 401

# -------------------------------------------------------------------
# Test: Wrong role
# -------------------------------------------------------------------
def test_get_stats_wrong_role(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)

    response = client.get(
        "/api/university-admin/stats",
        headers=headers,
    )
    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
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