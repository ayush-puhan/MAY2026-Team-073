from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.committee_routes  as committee_module



def test_get_committee_members_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    member_user1 = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    member_user2 = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    # Current user
    current_user = member_user1
    club_membership1 = ClubMembershipFactory(
        user=member_user1,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    club_membership2 = ClubMembershipFactory(
        user=member_user2,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    committee_membership1 = CommitteeMembershipFactory(
        committee=committee,
        membership=club_membership1,
    )

    committee_membership2 = CommitteeMembershipFactory(
        committee=committee,
        membership=club_membership2,
    )

    headers = auth_headers(current_user.email)
    response = client.get(
        f"/api/committees/{committee.id}/members",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    membership_ids = {
        item["committee_membership"]["membership_id"]
        for item in body
    }
    assert membership_ids == {
        club_membership1.id,
        club_membership2.id,
    }


def test_get_committee_members_contains_correct_membership_data(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    club_membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Sports Committee",
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=club_membership,
        role=CommitteeRole.MEMBER,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/committees/{committee.id}/members",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    item = body[0]

    assert item["committee_membership"]["id"] == committee_membership.id
    assert item["committee_membership"]["committee_id"] == committee.id
    assert item["committee_membership"]["membership_id"] == club_membership.id

    assert item["membership"]["id"] == club_membership.id
    assert item["membership"]["user_id"] == user.id
    assert item["membership"]["club_id"] == club.id
    assert item["membership"]["role_in_club"] == ClubMemberRole.MEMBER.value
    assert item["membership"]["status"] == MembershipStatus.APPROVED.value


def test_get_committee_members_committee_not_found(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(user.email)

    response = client.get(
        "/api/committees/999999/members",
        headers=headers,
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["message"] == "Committee not found"


def test_get_committee_members_forbidden_for_non_member(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    outsider = UserFactory(
        email="outsider@campus.edu",
        university=university,
    )

    committee = CommitteeFactory(
        club=club,
    )

    headers = auth_headers(outsider.email)

    response = client.get(
        f"/api/committees/{committee.id}/members",
        headers=headers,
    )

    assert response.status_code == 403

    body = response.get_json()

    assert body["message"] == "You are not a member of this club"


def test_get_committee_members_empty(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/committees/{committee.id}/members",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_committee_members_unauthorized(
    client,
):
    response = client.get(
        "/api/committees/1/members",
    )

    assert response.status_code == 401



from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError


def test_get_committee_members_database_error(
    client,
    auth_headers,
    db_error
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    headers = auth_headers(user.email)
    db_error(committee_module)
    response = client.get(
        f"/api/committees/{committee.id}/members",
        headers=headers,
    )

    assert response.status_code == 500