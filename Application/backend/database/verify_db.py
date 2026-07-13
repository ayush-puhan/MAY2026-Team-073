"""Compact verification script for the ClubConnect SQLite database.

Run from the repository root:

    python -m application.backend.database.verify_db
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
from rich.console import Console

from .base import Base
from .database import DB_PATH, engine
from . import models  

EXPECTED_TABLE_COUNT = 24
console = Console()

def main() -> None:
    orm.configure_mappers()  # raises if any relationship/mapper is misconfigured
    mapped_tables = sorted(Base.metadata.tables.keys())

    result = {
        "Mapper configuration" : "OK",
        "Mapped tables in metadata" : len(mapped_tables),
        "Expected" : EXPECTED_TABLE_COUNT,
        "SQLite file" : "",
        "Tables in SQLite" : 0,
        "MISSING" : 0,
        "EXTRA" : 0,
        "Table name parity" : ""
    }
    #print(f"| Mapper configuration: OK")
    #print(f"| Mapped tables in metadata: {len(mapped_tables)} (expected {EXPECTED_TABLE_COUNT})")

    if not DB_PATH.exists():
        print(f"!! SQLite file not found at {DB_PATH} !! \nCHECK : Run init_db first.")
        error = {
            "Message" : f"!! SQLite file not found at {DB_PATH} !!",
            "CHECK" : "Run init_db first."
        }
        console.print_json(data=error)
        return

    inspector = sa.inspect(engine)
    db_tables = sorted(inspector.get_table_names())

    result['SQLite file'] = str(DB_PATH)
    result['Tables in SQLite'] = len(db_tables)
    #print(f"| SQLite file: {DB_PATH}")
    #print(f"| Tables in SQLite: {len(db_tables)}")

    missing = set(mapped_tables) - set(db_tables)
    extra = set(db_tables) - set(mapped_tables)
    if missing:
        result["MISSING"] = sorted(missing)
        #print(f"[] MISSING from SQLite: {sorted(missing)}")
    if extra:
        result["EXTRA"] = sorted(extra)
        #print(f"[] EXTRA in SQLite: {sorted(extra)}")
    if not missing and not extra:
        result['Table name parity'] = "OK (metadata matches SQLite exactly)"
        #print("[] Table name parity: OK (metadata matches SQLite exactly)")

    console.print_json(data=result)
    

if __name__ == "__main__":
    main()
