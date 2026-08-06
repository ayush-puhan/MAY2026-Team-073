# tests/modules/system_admin/test_delete_user.py
import bcrypt
from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)
from app.database.models import User


# -------------------------------------------------------------------
# Test: Successfully soft delete a user
# -------------------------------------------------------------------
def test_delete_user_success(client,auth_headers,system_admin_user,db_session):
    user = UserFactory(
        is_active=True,
        deleted_at=None,
    )
    headers = auth_headers(system_admin_user.email)
    response = client.delete(
        f"/api/admin/users/{user.id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert "User deleted." in response.get_json()["message"]
    db_session.refresh(user)
    updated_user = db_session.query(User).filter_by(id=user.id).first()
    assert user is not None
    assert user.full_name == updated_user.full_name
    assert user.email == updated_user.email
    assert user.is_active is False and user.is_active == updated_user.is_active
    assert user.deleted_at is not None and user.deleted_at == updated_user.deleted_at


# -------------------------------------------------------------------
# Test: User not found
# -------------------------------------------------------------------
def test_delete_user_not_found(client,auth_headers,system_admin_user,):
    headers = auth_headers(system_admin_user.email)
    response = client.delete(
        "/api/admin/users/999999",
        headers=headers,
    )
    assert response.status_code == 404
    assert "No user found with the provided id" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_delete_user_unauthorized(client):
    response = client.delete(
        "/api/admin/users/1",
    )
    assert response.status_code == 401

# -------------------------------------------------------------------
# Test: Forbidden request (non-admin)
# -------------------------------------------------------------------
def test_delete_user_forbidden(client,auth_headers,student_user,):
    headers = auth_headers(student_user.email)
    response = client.delete(
        "/api/admin/users/1",
        headers=headers,
    )
    assert response.status_code == 403

# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_delete_user_database_error(client,auth_headers,system_admin_user,monkeypatch,):
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session,
    )
    headers = auth_headers(system_admin_user.email)
    response = client.delete(
        "/api/admin/users/1",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]