import bcrypt
import pytest

@pytest.fixture
def auth_headers(client):
    def _auth_headers(email, password="Password@123"):
        response = client.post(
            "/api/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )
        body = response.get_json()
        assert response.status_code == 200

        return {
            "Authorization": f"Bearer {body['access_token']}"
        }

    return _auth_headers



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
