import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session
from app.database.models.events import Event, EventSession, EventRegistration, AttendanceRecord, ExternalParticipant
from app.database.models.interests import EventInterest
from migration_scripts.seed_base import load_mock_data, parse_datetime

def run_events_migration():
    data = load_mock_data()
    print("Migrating Events, Sessions, and Registrations...")

    with get_session() as db:
        # Events
        for e in data.get("events", []):
            if not db.query(Event).filter_by(id=e["id"]).first():
                obj = Event(
                    id=e["id"],
                    club_id=e["club_id"],
                    title=e["title"],
                    description=e.get("description"),
                    banner_url=e.get("banner_url"),
                    event_type=str(e.get("event_type", "IN_PERSON")).upper(),
                    venue=e.get("venue"),
                    meeting_link=e.get("meeting_link"),
                    capacity=e.get("capacity"),
                    status=str(e.get("status", "PUBLISHED")).upper(),
                    organizer_id=e.get("organizer_id")
                )
                db.add(obj)

        # Event Sessions
        for es in data.get("event_sessions", []):
            if not db.query(EventSession).filter_by(id=es["id"]).first():
                obj = EventSession(
                    id=es["id"],
                    event_id=es["event_id"],
                    title=es.get("title", "Main Session"),
                    start_time=parse_datetime(es.get("start_time")),
                    end_time=parse_datetime(es.get("end_time")),
                    speaker_name=es.get("speaker_name"),
                    venue=es.get("venue")
                )
                db.add(obj)
                
        # Event Interests
        for ei in data.get("event_interests", []):
            if not db.query(EventInterest).filter_by(event_id=ei["event_id"], interest_id=ei["interest_id"]).first():
                obj = EventInterest(event_id=ei["event_id"], interest_id=ei["interest_id"])
                db.add(obj)

        # Event Registrations
        for er in data.get("event_registrations", []):
            if not db.query(EventRegistration).filter_by(id=er["id"]).first():
                obj = EventRegistration(
                    id=er["id"],
                    user_id=er["user_id"],
                    event_id=er["event_id"],
                    status=str(er.get("status", "REGISTERED")).upper(),
                    registered_at=parse_datetime(er.get("registered_at"))
                )
                db.add(obj)

        # Attendance Records
        for ar in data.get("attendance_records", []):
            if not db.query(AttendanceRecord).filter_by(id=ar["id"]).first():
                obj = AttendanceRecord(
                    id=ar["id"],
                    user_id=ar["user_id"],
                    event_id=ar["event_id"],
                    session_id=ar.get("session_id"),
                    check_in_time=parse_datetime(ar.get("check_in_time")),
                    checked_in_by=ar.get("checked_in_by")
                )
                db.add(obj)

        # External Participants
        for ep in data.get("external_participants", []):
            if not db.query(ExternalParticipant).filter_by(id=ep["id"]).first():
                obj = ExternalParticipant(
                    id=ep["id"],
                    event_id=ep["event_id"],
                    full_name=ep["full_name"],
                    email=ep["email"],
                    organization=ep.get("organization")
                )
                db.add(obj)

        db.commit()
    print("Events migration complete.\n")

if __name__ == "__main__":
    run_events_migration()
