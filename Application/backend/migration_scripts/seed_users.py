import os
import sys
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session
from app.database.models.auth import User
from app.database.models.academics import StudentProfile
from app.database.models.interests import UserInterest
from migration_scripts.seed_base import load_mock_data, parse_date

def run_users_migration():
    data = load_mock_data()
    print("Migrating Users, Student Profiles, and User Interests...")

    with get_session() as db:
        # Users
        for u in data.get("users", []):
            if not db.query(User).filter_by(id=u["id"]).first():
                # Correct bcrypt hashing
                raw_password = u.get("password_hash", "Password@123").encode('utf-8')
                hashed_pw = bcrypt.hashpw(raw_password, bcrypt.gensalt()).decode('utf-8')

                obj = User(
                    id=u["id"],
                    email=u["email"],
                    password_hash=hashed_pw,
                    full_name=u["full_name"],
                    roll_number=u.get("roll_number"),
                    role=str(u.get("role", "STUDENT")).upper(),
                    phone=u.get("phone"),
                    profile_photo_url=u.get("profile_photo_url"),
                    accessibility_prefs=u.get("accessibility_prefs"),
                    is_active=u.get("is_active", True),
                    email_verified=u.get("email_verified", True),
                    google_id=u.get("google_id"),
                    dob=parse_date(u.get("dob")),
                    auth_provider=str(u.get("auth_provider", "LOCAL")).upper(),
                    department_id=u.get("department_id"),
                    university_id=u.get("university_id"),
                    gender=str(u.get("gender", "OTHER")).upper() if u.get("gender") else None,
                    color_blind_mode=u.get("color_blind_mode", False)
                )
                db.add(obj)

        # Student Profiles
        for sp in data.get("student_profiles", []):
            if not db.query(StudentProfile).filter_by(user_id=sp["user_id"]).first():
                obj = StudentProfile(
                    user_id=sp["user_id"],
                    program_id=sp.get("program_id", 1),
                    academic_year=sp.get("year_of_study", 1),
                )
                db.add(obj)

        # User Interests
        for ui in data.get("user_interests", []):
            if not db.query(UserInterest).filter_by(user_id=ui["user_id"], interest_id=ui["interest_id"]).first():
                obj = UserInterest(
                    user_id=ui["user_id"],
                    interest_id=ui["interest_id"]
                )
                db.add(obj)

        db.commit()
    print("Users migration complete.\n")

if __name__ == "__main__":
    run_core_migration = run_users_migration
    run_users_migration()
