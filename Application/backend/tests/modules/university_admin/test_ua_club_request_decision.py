from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module

# Approve club req
def test_decide_club_request_approve(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university
    advisor = UserFactory(
        university=university,
        role=UserRole.FACULTY_ADVISOR,
    )
    student = UserFactory(university=university)
    club_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED,
    )
    headers = auth_headers(university_admin_user.email)
    payload = {
        "status": ClubRequestStatus.APPROVED.value,
        "reviewed_by": university_admin_user.id,
        "review_comments": "Approved",
        "faculty_advisor_id": advisor.id,
    }
    response = client.patch(
        f"/api/university-admin/club-requests/{club_request.id}/decision",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == f"Request {payload['status']}"
    assert body["club_id"] is not None


# 2. Reject request
def test_decide_club_request_reject(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university
    student = UserFactory(university=university)
    club_request = ClubCreationRequestFactory(
        requester=student,
        status=ClubRequestStatus.SUBMITTED,
    )

    headers = auth_headers(university_admin_user.email)
    payload = {
        "status": ClubRequestStatus.REJECTED.value,
        "reviewed_by": university_admin_user.id,
        "review_comments": "Duplicate request",
        "faculty_advisor_id": None,
    }
    response = client.patch(
        f"/api/university-admin/club-requests/{club_request.id}/decision",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == f"Request {payload['status']}"
    assert body["club_id"] is None

# 3. Request not found
def test_decide_club_request_not_found(
    client,
    auth_headers,
    university_admin_user,
):
    headers = auth_headers(university_admin_user.email)
    payload = {
        "status": ClubRequestStatus.APPROVED.value,
        "reviewed_by": university_admin_user.id,
    }
    response = client.patch(
        "/api/university-admin/club-requests/99999/decision",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Required Resource not found or empty resource"


# 4. Unothrized
def test_decide_club_request_unauthorized(client):
    response = client.patch(
        "/api/university-admin/club-requests/1/decision",
        json={},
    )
    assert response.status_code == 401

# 5. Forbidden
def test_decide_club_request_forbidden(
    client,
    auth_headers,
):
    student = UserFactory(role=UserRole.STUDENT)
    headers = auth_headers(student.email)
    response = client.patch(
        "/api/university-admin/club-requests/1/decision",
        headers=headers,
        json={},
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