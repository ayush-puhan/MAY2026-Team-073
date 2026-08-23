from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.membership_routes  as member_module
#
def test_update_member_role_success(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    membership = ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        f"/api/memberships/{membership.id}/role",
        headers=headers,
        json={
            "role": ClubMemberRole.SECRETARY.value
        },
    )
    body = response.get_json()
    assert response.status_code == 200
    assert body["message"] == (
        "Member role updated successfully."
    )
    assert body["membership"]["id"] == membership.id
    assert body["membership"]["role_in_club"] == "secretary"


def test_update_member_role_missing_body(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        "/api/memberships/1/role",
        headers=headers,
        json={},
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Request body required."




def test_update_member_role_missing_role(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        "/api/memberships/1/role",
        headers=headers,
        json={
            "name": "Something"
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "role is required."
    )


def test_update_member_role_empty_role(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        "/api/memberships/1/role",
        headers=headers,
        json={
            "role": ""
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "role is required."
    )


def test_update_member_role_invalid_role(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )

    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    membership = ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        f"/api/memberships/{membership.id}/role",
        headers=headers,
        json={
            "role": "invalid_role"
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert "Invalid club role." in body["message"]



def test_update_member_role_membership_not_found(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        "/api/memberships/999999/role",
        headers=headers,
        json={
            "role": "member"
        },
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Membership not found."

#
def test_update_member_role_non_president_forbidden(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    current_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    target_user = UserFactory(
        email="target@campus.edu",
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

    headers = auth_headers(current_user.email)
    mock_resolve_club_id(current_user)
    response = client.patch(
        f"/api/memberships/{target_membership.id}/role",
        headers=headers,
        json={
            "role": "secretary"
        },
    )

    assert response.status_code == 403

#
def test_update_member_role_uppercase_input(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )

    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    membership = ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        f"/api/memberships/{membership.id}/role",
        headers=headers,
        json={
            "role": ClubMemberRole.SECRETARY.value
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["membership"]["role_in_club"] == "secretary"



def test_update_member_role_database_query_error(
    client,
    auth_headers,mock_resolve_club_id,
    db_error,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    db_error(member_module)
    response = client.patch(
        "/api/memberships/1/role",
        headers=headers,
        json={
            "role": "secretary"
        },
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]


def test_update_member_role_requires_authentication(
    client,
):
    response = client.patch(
        "/api/memberships/1/role",
        json={
            "role": "secretary"
        },
    )

    assert response.status_code == 401