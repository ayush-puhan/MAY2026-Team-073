from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.application_routes  as club_application_module

# get club precident all application successfully
def test_get_club_applications_success(
    client,
    auth_headers,
):
    club = ClubFactory(university=UniversityFactory())
    president = UserFactory(email="president_club@campus.edu")
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant1 = UserFactory(email="user100@campus.edu")
    applicant2 = UserFactory(email="user200@campus.edu")

    application1 = ClubJoinApplicationFactory(
        club=club,
        user=applicant1,
        status=MembershipStatus.PENDING,
    )

    application2 = ClubJoinApplicationFactory(
        club=club,
        user=applicant2,
        status=MembershipStatus.APPROVED,
    )

    headers = auth_headers(president.email)

    response = client.get(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    ids = {application["id"] for application in body}

    assert ids == {
        application1.id,
        application2.id,
    }


# get by status
def test_get_club_applications_by_status(
    client,
    auth_headers,
):
    club = ClubFactory(university=UniversityFactory())
    president = UserFactory(email="president_club@campus.edu")

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant1 = UserFactory(email="user100@campus.edu")
    applicant2 = UserFactory(email="user200@campus.edu")

    pending_application = ClubJoinApplicationFactory(
        club=club,
        user=applicant1,
        status=MembershipStatus.PENDING,
    )

    ClubJoinApplicationFactory(
        club=club,
        user=applicant2,
        status=MembershipStatus.APPROVED,
    )

    headers = auth_headers(president.email)

    response = client.get(
        f"/api/clubs/{club.id}/applications?status=pending",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == pending_application.id
    assert body[0]["status"] == "pending"

#
def test_get_club_applications_invalid_status(
    client,
    auth_headers,
):
    club = ClubFactory(university=UniversityFactory())
    president = UserFactory(email="president_club@campus.edu")

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)

    response = client.get(
        f"/api/clubs/{club.id}/applications?status=invalid_status",
        headers=headers,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Invalid application status."


#
def test_get_club_applications_empty(
    client,
    auth_headers,
):
    club = ClubFactory(university=UniversityFactory())
    president = UserFactory(email="president_club@campus.edu")
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)

    response = client.get(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


#
def test_get_club_applications_only_requested_club(
    client,
    auth_headers,
):
    club1 = ClubFactory(university=UniversityFactory())
    club2 = ClubFactory(university=UniversityFactory())
    president = UserFactory(email="president_club@campus.edu")

    ClubMembershipFactory(
        user=president,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant1 = UserFactory(email="user100@campus.edu")
    applicant2 = UserFactory(email="user200@campus.edu")

    application = ClubJoinApplicationFactory(
        club=club1,
        user=applicant1,
        status=MembershipStatus.PENDING,
    )

    ClubJoinApplicationFactory(
        club=club2,
        user=applicant2,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(president.email)

    response = client.get(
        f"/api/clubs/{club1.id}/applications",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == application.id
    assert body[0]["club_id"] == club1.id


#
def test_get_club_applications_as_vice_president(
    client,
    auth_headers,
):
    club = ClubFactory(university=UniversityFactory())
    vice_president = UserFactory(email="vice_club@campus.edu")

    ClubMembershipFactory(
        user=vice_president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )

    applicant = UserFactory(email="user100@campus.edu")
    application = ClubJoinApplicationFactory(
        club=club,
        user=applicant,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(vice_president.email)

    response = client.get(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == application.id

#
def test_get_club_applications_forbidden_for_member(
    client,
    auth_headers,
):
    club = ClubFactory(university=UniversityFactory())
    member = UserFactory()

    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(member.email)

    response = client.get(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
    )

    assert response.status_code == 403


#
def test_get_club_applications_unauthorized(client):
    response = client.get(
        "/api/clubs/1/applications",
    )

    assert response.status_code == 401

# Database error check
def test_get_database_error(
    client,
    auth_headers,
    university_admin_user,
    db_error,
):
    club = ClubFactory(university=UniversityFactory())
    president = UserFactory(email="president_club@campus.edu")
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    db_error(club_application_module)
    headers = auth_headers(president.email)
    response = client.get(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]