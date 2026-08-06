from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory
)
from datetime import datetime

#1. Successful analytics retrieval (default month)
def test_get_platform_analytics_month(client,auth_headers,system_admin_user,):

    UserFactory(created_at=datetime(2026, 1, 10))
    UserFactory(created_at=datetime(2026, 1, 15))
    UserFactory(created_at=datetime(2026, 2, 1))

    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/analytics",
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 200
    assert "growth" in data
    assert data["growth"]["2026-01"] == 2
    assert data["growth"]["2026-02"] == 1

# 2. Year wise analytics
def test_get_platform_analytics_year(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)

    UserFactory(created_at=datetime(2020, 5, 1))
    UserFactory(created_at=datetime(2030, 3, 1))
    UserFactory(created_at=datetime(2030, 4, 1))

    response = client.get(
        "/api/admin/analytics?range=year",
        headers=headers,
    )
    growth = response.get_json()["growth"]
    assert response.status_code == 200
    assert growth["2020"] == 1
    assert growth["2030"] == 2 

# 3. Week wise analysis
def test_get_platform_analytics_week(
    client,
    auth_headers,
    system_admin_user,
):
    headers = auth_headers(system_admin_user.email)

    UserFactory(created_at=datetime(2030, 1, 5))
    UserFactory(created_at=datetime(2030, 1, 6))
    UserFactory(created_at=datetime(2030, 1, 20))

    response = client.get(
        "/api/admin/analytics?range=week",
        headers=headers,
    )

    assert response.status_code == 200
    assert "growth" in response.get_json()


# 4. Unauthorized and forbidden
def test_get_platform_analytics_unauthorized(client):
    response = client.get("/api/admin/analytics")
    assert response.status_code == 401
def test_get_platform_analytics_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.get(
        "/api/admin/analytics",
        headers=headers,
    )
    assert response.status_code == 403

# 5. DB Error 
def test_get_admin_stats_database_error(client,auth_headers,system_admin_user,monkeypatch):
    def broken_session():
        raise Exception("Database failure")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/analytics",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database failure" in response.get_json()["message"]