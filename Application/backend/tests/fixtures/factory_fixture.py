import bcrypt
import pytest
from datetime import datetime, timedelta

from app.database.models.auth import User, UserOTP
from app.database.enums import UserRole

@pytest.fixture
def active_user(db_session):
    user = User(
        email="active@example.com",
        full_name="Active User",
        password_hash=bcrypt.hashpw(b"Password@123",bcrypt.gensalt()).decode("utf-8"),
        role=UserRole.STUDENT,
        auth_provider="LOCAL",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def inactive_user(db_session):
    user = User(
        email="inactive@example.com",
        full_name="Inactive User",
        password_hash=bcrypt.hashpw(b"Password@123",bcrypt.gensalt()).decode("utf-8"),
        role=UserRole.STUDENT,
        auth_provider="LOCAL",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def inactive_user_with_otp(db_session):
    user = User(
        email="user@example.com",
        full_name="Test User",
        password_hash=bcrypt.hashpw(b"Password@123",bcrypt.gensalt()).decode("utf-8"),
        auth_provider="LOCAL",
        is_active=False,
        email_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    otp = UserOTP(
        user_id=user.id,
        otp_code="123456",
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db_session.add(otp)
    db_session.commit()
    return user

@pytest.fixture
def expired_otp_user(db_session):
    user = User(
        email="expired@example.com",
        full_name="Expired User",
        password_hash=bcrypt.hashpw(b"Password@123",bcrypt.gensalt()).decode("utf-8"),
        auth_provider="LOCAL",
        is_active=False,
        email_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    otp = UserOTP(
        user_id=user.id,
        otp_code="123456",
        expires_at=datetime.utcnow() - timedelta(minutes=5)
    )
    db_session.add(otp)
    db_session.commit()
    return user

@pytest.fixture
def system_admin_user(db_session):
    user = User(
        email="admin@test.com",
        full_name="System Admin",
        password_hash=bcrypt.hashpw(
            b"Password@123",
            bcrypt.gensalt()
        ).decode(),
        role=UserRole.SYSTEM_ADMIN,
        is_active=True,
        auth_provider="LOCAL",
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def student_user(db_session):
    user = User(
        email="student@test.com",
        full_name="Student",
        password_hash=bcrypt.hashpw(
            b"Password@123",
            bcrypt.gensalt()
        ).decode(),
        role=UserRole.STUDENT,
        is_active=True,
        auth_provider="LOCAL",
    )
    db_session.add(user)
    db_session.commit()
    return user
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# More Modular Factory db for facking real database resources
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory,DepartmentFactory
)

@pytest.fixture(autouse=True)
def factory_session(db_session):
    factories = [
        UserFactory,
        UniversityFactory,
        ClubFactory,
        EventFactory,
        SupportTicketFactory,
        AuditLogFactory,
        DepartmentFactory
    ]
    for factory_cls in factories:
        factory_cls._meta.sqlalchemy_session = db_session