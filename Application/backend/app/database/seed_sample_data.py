"""Single, documented way to load ALL sample data for ClubConnect.

Why this exists:
    `sql/sample_data.sql` cannot create real password hashes because plain
    SQL has no access to Werkzeug's `generate_password_hash()`. This script
    is the one supported workflow: it inserts the 9 sample users with real
    hashed passwords via SQLAlchemy, then executes the rest of
    `sql/sample_data.sql` (auth_sessions, clubs, events, finance, academics,
    interests, club join applications, etc.) so every other table's
    relationship-testing data is preserved unchanged.

Run from Application/backend/app/ (see README):

    python -m database.seed_sample_data

Sample login credentials (fictional, safe to publish in a student project):
    All 9 sample users share the same demo password: "ClubConnect#2026"
    (used as their local password hash even for the GOOGLE-auth demo user).
    e.g. priya.sharma@campus.edu / ClubConnect#2026

Safe to re-run: it refuses to run if the `users` table already has rows,
so it won't create duplicate users or clash with data already loaded.
"""

import sqlite3
from datetime import date, datetime
from pathlib import Path

from werkzeug.security import generate_password_hash

from .database import DB_PATH, get_session, init_engine
from .models.auth import User
from .enums import AuthProvider, Gender, UserRole
from .models.university import University, UniversityDomain
from .session_manager import cleanup_expired_tokens, generate_and_store_token

SQL_DIR = Path(__file__).resolve().parent / "sql"
SAMPLE_DATA_SQL = SQL_DIR / "sample_data.sql"

DEMO_PASSWORD = "ClubConnect#2026"

# Same 9 users/ids/roles the rest of sample_data.sql expects to already exist.
SAMPLE_USERS = [
    dict(id=1, email="priya.sharma@campus.edu", full_name="Priya Sharma",
         roll_number="CS2023001", role=UserRole.STUDENT, phone="9990000001",
         is_active=True, email_verified=True, dob=date(2004, 3, 12), gender=Gender.FEMALE,
         university_id=1, created_at=datetime(2026, 1, 15, 10, 0)),
    dict(id=2, email="arjun.mehta@campus.edu", full_name="Arjun Mehta",
         roll_number="CS2023002", role=UserRole.STUDENT, phone="9990000002",
         is_active=True, email_verified=True, dob=date(2004, 7, 22), gender=Gender.MALE,
         university_id=1, created_at=datetime(2026, 2, 10, 10, 0)),
    dict(id=3, email="ananya.gupta@campus.edu", full_name="Ananya Gupta",
         roll_number="EC2023011", role=UserRole.STUDENT, phone="9990000003",
         is_active=True, email_verified=True, dob=date(2003, 11, 4), gender=Gender.FEMALE,
         university_id=1, created_at=datetime(2026, 2, 18, 10, 0)),
    dict(id=4, email="dr.rao@campus.edu", full_name="Dr. Rao",
         roll_number=None, role=UserRole.FACULTY_ADVISOR, phone="9990000004",
         is_active=True, email_verified=True, university_id=1, created_at=datetime(2026, 3, 5, 10, 0)),
    dict(id=5, email="dean.welfare@campus.edu", full_name="Dean of Student Welfare",
         roll_number=None, role=UserRole.DEAN_STUDENT_WELFARE, phone="9990000005",
         is_active=True, email_verified=True, university_id=1, created_at=datetime(2026, 3, 12, 10, 0)),
    dict(id=6, email="affairs.office@campus.edu", full_name="Student Affairs Office",
         roll_number=None, role=UserRole.STUDENT_AFFAIRS_OFFICE, phone="9990000006",
         is_active=True, email_verified=True, university_id=1, created_at=datetime(2026, 4, 1, 10, 0)),
    dict(id=7, email="admin@campus.edu", full_name="System Admin",
         roll_number=None, role=UserRole.SYSTEM_ADMIN, phone="9990000007",
         is_active=True, email_verified=True, university_id=None, created_at=datetime(2026, 4, 20, 10, 0)),
    dict(id=8, email="rohit.singh@campus.edu", full_name="Rohit Singh",
         roll_number="ME2023044", role=UserRole.STUDENT, phone="9990000008",
         is_active=True, email_verified=False, color_blind_mode=True, university_id=1, created_at=datetime(2026, 5, 15, 10, 0)),
    dict(id=9, email="kavya.iyer@campus.edu", full_name="Kavya Iyer",
         roll_number="DS2023019", role=UserRole.STUDENT, phone="9990000009",
         is_active=True, email_verified=True, auth_provider=AuthProvider.GOOGLE,
         google_id="google-oauth2|kavya-iyer-demo", gender=Gender.FEMALE, university_id=1, created_at=datetime(2026, 6, 2, 10, 0)),
]


def seed_universities() -> None:
    """Insert sample universities needed by users."""
    with get_session() as session:
        if session.query(University).count() > 0:
            print("Universities table already has data — skipping university seeding.")
            return

        u1 = University(id=1, name='Indian Institute of Technology Delhi', short_name='IITD', domain='iitd.ac.in', website='https://iitd.ac.in')
        u2 = University(id=2, name='BITS Pilani', short_name='BITS', domain='bits-pilani.ac.in', website='https://bits-pilani.ac.in')
        
        session.add_all([u1, u2])
        session.commit()
        
        d1 = UniversityDomain(university_id=1, domain='iitd.ac.in')
        d2 = UniversityDomain(university_id=1, domain='admin.iitd.ac.in')
        d3 = UniversityDomain(university_id=1, domain='campus.edu')
        d4 = UniversityDomain(university_id=2, domain='bits-pilani.ac.in')
        session.add_all([d1, d2, d3, d4])
        session.commit()
        
        print("Seeded 2 sample universities and their domains.")

def seed_users() -> None:
    """Insert the 8 sample users with real Werkzeug password hashes."""
    with get_session() as session:
        if session.query(User).count() > 0:
            print("Users table already has data — skipping user seeding.")
            return

        for u in SAMPLE_USERS:
            user = User(
                id=u["id"],
                email=u["email"],
                password_hash=generate_password_hash(DEMO_PASSWORD),
                full_name=u["full_name"],
                roll_number=u["roll_number"],
                role=u["role"],
                phone=u["phone"],
                is_active=u["is_active"],
                email_verified=u["email_verified"],
                dob=u.get("dob"),
                gender=u.get("gender"),
                auth_provider=u.get("auth_provider", AuthProvider.LOCAL),
                google_id=u.get("google_id"),
                university_id=u.get("university_id"),
                color_blind_mode=u.get("color_blind_mode", False),
                created_at=u.get("created_at")
            )
            session.add(user)
        session.commit()
        print(f"Seeded {len(SAMPLE_USERS)} sample users with real password hashes.")


def seed_remaining_tables() -> None:
    """Execute seed_data_postgres.sql for every table other than users."""
    from sqlalchemy import text
    from .database import engine
    
    sql_path = Path(__file__).parent.parent.parent / 'migration_scripts' / 'seed_data_postgres.sql'
    sql_statements = sql_path.read_text(encoding="utf-8").split(";")
    
    with engine.begin() as conn:
        for stmt in sql_statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith("PRAGMA") and not stmt.startswith("BEGIN TRANSACTION"):
                # if running against sqlite locally, strip the ON CONFLICT because of boolean false vs 0 issues
                if engine.dialect.name == "sqlite":
                     stmt = stmt.replace("ON CONFLICT (id) DO NOTHING", "")
                     stmt = stmt.replace("false", "0")
                conn.execute(text(stmt))
    print("Loaded remaining sample data from seed_data_postgres.sql.")


def seed_auth_sessions() -> None:
    """Give a couple of sample users a real, active login session.

    Uses `session_manager.generate_and_store_token()` so `auth_sessions`
    holds genuine 1-hour JWTs (matching what a real login would produce)
    instead of fake placeholder values.
    """
    with get_session() as session:
        from .models.auth import AuthSession

        if session.query(AuthSession).count() > 0:
            print("auth_sessions already has data — skipping session seeding.")
            return

        for user_id in (1, 2):
            generate_and_store_token(user_id, session=session)
        print("Seeded 2 real JWT sessions in auth_sessions.")


def main() -> None:
    init_engine()  # ensure tables exist; safe to call even if already initialized
    seed_universities()
    seed_users()
    seed_remaining_tables()
    seed_auth_sessions()
    cleanup_expired_tokens()
    print(f"\nDemo login for any sample user: <email> / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
