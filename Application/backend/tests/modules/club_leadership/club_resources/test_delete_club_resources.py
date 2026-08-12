from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.club_resources  as club_resource_module


def test_delete_club_resource_success(
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
    document = DocumentFactory(
        owner=president,
        club=club,
        committee_id=None,
    )
    headers = auth_headers(president.email)
    response = client.delete(
        f"/api/clubs/{club.id}/resources/{document.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "Resource deleted successfully"



def test_delete_club_resource_removed_from_database(
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
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    document = DocumentFactory(
        owner=president,
        club=club,
        committee=None,
    )
    document_id = document.id
    headers = auth_headers(president.email)
    response = client.delete(
        f"/api/clubs/{club.id}/resources/{document_id}",
        headers=headers,
    )
    assert response.status_code == 200
    #db_session.expire_all()
    deleted_document = (
        db_session.query(Document)
        .filter(Document.id == document_id)
        .first()
    )
    assert deleted_document is None



def test_delete_club_resource_not_found(
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
    response = client.delete(
        f"/api/clubs/{club.id}/resources/999999",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Resource not found"


def test_delete_club_resource_from_wrong_club(
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
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    document = DocumentFactory(
        owner=president,
        club=club2,
        committee=None,
    )
    headers = auth_headers(president.email)
    response = client.delete(
        f"/api/clubs/{club1.id}/resources/{document.id}",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Resource not found"


def test_delete_club_resource_forbidden_for_non_president(
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
    document = DocumentFactory(
        owner=secretary,
        club=club,
        committee_id=None,
    )
    headers = auth_headers(secretary.email)
    response = client.delete(
        f"/api/clubs/{club.id}/resources/{document.id}",
        headers=headers,
    )
    assert response.status_code == 403



def test_delete_club_resource_unauthorized(
    client,
):
    response = client.delete(
        "/api/clubs/1/resources/1",
    )

    assert response.status_code == 401