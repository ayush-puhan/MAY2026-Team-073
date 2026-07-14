"""Local SQLite database initializer for ClubConnect.

Run from Application/backend/app/ (see README):

    python -m database.init_db
"""

from .base import Base
from .database import DB_PATH, engine, init_engine
from . import models  # noqa: F401 - import registers all mapped tables


def main() -> None:
    init_engine()
    table_names = sorted(Base.metadata.tables.keys())

    print("ClubConnect SQLite database initialized successfully.")
    print(f"Database file: {DB_PATH}")
    print(f"Tables created: {len(table_names)}")
    for name in table_names:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
