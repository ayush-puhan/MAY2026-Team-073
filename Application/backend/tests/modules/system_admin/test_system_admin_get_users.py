from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory,
    DepartmentFactory
)

# 1. Successfully retrieve users
def test_get_all_users_success(client,auth_headers,system_admin_user):
    UserFactory(
        full_name="Alice",
        email="alice@test.com",
    )
    UserFactory(
        full_name="Bob",
        email="bob@test.com",
    )
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/users",
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) >= 2

    user = data[0]

    assert "id" in user
    assert "full_name" in user
    assert "email" in user
    assert "role" in user
    assert "is_active" in user
    assert "created_at" in user
    assert "department" in user
    assert "university_name" in user
    assert "roll_number" in user

# 2. Empty Users list
def test_get_all_users_without_department_or_university(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    user = UserFactory(
        university=None,
        department=None,
    )
    response = client.get(
        "/api/admin/users",
        headers=headers,
    )
    print(user)
    assert response.status_code == 200
    found = next(
        u for u in response.get_json() if u["id"] == user.id
    )
    assert found["department"] is None
    assert found["university_name"] is None

#3. Unauthorized
def test_get_all_users_with_unauthorized_access(client):
    response = client.get("/api/admin/users")
    assert response.status_code == 401

# 4. Forbidden
def test_get_all_users_forbidden_access(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.get(
        "/api/admin/users",
        headers=headers,
    )
    assert response.status_code == 403

# 5. DataBase Exception Test
def test_get_all_users_database_error_handeling(client,auth_headers,system_admin_user,monkeypatch):
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    
    headers = auth_headers(system_admin_user.email)
    response = client.post(
        "/api/admin/audit-logs",
        headers=headers,
        json={
            "action": "CREATE",
            "entity_type": "CLUB",
            "entity_id": 1,
        },
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]


# 6. Outer join success test
def test_get_all_users_with_department_and_university(client,auth_headers,system_admin_user):
    university = UniversityFactory(name="IIT Madras")
    department = DepartmentFactory(
        university=university,
        name="Computer Science",
    )
    user = UserFactory(
        university=university,
        department=department,
    )

    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/users",
        headers=headers,
    )
    data = response.get_json()
    found = next(
        u for u in data if u["id"] == user.id
    )
    assert found["university_name"] == "IIT Madras"
    assert found["department"] == "Computer Science"
