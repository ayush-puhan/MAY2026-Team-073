from app.database.models.auth import UserOTP
from datetime import datetime, timedelta

def test_resend_otp_success(client, db_session, inactive_user):
    old_otp = UserOTP(
        user_id=inactive_user.id,
        otp_code="111111",
        expires_at=datetime.utcnow() + timedelta(minutes=1)
    )

    db_session.add(old_otp)
    db_session.commit()

    response = client.post(
        "/api/auth/resend-otp",
        json={
            "email": "inactive@example.com"
        }
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == \
        "A new OTP has been sent to your email."

    otps = db_session.query(UserOTP).filter_by(
        user_id=inactive_user.id
    ).all()

    assert len(otps) == 1
    assert otps[0].otp_code != "111111"

def test_resend_otp_missing_email(client):
    response = client.post(
        "/api/auth/resend-otp",
        json={}
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Email is required."
    

def test_resend_otp_user_not_found(client):
    response = client.post(
        "/api/auth/resend-otp",
        json={
            "email": "unknown@example.com"
        }
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "User not found."


def test_resend_otp_user_already_verified(client,active_user):
    response = client.post(
        "/api/auth/resend-otp",
        json={
            "email": "active@example.com"
        }
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "User is already verified and active."



def test_resend_otp_creates_new_record(client,db_session,inactive_user):
    response = client.post(
        "/api/auth/resend-otp",
        json={
            "email": "inactive@example.com"
        }
    )

    assert response.status_code == 200

    otp = db_session.query(UserOTP).filter_by(
        user_id=inactive_user.id
    ).first()

    assert otp is not None
    assert len(otp.otp_code) == 6
