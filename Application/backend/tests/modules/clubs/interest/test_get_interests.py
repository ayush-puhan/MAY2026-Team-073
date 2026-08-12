from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.core.interests  as interest_module

def test_get_interests_success(
    client,
):
    InterestFactory(name="Sports")
    InterestFactory(name="Music")
    InterestFactory(name="Technology")

    response = client.get(
        "/api/interests"
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 3

    assert [item["name"] for item in body] == [
        "Music",
        "Sports",
        "Technology",
    ]

def test_get_interests_empty(
    client,
):
    response = client.get(
        "/api/interests"
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []


def test_get_interests_ordered_by_name(
    client,
):
    InterestFactory(name="Zoology")
    InterestFactory(name="Art")
    InterestFactory(name="Music")
    InterestFactory(name="Biology")

    response = client.get(
        "/api/interests"
    )
    assert response.status_code == 200
    body = response.get_json()
    names = [item["name"] for item in body]
    assert names == [
        "Art",
        "Biology",
        "Music",
        "Zoology",
    ]


def test_get_interests_database_error(
    client,
    db_error
):
    db_error(interest_module)
    response = client.get(
        "/api/interests"
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]