from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.committee_routes  as committee_module


def test_delete_committee_member_success(
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
    response = client.delete(
        f"/api/committee-memberships/{committee_membership.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == (
        "Committee member removed successfully"
    )


def test_delete_committee_member_persists(
    client,
    auth_headers,
    db_session,
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
    membership_id = committee_membership.id
    headers = auth_headers(president.email)
    response = client.delete(
        f"/api/committee-memberships/{membership_id}",
        headers=headers,
    )
    assert response.status_code == 200
    deleted_membership = (
        db_session.query(CommitteeMembership)
        .filter_by(id=membership_id)
        .first()
    )
    assert deleted_membership is None


def test_delete_committee_member_not_found(
    client,
    auth_headers,
):
    president = UserFactory(
        email="president@campus.edu",
    )
    headers = auth_headers(president.email)
    response = client.delete(
        "/api/committee-memberships/999999",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == (
        "Committee membership not found"
    )


def test_delete_committee_member_user_not_club_member(
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
    response = client.delete(
        f"/api/committee-memberships/{committee_membership.id}",
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "You are not a member of this club"
    )

def test_delete_committee_member_not_president(
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
    response = client.delete(
        f"/api/committee-memberships/{committee_membership.id}",
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "Only the President can remove committee members"
    )


def test_delete_committee_member_regular_member_forbidden(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    target_user = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    target_membership = ClubMembershipFactory(
        user=target_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=target_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(current_user.email)
    response = client.delete(
        f"/api/committee-memberships/{committee_membership.id}",
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "Only the President can remove committee members"
    )



def test_delete_committee_member_unapproved_president(
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
    response = client.delete(
        f"/api/committee-memberships/{committee_membership.id}",
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "You are not a member of this club"
    )


def test_delete_committee_member_database_error(
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
    )
    committee_membership = CommitteeMembershipFactory(
        committee=committee,
        membership=member_membership,
        role=CommitteeRole.MEMBER,
    )
    
    headers = auth_headers(president.email)
    db_error(committee_module)
    response = client.delete(
        f"/api/committee-memberships/{committee_membership.id}",
        headers=headers,
    )

    assert response.status_code == 500