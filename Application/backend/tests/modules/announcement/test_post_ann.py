from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
# we can take any module where get_session() is being called to test db error like
# with get_session() as db:
import app.modules.announcements.routes  as ann_module

# Club president can create announcement
def test_create_club_announcement_as_president(
    client,
    auth_headers,
):
    user = UserFactory()
    university=UniversityFactory()
    club = ClubFactory(
        university=university
    )

    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(user.email)

    payload = {
        "club_id": club.id,
        "title": "Club Meeting",
        "body": "Meeting will be held tomorrow.",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["club_id"] == club.id
    assert body["posted_by"] == user.id
    assert body["title"] == "Club Meeting"
    assert body["body"] == "Meeting will be held tomorrow."
    assert body["target_audience"] == (
        AnnouncementAudience.ALL_MEMBERS.value
    )

# Club president can create announcement
def test_create_club_announcement_as_secretary(
    client,
    auth_headers,
):
    user = UserFactory()
    club = ClubFactory(university=UniversityFactory())

    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
    )

    headers = auth_headers(user.email)

    payload = {
        "club_id": club.id,
        "title": "Club Update",
        "body": "Important club update.",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["club_id"] == club.id
    assert body["posted_by"] == user.id


# Normal club member can not create announcements
def test_create_club_announcement_forbidden_for_member(
    client,
    auth_headers,
):
    user = UserFactory()
    club = ClubFactory(university=UniversityFactory())

    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(user.email)

    payload = {
        "club_id": club.id,
        "title": "Unauthorized",
        "body": "This should not be posted.",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403

    body = response.get_json()

    assert body["message"] == (
        "Only club President or Secretary can post announcements."
    )

# Pending member can not create
def test_create_club_announcement_pending_member_forbidden(
    client,
    auth_headers,
):
    user = UserFactory()
    club = ClubFactory(university=UniversityFactory())

    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(user.email)

    payload = {
        "club_id": club.id,
        "title": "Club Announcement",
        "body": "Should fail.",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403


# University can create university wide ann
def test_create_university_announcement(
    client,
    auth_headers,
):
    user = UserFactory(
        role=UserRole.STUDENT_AFFAIRS_OFFICE,
    )

    headers = auth_headers(user.email)

    payload = {
        "title": "University Announcement",
        "body": "University event announcement.",
        "target_audience": AnnouncementAudience.UNIVERSITY_WIDE.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["club_id"] is None
    assert body["posted_by"] == user.id
    assert body["title"] == "University Announcement"
    assert body["target_audience"] == (
        AnnouncementAudience.UNIVERSITY_WIDE.value
    )

# University can create system wide ann
def test_create_system_announcement(
    client,
    auth_headers,
):
    user = UserFactory(
        role=UserRole.DEAN_STUDENT_WELFARE,
    )

    headers = auth_headers(user.email)

    payload = {
        "title": "System Announcement",
        "body": "System-wide announcement.",
        "target_audience": AnnouncementAudience.SYSTEM_WIDE.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["club_id"] is None
    assert body["posted_by"] == user.id
    assert body["target_audience"] == (
        AnnouncementAudience.SYSTEM_WIDE.value
    )



# NOrmal user can not create ann
def test_create_university_announcement_permission_denied(
    client,
    auth_headers,
):
    user = UserFactory(
        role=UserRole.STUDENT,
    )

    headers = auth_headers(user.email)

    payload = {
        "title": "Unauthorized University Announcement",
        "body": "Should not be allowed.",
        "target_audience": AnnouncementAudience.UNIVERSITY_WIDE.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403

    assert response.get_json()["message"] == "Permission denied."



# WIthout club id
def test_create_announcement_without_club_id_invalid_audience(
    client,
    auth_headers,
):
    user = UserFactory(
        role=UserRole.STUDENT,
    )

    headers = auth_headers(user.email)

    payload = {
        "title": "Invalid Announcement",
        "body": "Missing club.",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }

    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "club_id is required for club announcements."
    )


# Authentication fails
def test_create_announcement_unauthorized(client):
    payload = {
        "title": "Test Announcement",
        "body": "Test body",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }

    response = client.post(
        "/api/announcements",
        json=payload,
    )

    assert response.status_code == 401


# Database error check
def test_get_stats_database_error(
    client,
    auth_headers,
    university_admin_user,
    db_error,
):
    db_error(ann_module)
    payload = {
        "title": "Test Announcement",
        "body": "Test body",
        "target_audience": AnnouncementAudience.ALL_MEMBERS.value,
    }
    headers = auth_headers(university_admin_user.email)
    response = client.post(
        "/api/announcements",
        headers=headers,
        json=payload
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]