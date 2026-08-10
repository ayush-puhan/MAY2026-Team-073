from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.committee_routes  as committee_module


def test_add_committee_member_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    current_user_membership = ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    target_membership = ClubMembershipFactory(
        user=member_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "Member added successfully"
    assert (
        body["committee_membership"]["membership_id"]
        == target_membership.id
    )
    assert (
        body["committee_membership"]["committee_id"]
        == committee.id
    )


# missing club membership_id
def test_add_committee_member_missing_membership_id(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={},
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "membership_id is required"


def test_add_committee_member_committee_not_found(
    client,
    auth_headers,
):
    current_user = UserFactory(
        email="president@campus.edu",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        "/api/committees/999999/members",
        json={
            "membership_id": 1,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Committee not found"


def test_add_committee_member_current_user_not_club_member(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="outsider@campus.edu",
        university=university,
    )
    target_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    target_membership = ClubMembershipFactory(
        user=target_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == "You are not a member of this club"


def test_add_committee_member_insufficient_permissions(
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
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == "Insufficient permissions"

def test_add_committee_member_membership_not_found(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": 999999,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Membership not found"


def test_add_committee_member_membership_from_another_club(
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
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    target_user = UserFactory(
        email="otherclub@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    target_membership = ClubMembershipFactory(
        user=target_user,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club1,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Member does not belong to this club"


def test_add_committee_member_already_exists(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    target_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    target_membership = ClubMembershipFactory(
        user=target_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    CommitteeMembershipFactory(
        committee=committee,
        membership=target_membership,
        role=CommitteeRole.MEMBER,
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 409
    body = response.get_json()
    assert body["message"] == "Member already exists in committee"


def test_add_committee_member_invalid_role(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    target_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    target_membership = ClubMembershipFactory(
        user=target_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": "INVALID_ROLE",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Invalid committee role"


def test_add_committee_member_current_user_membership_not_approved(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    target_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    target_membership = ClubMembershipFactory(
        user=target_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee = CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/committees/{committee.id}/members",
        json={
            "membership_id": target_membership.id,
            "role": CommitteeRole.MEMBER.value,
        },
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == "You are not a member of this club"