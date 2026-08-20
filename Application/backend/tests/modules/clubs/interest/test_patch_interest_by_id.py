from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.core.interests  as interest_module


def test_update_interest_success(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        json={
            "name": "Football"
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == interest.id
    assert body["name"] == "Football"

def test_update_interest_not_found(
    client,
):
    response = client.patch(
        "/api/interests/999999",
        json={
            "name": "Football"
        },
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Interest not found"


def test_update_interest_name(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        json={
            "name": "Music"
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["name"] == "Music"


def test_update_interest_empty_json(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        json={},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == interest.id
    assert body["name"] == "Sports"


def test_update_interest_ignores_unknown_fields(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        json={
            "description": "Outdoor activity",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == interest.id
    assert body["name"] == "Sports"



def test_update_interest_query_database_error(
    client,
    db_error,
):
    db_error(interest_module)
    response = client.patch(
        "/api/interests/1",
        json={
            "name": "Football"
        },
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]


def test_update_interest_empty_name_current_behavior(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.patch(
        f"/api/interests/{interest.id}",
        json={
            "name": ""
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["name"] == ""