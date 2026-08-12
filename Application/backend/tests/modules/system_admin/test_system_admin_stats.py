from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory
)


# 1. Successful request
def test_get_admin_stats_success(client, auth_headers, system_admin_user):
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/stats",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "totalUsers" in body
    assert "activeUsers" in body
    assert "totalClubs" in body
    assert "totalEvents" in body
    assert "openTickets" in body
    assert "userTrend" in body
    assert "eventsTrend" in body
    assert "ticketsTrend" in body

# 2.No token Unauthorized
def test_get_admin_stats_unauthorized(client):
    response = client.get("/api/admin/stats")
    assert response.status_code == 401

# 3.Forbidden
def test_get_admin_stats_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.get(
        "/api/admin/stats",
        headers=headers,
    )
    assert response.status_code == 403

# 4.Database exception
def test_get_admin_stats_database_error(client,auth_headers,system_admin_user,monkeypatch):

    def broken_session():
        raise Exception("Database failure")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/stats",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database failure" in response.get_json()["message"]

# 5. Verify returned statistics
def test_get_admin_stats_counts(client,auth_headers,system_admin_user):
    user = UserFactory()
    user_in_active = UserFactory(is_active=False)
    university=UniversityFactory()
    club = ClubFactory(university=university)
    event = EventFactory(creator=user,club=club)
    st = SupportTicketFactory(raised_by_user=user,university=university)

    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/stats",
        headers=headers,
    )
    body = response.get_json()

    assert body["totalUsers"] == 3
    assert body["activeUsers"] == 2
    assert body["totalClubs"] == 1
    assert body["totalEvents"] == 1
    assert body["openTickets"] == 1












