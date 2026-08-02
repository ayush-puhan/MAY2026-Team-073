def test_logout_success(client):
    response = client.post(
        "/api/auth/logout",
        headers={
            "Authorization": "Bearer test-token"
        }
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
    # If require_auth allows it through:
    assert response.status_code in (400, 401)
    assert response.get_json()["message"] == "Missig Bearer token"

    # Otherwise, require_auth may return 401 first.