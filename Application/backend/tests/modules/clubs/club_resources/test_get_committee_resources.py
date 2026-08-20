from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_resources  as club_resource_module

def test_get_committee_resources_success(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee = CommitteeFactory(
        club=club,
    )
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    cm = ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    CommitteeMembershipFactory(
        committee = committee,
        membership=cm
    )
    document1 = DocumentFactory(
        owner=member,
        club=club,
        committee=committee,
    )
    document2 = DocumentFactory(
        owner=member,
        club=club,
        committee=committee,
    )
    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.get(
        f"/api/committees/{committee.id}/resources",
        headers=headers,
    )
    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 2
    ids = {document["id"] for document in body}
    assert ids == {
        document1.id,
        document2.id,
    }



def test_get_committee_resources_returns_only_committee_documents(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee1 = CommitteeFactory(
        club=club,
    )
    committee2 = CommitteeFactory(
        club=club,
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
        committee=committee1,
    )
    document2 = DocumentFactory(
        owner=member,
        club=club,
        committee=committee2,
    )
    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.get(
        f"/api/committees/{committee1.id}/resources",
        headers=headers,
    )
    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["id"] == document1.id
    assert body[0]["id"] != document2.id



def test_get_committee_resources_empty(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee = CommitteeFactory(
        club=club,
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
        f"/api/committees/{committee.id}/resources",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_committee_resources_not_found(
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
        "/api/committees/999999/resources",
        headers=headers,
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["message"] == "Committee not found"


def test_get_committee_resources_ordered_by_latest_first(
    client,
    auth_headers,
    mock_resolve_club_id
):
    from datetime import datetime, timedelta
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee = CommitteeFactory(
        club=club,
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
        committee=committee,
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    newer_document = DocumentFactory(
        owner=member,
        club=club,
        committee=committee,
        created_at=datetime.utcnow(),
    )
    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.get(
        f"/api/committees/{committee.id}/resources",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    assert body[0]["id"] == newer_document.id
    assert body[1]["id"] == older_document.id


def test_get_committee_resources_forbidden_for_non_member(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee = CommitteeFactory(
        club=club,
    )
    user = UserFactory(
        email="user@campus.edu",
        university=university,
    )
    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.get(
        f"/api/committees/{committee.id}/resources",
        headers=headers,
    )

    assert response.status_code in [403,400]


def test_get_committee_resources_unauthorized(
    client,
):
    response = client.get(
        "/api/committees/1/resources",
    )

    assert response.status_code == 401


import pytest
@pytest.mark.parametrize(
    "club_role",
    [
        ClubMemberRole.MEMBER,
        ClubMemberRole.SECRETARY,
        ClubMemberRole.PRESIDENT,
    ],
)
def test_get_committee_resources_allowed_club_roles(
    client,
    auth_headers,
    club_role,
    mock_resolve_club_id
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    committee = CommitteeFactory(
        club=club,
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
        committee=committee,
    )

    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.get(
        f"/api/committees/{committee.id}/resources",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == document.id