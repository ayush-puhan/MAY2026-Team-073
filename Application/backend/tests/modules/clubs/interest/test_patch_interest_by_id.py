from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.core.interests  as interest_module


def test_update_interest_success(
    client,auth_headers,active_user
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        headers=auth_headers(active_user.email),
        json={
            "name": "Football"
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == interest.id
    assert body["name"] == "Football"

def test_update_interest_not_found(
    client,auth_headers,active_user
):
    response = client.patch(
        "/api/interests/999999",
        headers=auth_headers(active_user.email),
        json={
            "name": "Football"
        },
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Interest not found"


def test_update_interest_name(
    client,auth_headers,active_user
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        headers=auth_headers(active_user.email),
        json={
            "name": "Music"
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["name"] == "Music"


def test_update_interest_empty_json(
    client,auth_headers,active_user
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        headers=auth_headers(active_user.email),
        json={},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert "Nothing to update" in body["message"] 


def test_update_interest_query_database_error(
    client,
    db_error,auth_headers,active_user
):
    db_error(interest_module)
    response = client.patch(
        "/api/interests/1",
        headers=auth_headers(active_user.email),
        json={
            "name": "Football"
        },
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]


def test_update_interest_empty_name_current_behavior(
    client,auth_headers,active_user
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        headers=auth_headers(active_user.email),
        json={
            "name": ""
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert "Interest name cannot be empty" in body["message"]