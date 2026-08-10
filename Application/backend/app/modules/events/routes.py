"""
Event management module APIs.

Handles:
- Events
- Event registrations
- External participants
- Event sessions
- Attendance
"""

from datetime import datetime

from flask import Blueprint, request, g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import (
    Event,
    EventSession,
    EventRegistration,
    AttendanceRecord,
    ExternalParticipant,
)
from app.middleware.auth_middleware import require_auth, require_club_role


event_bp = Blueprint("events", __name__)
api = Api(event_bp)


# ============================================================
# HELPERS
# ============================================================


def _json_data():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _parse_iso(dt_value, field_name):
    if not dt_value:
        return None
    try:
        return datetime.fromisoformat(dt_value)
    except Exception:
        raise ValueError(f"Invalid datetime format for {field_name}")


def _int_or_400(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        return {"message": f"Invalid {field_name}"}, 400


def get_event_or_404(session, event_id):
    event = session.query(Event).filter_by(id=event_id).first()
    if not event:
        return None, ({"message": "Event not found"}, 404)
    return event, None


def get_attendance_or_404(session, record_id):
    record = session.query(AttendanceRecord).filter_by(id=record_id).first()
    if not record:
        return None, ({"message": "Attendance not found"}, 404)
    return record, None


# ============================================================
# SERIALIZERS
# ============================================================


def serialize_session(session):
    return {
        "id": session.id,
        "event_id": session.event_id,
        "title": session.title,
        "description": session.description,
        "venue": session.venue,
        "start_at": session.start_at.isoformat() if session.start_at else None,
        "end_at": session.end_at.isoformat() if session.end_at else None,
        "session_order": session.session_order,
    }



def serialize_event(event):
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "start_at": event.start_at.isoformat() if event.start_at else None,
        "end_at": event.end_at.isoformat() if event.end_at else None,
        "registration_deadline": (
            event.registration_deadline.isoformat()
            if event.registration_deadline
            else None
        ),
        "capacity": event.capacity,
        "status": event.status.value if event.status else None,
        "banner": event.banner,
        "club_id": event.club_id,
        "is_public": event.is_public,
        "club": {
            "id": event.club.id,
            "name": event.club.name,
            "logo_url": getattr(event.club, "logo_url", None),
            "university_id": event.club.university_id,
            "university": {
                "id": event.club.university.id,
                "name": event.club.university.name,
            }
            if event.club.university
            else None,
        }
        if event.club
        else None,
        "event_sessions": [serialize_session(s) for s in event.event_sessions],
    }


# ============================================================
# GET ALL EVENTS
# GET /api/events
# ============================================================


class EventListResource(Resource):
    @require_auth
    def get(self):
        try:
            club_id = request.args.get("club_id")

            with get_session() as session:
                query = session.query(Event)
                if club_id:
                    parsed = _int_or_400(club_id, "club_id")
                    if isinstance(parsed, tuple):
                        return parsed
                    query = query.filter(Event.club_id == parsed)

                events = query.all()
                return [serialize_event(event) for event in events], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

    @require_auth
    @require_club_role("event_coordinator", "president")
    def post(self):
        try:
            data = _json_data()

            if "title" not in data:
                return {"message": "title is required"}, 400
            if "start_at" not in data:
                return {"message": "start_at is required"}, 400
            if "end_at" not in data:
                return {"message": "end_at is required"}, 400

            try:
                start_at = _parse_iso(data["start_at"], "start_at")
                end_at = _parse_iso(data["end_at"], "end_at")
                registration_deadline = _parse_iso(
                    data.get("registration_deadline"), "registration_deadline"
                )
            except ValueError as e:
                return {"message": str(e)}, 400

            with get_session() as session:
                event = Event(
                    club_id=g.club_id,
                    title=data["title"],
                    description=data.get("description"),
                    venue=data.get("venue"),
                    start_at=start_at,
                    end_at=end_at,
                    registration_deadline=registration_deadline,
                    capacity=data.get("capacity"),
                    banner=data.get("banner"),
                    created_by=g.current_user.id,
                    is_public=data.get("is_public", False),
                )

                session.add(event)
                session.commit()
                session.refresh(event)

                return serialize_event(event), 201
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# GET EVENT BY ID
# GET /api/events/<event_id>
# ============================================================


class EventDetailResource(Resource):
    @require_auth
    def get(self, event_id):
        try:
            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error
                return serialize_event(event), 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500
    @require_auth
    @require_club_role("event_coordinator", "president")
    def patch(self, event_id):
        try:
            data = _json_data()

            with get_session() as session:

                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                if "title" in data:
                    event.title = data["title"]

                if "description" in data:
                    event.description = data["description"]

                if "venue" in data:
                    event.venue = data["venue"]

                if "capacity" in data:
                    event.capacity = data["capacity"]

                if "registration_deadline" in data:
                    event.registration_deadline = (
                        _parse_iso(
                            data["registration_deadline"],
                            "registration_deadline"
                        )
                        if data["registration_deadline"]
                        else None
                    )

                if "banner_url" in data:
                    event.banner_url = data["banner_url"]

                if "visibility" in data:
                    event.visibility = data["visibility"]

                session.commit()

                return {
                    "message": "Event updated successfully."
                }, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

# ============================================================
# EVENT REGISTRATION
# POST   /api/events/<event_id>/register
# DELETE /api/events/<event_id>/register
# ============================================================


class EventRegistrationResource(Resource):
    @require_auth
    def post(self, event_id):
        try:
            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                existing = (
                    session.query(EventRegistration)
                    .filter_by(event_id=event_id, user_id=g.current_user.id)
                    .first()
                )
                if existing:
                    return {"message": "Already registered"}, 400

                registration = EventRegistration(event_id=event.id, user_id=g.current_user.id)
                session.add(registration)
                session.commit()

                return {"message": "Registered successfully", "id": registration.id}, 201
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

    @require_auth
    def delete(self, event_id):
        try:
            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                registration = (
                    session.query(EventRegistration)
                    .filter_by(event_id=event.id, user_id=g.current_user.id)
                    .first()
                )
                if not registration:
                    return {"message": "Registration not found"}, 404

                session.delete(registration)
                session.commit()

                return {"message": "Unregistered successfully"}, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# EXTERNAL PARTICIPANTS
# POST /api/events/<event_id>/register-external
# ============================================================


class ExternalRegistrationResource(Resource):
    @require_auth
    @require_club_role("event_coordinator", "president")
    def post(self, event_id):
        try:
            data = _json_data()

            required_fields = ["full_name", "participant_type"]
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return {"message": f"Missing required fields: {', '.join(missing)}"}, 400

            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                participant = ExternalParticipant(
                    event_id=event.id,
                    full_name=data["full_name"],
                    email=data.get("email"),
                    affiliation=data.get("affiliation"),
                    participant_type=data["participant_type"],
                )

                session.add(participant)
                session.commit()

                return {"message": "External participant registered", "id": participant.id}, 201
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# USER EVENTS
# GET /api/users/<user_id>/events
# ============================================================


class UserEventsResource(Resource):
    @require_auth
    def get(self, user_id):
        try:
            user_id = _int_or_400(user_id, "user_id")
            if isinstance(user_id, tuple):
                return user_id

            with get_session() as session:
                registrations = session.query(EventRegistration).filter_by(user_id=user_id).all()
                return [serialize_event(r.event) for r in registrations], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# EVENT SESSIONS
# GET    /api/events/<event_id>/sessions
# POST   /api/events/<event_id>/sessions
# DELETE /api/events/<event_id>/sessions
# ============================================================


class EventSessionsResource(Resource):
    @require_auth
    def get(self, event_id):
        try:
            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                sessions = session.query(EventSession).filter_by(event_id=event.id).all()
                return [serialize_session(s) for s in sessions], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

    @require_auth
    @require_club_role("event_coordinator", "president")
    def post(self, event_id):
        try:
            data = _json_data()

            required_fields = ["title", "start_at", "end_at"]
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return {"message": f"Missing required fields: {', '.join(missing)}"}, 400

            try:
                start_at = _parse_iso(data["start_at"], "start_at")
                end_at = _parse_iso(data["end_at"], "end_at")
            except ValueError as e:
                return {"message": str(e)}, 400

            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                session_obj = EventSession(
                    event_id=event.id,
                    title=data["title"],
                    description=data.get("description"),
                    venue=data.get("venue"),
                    start_at=start_at,
                    end_at=end_at,
                    session_order=data.get("session_order", 1),
                )

                session.add(session_obj)
                session.commit()

                return {"message": "Session created", "id": session_obj.id}, 201
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

    @require_auth
    @require_club_role("event_coordinator", "president")
    def delete(self, event_id):
        try:
            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                session.query(EventSession).filter_by(event_id=event.id).delete()
                session.commit()

                return {"message": "Sessions deleted"}, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# ATTENDANCE
# GET  /api/events/<event_id>/attendance
# POST /api/events/<event_id>/attendance
# ============================================================


class EventAttendanceResource(Resource):
    @require_auth
    @require_club_role(
        "member",
        "volunteer_coordinator",
        "event_coordinator",
        "secretary",
        "treasurer",
        "vice_president",
        "president",
    )
    def get(self, event_id):
        try:
            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                records = session.query(AttendanceRecord).filter_by(event_id=event.id).all()
                return [
                    {
                        "id": r.id,
                        "event_id": r.event_id,
                        "user_id": r.user_id,
                        "checked_in_at": r.checked_in_at.isoformat() if r.checked_in_at else None,
                    }
                    for r in records
                ], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

    @require_auth
    @require_club_role("event_coordinator", "volunteer_coordinator", "president")
    def post(self, event_id):
        try:
            data = _json_data()

            if not data.get("user_id"):
                return {"message": "user_id is required"}, 400

            user_id = _int_or_400(data["user_id"], "user_id")
            if isinstance(user_id, tuple):
                return user_id

            with get_session() as session:
                event, error = get_event_or_404(session, event_id)
                if error:
                    return error

                record = AttendanceRecord(
                    event_id=event.id,
                    user_id=user_id,
                    recorded_by=g.current_user.id,
                )

                session.add(record)
                session.commit()

                return {"message": "Checked in", "id": record.id}, 201
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# DELETE ATTENDANCE
# DELETE /api/attendance/<record_id>
# ============================================================


class AttendanceDeleteResource(Resource):
    @require_auth
    @require_club_role("event_coordinator", "president")
    def delete(self, record_id):
        try:
            with get_session() as session:
                record_id = _int_or_400(record_id, "record_id")
                if isinstance(record_id, tuple):
                    return record_id

                record, error = get_attendance_or_404(session, record_id)
                if error:
                    return error

                session.delete(record)
                session.commit()

                return {"message": "Check-in removed"}, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


# ============================================================
# ROUTE REGISTRATION
# ============================================================


api.add_resource(EventListResource, "/events")
api.add_resource(EventDetailResource, "/events/<int:event_id>")
api.add_resource(EventRegistrationResource, "/events/<int:event_id>/register")
api.add_resource(ExternalRegistrationResource, "/events/<int:event_id>/register-external")
api.add_resource(UserEventsResource, "/users/<int:user_id>/events")
api.add_resource(EventSessionsResource, "/events/<int:event_id>/sessions")
api.add_resource(EventAttendanceResource, "/events/<int:event_id>/attendance")
api.add_resource(AttendanceDeleteResource, "/attendance/<int:record_id>")
