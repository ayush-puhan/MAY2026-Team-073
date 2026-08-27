"""
Calendar-related APIs.

Handles:
- Calendar event sessions
- Updating event sessions
- Deleting event sessions
- Google Calendar synchronization
"""

from datetime import timezone

from flask import Blueprint, request, g
from flask_restful import Api, Resource
from sqlalchemy import or_

from app.database.database import get_session
from app.database.models import (
    Event,
    EventSession,
    EventRegistration,
)
from app.middleware.auth_middleware import (
    require_auth,
    require_club_role,
)


calendar_bp = Blueprint("calendar", __name__)
api = Api(calendar_bp)


# ============================================================
# HELPERS
# ============================================================


def _json_data():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _parse_iso(dt_value, field_name):
    """
    Parse an ISO-8601 datetime string.

    Example:
    2026-08-15T09:00:00
    2026-08-15T09:00:00+05:30
    """
    if not dt_value:
        return None

    from datetime import datetime

    try:
        return datetime.fromisoformat(dt_value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid datetime format for {field_name}"
        )


def _int_or_400(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        return {
            "message": f"Invalid {field_name}"
        }, 400


def _parse_bool(value, default=False):
    """
    Converts query values such as:
    true, false, 1, 0, yes, no, on, off
    """
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes", "on"}:
        return True

    if normalized in {"false", "0", "no", "off"}:
        return False

    return default


def get_event_session_or_404(session, session_id):
    event_session = (
        session.query(EventSession)
        .filter(EventSession.id == session_id)
        .first()
    )

    if not event_session:
        return None, {
            "message": "Event session not found"
        }, 404

    return event_session, None, None


def get_event_or_404(session, event_id):
    event = (
        session.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        return None, {
            "message": "Event not found"
        }, 404

    return event, None, None


def enum_value(value):
    if value is None:
        return None

    return value.value if hasattr(value, "value") else value


def _to_google_datetime(value):
    """
    Google Calendar expects an RFC3339 datetime.

    Naive database datetimes are treated as UTC. If your database
    stores local time, replace this behavior with your application's
    configured timezone.
    """
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.isoformat()


def serialize_calendar_session(
    event_session,
    is_registered=False,
    has_conflict=False,
):
    event = event_session.event
    club = event.club if event else None
    university = club.university if club else None

    return {
        "session_id": event_session.id,
        "session_title": event_session.title,
        "event_id": event.id if event else None,
        "event_title": event.title if event else None,
        "club_id": club.id if club else None,
        "club_name": club.name if club else None,
        "club_logo": (
            getattr(club, "logo_url", None)
            if club
            else None
        ),
        "university_id": (
            university.id
            if university
            else getattr(club, "university_id", None)
        ),
        "venue": (
            event_session.venue
            or event.venue
            if event
            else event_session.venue
        ),
        "start_at": (
            event_session.start_at.isoformat()
            if event_session.start_at
            else None
        ),
        "end_at": (
            event_session.end_at.isoformat()
            if event_session.end_at
            else None
        ),
        "is_public": (
            bool(event.is_public)
            if event
            else False
        ),
        "is_registered": is_registered,
        "has_conflict": has_conflict,
        "status": enum_value(event.status) if event else None,
    }


def serialize_google_event(event_session):
    """
    Converts an EventSession into a Google Calendar event body.

    Google Calendar's events.insert API requires start and end values.
    """
    event = event_session.event
    club = event.club if event else None

    description_parts = []

    if event and event.description:
        description_parts.append(event.description)

    if event_session.description:
        description_parts.append(event_session.description)

    description_parts.append(
        f"Event ID: {event.id if event else event_session.event_id}"
    )

    return {
        "summary": (
            f"{event.title} - {event_session.title}"
            if event
            else event_session.title
        ),
        "description": "\n\n".join(description_parts),
        "location": (
            event_session.venue
            or event.venue
            if event
            else event_session.venue
        ),
        "start": {
            "dateTime": _to_google_datetime(
                event_session.start_at
            ),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": _to_google_datetime(
                event_session.end_at
            ),
            "timeZone": "UTC",
        },
        "extendedProperties": {
            "private": {
                "application": "club-event-management",
                "event_id": str(
                    event.id if event else event_session.event_id
                ),
                "event_session_id": str(event_session.id),
                "club_id": str(club.id) if club else "",
            }
        },
    }


def get_google_calendar_service(user):
    """
    Return an authenticated Google Calendar service for the user.

    Implement this function according to your authentication design.

    For example, it may:
    1. Load the user's stored Google OAuth credentials.
    2. Refresh the credentials if expired.
    3. Build a Google Calendar API service.

    Expected return value:

        google_service

    The service must support:

        service.events().insert(
            calendarId="primary",
            body=google_event
        ).execute()
    """

    # Replace this with your real OAuth implementation.
    return None


# ============================================================
# GET CALENDAR EVENTS
# GET /api/calendar/events
# ============================================================


class CalendarEventsResource(Resource):
    """
    Query parameters:

    show_public=true|false
    university_id=<id>
    club_id=<id>
    """

    @require_auth
    def get(self):
        show_public = _parse_bool(
            request.args.get("show_public"),
            default=False,
        )

        university_id = request.args.get("university_id")
        club_id = request.args.get("club_id")

        if university_id is not None:
            university_id = _int_or_400(
                university_id,
                "university_id",
            )

            if isinstance(university_id, tuple):
                return university_id

        if club_id is not None:
            club_id = _int_or_400(
                club_id,
                "club_id",
            )

            if isinstance(club_id, tuple):
                return club_id

        with get_session() as session:
            from sqlalchemy.orm import joinedload
            from app.database.models import Club
            query = (
                session.query(EventSession)
                .options(
                    joinedload(EventSession.event)
                    .joinedload(Event.club)
                    .joinedload(Club.university)
                )
                .join(Event, EventSession.event_id == Event.id)
                .join(Event.club)
            )

            if university_id is not None:
                query = query.filter(
                    Event.club.has(
                        university_id=university_id
                    )
                )

            if club_id is not None:
                query = query.filter(
                    Event.club_id == club_id
                )

            if show_public:
                """
                When show_public is true, return:
                - public events
                - private events where the current user is registered
                """
                query = query.filter(
                    or_(
                        Event.is_public.is_(True),
                        Event.registrations.any(
                            EventRegistration.user_id == g.current_user.id
                        ),
                    )
                )
            else:
                """
                When show_public is false, return:
                - ONLY events where the current user is registered
                """
                query = query.filter(
                    Event.registrations.any(
                        EventRegistration.user_id == g.current_user.id
                    )
                )

            event_sessions = (
                query
                .order_by(EventSession.start_at.asc())
                .all()
            )

            registered_event_ids = {
                registration.event_id
                for registration in (
                    session.query(EventRegistration)
                    .filter(
                        EventRegistration.user_id
                        == g.current_user.id
                    )
                    .all()
                )
            }

            registered_sessions = (
                session.query(EventSession)
                .join(Event, EventSession.event_id == Event.id)
                .join(
                    EventRegistration,
                    EventRegistration.event_id == Event.id,
                )
                .filter(
                    EventRegistration.user_id == g.current_user.id
                )
                .all()
            )

            response = []

            for current_session in event_sessions:
                current_event = current_session.event

                is_registered = (
                    current_event.id
                    in registered_event_ids
                )

                has_conflict = False
                for reg_session in registered_sessions:
                    if reg_session.id != current_session.id:
                        if (reg_session.start_at < current_session.end_at and 
                            reg_session.end_at > current_session.start_at):
                            has_conflict = True
                            break

                response.append(
                    serialize_calendar_session(
                        current_session,
                        is_registered=is_registered,
                        has_conflict=has_conflict
                    )
                )

            return response, 200


# ============================================================
# UPDATE / DELETE EVENT SESSION
# PATCH /api/event-sessions/<session_id>
# DELETE /api/event-sessions/<session_id>
# ============================================================


class EventSessionDetailResource(Resource):

    @require_auth
    @require_club_role(
        "event_coordinator",
        "president",
    )
    def patch(self, session_id):
        data = _json_data()

        with get_session() as session:
            event_session, error, status_code = (
                get_event_session_or_404(
                    session,
                    session_id,
                )
            )

            if error:
                return error, status_code

            if "title" in data:
                if not isinstance(data["title"], str):
                    return {
                        "message": "title must be a string"
                    }, 400

                if not data["title"].strip():
                    return {
                        "message": "title cannot be empty"
                    }, 400

                event_session.title = data["title"].strip()

            if "description" in data:
                event_session.description = data["description"]

            if "venue" in data:
                event_session.venue = data["venue"]

            if "session_order" in data:
                session_order = _int_or_400(
                    data["session_order"],
                    "session_order",
                )

                if isinstance(session_order, tuple):
                    return session_order

                if session_order < 1:
                    return {
                        "message": (
                            "session_order must be at least 1"
                        )
                    }, 400

                event_session.session_order = session_order

            try:
                if "start_at" in data:
                    parsed_start_at = _parse_iso(
                        data["start_at"],
                        "start_at",
                    )

                    if parsed_start_at is None:
                        return {
                            "message": (
                                "start_at cannot be empty"
                            )
                        }, 400

                    event_session.start_at = parsed_start_at

                if "end_at" in data:
                    parsed_end_at = _parse_iso(
                        data["end_at"],
                        "end_at",
                    )

                    if parsed_end_at is None:
                        return {
                            "message": (
                                "end_at cannot be empty"
                            )
                        }, 400

                    event_session.end_at = parsed_end_at

            except ValueError as exc:
                return {
                    "message": str(exc)
                }, 400

            if (
                event_session.end_at
                < event_session.start_at
            ):
                return {
                    "message": (
                        "end_at must be greater than or equal "
                        "to start_at"
                    )
                }, 400

            session.commit()
            session.refresh(event_session)

            return {
                "message": (
                    "Event session updated successfully"
                ),
                "session": serialize_calendar_session(
                    event_session
                ),
            }, 200

    @require_auth
    @require_club_role(
        "event_coordinator",
        "president",
    )
    def delete(self, session_id):
        with get_session() as session:
            event_session, error, status_code = (
                get_event_session_or_404(
                    session,
                    session_id,
                )
            )

            if error:
                return error, status_code

            session.delete(event_session)
            session.commit()

            return {
                "message": (
                    "Event session deleted successfully"
                )
            }, 200


# ============================================================
# GOOGLE CALENDAR SYNC
# POST /api/calendar/sync-google
# ============================================================


class GoogleCalendarSyncResource(Resource):

    @require_auth
    def post(self):
        data = _json_data()

        event_id = data.get("event_id")
        session_ids = data.get("session_ids")
        calendar_id = data.get("calendar_id", "primary")

        if event_id is None and not session_ids:
            return {
                "message": (
                    "Either event_id or session_ids is required"
                )
            }, 400

        if event_id is not None and session_ids:
            return {
                "message": (
                    "Send either event_id or session_ids, "
                    "not both"
                )
            }, 400

        with get_session() as session:
            if event_id is not None:
                event_id = _int_or_400(
                    event_id,
                    "event_id",
                )

                if isinstance(event_id, tuple):
                    return event_id

                event, error, status_code = get_event_or_404(
                    session,
                    event_id,
                )

                if error:
                    return error, status_code

                event_sessions = (
                    session.query(EventSession)
                    .filter(
                        EventSession.event_id == event.id
                    )
                    .order_by(EventSession.start_at.asc())
                    .all()
                )

            else:
                if not isinstance(session_ids, list):
                    return {
                        "message": (
                            "session_ids must be an array"
                        )
                    }, 400

                if not session_ids:
                    return {
                        "message": (
                            "session_ids cannot be empty"
                        )
                    }, 400

                parsed_session_ids = []

                for value in session_ids:
                    parsed_id = _int_or_400(
                        value,
                        "session_id",
                    )

                    if isinstance(parsed_id, tuple):
                        return parsed_id

                    parsed_session_ids.append(parsed_id)

                event_sessions = (
                    session.query(EventSession)
                    .filter(
                        EventSession.id.in_(
                            parsed_session_ids
                        )
                    )
                    .order_by(EventSession.start_at.asc())
                    .all()
                )

                if not event_sessions:
                    return {
                        "message": (
                            "No event sessions found"
                        )
                    }, 404

            if not event_sessions:
                return {
                    "message": (
                        "The event has no sessions"
                    )
                }, 400

            google_service = get_google_calendar_service(
                g.current_user
            )

            if google_service is None:
                return {
                    "message": (
                        "Google Calendar is not connected "
                        "for this user"
                    ),
                    "required": [
                        "Google OAuth credentials",
                        "Google Calendar API service",
                    ],
                }, 501

            synced_events = []
            failed_events = []

            for event_session in event_sessions:
                google_event_body = serialize_google_event(
                    event_session
                )

                try:
                    google_event = (
                        google_service.events()
                        .insert(
                            calendarId=calendar_id,
                            body=google_event_body,
                        )
                        .execute()
                    )

                    synced_events.append(
                        {
                            "session_id": event_session.id,
                            "google_event_id": google_event.get(
                                "id"
                            ),
                            "html_link": google_event.get(
                                "htmlLink"
                            ),
                        }
                    )

                except Exception as exc:
                    failed_events.append(
                        {
                            "session_id": event_session.id,
                            "message": str(exc),
                        }
                    )

            if failed_events and not synced_events:
                return {
                    "message": (
                        "Google Calendar synchronization failed"
                    ),
                    "synced": [],
                    "failed": failed_events,
                }, 502

            return {
                "message": (
                    "Google Calendar synchronization completed"
                ),
                "synced": synced_events,
                "failed": failed_events,
            }, 200


# ============================================================
# ROUTE REGISTRATION
# ============================================================


api.add_resource(
    CalendarEventsResource,
    "/calendar/events",
)

api.add_resource(
    EventSessionDetailResource,
    "/event-sessions/<int:session_id>",
)

api.add_resource(
    GoogleCalendarSyncResource,
    "/calendar/sync-google",
)