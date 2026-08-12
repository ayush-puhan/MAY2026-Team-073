# tests/modules/faculty_advisor/test_event_decision.py
from app.database.enums import *
from db_factory.factory import *

# -------------------------------------------------------------------
# Test: Successfully approve an event
# -------------------------------------------------------------------
def test_event_approve_success(
    client,
    auth_headers,
    faculty_advisor_user,
    db_session
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    event = EventFactory(
        club=club,
        creator=faculty_advisor_user,
        status=EventStatus.PENDING_APPROVAL,
    )

    response = client.patch(
        f"/api/faculty/events/{event.id}/decision",
        headers=headers,
        json={
            "approval_status": "approved",
            "review_comments": "Looks good.",
            "reviewed_by": faculty_advisor_user.id,
        },
    )

    assert response.status_code == 200

    db_session.refresh(event)
    assert event.status == EventStatus.SCHEDULED

    body = response.get_json()
    assert body["created_by"] == faculty_advisor_user.id
    assert body["title"] == event.title


# -------------------------------------------------------------------
# Test: Reject an event
# -------------------------------------------------------------------
def test_event_reject_success(
    client,
    auth_headers,
    faculty_advisor_user,
    db_session,
):

    university = UniversityFactory()

    club1 = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    event = EventFactory(
        club=club1,
        creator=faculty_advisor_user,
        status=EventStatus.PENDING_APPROVAL,
    )

    headers = auth_headers(faculty_advisor_user.email)
    response = client.patch(
        f"/api/faculty/events/{event.id}/decision",
        headers=headers,
        json={
            "approval_status": EventStatus.REJECTED.value,
            "review_comments": "Looks not good.",
            "reviewed_by": faculty_advisor_user.id,
        },
    )

    assert response.status_code == 200

    db_session.refresh(event)
    assert event.status == EventStatus.REJECTED


# -------------------------------------------------------------------
# Test: Advisor cannot update another advisor's event
# -------------------------------------------------------------------
def test_event_decision_forbidden(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    another_advisor = UserFactory(role=UserRole.FACULTY_ADVISOR)
    university = UniversityFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=another_advisor,
    )

    event = EventFactory(
        club=club,
        creator=another_advisor,
    )

    response = client.patch(
        f"/api/faculty/events/{event.id}/decision",
        headers=headers,
        json={
            "approval_status": EventStatus.PENDING_APPROVAL.value,
        },
    )

    assert response.status_code == 403
    assert "Forbidden" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_event_decision_unauthorized(
    client,
):
    response = client.patch(
        "/api/faculty/events/1/decision",
        json={
            "approval_status": EventStatus.PENDING_APPROVAL.value,
        },
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Wrong role
# -------------------------------------------------------------------
def test_event_decision_wrong_role(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)

    response = client.patch(
        "/api/faculty/events/1/decision",
        headers=headers,
        json={
            "approval_status": EventStatus.PENDING_APPROVAL.value,
        },
    )

    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_event_decision_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    db_error,
):
    import app.modules.faculty.routes as faculty_module
    db_error(faculty_module)

    headers = auth_headers(faculty_advisor_user.email)

    response = client.patch(
        "/api/faculty/events/1/decision",
        headers=headers,
        json={
            "approval_status": EventStatus.PENDING_APPROVAL.value,
        },
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]