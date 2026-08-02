# tests/conftest.py
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from app import create_app
from app.database import models
from app.database import Base
import  app.database.database as db_module
from app.database.models.auth import User,UserOTP



engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True
)

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(monkeypatch):
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        future=True
    )
    session = TestingSessionLocal()
    @contextmanager
    def get_test_session():
        try:
            yield session
        finally:
            pass
    monkeypatch.setattr( db_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(db_module, "get_session", get_test_session)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    app = create_app()

    with app.test_client() as client:
        yield client



#------------------
import bcrypt
import pytest

from app.database.models import User
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


@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    monkeypatch.setattr(
        "app.modules.auth.auth_routes.send_otp_email",
        lambda *args, **kwargs: None
    )


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    monkeypatch.setattr(
        "app.modules.auth.auth_routes.send_welcome_email",
        lambda *args, **kwargs: None
    )

    monkeypatch.setattr(
        "app.modules.auth.auth_routes.generate_and_store_token",
        lambda user_id, session=None: "test-token"
    )


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

@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    # Pretend the JWT is structurally valid
    monkeypatch.setattr(
        "app.middleware.auth_middleware.verify_jwt_in_request",   # replace with your module
        lambda: None
    )

    # Pretend the token exists in AuthSession
    monkeypatch.setattr(
        "app.middleware.auth_middleware.validate_stored_token",   # replace with your module
        lambda token: True
    )

    # Mock logout
    monkeypatch.setattr(
        "app.modules.auth.auth_routes.delete_token",   # Replace with your module
        lambda token: True
    )



