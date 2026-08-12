"""Calendar module: aggregates event sessions relevant to the requesting
user (their advised clubs for a faculty advisor, their registrations for
a student), matching the shape expected by the frontend's GlobalCalendar.
"""

from flask import Blueprint, request, g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import Event, EventSession, EventRegistration, Club, University
from app.database.enums import UserRole
from app.middleware.auth_middleware import require_auth

calendar_bp = Blueprint("calendar", __name__)
api = Api(calendar_bp)


def serialize_session(session_row, event, club, university, is_registered):
    return {
        "session_id": session_row.id,
        "session_title": session_row.title,
        "event_id": event.id,
        "event_title": event.title,
        "club_id": club.id if club else None,
        "club_name": club.name if club else None,
        "club_logo": club.logo_url if club else None,
        "university_id": university.id if university else None,
        "venue": session_row.venue or event.venue,
        "start_at": session_row.start_at.isoformat(),
        "end_at": session_row.end_at.isoformat(),
        "is_public": event.is_public,
        "is_registered": is_registered,
        "has_conflict": False,
        "status": event.status.value if hasattr(event.status, "value") else event.status,
    }


class CalendarEventsResource(Resource):
    @require_auth
    def get(self):
        user = g.current_user
        show_public = request.args.get("show_public", "false").lower() == "true"
        university_id = request.args.get("university_id")
        club_id = request.args.get("club_id")

        with get_session() as db:
            query = (
                db.query(EventSession, Event, Club, University)
                .join(Event, EventSession.event_id == Event.id)
                .outerjoin(Club, Event.club_id == Club.id)
                .outerjoin(University, Club.university_id == University.id)
            )

            if club_id:
                query = query.filter(Event.club_id == int(club_id))
            if university_id:
                query = query.filter(Club.university_id == int(university_id))

            rows = query.all()

            registered_event_ids = {
                r.event_id
                for r in db.query(EventRegistration.event_id).filter(
                    EventRegistration.user_id == user.id
                )
            }

            is_advisor = user.role == UserRole.FACULTY_ADVISOR

            result = []
            for session_row, event, club, university in rows:
                advises_club = is_advisor and club is not None and club.faculty_advisor_id == user.id
                registered = event.id in registered_event_ids

                is_registered = advises_club or registered
                if not is_registered and show_public and event.is_public:
                    is_registered = True

                if not is_registered:
                    continue

                result.append(serialize_session(session_row, event, club, university, is_registered))

            return result, 200


api.add_resource(CalendarEventsResource, "/events")
