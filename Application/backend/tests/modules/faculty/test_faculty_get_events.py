# tests/modules/faculty_advisor/test_get_events.py
from app.database.enums import *
from db_factory.factory import *

# -------------------------------------------------------------------
# Test: Successfully retrieve pending approval events (default status)
# -------------------------------------------------------------------
def test_get_events_default_status(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    EventFactory(
        club=club,
        creator=faculty_advisor_user,
        title="Hackathon",
        status=EventStatus.PENDING_APPROVAL,
    )

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/events",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["title"] == "Hackathon"
    assert body[0]["club_name"] == club.name
    assert body[0]["status"] == EventStatus.PENDING_APPROVAL.value


# -------------------------------------------------------------------
# Test: Retrieve events using status query parameter
# -------------------------------------------------------------------
def test_get_events_by_status(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )


    EventFactory(
        club=club,
        creator=faculty_advisor_user,
        title="Completed Event",
        status=EventStatus.PENDING_APPROVAL,
    )

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/events?status=pending_approval",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["status"] == EventStatus.PENDING_APPROVAL.value


# -------------------------------------------------------------------
# Test: Advisor requesting another advisor's events
# -------------------------------------------------------------------
def test_get_events_forbidden(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)

    another_advisor = UserFactory(
        role=UserRole.FACULTY_ADVISOR,
    )

    response = client.get(
        f"/api/faculty/{another_advisor.id}/events",
        headers=headers,
    )

    assert response.status_code == 404
    assert "Forbidden" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: No events found
# -------------------------------------------------------------------
def test_get_events_empty(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/events",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_events_unauthorized(client):

    response = client.get(
        "/api/faculty/1/events",
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_get_events_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    db_error,
):
    import app.modules.faculty.routes as faculty_module
    db_error(faculty_module)
    headers = auth_headers(faculty_advisor_user.email)

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/events",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]