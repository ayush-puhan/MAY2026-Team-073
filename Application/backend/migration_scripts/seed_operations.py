import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session
from app.database.models.finance import Budget, Expense
from app.database.models.events import VolunteerAssignment
from app.database.models.communication import Document
from migration_scripts.seed_base import load_mock_data, parse_datetime, str_to_bool

def run_operations_migration():
    data = load_mock_data()
    print("Migrating Budgets, Expenses, Assignments, and Documents...")

    with get_session() as db:
        # Budgets
        for b in data.get("budgets", []):
            if not db.query(Budget).filter_by(id=b["id"]).first():
                obj = Budget(
                    id=b["id"],
                    club_id=b["club_id"],
                    academic_year=b.get("academic_year", "2023-2024"),
                    total_amount=b.get("total_amount", 0.0),
                    allocated_amount=b.get("allocated_amount", 0.0),
                    spent_amount=b.get("spent_amount", 0.0),
                    status=str(b.get("status", "DRAFT")).upper(),
                    submitted_by=b.get("submitted_by"),
                    approved_by=b.get("approved_by")
                )
                db.add(obj)

        # Expenses
        for exp in data.get("expenses", []):
            if not db.query(Expense).filter_by(id=exp["id"]).first():
                obj = Expense(
                    id=exp["id"],
                    budget_id=exp["budget_id"],
                    event_id=exp.get("event_id"),
                    submitted_by=exp["submitted_by"],
                    amount=exp["amount"],
                    description=exp.get("description"),
                    receipt_url=exp.get("receipt_url"),
                    status=str(exp.get("status", "PENDING")).upper(),
                    approved_by=exp.get("approved_by")
                )
                db.add(obj)

        # Volunteer Assignments
        for va in data.get("volunteer_assignments", []):
            if not db.query(VolunteerAssignment).filter_by(id=va["id"]).first():
                obj = VolunteerAssignment(
                    id=va["id"],
                    event_id=va["event_id"],
                    user_id=va["user_id"],
                    role_description=va.get("role_description"),
                    status=str(va.get("status", "ASSIGNED")).upper(),
                    assigned_by=va.get("assigned_by")
                )
                db.add(obj)

        # Documents
        for d in data.get("documents", []):
            if not db.query(Document).filter_by(id=d["id"]).first():
                obj = Document(
                    id=d["id"],
                    club_id=d.get("club_id"),
                    uploader_id=d["uploader_id"],
                    title=d["title"],
                    file_url=d["file_url"],
                    document_type=str(d.get("document_type", "OTHER")).upper(),
                    is_public=str_to_bool(d.get("is_public", True))
                )
                db.add(obj)

        db.commit()
    print("Operations migration complete.\n")

if __name__ == "__main__":
    run_operations_migration()
