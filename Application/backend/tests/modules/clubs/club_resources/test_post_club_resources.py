from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_resources  as club_resource_module




def test_create_club_resource_success(
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
    payload = {
        "title": "Club Constitution",
        "file_url": "https://example.com/constitution.pdf",
        "doc_type": "GENERAL",
    }
    response = client.post(
        f"/api/clubs/{club.id}/resources",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["owner_id"] == president.id
    assert body["club_id"] == club.id
    assert body["committee_id"] is None
    assert body["event_id"] is None
    assert body["title"] == "Club Constitution"
    assert body["file_url"] == "https://example.com/constitution.pdf"
    assert body["doc_type"] == DocumentType.GENERAL.value
    assert body["created_at"] is not None


def test_create_club_resource_success_for_secretary(
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
    payload = {
        "title": "Annual Report",
        "file_url": "https://example.com/report.pdf",
    }
    response = client.post(
        f"/api/clubs/{club.id}/resources",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201

    body = response.get_json()

    assert body["owner_id"] == secretary.id
    assert body["club_id"] == club.id
    assert body["title"] == "Annual Report"
    assert body["file_url"] == "https://example.com/report.pdf"


def test_create_club_resource_missing_title(
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
        f"/api/clubs/{club.id}/resources",
        json={
            "file_url": "https://example.com/file.pdf",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "title is required"


def test_create_club_resource_missing_file_url(
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
        f"/api/clubs/{club.id}/resources",
        json={
            "title": "Club Rules",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "file_url is required"

def test_create_club_resource_invalid_doc_type(
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
        f"/api/clubs/{club.id}/resources",
        json={
            "title": "Club Document",
            "file_url": "https://example.com/document.pdf",
            "doc_type": "INVALID_TYPE",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Invalid document type"

def test_create_club_resource_defaults_to_general(
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
        f"/api/clubs/{club.id}/resources",
        json={
            "title": "General Information",
            "file_url": "https://example.com/info.pdf",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["doc_type"] == DocumentType.GENERAL.value


def test_create_club_resource_forbidden_for_regular_member(
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
    response = client.post(
        f"/api/clubs/{club.id}/resources",
        json={
            "title": "Unauthorized Document",
            "file_url": "https://example.com/file.pdf",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_club_resource_unauthorized(
    client,
):
    response = client.post(
        "/api/clubs/1/resources",
        json={
            "title": "Club Document",
            "file_url": "https://example.com/file.pdf",
        },
    )

    assert response.status_code == 401


def test_create_club_resource_persists_to_database(
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
    headers = auth_headers(president.email)
    response = client.post(
        f"/api/clubs/{club.id}/resources",
        json={
            "title": "Meeting Minutes",
            "file_url": "https://example.com/minutes.pdf",
            "doc_type": "GENERAL",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    document = (
        db_session.query(Document)
        .filter(Document.id == body["id"])
        .first()
    )
    assert document is not None
    assert document.owner_id == president.id
    assert document.club_id == club.id
    assert document.committee_id is None
    assert document.event_id is None
    assert document.title == "Meeting Minutes"
    assert document.file_url == "https://example.com/minutes.pdf"
    assert document.doc_type == DocumentType.GENERAL