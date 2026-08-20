from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.leave_club  as leave_module

def test_leave_club_success(
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
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.post(
        f"/api/memberships/{membership.id}/leave",
        headers=headers,
    )
    body = response.get_json()
    assert response.status_code == 200
    assert body["message"] == "Successfully left the club."
    assert (
        body["membership"]["id"]
        == membership.id
    )
    assert (
        body["membership"]["status"]
        == MembershipStatus.WITHDRAWN.value
    )


def test_leave_club_membership_not_found(
    client,
    auth_headers,
):
    user = UserFactory(
        email="member@campus.edu",
    )
    headers = auth_headers(user.email)
    response = client.post(
        "/api/memberships/999999/leave",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Membership not found."

def test_leave_club_other_users_membership(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    current_user = UserFactory(
        email="user1@campus.edu",
        university=university,
    )
    other_user = UserFactory(
        email="user2@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=other_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(current_user.email)
    response = client.post(
        f"/api/memberships/{membership.id}/leave",
        headers=headers,
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "You can only leave your own club membership."
    )


def test_leave_club_membership_not_approved(
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
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.post(
        f"/api/memberships/{membership.id}/leave",
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "Only approved members can leave a club."
    )


from sqlalchemy.orm import Session


def test_leave_club_query_database_error(
    client,
    auth_headers,
    db_error
):
    user = UserFactory(
        email="member@campus.edu",
    )
    headers = auth_headers(user.email)
    db_error(leave_module)
    response = client.post(
        "/api/memberships/1/leave",
        headers=headers,
    )

    assert response.status_code == 500
    body = response.get_json()
    assert body["messge"] == "Uncaught Error"



def test_leave_club_sets_withdrawn_status(
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
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.post(
        f"/api/memberships/{membership.id}/leave",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert (
        body["membership"]["status"]
        == MembershipStatus.WITHDRAWN.value
    )
    assert body["membership"]["decided_at"] is not None