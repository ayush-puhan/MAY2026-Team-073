from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory,
    DepartmentFactory
)
from app.database.models import User


# Test: Successfully retrieve a user by ID
def test_get_user_by_id_success(client,auth_headers,system_admin_user):
    university = UniversityFactory(name="IIT Madras")
    department = DepartmentFactory(
        name="Computer Science",
        university=university,
    )
    user = UserFactory(
        full_name="John Doe",
        email="john@test.com",
        role=UserRole.STUDENT,
        university=university,
        department=department,
    )

    headers = auth_headers(system_admin_user.email)
    response = client.get(
        f"/api/admin/users/{user.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == user.id
    assert body['role'] == 'student'
    assert body["full_name"] == "John Doe"
    assert body["email"] == "john@test.com"
    assert body["department"] == "Computer Science"
    assert body["university_name"] == "IIT Madras"



# Test: Retrieve user without department/university
# Verifies outerjoin() works correctly.
def test_get_user_by_id_without_department_or_university(client,auth_headers,system_admin_user,):
    user = UserFactory(
        university=None,
        department=None,
    )
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        f"/api/admin/users/{user.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == user.id
    assert body["department"] is None
    assert body["university_name"] is None

# Test: Unauthorized request (no JWT)
def test_get_user_by_id_unauthorized(client):
    response = client.get("/api/admin/users/1")
    assert response.status_code == 401

# Test: Forbidden request (non-system admin)
def test_get_user_by_id_forbidden(client,auth_headers,student_user,):
    headers = auth_headers(student_user.email)
    response = client.get(
        "/api/admin/users/1",
        headers=headers,
    )
    assert response.status_code == 403



# Test: User does not exist
def test_get_user_by_id_not_found(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/users/999999",
        headers=headers,
    )
    assert response.status_code == 404
    assert "User not found." in response.get_json()["message"]



# Test: Database exception
def test_get_user_by_id_database_error(client,auth_headers,system_admin_user,monkeypatch):
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/users/1",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]