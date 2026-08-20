from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.membership_routes  as member_module

def test_get_user_role_in_club_success(
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
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/members/{user.id}/role",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["club_id"] == club.id
    assert body["user_id"] == user.id
    assert body["role_in_club"] == "president"



def test_get_user_role_in_club_membership_not_found(
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
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/members/{user.id}/role",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Membership not found."



def test_get_user_role_in_club_pending_membership(
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
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/clubs/{club.id}/members/{user.id}/role",
        headers=headers,
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["message"] == "Membership not found."


def test_get_user_role_in_club_wrong_club(
    client,
    auth_headers,
):
    university = UniversityFactory()

    actual_club = ClubFactory(
        university=university,
    )

    requested_club = ClubFactory(
        university=university,
    )

    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=user,
        club=actual_club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/clubs/{requested_club.id}/members/{user.id}/role",
        headers=headers,
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["message"] == "Membership not found."


import pytest


@pytest.mark.parametrize(
    "role,expected_role",
    [
        (ClubMemberRole.PRESIDENT, "president"),
        (ClubMemberRole.VICE_PRESIDENT, "vice_president"),
        (ClubMemberRole.SECRETARY, "secretary"),
        (ClubMemberRole.MEMBER, "member"),
    ],
)
def test_get_user_role_in_club_roles(
    client,
    auth_headers,
    role,
    expected_role,
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
        role_in_club=role,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/clubs/{club.id}/members/{user.id}/role",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["club_id"] == club.id
    assert body["user_id"] == user.id
    assert body["role_in_club"] == expected_role

def test_get_user_role_in_club_database_error(
    client,
    auth_headers,
    db_error
):
    user = UserFactory(
        email="member@campus.edu",
    )

    headers = auth_headers(user.email)
    db_error(member_module)
    response = client.get(
        f"/api/clubs/1/members/{user.id}/role",
        headers=headers,
    )

    assert response.status_code == 500

    body = response.get_json()

    assert "Database Error" in body["message"]



def test_get_user_role_in_club_requires_authentication(
    client,
):
    response = client.get(
        "/api/clubs/1/members/1/role"
    )

    assert response.status_code == 401