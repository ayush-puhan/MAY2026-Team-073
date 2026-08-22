from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.core.interests  as interest_module

def test_create_interest_success(
    client,auth_headers,active_user
):
    response = client.post(
        "/api/interests",
        headers=auth_headers(active_user.email),
        json={
            "name": "Sports"
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Sports"


def test_create_interest_missing_data(
    client,auth_headers,active_user
):
    response = client.post(
        "/api/interests",
        headers=auth_headers(active_user.email),
        json={},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Interest name is required"

def test_create_interest_missing_name(
    client,auth_headers,active_user
):
    response = client.post(
        "/api/interests",
        headers=auth_headers(active_user.email),
        json={
            "description": "Something"
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Interest name is required"


def test_create_interest_empty_name(
    client,auth_headers,active_user
):
    response = client.post(
        "/api/interests",
        headers=auth_headers(active_user.email),
        json={
            "name": ""
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Interest name is required"


def test_create_interest_duplicate(
    client,auth_headers,active_user
):
    InterestFactory(
        name="Sports"
    )
    response = client.post(
        "/api/interests",
        headers=auth_headers(active_user.email),
        json={
            "name": "Sports"
        },
    )
    assert response.status_code == 409
    body = response.get_json()
    assert body["message"] == "Interest already exists"

def test_create_interest_query_database_error(
    client,
    db_error,auth_headers,active_user
):
    db_error(interest_module)
    response = client.post(
        "/api/interests",
        headers=auth_headers(active_user.email),
        json={
            "name": "Sports"
        },
    )

    assert response.status_code == 500

    body = response.get_json()

    assert "Database Error" in body["message"]