import bcrypt
from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)
from app.database.models import User

# 1. Successfull User creation
def test_admin_create_user_success(client,auth_headers,system_admin_user,monkeypatch,db_session):
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.send_email",
        lambda *args, **kwargs: None,
    )
    university = UniversityFactory()

    headers = auth_headers(system_admin_user.email)
    response = client.post(
        "/api/admin/users",
        headers=headers,
        json={
            "full_name": "John Doe",
            "email": "john@test.com",
            "role": "STUDENT",
            "university_id": university.id,
        },
    )
    body = response.get_json()
    assert response.status_code == 201
    assert body["message"] == "User created successfully"
    assert body["email"] == "john@test.com"
    assert body["password"] == "Password@123"

    user = db_session.query(User).filter_by(email=body["email"]).first()
    assert user is not None
    assert user.email == body["email"]
    assert user.role == "student"
    assert user.password_hash is not None
    assert user.password_hash != body['password']

# 2. User already exists and active
def test_admin_create_user_existing_active(client,auth_headers,system_admin_user,):
    UserFactory(
        email="john@test.com",
        is_active=True,
    )
    headers = auth_headers(system_admin_user.email)
    response = client.post(
        "/api/admin/users",
        headers=headers,
        json={
            "full_name": "John Doe",
            "email": "john@test.com",
            "role": "STUDENT",
        },
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "User with this email already exists."

# 3. Existing inactive user updated
def test_admin_create_user_updates_inactive_user(client,auth_headers,system_admin_user,db_session):
    user = UserFactory(
        email="inactive@test.com",
        full_name="Old Name",
        is_active=False,
    )
    headers = auth_headers(system_admin_user.email)
    response = client.post(
        "/api/admin/users",
        headers=headers,
        json={
            "full_name": "New Name",
            "email": "inactive@test.com",
            "role": "STUDENT",
        },
    )
    assert response.status_code == 201
    db_session.refresh(user)

    assert user.full_name == "New Name"
    assert user.email == "inactive@test.com"
    

# 4. Unauthorized and forbidden
def test_admin_create_user_unauthorized(client):
    response = client.post(
        "/api/admin/users",
        json={},
    )
    assert response.status_code == 401

def test_admin_create_user_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.post(
        "/api/admin/users",
        headers=headers,
        json={},
    )
    assert response.status_code == 403


## 5. DataBase Exception
def test_admin_create_user_database_error(client,auth_headers,system_admin_user,monkeypatch):
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    
    headers = auth_headers(system_admin_user.email)
    response = client.post(
        "/api/admin/users",
        headers=headers,
        json={},
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]