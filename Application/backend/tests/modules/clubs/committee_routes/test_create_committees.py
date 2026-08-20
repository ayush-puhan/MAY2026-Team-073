from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.committee_routes  as committee_module

def test_create_committee_success(
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
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "name": "Finance Committee",
            "description": "Handles club finances.",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "Committee created successfully"
    committee = body["committee"]
    assert committee["club_id"] == club.id
    assert committee["name"] == "Finance Committee"
    assert committee["description"] == "Handles club finances."
    assert committee["id"] is not None
    assert committee["created_at"] is not None


def test_create_committee_without_description(
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
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "name": "Event Committee",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["committee"]["name"] == "Event Committee"
    assert body["committee"]["description"] is None


def test_create_committee_missing_name(
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
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "description": "Committee description",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Committee name is required"


def test_create_committee_empty_name(
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
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "name": "",
            "description": "Committee description",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Committee name is required"


def test_create_committee_club_not_found(
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
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.post(
        "/api/clubs/999999/committees",
        json={
            "name": "Finance Committee",
            "description": "Handles finances.",
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Club not found"

def test_create_committee_duplicate_name(
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
    CommitteeFactory(
        club=club,
        name="Finance Committee",
    )
    headers = auth_headers(president.email)
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "name": "Finance Committee",
            "description": "Another finance committee.",
        },
        headers=headers,
    )
    assert response.status_code == 409
    body = response.get_json()
    assert body["message"] == "Committee already exists"


def test_create_committee_same_name_different_club(
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
    ClubMembershipFactory(
        user=president,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    CommitteeFactory(
        club=club1,
        name="Finance Committee",
    )
    headers = auth_headers(president.email)
    response = client.post(
        f"/api/clubs/{club2.id}/committees",
        json={
            "name": "Finance Committee",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["committee"]["club_id"] == club2.id
    assert body["committee"]["name"] == "Finance Committee"

def test_create_committee_forbidden_for_non_president(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    secretary = UserFactory(
        email="secretary@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=secretary,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
    )
    headers = auth_headers(secretary.email)
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "name": "Finance Committee",
        },
        headers=headers,
    )
    assert response.status_code == 403

def test_create_committee_unauthorized(
    client,
):
    response = client.post(
        "/api/clubs/1/committees",
        json={
            "name": "Finance Committee",
        },
    )

    assert response.status_code == 401

def test_create_committee_database_error(
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
    db_error(committee_module)
    response = client.post(
        f"/api/clubs/{club.id}/committees",
        json={
            "name": "Finance Committee",
        },
        headers=headers,
    )
    assert response.status_code == 500