"""Compact verification script for the ClubConnect SQLite database.

Run from the repository root:

    python -m application.backend.database.verify_db
"""

import sqlalchemy as sa

from .base import Base
from .database import DB_PATH, engine
from . import models  # noqa: F401 - import registers all mapped tables

EXPECTED_TABLE_COUNT = 24


def main() -> None:
    sa.orm.configure_mappers()  # raises if any relationship/mapper is misconfigured
    mapped_tables = sorted(Base.metadata.tables.keys())

    print(f"Mapper configuration: OK")
    print(f"Mapped tables in metadata: {len(mapped_tables)} (expected {EXPECTED_TABLE_COUNT})")

    if not DB_PATH.exists():
        print(f"SQLite file not found at {DB_PATH}. Run init_db first.")
        return

    inspector = sa.inspect(engine)
    db_tables = sorted(inspector.get_table_names())

    print(f"SQLite file: {DB_PATH}")
    print(f"Tables in SQLite: {len(db_tables)}")

    missing = set(mapped_tables) - set(db_tables)
    extra = set(db_tables) - set(mapped_tables)
    if missing:
        print(f"MISSING from SQLite: {sorted(missing)}")
    if extra:
        print(f"EXTRA in SQLite: {sorted(extra)}")
    if not missing and not extra:
        print("Table name parity: OK (metadata matches SQLite exactly)")


if __name__ == "__main__":
    main()
