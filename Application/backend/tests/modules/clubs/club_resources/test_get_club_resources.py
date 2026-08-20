from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_resources  as club_resource_module


def test_get_club_resources_success(
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

    document1 = DocumentFactory(
        owner=member,
        club=club,
        committee=None,
    )

    document2 = DocumentFactory(
        owner=member,
        club=club,
        committee=None,
    )

    headers = auth_headers(member.email)

    response = client.get(
        f"/api/clubs/{club.id}/resources",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    ids = {document["id"] for document in body}

    assert ids == {
        document1.id,
        document2.id,
    }


def test_get_club_resources_excludes_committee_documents(
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

    resource = DocumentFactory(
        owner=member,
        club=club,
        committee=None,
    )

    committee_document = DocumentFactory(
        owner=member,
        club=club,
        committee=CommitteeFactory(club=club)
    )

    headers = auth_headers(member.email)

    response = client.get(
        f"/api/clubs/{club.id}/resources",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    assert body[0]["id"] == resource.id
    assert body[0]["id"] != committee_document.id



def test_get_club_resources_returns_only_requested_club_resources(
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
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=member,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    resource1 = DocumentFactory(
        owner=member,
        club=club1,
        committee=None,
    )
    resource2 = DocumentFactory(
        owner=member,
        club=club2,
        committee=None,
    )

    headers = auth_headers(member.email)
    response = client.get(
        f"/api/clubs/{club1.id}/resources",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1

    assert body[0]["id"] == resource1.id
    assert body[0]["id"] != resource2.id


def test_get_club_resources_ordered_by_latest_first(
    client,
    auth_headers,
):
    from datetime import datetime, timedelta
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
    older_document = DocumentFactory(
        owner=member,
        club=club,
        committee=None,
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    newer_document = DocumentFactory(
        owner=member,
        club=club,
        committee=None,
        created_at=datetime.utcnow(),
    )
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/clubs/{club.id}/resources",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    assert body[0]["id"] == newer_document.id
    assert body[1]["id"] == older_document.id



def test_get_club_resources_empty(
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
        f"/api/clubs/{club.id}/resources",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_club_resources_forbidden_for_non_member(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="user@campus.edu",
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/resources",
        headers=headers,
    )
    assert response.status_code == 403

def test_get_club_resources_unauthorized(
    client,
):
    response = client.get(
        "/api/clubs/1/resources",
    )

    assert response.status_code == 401

import pytest
@pytest.mark.parametrize(
    "club_role",
    [
        ClubMemberRole.MEMBER,
        ClubMemberRole.SECRETARY,
        ClubMemberRole.VOLUNTEER_COORDINATOR,
        ClubMemberRole.EVENT_COORDINATOR,
        ClubMemberRole.TREASURER,
        ClubMemberRole.VICE_PRESIDENT,
        ClubMemberRole.PRESIDENT,
    ],
)
def test_get_club_resources_allowed_roles(
    client,
    auth_headers,
    club_role,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email=f"{club_role.value}@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=club_role,
    )
    document = DocumentFactory(
        owner=user,
        club=club,
        committee_id=None,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/resources",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == document.id

    