from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.committee_routes  as committee_module

def test_update_committee_member_role_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == (
        "Committee member role updated successfully"
    )
    assert (
        body["committee_membership"]["id"]
        == committee_membership.id
    )
    assert (
        body["committee_membership"]["role"]
        == CommitteeRole.HEAD.value
    )


def test_update_committee_member_role_missing_role(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={},
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "role is required"


def test_update_committee_member_not_found(
    client,
    auth_headers,
):
    president = UserFactory(
        email="president@campus.edu",
    )
    headers = auth_headers(president.email)
    response = client.patch(
        "/api/committee-memberships/999999",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Committee membership not found"



def test_update_committee_member_user_not_club_member(
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
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(outsider.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == "You are not a member of this club"


def test_update_committee_member_role_not_president(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    vice_president = UserFactory(
        email="vp@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=vice_president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(vice_president.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "Only the President can update committee roles"
    )

def test_update_committee_member_invalid_role(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": "INVALID_ROLE",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Invalid committee role"


def test_update_committee_member_role_persists(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert (
        body["committee_membership"]["role"]
        == CommitteeRole.HEAD.value
    )


def test_update_committee_member_unapproved_president(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == "You are not a member of this club"



def test_update_committee_member_role_database_error(
    client,
    auth_headers,
    db_error
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    member_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(president.email)
    db_error(committee_module)
    response = client.patch(
        f"/api/committee-memberships/{committee_membership.id}",
        json={
            "role": CommitteeRole.HEAD.value,
        },
        headers=headers,
    )

    assert response.status_code == 500

    body = response.get_json()

    assert "Database Error" in body["message"]


