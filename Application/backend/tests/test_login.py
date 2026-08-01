from app.database.enums import UserRole
def test_login_success(client, active_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "active@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Login successful"
    assert "access_token" in body.keys()

    assert body["user"]["email"] == "active@example.com"
    assert body["user"]["full_name"] == "Active User"
    assert body["user"]["role"] == UserRole.STUDENT
    assert body["user"]["has_password"] is True



def test_login_wrong_password(client, active_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "active@example.com",
            "password": "wrongpassword",
        },
    )
    body = response.get_json()
    assert response.status_code == 401
    assert body["message"] == "Invalid credentials."


def test_login_unknown_email(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "Password@123",
        },
    )
    body = response.get_json()
    assert response.status_code == 401
    assert body["message"] == "Invalid credentials or inactive account."


def test_login_inactive_user(client, inactive_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "password123",
        },
    )
    body = response.get_json()
    assert response.status_code == 401
    assert body["message"] == "Invalid credentials or inactive account."


def test_login_missing_email(client):
    response = client.post(
        "/api/auth/login",
        json={
            "password": "password123",
        },
    )
    body = response.get_json()
    assert response.status_code == 400
    assert body["message"] == "Email and password are required."


def test_login_missing_password(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "john@example.com",
        },
    )
    body = response.get_json()
    assert response.status_code == 400
    assert body["message"] == "Email and password are required."


def test_login_empty_json(client):
    response = client.post(
        "/api/auth/login",
        json={},
    )
    body = response.get_json()
    assert response.status_code == 400
    assert body["message"] == "Email and password are required."