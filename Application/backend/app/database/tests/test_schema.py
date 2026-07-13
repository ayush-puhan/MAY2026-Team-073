"""Mapper configuration, table count, and exact table names."""

import sqlalchemy as sa

from database.base import Base
from database import models  # noqa: F401

EXPECTED_TABLE_COUNT = 24

EXPECTED_TABLE_NAMES = {
    "announcements",
    "attendance_records",
    "auth_sessions",
    "budgets",
    "club_creation_requests",
    "club_memberships",
    "club_sponsors",
    "clubs",
    "committee_memberships",
    "committees",
    "documents",
    "emergency_reports",
    "event_registrations",
    "events",
    "expenses",
    "external_participants",
    "notifications",
    "reward_points_ledger",
    "reward_redemptions",
    "sponsors",
    "support_tickets",
    "ticket_responses",
    "users",
    "volunteer_assignments",
}


def test_mapper_configuration_succeeds():
    sa.orm.configure_mappers()


def test_table_count():
    assert len(Base.metadata.tables) == EXPECTED_TABLE_COUNT


def test_exact_table_names():
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLE_NAMES


def test_schema_creates_in_sqlite(engine):
    inspector = sa.inspect(engine)
    db_tables = set(inspector.get_table_names())
    assert db_tables == EXPECTED_TABLE_NAMES
