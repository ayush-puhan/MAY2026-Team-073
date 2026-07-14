"""Mapper configuration, table count, and exact table names."""

import sqlalchemy as sa

from database.base import Base
from database import models  # noqa: F401

EXPECTED_TABLE_COUNT = 33

EXPECTED_TABLE_NAMES = {
    "announcements",
    "application_interests",
    "attendance_records",
    "auth_sessions",
    "budgets",
    "club_creation_requests",
    "club_interests",
    "club_join_applications",
    "club_memberships",
    "club_sponsors",
    "clubs",
    "committee_memberships",
    "committees",
    "departments",
    "documents",
    "emergency_reports",
    "event_interests",
    "event_registrations",
    "events",
    "expenses",
    "external_participants",
    "interests",
    "notifications",
    "programs",
    "reward_points_ledger",
    "reward_redemptions",
    "sponsors",
    "student_profiles",
    "support_tickets",
    "ticket_responses",
    "user_interests",
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
