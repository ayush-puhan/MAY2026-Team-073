from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.interests  as interest_module

def test_create_interest_success(
    client,
):
    response = client.post(
        "/api/interests",
        json={
            "name": "Sports"
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Sports"


def test_create_interest_missing_data(
    client,
):
    response = client.post(
        "/api/interests",
        json={},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Interest name is required"

def test_create_interest_missing_name(
    client,
):
    response = client.post(
        "/api/interests",
        json={
            "description": "Something"
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["message"] == "Interest name is required"


def test_create_interest_empty_name(
    client,
):
    response = client.post(
        "/api/interests",
        json={
            "name": ""
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Interest name is required"


def test_create_interest_duplicate(
    client,
):
    InterestFactory(
        name="Sports"
    )
    response = client.post(
        "/api/interests",
        json={
            "name": "Sports"
        },
    )
    assert response.status_code == 409
    body = response.get_json()
    assert body["message"] == "Interest already exists"

def test_create_interest_query_database_error(
    client,
    db_error
):
    db_error(interest_module)
    response = client.post(
        "/api/interests",
        json={
            "name": "Sports"
        },
    )

    assert response.status_code == 500

    body = response.get_json()

    assert body["messge"] == "Uncaught Error"