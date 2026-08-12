from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.committee_routes  as committee_module

def test_get_committees_success(
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
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    committee1 = CommitteeFactory(
        club=club,
        name="Cultural Committee",
    )
    committee2 = CommitteeFactory(
        club=club,
        name="Sports Committee",
    )
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/clubs/{club.id}/committees",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    ids = {committee["id"] for committee in body}
    assert ids == {
        committee1.id,
        committee2.id,
    }


def test_get_committees_sorted_by_name(
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
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    CommitteeFactory(
        club=club,
        name="Sports Committee",
    )
    CommitteeFactory(
        club=club,
        name="Cultural Committee",
    )
    CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/clubs/{club.id}/committees",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert [committee["name"] for committee in body] == [
        "Cultural Committee",
        "Finance Committee",
        "Sports Committee",
    ]

def test_get_committees_empty(
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
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/clubs/{club.id}/committees",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_committees_club_not_found(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.get(
        "/api/clubs/999999/committees",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Club not found"


def test_get_committees_unauthorized(
    client,
):
    response = client.get(
        "/api/clubs/1/committees",
    )

    assert response.status_code == 401



def test_get_committees_forbidden_for_non_member(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="outsider@campus.edu",
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/committees",
        headers=headers,
    )
    assert response.status_code == 403


def test_get_committees_database_error(
    client,
    auth_headers ,
    db_error,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(member.email)
    
    db_error(committee_module)
    response = client.get(
        f"/api/clubs/{club.id}/committees",
        headers=headers,
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]