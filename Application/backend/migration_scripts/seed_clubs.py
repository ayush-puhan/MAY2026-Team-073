import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session
from app.database.models.clubs import Club, ClubMembership, ClubCreationRequest, Committee, CommitteeMembership
from app.database.models.applications import ClubJoinApplication
from app.database.models.interests import ClubInterest
from app.database.models.external_relations import ClubSponsor
from migration_scripts.seed_base import load_mock_data, parse_datetime

def run_clubs_migration():
    data = load_mock_data()
    print("Migrating Clubs, Committees, and Applications...")

    with get_session() as db:
        # Clubs
        for c in data.get("clubs", []):
            if not db.query(Club).filter_by(id=c["id"]).first():
                obj = Club(
                    id=c["id"],
                    name=c["name"],
                    description=c.get("description"),
                    logo_url=c.get("logo_url"),
                    banner_url=c.get("banner_url"),
                    guidelines=c.get("guidelines"),
                    faculty_advisor_id=c.get("faculty_advisor_id"),
                    university_id=c.get("university_id"),
                    status=str(c.get("status", "ACTIVE")).upper()
                )
                db.add(obj)
                
        # Club Creation Requests
        for req in data.get("club_creation_requests", []):
            if not db.query(ClubCreationRequest).filter_by(id=req["id"]).first():
                obj = ClubCreationRequest(
                    id=req["id"],
                    applicant_id=req["applicant_id"],
                    proposed_name=req["proposed_name"],
                    proposed_description=req.get("proposed_description"),
                    faculty_advisor_id=req.get("faculty_advisor_id"),
                    status=str(req.get("status", "SUBMITTED")).upper(),
                    admin_notes=req.get("admin_notes")
                )
                db.add(obj)

        # Club Interests
        for ci in data.get("club_interests", []):
            if not db.query(ClubInterest).filter_by(club_id=ci["club_id"], interest_id=ci["interest_id"]).first():
                obj = ClubInterest(club_id=ci["club_id"], interest_id=ci["interest_id"])
                db.add(obj)

        # Club Sponsors
        for cs in data.get("club_sponsors", []):
            if not db.query(ClubSponsor).filter_by(club_id=cs["club_id"], sponsor_id=cs["sponsor_id"]).first():
                obj = ClubSponsor(
                    club_id=cs["club_id"], 
                    sponsor_id=cs["sponsor_id"],
                    sponsorship_details=f"{cs.get('sponsorship_type', 'FINANCIAL')} - ${cs.get('amount', 0)}"
                )
                db.add(obj)

        # Club Memberships
        for cm in data.get("club_memberships", []):
            if not db.query(ClubMembership).filter_by(id=cm["id"]).first():
                obj = ClubMembership(
                    id=cm["id"],
                    user_id=cm["user_id"],
                    club_id=cm["club_id"],
                    role=str(cm.get("role", "MEMBER")).upper(),
                    joined_at=parse_datetime(cm.get("joined_at"))
                )
                db.add(obj)

        # Club Join Applications
        for cja in data.get("club_join_applications", []):
            if not db.query(ClubJoinApplication).filter_by(id=cja["id"]).first():
                obj = ClubJoinApplication(
                    id=cja["id"],
                    user_id=cja["user_id"],
                    club_id=cja["club_id"],
                    statement_of_purpose=cja.get("statement_of_purpose"),
                    status=str(cja.get("status", "PENDING")).upper(),
                    reviewed_by=cja.get("reviewed_by")
                )
                db.add(obj)

        # Committees
        for com in data.get("committees", []):
            if not db.query(Committee).filter_by(id=com["id"]).first():
                obj = Committee(
                    id=com["id"],
                    club_id=com["club_id"],
                    name=com["name"],
                    description=com.get("description")
                )
                db.add(obj)

        # Committee Memberships
        for cmm in data.get("committee_memberships", []):
            if not db.query(CommitteeMembership).filter_by(id=cmm["id"]).first():
                obj = CommitteeMembership(
                    id=cmm["id"],
                    user_id=cmm["user_id"],
                    committee_id=cmm["committee_id"],
                    role=str(cmm.get("role", "MEMBER")).upper(),
                    joined_at=parse_datetime(cmm.get("joined_at"))
                )
                db.add(obj)

        db.commit()
    print("Clubs migration complete.\n")

if __name__ == "__main__":
    run_clubs_migration()
