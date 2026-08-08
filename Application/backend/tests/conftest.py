# tests/conftest.py
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from app import create_app
from app.database.enums import MembershipStatus
from app.database.models.clubs import ClubMembership
from app.database import Base
import  app.database.database as db_module
from app.database.models.auth import User,UserOTP




pytest_plugins =[
    "tests.fixtures.auth_fixture",
    "tests.fixtures.factory_fixture"
]

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
def db_error(monkeypatch):
    def _patch(module):
        def broken_session():
            raise Exception("Database Error")

        monkeypatch.setattr(
            module,
            "get_session",
            broken_session,
        )

    return _patch


@pytest.fixture
def mock_resolve_club_id(monkeypatch):
    def _mock_resolve_club_id(user):
        def fake_resolve_club_id(db, kwargs):
            membership = (
                db.query(ClubMembership)
                .filter(
                    ClubMembership.user_id == user.id,
                    ClubMembership.status == MembershipStatus.APPROVED,
                )
                .first()
            )

            return membership.club_id if membership else None

        monkeypatch.setattr(
            "app.middleware.auth_middleware.resolve_club_id", #"app.modules.middleware.auth_middleware.resolve_club_id"
            fake_resolve_club_id,
        )

    return _mock_resolve_club_id

@pytest.fixture
def client(db_session):
    app = create_app()

    with app.test_client() as client:
        yield client







