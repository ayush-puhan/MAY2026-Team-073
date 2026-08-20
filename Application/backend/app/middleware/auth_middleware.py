from functools import wraps

from flask import request, g, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.database.session_manager import validate_stored_token
from app.database.database import get_session
from app.database.models import User, ClubMembership, Event, AttendanceRecord, VolunteerAssignment, Budget,ClubJoinApplication, Committee, Club
from app.database.enums import MembershipStatus, UserRole


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
        
    # Check for event_id in kwargs or JSON body
    event_id = kwargs.get("event_id") or json_data.get("event_id")
    event_id = _to_int(event_id)
    if event_id is not None:
        event = db.query(Event).filter_by(id=event_id).first()
        if not event:
            return {"message": "Event not found"}, 404
        return event.club_id
    
    # Check for budget_id in kwargs or JSON body
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
    
    # Check for attendance record ID in kwargs
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

    application_id = kwargs.get("application_id") or request.args.get("application_id") or json_data.get("application_id")
    application_id = _to_int(application_id)
    if application_id is not None:
        from app.database.models.applications import ClubJoinApplication
        application = db.query(ClubJoinApplication).filter_by(id=application_id).first()
        if not application:
            return {"message": "Application not found"}, 404
        return application.club_id

    committee_id = kwargs.get("committee_id") or request.args.get("committee_id") or json_data.get("committee_id")
    committee_id = _to_int(committee_id)
    if committee_id is not None:
        from app.database.models import Committee
        committee = db.query(Committee).filter_by(id=committee_id).first()
        if not committee:
            return {"message": "Committee not found"}, 404
        return committee.club_id

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
    
    # Check for membership ID in kwargs
    membership_id = _to_int(kwargs.get("membershipId"))

    if membership_id is not None:
        membership = (
            db.query(ClubMembership)
            .filter_by(id=membership_id)
            .first()
        )

        if membership:
            return membership.club_id

    # Check for application ID in kwargs

    application_id = _to_int(kwargs.get("applicationId"))

    if application_id is not None:
        application = (
            db.query(ClubJoinApplication)
            .filter_by(id=application_id)
            .first()
        )

        if application:
            return application.club_id
    # Check for committee ID in kwargs
    committee_id = _to_int(kwargs.get("committeeId"))

    if committee_id is not None:
        committee = (
            db.query(Committee)
            .filter_by(id=committee_id)
            .first()
        )

        if committee:
            return committee.club_id
        
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

def require_club_role_or_faculty_advisor(*allowed_roles):
    """
    Like require_club_role, but also grants access to the faculty advisor
    of the resolved club (who has no ClubMembership row to check against).
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "current_user"):
                return {"message": "Authentication required"}, 401

            with get_session() as db:
                resolved = resolve_club_id(db, kwargs)

                if isinstance(resolved, tuple):
                    return resolved

                if resolved is None:
                    return {"message": "Club ID missing"}, 400

                club_id = _to_int(resolved)
                if club_id is None:
                    return {"message": "Invalid club ID"}, 400

                if g.current_user.role == UserRole.FACULTY_ADVISOR:
                    club = db.query(Club).filter_by(id=club_id).first()
                    if club and club.faculty_advisor_id == g.current_user.id:
                        g.club_id = club_id
                        g.club_role = "faculty_advisor"
                        return fn(*args, **kwargs)

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

                if allowed_roles and club_role not in allowed_roles:
                    return {"message": "Insufficient club permissions"}, 403

                g.club_id = club_id
                g.club_role = club_role
                g.club_membership = membership

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def _require_club_role(*allowed_roles):
    """
    If no roles are provided, only checks that the user belongs to the club.
    Otherwise checks that the user's club role is one of the allowed roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            # Club ID can come from URL or request body
            club_id = kwargs.get("club_id")
            if club_id is None:
                return {"error": "club_id is required"}, 400
            with get_session() as session:
                membership = ( session.query(ClubMembership).filter(
                        ClubMembership.club_id == club_id,
                        ClubMembership.user_id == user_id,
                    ).first()
                )
                if membership is None:
                    return {"error": "You are not a member of this club"}, 403
                if allowed_roles and membership.role_in_club not in allowed_roles:
                    return {"error": "Insufficient club permissions"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
# Example usage:
# @app.get("/clubs/<int:club_id>/events")
# @require_auth
# @require_club_role("president", "secretary")
# def list_events(club_id):
#     ...