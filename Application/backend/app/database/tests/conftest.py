"""Pytest fixtures: fresh in-memory SQLite database per test."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database import models  # noqa: F401 - registers all mapped tables
from database.models.university import University


@pytest.fixture()
def engine():
    eng = create_engine("sqlite:///:memory:", future=True)

    @event.listens_for(eng, "connect")
    def _fk_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def session(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    sess = SessionLocal()
    yield sess
    sess.close()


@pytest.fixture(scope="function")
def sample_university(session):
    from database.models.university import University, UniversityDomain
    uni = University(name="Test University", domain="test.edu", is_active=True)
    session.add(uni)
    session.commit()
    
    domain = UniversityDomain(university_id=uni.id, domain="test.edu")
    session.add(domain)
    session.commit()
    
    return uni
