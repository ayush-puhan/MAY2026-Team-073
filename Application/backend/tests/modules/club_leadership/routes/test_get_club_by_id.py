from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.application_routes  as club_application_module


def test_get_club_by_id_success(client,auth_headers,):
    user = UserFactory()
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
        name="Coding Club",
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}",
        headers=headers,
    )
    assert response.status_code == 200

    body = response.get_json()

    assert body["id"] == club.id
    assert body["name"] == club.name
    assert body["slug"] == club.slug
    assert body["category"] == club.category
    assert body["description"] == club.description
    assert body["faculty_advisor_id"] == club.faculty_advisor_id


def test_get_club_by_id_includes_university(client,auth_headers):
    user = UserFactory()
    university = UniversityFactory(
        name="Test University",
    )
    club = ClubFactory(
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["university"] == {
        "id": university.id,
        "name": university.name,
    }


def test_get_club_by_id_member_count(client,auth_headers):
    user = UserFactory()
    club = ClubFactory(university=UniversityFactory())

    approved_user1 = UserFactory()
    approved_user2 = UserFactory()
    pending_user = UserFactory()

    ClubMembershipFactory(
        user=approved_user1,
        club=club,
        status=MembershipStatus.APPROVED,
    )

    ClubMembershipFactory(
        user=approved_user2,
        club=club,
        status=MembershipStatus.APPROVED,
    )

    ClubMembershipFactory(
        user=pending_user,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["members"] == 2



def test_get_club_by_id_interests(client,auth_headers):
    user = UserFactory()
    club = ClubFactory(university=UniversityFactory())

    interest1 = InterestFactory(
        name="Technology",
    )
    interest2 = InterestFactory(
        name="Robotics",
    )

    ClubInterestFactory(
        club=club,
        interest=interest1,
    )
    ClubInterestFactory(
        club=club,
        interest=interest2,
    )

    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert set(body["interests"]) == {
        "Technology",
        "Robotics",
    }


def test_get_club_by_id_not_found(client,auth_headers):
    user = UserFactory()
    headers = auth_headers(user.email)
    response = client.get(
        "/api/clubs/99999",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Club not found"


def test_get_club_by_id_unauthorized(client):
    response = client.get(
        "/api/clubs/1",
    )
    assert response.status_code == 401