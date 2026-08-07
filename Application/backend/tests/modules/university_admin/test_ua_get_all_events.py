from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module


# get all events
def test_get_all_events_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university
    event_creator = UserFactory(role=UserRole.STUDENT,university=university)
    club = ClubFactory(
        university=university,
        name="Coding Club",
    )

    event = EventFactory(
        club=club,
        creator=event_creator,
        title="Hackathon",
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/events",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == event.id
    assert body[0]["club_id"] == club.id
    assert body[0]["club_name"] == club.name
    assert body[0]["title"] == event.title

# ONlly return events of university admin's university
def test_get_all_events_filters_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    other_university = UniversityFactory()
    own_event_creator = UserFactory(role=UserRole.STUDENT,university=university)
    other_event_creator = UserFactory(role=UserRole.STUDENT,university=other_university)
    university_admin_user.university = university

    own_club = ClubFactory(university=university)
    other_club = ClubFactory(university=other_university)

    own_event = EventFactory(club=own_club,creator=own_event_creator,)
    EventFactory(club=other_club,creator=other_event_creator,)

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/events",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == own_event.id


# Returned event are ordered
from datetime import datetime, timedelta
def test_get_all_events_ordered_by_start_at(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    club = ClubFactory(university=university)
    event_creator = UserFactory(role=UserRole.STUDENT,university=university)
    old_event = EventFactory(
        club=club,
        start_at=datetime.utcnow() - timedelta(days=1),
        creator=event_creator
    )

    new_event = EventFactory(
        club=club,
        start_at=datetime.utcnow(),
        creator=event_creator
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/events",
        headers=headers,
    )

    body = response.get_json()

    assert body[0]["id"] == new_event.id
    assert body[1]["id"] == old_event.id


# Return empty list when no events present
def test_get_all_events_empty(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/events",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# Authentication
def test_get_all_ua_clubs_unauthorized(
    client,
):
    response = client.get(
        "/api/university-admin/clubs",
    )

    assert response.status_code == 401

# Forbidden
def test_get_all_ua_clubs_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)

    headers = auth_headers(student.email)

    response = client.get(
        "/api/university-admin/clubs",
        headers=headers,
    )

    assert response.status_code == 403



# 6. Database error
def test_get_stats_database_error(
    client,
    auth_headers,
    university_admin_user,
    db_error,
):
    db_error(university_admin_module)
    headers = auth_headers(university_admin_user.email)
    response = client.get(
        "/api/university-admin/stats",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]