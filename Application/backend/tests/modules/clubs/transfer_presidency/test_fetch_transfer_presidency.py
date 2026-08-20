from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.transfer_presidency  as tp_module


def test_transfer_presidency_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )
    current_membership = ClubMembershipFactory(
        user=current_president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )
    headers = auth_headers(current_president.email)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == (
        "Presidency transferred successfully."
    )
    assert body["previous_president_membership_id"] == (
        current_membership.id
    )
    assert body["new_president_membership_id"] == (
        successor_membership.id
    )


def test_transfer_presidency_missing_current_membership_id(
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
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "successor_membership_id": 2,
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "current_membership_id is required"
    )



def test_transfer_presidency_missing_successor_membership_id(
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
    membership = ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": membership.id,
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "successor_membership_id is required"
    )



def test_transfer_presidency_empty_body(
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
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "current_membership_id is required"
    )


def test_transfer_presidency_current_membership_not_found(
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
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )
    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": 999999,
            "successor_membership_id": successor_membership.id,
        },
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == (
        "Current membership not found."
    )


def test_transfer_presidency_successor_membership_not_found(
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
    current_membership = ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": 999999,
        },
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == (
        "Successor membership not found."
    )



def test_transfer_presidency_current_membership_wrong_club(
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
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )
    current_membership = ClubMembershipFactory(
        user=president,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )
    # Authentication must be president of club1.
    president_membership_club1 = ClubMembershipFactory(
        user=president,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club1.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "Current membership does not belong to this club."
    )


def test_transfer_presidency_successor_wrong_club(
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
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )
    current_membership = ClubMembershipFactory(
        user=president,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/clubs/{club1.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "Successor membership does not belong to this club."
    )



def test_transfer_presidency_current_member_not_president(
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

    current_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )

    # Required so the authenticated user passes
    # @require_club_role("president").
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    current_membership = ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )

    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    # This test directly exercises the resource's
    # current_membership role check. Therefore the
    # authenticated user must be the actual president.
    headers = auth_headers(president.email)

    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == (
        "Current member is not the President."
    )



def test_transfer_presidency_successor_not_approved(
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

    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )

    current_membership = ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(president.email)

    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == (
        "Successor must be an approved member."
    )




def test_transfer_presidency_successor_already_president(
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

    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )

    current_membership = ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(president.email)

    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": current_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == (
        "Selected member is already the President."
    )


def test_transfer_presidency_non_president_forbidden(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )

    successor = UserFactory(
        email="successor@campus.edu",
        university=university,
    )

    member_membership = ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    successor_membership = ClubMembershipFactory(
        user=successor,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )

    headers = auth_headers(member.email)

    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": member_membership.id,
            "successor_membership_id": successor_membership.id,
        },
    )

    assert response.status_code == 403


from sqlalchemy.orm import Session


def test_transfer_presidency_database_get_error(
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
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    db_error(tp_module)
    response = client.patch(
        f"/api/clubs/{club.id}/transfer-presidency",
        headers=headers,
        json={
            "current_membership_id": 1,
            "successor_membership_id": 2,
        },
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]