"""SQLite engine and session configuration for ClubConnect.

The database file path is derived from this file's location (not the
process's current working directory), so the project behaves consistently
regardless of where it is launched from.
"""

from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

import os

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "clubconnect.db"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine: Engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enable SQLite foreign-key constraint enforcement on every new connection."""
    if engine.dialect.name == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


def init_engine() -> None:
    """Import all models (registering their tables) and create the SQLite schema."""
    from . import models  # noqa: F401 - import registers all mapped tables
    from .base import Base

    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Session: #type:ignore
    """Context-manager helper for obtaining a scoped DB session.

    Usage:
        with get_session() as session:
            session.add(obj)
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
