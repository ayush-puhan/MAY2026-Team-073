from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.application_routes  as club_application_module


#
def test_get_all_clubs_success(
    client,
    auth_headers,
):
    user = UserFactory()
    university = UniversityFactory()
    club1 = ClubFactory(
        university=university,
    )
    club2 = ClubFactory(
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        "/api/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    ids = {club["id"] for club in body}
    assert ids == {
        club1.id,
        club2.id,
    }



def test_get_clubs_filter_by_university(
    client,
    auth_headers,
):
    user = UserFactory()

    university1 = UniversityFactory()
    university2 = UniversityFactory()

    club1 = ClubFactory(
        university=university1,
    )

    ClubFactory(
        university=university2,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/clubs?university_id={university1.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    assert body[0]["id"] == club1.id
    assert body[0]["university"]["id"] == university1.id


def test_get_club_approved_member_count(
    client,
    auth_headers,
):
    user = UserFactory()
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
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
        "/api/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == club.id
    assert body[0]["members"] == 2



def test_get_club_university_details(
    client,
    auth_headers,
):
    user = UserFactory()
    university = UniversityFactory(
        name="IIT Example",
    )
    club = ClubFactory(
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        "/api/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["university"] == {
        "id": university.id,
        "name": "IIT Example",
    }


def test_get_club_interests(
    client,
    auth_headers,
):
    user = UserFactory()
    university = UniversityFactory()
    club = ClubFactory(university=university)

    interest1 = InterestFactory(name="Technology")
    interest2 = InterestFactory(name="Programming")

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
        "/api/clubs",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    assert set(body[0]["interests"]) == {
        "Technology",
        "Programming",
    }


def test_get_club_serialization(
    client,
    auth_headers,
):
    user = UserFactory()
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
        name="Coding Club",
        description="Programming and technology club",
    )
    headers = auth_headers(user.email)
    response = client.get(
        "/api/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    result = body[0]
    assert result["id"] == club.id
    assert result["name"] == club.name
    assert result["slug"] == club.slug
    assert result["category"] == club.category
    assert result["description"] == club.description
    assert result["faculty_advisor_id"] == club.faculty_advisor_id


def test_get_all_clubs_empty(client,auth_headers,):
    user = UserFactory()

    headers = auth_headers(user.email)

    response = client.get(
        "/api/clubs",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []



def test_get_clubs_for_university_with_no_clubs(client,auth_headers,):
    user = UserFactory()
    university = UniversityFactory()
    # Club belongs to another university
    ClubFactory(
        university=UniversityFactory(),
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs?university_id={university.id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_all_clubs_unauthorized(client):
    response = client.get(
        "/api/clubs",
    )
    assert response.status_code == 401