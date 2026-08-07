from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.university_administration.university_admin  as university_admin_module


from datetime import datetime

def test_get_analytics_success(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    club1 = ClubFactory(
        university=university,
        category="Technical",
        created_at=datetime(2025, 1, 10),
    )

    club2 = ClubFactory(
        university=university,
        category="Technical",
        created_at=datetime(2025, 1, 20),
    )

    student = UserFactory(university=university)

    ClubMembershipFactory(
        club=club1,
        user=student,
        status=MembershipStatus.APPROVED,
        applied_at=datetime(2025, 2, 1),
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/analytics",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body["categoryDistribution"]) == 1
    assert body["categoryDistribution"][0]["category"] == "Technical"
    assert body["categoryDistribution"][0]["count"] == 2

    assert body["clubGrowth"][0]["month"] == "2025-01"
    assert body["clubGrowth"][0]["count"] == 2

    assert body["membershipGrowth"][0]["month"] == "2025-02"
    assert body["membershipGrowth"][0]["count"] == 1


# Analytics only include admin's/dean's university
from datetime import datetime

def test_get_analytics_filters_other_university(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    other = UniversityFactory()

    university_admin_user.university = university

    ClubFactory(
        university=university,
        category="Technical",
        created_at=datetime(2025, 1, 1),
    )

    ClubFactory(
        university=other,
        category="Sports",
        created_at=datetime(2025, 1, 1),
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/analytics",
        headers=headers,
    )

    body = response.get_json()

    assert len(body["categoryDistribution"]) == 1
    assert body["categoryDistribution"][0]["category"] == "Technical"


# Only approved membership are counted
from datetime import datetime

def test_get_analytics_only_approved_memberships(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    club = ClubFactory(
        university=university,
        created_at=datetime(2025, 1, 1),
    )

    student = UserFactory(university=university)

    ClubMembershipFactory(
        club=club,
        user=student,
        status=MembershipStatus.APPROVED,
        applied_at=datetime(2025, 2, 1),
    )

    ClubMembershipFactory(
        club=club,
        user=UserFactory(university=university),
        status=MembershipStatus.PENDING,
        applied_at=datetime(2025, 2, 1),
    )

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/analytics",
        headers=headers,
    )

    body = response.get_json()

    assert len(body["membershipGrowth"]) == 1
    assert body["membershipGrowth"][0]["count"] == 1


# Empty analytics
def test_get_analytics_empty(
    client,
    auth_headers,
    university_admin_user,
):
    university = UniversityFactory()
    university_admin_user.university = university

    headers = auth_headers(university_admin_user.email)

    response = client.get(
        "/api/university-admin/analytics",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["categoryDistribution"] == []
    assert body["clubGrowth"] == []
    assert body["membershipGrowth"] == []



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