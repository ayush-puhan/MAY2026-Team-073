from app.database.enums import *
from db_factory.factory import *
from app.database.models import *


# 1. Get all announcements
def test_get_announcements_success(
    client,
    auth_headers
):
    university = UniversityFactory()
    user = UserFactory(university=university)
    club = ClubFactory(university=university)
    announcement1 = AnnouncementFactory(
        club = club,
        poster=user,
        target_audience=AnnouncementAudience.UNIVERSITY_WIDE,
    )

    announcement2 = AnnouncementFactory(
        club=club,
        poster=user,
        target_audience=AnnouncementAudience.SYSTEM_WIDE,
    )

    headers = auth_headers(user.email)

    response = client.get(
        "/api/announcements",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2
    assert body[0]["id"] == announcement2.id
    assert body[1]["id"] == announcement1.id


# Filter announjcement by club id
def test_get_announcements_by_club(
    client,
    auth_headers,
):
    university = UniversityFactory()
    user = UserFactory(university=university)
    club1 = ClubFactory(university=university)
    club2 = ClubFactory(university=university)

    announcement1 = AnnouncementFactory(
        club=club1,
        poster=user,
        target_audience=AnnouncementAudience.ALL_MEMBERS,
    )

    AnnouncementFactory(
        club=club2,
        poster=user,
        target_audience=AnnouncementAudience.ALL_MEMBERS,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/announcements?club_id={club1.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == announcement1.id
    assert body[0]["club_id"] == club1.id



# Filter announcement
def test_get_university_announcements(
    client,
    auth_headers,
):
    university = UniversityFactory()
    user = UserFactory(university=university)
    university_announcement = AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.UNIVERSITY_WIDE,
    )

    system_announcement = AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.SYSTEM_WIDE,
    )

    all_members_announcement = AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.ALL_MEMBERS,
    )

    AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.COMMITTEE,
    )

    headers = auth_headers(user.email)

    response = client.get(
        "/api/announcements?type=university",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    ids = {item["id"] for item in body}

    assert ids == {
        university_announcement.id,
        system_announcement.id,
        all_members_announcement.id,
    }

# Filter system announcement
def test_get_system_announcements(
    client,
    auth_headers,
):
    user = UserFactory()

    system_announcement = AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.SYSTEM_WIDE,
    )

    AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.UNIVERSITY_WIDE,
    )

    AnnouncementFactory(
        poster=user,
        target_audience=AnnouncementAudience.ALL_MEMBERS,
    )

    headers = auth_headers(user.email)

    response = client.get(
        "/api/announcements?type=system",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == system_announcement.id
    assert (
        body[0]["target_audience"]
        == AnnouncementAudience.SYSTEM_WIDE.value
    )

# Empty result
def test_get_announcements_empty(
    client,
    auth_headers,
):
    user = UserFactory()

    headers = auth_headers(user.email)

    response = client.get(
        "/api/announcements?club_id=99999",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# serialize fields
def test_get_announcement_serialization(
    client,
    auth_headers,
):
    user = UserFactory()
    university = UniversityFactory()
    club = ClubFactory(university=university)

    announcement = AnnouncementFactory(
        club=club,
        poster=user,
        title="Important Announcement",
        body="This is an important announcement.",
        target_audience=AnnouncementAudience.UNIVERSITY_WIDE,
    )

    headers = auth_headers(user.email)

    response = client.get(
        f"/api/announcements?club_id={club.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1

    item = body[0]

    assert item["id"] == announcement.id
    assert item["club_id"] == announcement.club_id
    assert item["posted_by"] == announcement.posted_by
    assert item["title"] == announcement.title
    assert item["body"] == announcement.body
    assert (
        item["target_audience"]
        == announcement.target_audience.value
    )
    assert item["created_at"] == announcement.created_at.isoformat()


# Unauthenticated
def test_get_announcements_unauthorized(client):
    response = client.get(
        "/api/announcements",
    )

    assert response.status_code == 401

# Database error
# Database error check
def test_get_stats_database_error(
    client,
    auth_headers,
    university_admin_user,
    db_error,
):
    import app.modules.announcements.routes  as ann_module
    db_error(ann_module)
    headers = auth_headers(university_admin_user.email)
    response = client.get(
        "/api/announcements",
        headers=headers
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]