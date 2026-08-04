def test_logout_success(client, auth_headers):
    response = client.post(
        "/api/auth/logout",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "Successfully logged out."


def test_logout_missing_header(client):
    response = client.post("/api/auth/logout")

    # If require_auth blocks the request:
    assert response.status_code in (400, 401)

def test_logout_invalid_header(client):
    response = client.post(
        "/api/auth/logout",
        headers={
            "Authorization": "Token abc123"
        }
    )
    assert response.status_code in (400, 401)
    assert "Authentication failed" in response.get_json()["message"]
