import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session
from app.database.models.university import University, UniversityDomain
from app.database.models.academics import Department, Program
from app.database.models.interests import Interest
from app.database.models.external_relations import Sponsor
from migration_scripts.seed_base import load_mock_data

def run_core_migration():
    data = load_mock_data()
    print("Migrating Core Entities (Universities, Departments, Programs, Interests, Sponsors)...")

    with get_session() as db:
        # Universities
        for u in data.get("universities", []):
            if not db.query(University).filter_by(id=u["id"]).first():
                obj = University(
                    id=u["id"], 
                    name=u["name"], 
                    short_name=u.get("short_name", u["name"].split()[0]),
                    logo_url=u.get("logo_url"),
                    domain=u.get("domain", f"{u['name'].split()[0].lower()}.edu")
                )
                db.add(obj)

        # University Domains
        for d in data.get("university_domains", []):
            if not db.query(UniversityDomain).filter_by(id=d["id"]).first():
                obj = UniversityDomain(id=d["id"], university_id=d["university_id"], domain=d["domain"])
                db.add(obj)

        # Departments
        for d in data.get("departments", []):
            if not db.query(Department).filter_by(id=d["id"]).first():
                obj = Department(id=d["id"], name=d["name"], university_id=d["university_id"])
                db.add(obj)

        # Programs
        for p in data.get("programs", []):
            if not db.query(Program).filter_by(id=p["id"]).first():
                obj = Program(id=p["id"], name=p["name"], department_id=p["department_id"])
                db.add(obj)

        # Interests
        for i in data.get("interests", []):
            if not db.query(Interest).filter_by(id=i["id"]).first():
                obj = Interest(id=i["id"], name=i["name"])
                db.add(obj)

        # Sponsors
        for s in data.get("sponsors", []):
            if not db.query(Sponsor).filter_by(id=s["id"]).first():
                obj = Sponsor(
                    id=s["id"], 
                    organization_name=s.get("name", s.get("organization_name", "Unknown")), 
                    contact_email=s.get("contact_email"),
                    contact_person=s.get("contact_person")
                )
                db.add(obj)

        db.commit()
    print("Core Entities migration complete.\n")

if __name__ == "__main__":
    run_core_migration()
