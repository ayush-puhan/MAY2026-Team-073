from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.application_routes  as club_application_module

#1. Get user's club applications successfully
def test_get_user_club_applications_success(
    client,
    auth_headers,
):
    user = UserFactory()
    club1 = ClubFactory(university=UniversityFactory())
    club2 = ClubFactory(university=UniversityFactory())
    application1 = ClubJoinApplicationFactory(
        user=user,
        club=club1,
        status=MembershipStatus.PENDING,
    )
    application2 = ClubJoinApplicationFactory(
        user=user,
        club=club2,
        status=MembershipStatus.APPROVED,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/club-applications",
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

#2. Only applications belonging to requested user are returned
def test_get_user_club_applications_filters_user(
    client,
    auth_headers,
):
    user1 = UserFactory()
    user2 = UserFactory()
    club = ClubFactory(university=UniversityFactory())

    application1 = ClubJoinApplicationFactory(
        user=user1,
        club=club,
        status=MembershipStatus.PENDING,
    )
    ClubJoinApplicationFactory(
        user=user2,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(user1.email)
    response = client.get(
        f"/api/users/{user1.id}/club-applications",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == application1.id
    assert body[0]["user_id"] == user1.id


#User has no application
def test_get_user_club_applications_empty(
    client,
    auth_headers,
):
    user = UserFactory()

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/users/{user.id}/club-applications",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# Non existannce userid return empty list
def test_get_user_club_applications_nonexistent_user(
    client,
    auth_headers,
):
    user = UserFactory()
    headers = auth_headers(user.email)
    response = client.get(
        "/api/users/99999/club-applications",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# Verify serializa application data
def test_get_user_club_applications_serialization(
    client,
    auth_headers,
):
    user = UserFactory(full_name="John Doe")
    club = ClubFactory(name="Coding Club",university=UniversityFactory())

    application = ClubJoinApplicationFactory(
        user=user,
        club=club,
        status=MembershipStatus.PENDING,
        motivation="I want to contribute.",
        contribution="Python development",
        previous_experience="Built web applications",
        skills="Python, Flask",
        portfolio_url="https://example.com",
        weekly_availability="10 hours",
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/users/{user.id}/club-applications",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    result = body[0]

    assert result["id"] == application.id
    assert result["user_id"] == user.id
    assert result["club_id"] == club.id
    assert result["user_name"] == user.full_name
    assert result["club_name"] == club.name
    assert result["motivation"] == application.motivation
    assert result["contribution"] == application.contribution
    assert result["previous_experience"] == application.previous_experience
    assert result["skills"] == application.skills
    assert result["portfolio_url"] == application.portfolio_url
    assert result["status"] == application.status.value.lower()



# Not Authenticated
def test_get_user_club_applications_unauthorized(client):
    response = client.get(
        "/api/users/1/club-applications",
    )

    assert response.status_code == 401


# Database error handelling check
def test_get_database_error(
    client,
    auth_headers,
    db_error,
):
    import app.modules.club_leadership.application_routes  as club_application_module
    user = UserFactory()
    db_error(club_application_module)
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/club-applications",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]