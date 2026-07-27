import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session
from app.database.models.clubs import Announcement
from app.database.models.communication import Notification
from app.database.models.support import SupportTicket, TicketResponse, EmergencyReport
from app.database.models.rewards import RewardPointsLedger, RewardStoreItem, RewardTask, RewardTaskCompletion
from app.database.models.audit import AuditLog
from migration_scripts.seed_base import load_mock_data, str_to_bool, parse_datetime

def run_systems_migration():
    data = load_mock_data()
    print("Migrating Systems (Announcements, Support, Rewards, Audit Logs)...")

    with get_session() as db:
        # Announcements
        for a in data.get("announcements", []):
            if not db.query(Announcement).filter_by(id=a["id"]).first():
                obj = Announcement(
                    id=a["id"],
                    title=a["title"],
                    content=a["content"],
                    author_id=a["author_id"],
                    target_audience=str(a.get("target_audience", "ALL_USERS")).upper(),
                    club_id=a.get("club_id"),
                    university_id=a.get("university_id")
                )
                db.add(obj)

        # Notifications
        for n in data.get("notifications", []):
            if not db.query(Notification).filter_by(id=n["id"]).first():
                obj = Notification(
                    id=n["id"],
                    user_id=n["user_id"],
                    title=n["title"],
                    message=n["message"],
                    notification_type=str(n.get("notification_type", "SYSTEM")).upper(),
                    is_read=str_to_bool(n.get("is_read", False)),
                    action_url=n.get("action_url")
                )
                db.add(obj)

        # Support Tickets
        for st in data.get("support_tickets", []):
            if not db.query(SupportTicket).filter_by(id=st["id"]).first():
                obj = SupportTicket(
                    id=st["id"],
                    user_id=st["user_id"],
                    subject=st["subject"],
                    description=st["description"],
                    status=str(st.get("status", "OPEN")).upper(),
                    priority=str(st.get("priority", "MEDIUM")).upper(),
                    category=str(st.get("category", "GENERAL")).upper(),
                    assigned_to=st.get("assigned_to")
                )
                db.add(obj)

        # Ticket Responses
        for tr in data.get("ticket_responses", []):
            if not db.query(TicketResponse).filter_by(id=tr["id"]).first():
                obj = TicketResponse(
                    id=tr["id"],
                    ticket_id=tr["ticket_id"],
                    responder_id=tr["responder_id"],
                    message=tr["message"],
                    is_internal=str_to_bool(tr.get("is_internal", False))
                )
                db.add(obj)

        # Emergency Reports
        for er in data.get("emergency_reports", []):
            if not db.query(EmergencyReport).filter_by(id=er["id"]).first():
                obj = EmergencyReport(
                    id=er["id"],
                    reporter_id=er["reporter_id"],
                    incident_type=str(er.get("incident_type", "OTHER")).upper(),
                    description=er["description"],
                    location=er.get("location"),
                    status=str(er.get("status", "REPORTED")).upper(),
                    resolved_by=er.get("resolved_by")
                )
                db.add(obj)

        # Reward Points Ledger
        for rp in data.get("reward_points_ledger", []):
            if not db.query(RewardPointsLedger).filter_by(id=rp["id"]).first():
                obj = RewardPointsLedger(
                    id=rp["id"],
                    user_id=rp["user_id"],
                    points=rp["points"],
                    transaction_type=str(rp.get("transaction_type", "EARNED")).upper(),
                    description=rp.get("description"),
                    reference_id=rp.get("reference_id")
                )
                db.add(obj)

        # Reward Store Items
        for rsi in data.get("reward_store_items", []):
            if not db.query(RewardStoreItem).filter_by(id=rsi["id"]).first():
                obj = RewardStoreItem(
                    id=rsi["id"],
                    name=rsi["name"],
                    description=rsi.get("description"),
                    points_cost=rsi["points_cost"],
                    image_url=rsi.get("image_url"),
                    stock_quantity=rsi.get("stock_quantity", 0),
                    is_active=str_to_bool(rsi.get("is_active", True))
                )
                db.add(obj)

        # Reward Tasks
        for rt in data.get("reward_tasks", []):
            if not db.query(RewardTask).filter_by(id=rt["id"]).first():
                obj = RewardTask(
                    id=rt["id"],
                    title=rt["title"],
                    description=rt.get("description"),
                    points_reward=rt["points_reward"],
                    task_type=str(rt.get("task_type", "OTHER")).upper(),
                    is_active=str_to_bool(rt.get("is_active", True))
                )
                db.add(obj)

        # Reward Task Completions
        for rtc in data.get("reward_task_completions", []):
            if not db.query(RewardTaskCompletion).filter_by(id=rtc["id"]).first():
                obj = RewardTaskCompletion(
                    id=rtc["id"],
                    user_id=rtc["user_id"],
                    task_id=rtc["task_id"],
                    completed_at=parse_datetime(rtc.get("completed_at"))
                )
                db.add(obj)

        # Audit Logs
        for al in data.get("audit_logs", []):
            if not db.query(AuditLog).filter_by(id=al["id"]).first():
                obj = AuditLog(
                    id=al["id"],
                    user_id=al["user_id"],
                    action=al["action"],
                    entity_type=al["entity_type"],
                    entity_id=al.get("entity_id"),
                    details=al.get("details"),
                    ip_address=al.get("ip_address")
                )
                db.add(obj)

        db.commit()
    print("Systems migration complete.\n")

if __name__ == "__main__":
    run_systems_migration()
