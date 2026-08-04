import bcrypt
import pytest

@pytest.fixture
def auth_headers(client, active_user):
    # Login using the test user
    response = client.post(
        "/api/auth/login",
        json={
            "email": active_user.email,
            "password": "Password@123"  
        },
    )
    print(response.status_code)
    print(response.get_json())  
    assert response.status_code == 200

    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }



@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    monkeypatch.setattr(
        "app.modules.auth.auth_routes.send_otp_email",
        lambda *args, **kwargs: None
    )


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    monkeypatch.setattr(
        "app.modules.auth.auth_routes.send_welcome_email",
        lambda *args, **kwargs: None
    )

    



"""@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    # Pretend the JWT is structurally valid
    monkeypatch.setattr(
        "app.middleware.auth_middleware.verify_jwt_in_request",   # replace with your module
        lambda: None
    )

    # Pretend the token exists in AuthSession
    monkeypatch.setattr(
        "app.middleware.auth_middleware.validate_stored_token",   # replace with your module
        lambda token: True
    )

    # Mock logout
    monkeypatch.setattr(
        "app.modules.auth.auth_routes.delete_token",   # Replace with your module
        lambda token: True
    )

    monkeypatch.setattr(
        "app.modules.auth.auth_routes.generate_and_store_token",
        lambda user_id, session=None: "test-token"
    )"""
