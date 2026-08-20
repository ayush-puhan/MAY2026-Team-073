from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.membership_routes  as member_module


def test_get_club_membership_requests_success(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    student1 = UserFactory(
        email="student1@campus.edu",
        university=university,
    )

    student2 = UserFactory(
        email="student2@campus.edu",
        university=university,
    )

    membership1 = ClubMembershipFactory(
        user=student1,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    membership2 = ClubMembershipFactory(
        user=student2,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(student1.email)

    response = client.get(
        f"/api/clubs/{club.id}/membership-requests",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    membership_ids = {
        item["id"]
        for item in body
    }

    assert membership_ids == {
        membership1.id,
        membership2.id,
    }


def test_get_club_membership_requests_only_pending(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    pending_user = UserFactory(
        email="pending@campus.edu",
        university=university,
    )

    approved_user = UserFactory(
        email="approved@campus.edu",
        university=university,
    )

    rejected_user = UserFactory(
        email="rejected@campus.edu",
        university=university,
    )

    pending_membership = ClubMembershipFactory(
        user=pending_user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    ClubMembershipFactory(
        user=approved_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    ClubMembershipFactory(
        user=rejected_user,
        club=club,
        status=MembershipStatus.REJECTED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(pending_user.email)

    response = client.get(
        f"/api/clubs/{club.id}/membership-requests",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == pending_membership.id
    assert body[0]["status"] == "pending"


def test_get_club_membership_requests_empty(
    client,
    auth_headers,
):
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
    )

    student = UserFactory(
        email="student@campus.edu",
        university=university,
    )

    ClubMembershipFactory(
        user=student,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(student.email)

    response = client.get(
        f"/api/clubs/{club.id}/membership-requests",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body == []



def test_get_club_membership_requests_filters_club(
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

    student1 = UserFactory(
        email="student1@campus.edu",
        university=university,
    )

    student2 = UserFactory(
        email="student2@campus.edu",
        university=university,
    )

    membership1 = ClubMembershipFactory(
        user=student1,
        club=club1,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    membership2 = ClubMembershipFactory(
        user=student2,
        club=club2,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(student1.email)

    response = client.get(
        f"/api/clubs/{club1.id}/membership-requests",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    membership_ids = {
        item["id"]
        for item in body
    }

    assert membership1.id in membership_ids
    assert membership2.id not in membership_ids



def test_get_club_membership_requests_nonexistent_club(
    client,
    auth_headers,
):
    student = UserFactory(
        email="student@campus.edu",
    )

    headers = auth_headers(student.email)

    response = client.get(
        "/api/clubs/999999/membership-requests",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body == []




from sqlalchemy.orm import Session


def test_get_club_membership_requests_database_error(
    client,
    auth_headers,
    db_error
):
    student = UserFactory(
        email="student@campus.edu",
    )

    headers = auth_headers(student.email)
    db_error(member_module)
    response = client.get(
        "/api/clubs/1/membership-requests",
        headers=headers,
    )

    assert response.status_code == 500

    body = response.get_json()

    assert "Database Error" in body["message"]


def test_get_club_membership_requests_requires_authentication(
    client,
):
    response = client.get(
        "/api/clubs/1/membership-requests"
    )
    assert response.status_code == 401


def test_get_club_membership_requests_requires_student_role(
    client,
    auth_headers,
):
    university = UniversityFactory()
    user = UserFactory(
        email="admin@campus.edu",
        university=university,
        role=UserRole.SYSTEM_ADMIN,
    )
    headers = auth_headers(user.email)
    response = client.get(
        "/api/clubs/1/membership-requests",
        headers=headers,
    )
    assert response.status_code == 403


