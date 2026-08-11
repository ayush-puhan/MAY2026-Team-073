from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.membership_routes  as member_module


def test_get_club_members_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user1 = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    user2 = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    membership1 = ClubMembershipFactory(
        user=user1,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    membership2 = ClubMembershipFactory(
        user=user2,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
    )
    headers = auth_headers(user1.email)
    response = client.get(
        f"/api/clubs/{club.id}/members",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    membership_ids = {
        item["id"]
        for item in body
    }
    assert membership_ids == {
        membership1.id,
        membership2.id,
    }



def test_get_club_members_only_approved(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    approved_user = UserFactory(
        email="approved@campus.edu",
        university=university,
    )
    pending_user = UserFactory(
        email="pending@campus.edu",
        university=university,
    )
    approved_membership = ClubMembershipFactory(
        user=approved_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=pending_user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(approved_user.email)
    response = client.get(
        f"/api/clubs/{club.id}/members",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == approved_membership.id


def test_get_club_members_empty(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    user = UserFactory(
        email="pending@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/clubs/{club.id}/members",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body == []



def test_get_club_members_by_query_parameter(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user1 = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    user2 = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    membership1 = ClubMembershipFactory(
        user=user1,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    membership2 = ClubMembershipFactory(
        user=user2,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
    )
    headers = auth_headers(user1.email)
    response = client.get(
        f"/api/club_memberships?club_id={club.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    membership_ids = {
        item["id"]
        for item in body
    }
    assert membership_ids == {
        membership1.id,
        membership2.id,
    }



def test_get_all_approved_club_memberships(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club1 = ClubFactory(
        university=university,
    )
    club2 = ClubFactory(
        university=university,
    )
    user1 = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    user2 = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    membership1 = ClubMembershipFactory(
        user=user1,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    membership2 = ClubMembershipFactory(
        user=user2,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user1.email)
    response = client.get(
        "/api/club_memberships",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    membership_ids = {
        item["id"]
        for item in body
    }
    assert membership1.id in membership_ids
    assert membership2.id in membership_ids


def test_get_club_members_filters_correct_club(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club1 = ClubFactory(
        university=university,
    )
    club2 = ClubFactory(
        university=university,
    )
    user1 = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    user2 = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    membership1 = ClubMembershipFactory(
        user=user1,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    membership2 = ClubMembershipFactory(
        user=user2,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user1.email)
    response = client.get(
        f"/api/clubs/{club1.id}/members",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    membership_ids = {
        item["id"]
        for item in body
    }
    assert membership1.id in membership_ids
    assert membership2.id not in membership_ids


def test_get_club_members_nonexistent_club(
    client,
    auth_headers,
):
    user = UserFactory(
        email="user@campus.edu",
    )
    headers = auth_headers(user.email)
    response = client.get(
        "/api/clubs/999999/members",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []



from sqlalchemy.orm import Session


def test_get_club_members_database_error(
    client,
    auth_headers,
    db_error
):
    user = UserFactory(
        email="user@campus.edu",
    )
    headers = auth_headers(user.email)
    db_error(member_module)
    response = client.get(
        "/api/clubs/1/members",
        headers=headers,
    )

    assert response.status_code == 500
    body = response.get_json()
    assert body["messge"] == "Uncaught Error"



def test_get_club_members_requires_authentication(
    client,
):
    response = client.get(
        "/api/clubs/1/members"
    )
    assert response.status_code == 401