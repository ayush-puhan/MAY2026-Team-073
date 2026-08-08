from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.application_routes  as club_application_module

def test_submit_club_application_success(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    club = ClubFactory(university=UniversityFactory())

    headers = auth_headers(student.email)
    payload = {
        "motivation": "I want to contribute to the club.",
        "contribution": "I can help with technical activities.",
        "previous_experience": "Worked on several software projects.",
        "skills": "Python, Flask, SQL",
        "portfolio_url": "https://example.com/portfolio",
        "resume_document_id": None,
        "weekly_availability": "5 hours",
    }

    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Application submitted successfully."

    application = body["application"]

    assert application["user_id"] == student.id
    assert application["club_id"] == club.id
    assert application["motivation"] == payload["motivation"]
    assert application["contribution"] == payload["contribution"]
    assert application["previous_experience"] == payload["previous_experience"]
    assert application["skills"] == payload["skills"]
    assert application["portfolio_url"] == payload["portfolio_url"]
    assert application["resume_document_id"] == payload["resume_document_id"]
    assert application["weekly_availability"] == payload["weekly_availability"]



# Request body missing
def test_submit_club_application_no_body(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    club = ClubFactory(university=UniversityFactory())

    headers = auth_headers(student.email)
    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json={}
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Request body required."

# Motivation is missing
def test_submit_club_application_missing_motivation(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    club = ClubFactory(university=UniversityFactory())

    headers = auth_headers(student.email)
    payload = {
        "contribution": "I can help with events.",
        "skills": "Python",
    }
    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing fields: motivation"

# Motivation is empty
def test_submit_club_application_empty_motivation(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)

    club = ClubFactory(university=UniversityFactory())

    headers = auth_headers(student.email)

    payload = {
        "motivation": "",
    }

    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Missing fields: motivation"


# Optional field can be ommitted
def test_submit_club_application_only_motivation(
    client,
    auth_headers,
):
    student = UserFactory(
        role=UserRole.STUDENT,
    )
    club = ClubFactory(university=UniversityFactory())

    headers = auth_headers(student.email)

    payload = {
        "motivation": "I would like to join this club.",
    }

    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Application submitted successfully."

    application = body["application"]

    assert application["user_id"] == student.id
    assert application["club_id"] == club.id
    assert application["motivation"] == payload["motivation"]

    assert application["contribution"] is None
    assert application["previous_experience"] is None
    assert application["skills"] is None
    assert application["portfolio_url"] is None
    assert application["resume_document_id"] is None
    assert application["weekly_availability"] is None


# Non student can not submit application
def test_submit_club_application_forbidden_for_non_student(
    client,
    auth_headers,
):
    user = UserFactory(role=UserRole.FACULTY_ADVISOR)
    club = ClubFactory(university=UniversityFactory())

    headers = auth_headers(user.email)
    payload = {
        "motivation": "I want to join the club.",
    }
    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403


# UnAuthenticated users can not
def test_submit_club_application_unauthorized(
    client,
):
    club = ClubFactory(university=UniversityFactory())

    response = client.post(
        f"/api/clubs/{club.id}/applications",
        json={
            "motivation": "I want to join this club.",
        },
    )
    assert response.status_code == 401

# database error
# Database error handelling check
def test_get_database_error(
    client,
    auth_headers,
    db_error,
):
    import app.modules.club_leadership.application_routes  as club_application_module
    user = UserFactory()
    club = ClubFactory(university=UniversityFactory())
    db_error(club_application_module)
    headers = auth_headers(user.email)
    payload = {
        "motivation": "I want to join the club.",
    }
    response = client.post(
        f"/api/clubs/{club.id}/applications",
        headers=headers,
        json=payload
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]