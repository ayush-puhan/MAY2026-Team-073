from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.interests  as interest_module

def test_delete_interest_success(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    response = client.delete(
        f"/api/interests/{interest.id}"
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == (
        "Interest deleted successfully"
    )


def test_delete_interest_not_found(
    client,
):
    response = client.delete(
        "/api/interests/999999"
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Interest not found"


def test_delete_interest_query_database_error(
    client,
    db_error,
):
    db_error(interest_module)
    response = client.delete(
        "/api/interests/1"
    )
    assert response.status_code == 500
    body = response.get_json()
    assert "Database Error" in body["message"]



def test_delete_interest_record_removed(
    client,
):
    interest = InterestFactory(
        name="Sports"
    )
    interest_id = interest.id
    delete_response = client.delete(
        f"/api/interests/{interest_id}"
    )
    assert delete_response.status_code == 200
    get_response = client.get(
        f"/api/interests/{interest_id}"
    )
    assert get_response.status_code == 404
    body = get_response.get_json()
    assert body["message"] == "Interest not found"