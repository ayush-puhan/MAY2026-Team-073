# tests/modules/system_admin/test_change_user_role.py
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
# Test: Successfully change user role
# -------------------------------------------------------------------
def test_change_user_role_success(client,auth_headers,system_admin_user,db_session):
    user = UserFactory(role=UserRole.STUDENT)

    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        f"/api/admin/users/{user.id}/role",
        headers=headers,
        json={
            "role": UserRole.FACULTY_ADVISOR.value
        },
    )
    assert response.status_code == 200
    assert "Status Changed." in response.get_json()["message"]
    db_session.refresh(user)
    assert user.role == UserRole.FACULTY_ADVISOR


# Test: Missing role field
def test_change_user_role_missing_role(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)

    user = UserFactory()

    response = client.patch(
        f"/api/admin/users/{user.id}/role",
        headers=headers,
        json={},
    )

    assert response.status_code == 400
    assert "role is required." in response.get_json()["message"]


# Test: User not found
def test_change_user_role_user_not_found(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        "/api/admin/users/999999/role",
        headers=headers,
        json={
            "role": UserRole.STUDENT.value
        },
    )
    assert response.status_code == 404
    assert "No user found with the provided id" in response.get_json()["message"] 


# Test: Unauthorized request
def test_change_user_role_unauthorized(client):
    response = client.patch(
        "/api/admin/users/1/role",
        json={
            "role": UserRole.STUDENT.value
        },
    )
    assert response.status_code == 401


# Test: Forbidden request (non-admin)
def test_change_user_role_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.patch(
        "/api/admin/users/1/role",
        headers=headers,
        json={
            "role": UserRole.SYSTEM_ADMIN.value
        },
    )
    assert response.status_code == 403

# Test: Database exception
def test_change_user_role_database_error(client,auth_headers,system_admin_user,monkeypatch,):
    headers = auth_headers(system_admin_user.email)

    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session,
    )
    response = client.patch(
        "/api/admin/users/1/role",
        headers=headers,
        json={
            "role": UserRole.STUDENT.value
        },
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]