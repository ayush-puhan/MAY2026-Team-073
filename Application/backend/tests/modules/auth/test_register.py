from app.database.enums import UserRole
from app.database.models.auth import UserOTP,User
def test_register_success(client, db_session):

    response = client.post(
        "/api/auth/register",
        json={
            "email": "john@example.com",
            "password": "password123",
            "full_name": "John Doe"
        }
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "OTP sent successfully."

    user = db_session.query(User).filter_by(
        email="john@example.com"
    ).first()

    assert user is not None
    assert user.full_name == "John Doe"
    assert user.is_active is False
    assert user.email_verified is False

    otp = db_session.query(UserOTP).filter_by(
        user_id=user.id
    ).first()

    assert otp is not None


def test_register_missing_email(client):

    response = client.post(
        "/api/auth/register",
        json={
            "password": "Password@123",
            "full_name": "John"
        }
    )

    assert response.status_code == 400


def test_register_missing_password(client):

    response = client.post(
        "/api/auth/register",
        json={
            "email": "john@example.com",
            "full_name": "John"
        }
    )

    assert response.status_code == 400


def test_register_missing_name(client):

    response = client.post(
        "/api/auth/register",
        json={
            "email": "john@example.com",
            "password": "Password@123"
        }
    )

    assert response.status_code == 400


def test_register_existing_active_user(client, active_user):

    response = client.post(
        "/api/auth/register",
        json={
            "email": "active@example.com",
            "password": "Password@123",
            "full_name": "Someone"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "User with this email already exists."



def test_register_existing_inactive_user(client,db_session,inactive_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "inactive@example.com",
            "password": "newpassword",
            "full_name": "New Name"
        }
    )

    assert response.status_code == 201

    db_session.refresh(inactive_user)

    assert inactive_user.full_name == "New Name"
    assert inactive_user.is_active is False

    otp = db_session.query(UserOTP).filter_by(
        user_id=inactive_user.id
    ).first()

    assert otp is not None