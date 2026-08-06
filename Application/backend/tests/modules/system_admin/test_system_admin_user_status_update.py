# tests/modules/system_admin/test_change_user_status.py
import bcrypt
from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)
from app.database.models import User

# Test: Successfully deactivate a user
def test_change_user_status_success(client,auth_headers,system_admin_user,db_session):
    user = UserFactory(is_active=True)

    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        f"/api/admin/users/{user.id}/status",
        headers=headers,
        json={
            "status": False
        },
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "Status Changed."
    db_session.refresh(user)
    assert user.is_active is False

# Test: Activate an inactive user
def test_change_user_status_activate(client,auth_headers,system_admin_user,db_session):
    user = UserFactory(is_active=False)

    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        f"/api/admin/users/{user.id}/status",
        headers=headers,
        json={
            "status": True
        },
    )
    assert response.status_code == 200
    db_session.refresh(user)
    assert user.is_active is True


# Test: User not found
def test_change_user_status_user_not_found(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        "/api/admin/users/999999/status",
        headers=headers,
        json={
            "status": False
        },
    )
    assert response.status_code == 404
    assert "User not found." in response.get_json()["message"]

# Test : Missing query parameter - status
def test_change_user_status_missing_status(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    user = UserFactory()

    response = client.patch(
        f"/api/admin/users/{user.id}/status",
        headers=headers,
        json={},
    )
    assert response.status_code == 400
    assert "status is required." in response.get_json()['message']

# Test: Unauthorized request
def test_change_user_status_unauthorized(client):
    response = client.patch(
        "/api/admin/users/1/status",
        json={
            "status": False
        },
    )
    assert response.status_code == 401

# Test: Forbidden request (non-admin)
def test_change_user_status_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.patch(
        "/api/admin/users/1/status",
        headers=headers,
        json={
            "status": False
        },
    )
    assert response.status_code == 403


# Test: Database exception
def test_change_user_status_database_error(client,auth_headers,system_admin_user,monkeypatch):
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        "/api/admin/users/1/status",
        headers=headers,
        json={
            "status": False
        },
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]