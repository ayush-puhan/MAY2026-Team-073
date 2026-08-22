from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.core.interests  as interest_module


def test_get_interest_success(
    client,active_user,auth_headers
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.get(
        f"/api/interests/{interest.id}",
        headers=auth_headers(active_user.email)
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == interest.id
    assert body["name"] == "Sports"



def test_get_interest_not_found(
    client,active_user,auth_headers
):
    response = client.get(
        "/api/interests/999999",
        headers=auth_headers(active_user.email)
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Interest not found"


def test_get_interest_database_error(
    client,
    db_error,active_user,auth_headers
):
    
    db_error(interest_module)
    response = client.get(
        "/api/interests/1",
        headers=auth_headers(active_user.email)
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]


