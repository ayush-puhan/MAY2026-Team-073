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
from datetime import date
from pathlib import Path

from werkzeug.security import generate_password_hash

from .database import DB_PATH, get_session, init_engine
from .models.auth import User
from .enums import AuthProvider, Gender, UserRole
from .session_manager import cleanup_expired_tokens, generate_and_store_token

SQL_DIR = Path(__file__).resolve().parent / "sql"
SAMPLE_DATA_SQL = SQL_DIR / "sample_data.sql"

DEMO_PASSWORD = "ClubConnect#2026"

# Same 9 users/ids/roles the rest of sample_data.sql expects to already exist.
SAMPLE_USERS = [
    dict(id=1, email="priya.sharma@campus.edu", full_name="Priya Sharma",
         roll_number="CS2023001", role=UserRole.STUDENT, phone="9990000001",
         is_active=True, email_verified=True, dob=date(2004, 3, 12), gender=Gender.FEMALE),
    dict(id=2, email="arjun.mehta@campus.edu", full_name="Arjun Mehta",
         roll_number="CS2023002", role=UserRole.STUDENT, phone="9990000002",
         is_active=True, email_verified=True, dob=date(2004, 7, 22), gender=Gender.MALE),
    dict(id=3, email="ananya.gupta@campus.edu", full_name="Ananya Gupta",
         roll_number="EC2023011", role=UserRole.STUDENT, phone="9990000003",
         is_active=True, email_verified=True, dob=date(2003, 11, 4), gender=Gender.FEMALE),
    dict(id=4, email="dr.rao@campus.edu", full_name="Dr. Rao",
         roll_number=None, role=UserRole.FACULTY_ADVISOR, phone="9990000004",
         is_active=True, email_verified=True),
    dict(id=5, email="dean.welfare@campus.edu", full_name="Dean of Student Welfare",
         roll_number=None, role=UserRole.DEAN_STUDENT_WELFARE, phone="9990000005",
         is_active=True, email_verified=True),
    dict(id=6, email="affairs.office@campus.edu", full_name="Student Affairs Office",
         roll_number=None, role=UserRole.STUDENT_AFFAIRS_OFFICE, phone="9990000006",
         is_active=True, email_verified=True),
    dict(id=7, email="admin@campus.edu", full_name="System Admin",
         roll_number=None, role=UserRole.SYSTEM_ADMIN, phone="9990000007",
         is_active=True, email_verified=True),
    dict(id=8, email="rohit.singh@campus.edu", full_name="Rohit Singh",
         roll_number="ME2023044", role=UserRole.STUDENT, phone="9990000008",
         is_active=True, email_verified=False, color_blind_mode=True),
    dict(id=9, email="kavya.iyer@campus.edu", full_name="Kavya Iyer",
         roll_number="DS2023019", role=UserRole.STUDENT, phone="9990000009",
         is_active=True, email_verified=True, auth_provider=AuthProvider.GOOGLE,
         google_id="google-oauth2|kavya-iyer-demo", gender=Gender.FEMALE),
]


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
                color_blind_mode=u.get("color_blind_mode", False),
            )
            session.add(user)
        session.commit()
        print(f"Seeded {len(SAMPLE_USERS)} sample users with real password hashes.")


def seed_remaining_tables() -> None:
    """Execute sample_data.sql for every table other than users."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SAMPLE_DATA_SQL.read_text())
        conn.commit()
        print("Loaded remaining sample data (clubs, events, finance, academics, etc.).")
    finally:
        conn.close()


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
    seed_users()
    seed_remaining_tables()
    seed_auth_sessions()
    cleanup_expired_tokens()
    print(f"\nDemo login for any sample user: <email> / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
