from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.membership_routes  as member_module

def test_get_user_clubs_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
        name="Coding Club",
        slug="coding-club",
    )
    user = UserFactory(
        email="student@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    club_data = body[0]
    assert club_data["id"] == club.id
    assert club_data["name"] == "Coding Club"
    assert club_data["slug"] == "coding-club"
    assert club_data["membership_id"] == membership.id
    assert club_data["role_in_club"] == "member"
    assert club_data["members"] == 1
    assert club_data["university"]["id"] == university.id
    assert club_data["university"]["name"] == university.name

def test_get_user_clubs_multiple_approved_clubs(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club1 = ClubFactory(
        university=university,
        name="Coding Club",
        slug="coding-club",
    )
    club2 = ClubFactory(
        university=university,
        name="Music Club",
        slug="music-club",
    )
    user = UserFactory(
        email="student@campus.edu",
        university=university,
    )
    membership1 = ClubMembershipFactory(
        user=user,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    membership2 = ClubMembershipFactory(
        user=user,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    club_ids = {
        item["id"]
        for item in body
    }
    membership_ids = {
        item["membership_id"]
        for item in body
    }
    assert club_ids == {
        club1.id,
        club2.id,
    }
    assert membership_ids == {
        membership1.id,
        membership2.id,
    }


def test_get_user_clubs_only_approved_memberships(
    client,
    auth_headers,
):
    university = UniversityFactory()
    approved_club = ClubFactory(
        university=university,
        name="Coding Club",
    )
    pending_club = ClubFactory(
        university=university,
        name="Sports Club",
    )
    rejected_club = ClubFactory(
        university=university,
        name="Music Club",
    )
    user = UserFactory(
        email="student@campus.edu",
        university=university,
    )
    approved_membership = ClubMembershipFactory(
        user=user,
        club=approved_club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=user,
        club=pending_club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=user,
        club=rejected_club,
        status=MembershipStatus.REJECTED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == approved_club.id
    assert (
        body[0]["membership_id"]
        == approved_membership.id
    )

def test_get_user_clubs_excludes_withdrawn_membership(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="student@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.WITHDRAWN,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_user_clubs_empty(
    client,
    auth_headers,
):
    university = UniversityFactory()
    user = UserFactory(
        email="student@campus.edu",
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/users/{user.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []



def test_get_user_clubs_member_count(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user1 = UserFactory(
        email="student1@campus.edu",
        university=university,
    )
    user2 = UserFactory(
        email="student2@campus.edu",
        university=university,
    )
    user3 = UserFactory(
        email="student3@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user1,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=user2,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=user3,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user1.email)
    response = client.get(
        f"/api/users/{user1.id}/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    # Only user1 and user2 are approved.
    assert body[0]["members"] == 2



def test_get_user_clubs_user_not_found(
    client,
    auth_headers,
):
    current_user = UserFactory(
        email="current@campus.edu",
    )
    headers = auth_headers(current_user.email)
    response = client.get(
        "/api/users/999999/clubs",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_user_clubs_database_error(
    client,
    auth_headers,
    db_error
):
    user = UserFactory(
        email="student@campus.edu",
    )

    headers = auth_headers(user.email)

    db_error(member_module)
    response = client.get(
        f"/api/users/{user.id}/clubs",
        headers=headers,
    )

    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]