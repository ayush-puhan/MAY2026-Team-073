from functools import wraps

from flask import request, g, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.database.session_manager import validate_stored_token
from app.database.database import get_session
from app.database.models import User, ClubMembership, Event, AttendanceRecord, VolunteerAssignment, Budget
from app.database.enums import MembershipStatus


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200

        try:
            verify_jwt_in_request()
        except Exception as e:
            return {"message": f"Authentication failed: {str(e)}"}, 401

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing Bearer token"}, 401

        token = auth_header.split(" ", 1)[1].strip()

        if not validate_stored_token(token):
            return {"message": "Token has been revoked or expired session"}, 401

        user_id = get_jwt_identity()

        with get_session() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if user is None:
                return {"message": "User not found"}, 404
            g.current_user = user

        return fn(*args, **kwargs)

    return wrapper
def require_role(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "current_user"):
                return {"message": "Authentication required"}, 401

            if g.current_user.role not in allowed_roles:
                return {"message": "Permission denied"}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def _to_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_json_data():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def resolve_club_id(db, kwargs):
    """
    Resolve club_id from supported locations.

    Resolution order:
    1. kwargs: club_id
    2. query params: club_id
    3. JSON body: club_id
    4. kwargs/body event_id -> event.club_id
    5. kwargs record_id -> attendance.event.club_id
    6. kwargs id -> volunteer_assignment.event.club_id
    """

    json_data = _extract_json_data()

    candidates = [
        kwargs.get("club_id"),
        request.args.get("club_id"),
        json_data.get("club_id"),
    ]
    for value in candidates:
        club_id = _to_int(value)
        if club_id is not None:
            return club_id

    event_id = kwargs.get("event_id") or json_data.get("event_id")
    event_id = _to_int(event_id)
    if event_id is not None:
        event = db.query(Event).filter_by(id=event_id).first()
        if not event:
            return {"message": "Event not found"}, 404
        return event.club_id
    budget_id = (
        kwargs.get("budget_id")
        or request.args.get("budget_id")
        or json_data.get("budget_id")
    )

    budget_id = _to_int(budget_id)

    if budget_id is not None:
        budget = db.query(Budget).filter_by(id=budget_id).first()
        if not budget:
            return {"message": "Budget not found"}, 404
        return budget.club_id
    record_id = kwargs.get("record_id")
    record_id = _to_int(record_id)
    if record_id is not None:
        attendance = db.query(AttendanceRecord).filter_by(id=record_id).first()
        if not attendance:
            return {"message": "Attendance record not found"}, 404
        event = db.query(Event).filter_by(id=attendance.event_id).first()
        if not event:
            return {"message": "Event not found"}, 404
        return event.club_id

    task_id = kwargs.get("id")
    task_id = _to_int(task_id)
    if task_id is not None:
        task = db.query(VolunteerAssignment).filter_by(id=task_id).first()
        if not task:
            return {"message": "Volunteer task not found"}, 404
        event = db.query(Event).filter_by(id=task.event_id).first()
        if not event:
            return {"message": "Event not found"}, 404
        return event.club_id

    return None


def require_club_role(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "current_user"):
                return {"message": "Authentication required"}, 401

            if not allowed_roles:
                return {"message": "No club roles configured"}, 500

            with get_session() as db:
                resolved = resolve_club_id(db, kwargs)

                if isinstance(resolved, tuple):
                    return resolved

                if resolved is None:
                    return {"message": "Club ID missing"}, 400

                club_id = _to_int(resolved)
                if club_id is None:
                    return {"message": "Invalid club ID"}, 400

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.user_id == g.current_user.id,
                        ClubMembership.club_id == club_id,
                        ClubMembership.status == MembershipStatus.APPROVED,
                    )
                    .first()
                )

                if not membership:
                    return {"message": "You are not an approved member of this club"}, 403

                club_role = membership.role_in_club.value if hasattr(membership.role_in_club, "value") else membership.role_in_club

                if club_role not in allowed_roles:
                    return {"message": "Insufficient club permissions"}, 403

                g.club_id = club_id
                g.club_role = club_role
                g.club_membership = membership

            return fn(*args, **kwargs)

        return wrapper

    return decorator


# Example usage:
# @app.get("/clubs/<int:club_id>/events")
# @require_auth
# @require_club_role("president", "secretary")
# def list_events(club_id):
#     ...