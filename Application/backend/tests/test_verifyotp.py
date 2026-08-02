from app.database.models.auth import UserOTP
def test_verify_otp_success(client, db_session, inactive_user_with_otp):

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "user@example.com",
            "otp_code": "123456"
        }
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Email verified successfully."
    assert body["token"] == "test-token"

    db_session.refresh(inactive_user_with_otp)

    assert inactive_user_with_otp.is_active is True
    assert inactive_user_with_otp.email_verified is True

    otp = db_session.query(UserOTP).filter_by(
        user_id=inactive_user_with_otp.id
    ).first()

    assert otp is None

def test_verify_otp_missing_email(client):
    response = client.post(
        "/api/auth/verify-otp",
        json={
            "otp_code": "123456"
        }
    )

    assert response.status_code == 400


def test_verify_otp_missing_code(client):
    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "user@example.com"
        }
    )

    assert response.status_code == 400

def test_verify_otp_unknown_user(client):
    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "unknown@example.com",
            "otp_code": "123456"
        }
    )

    assert response.status_code == 404


def test_verify_otp_already_verified(client, active_user):
    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "active@example.com",
            "otp_code": "123456"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "User is already verified and active."


def test_verify_otp_invalid_code(client, inactive_user_with_otp):

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "user@example.com",
            "otp_code": "999999"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Invalid OTP code."


def test_verify_otp_expired(client, expired_otp_user):

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "expired@example.com",
            "otp_code": "123456"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "OTP has expired. Please request a new one."


