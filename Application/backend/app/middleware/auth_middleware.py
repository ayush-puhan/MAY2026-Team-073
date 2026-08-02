from functools import wraps
from flask import request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from app.database.session_manager import validate_stored_token
from app.database.database import get_session
from app.database.models import User, ClubMembership, Event,AttendanceRecord
from app.database.enums import MembershipStatus


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 1. Verify standard JWT structure and signature using Flask-JWT-Extended
        try:
            verify_jwt_in_request()
        except Exception as e:
            return {"message": f"Authentication failed: {str(e)}"}, 401
            
        # 2. Extract the raw token string from the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing Bearer token"}, 401
            
        token = auth_header.split(" ")[1]
        
        # 3. Verify that this specific token is active in our AuthSession database table
        if not validate_stored_token(token):
            return {"message": "Token has been revoked or expired session"}, 401
            
        # Optional: you can pass the user_id to the endpoint via request if needed
        # 4. Load the authenticated user
        user_id = get_jwt_identity()

        with get_session() as db:
            user = db.query(User).filter_by(id=user_id).first()

            if user is None:
                return {"message": "User not found"}, 404

            # Make the current user available throughout this request
            g.current_user = user
            
        return fn(*args, **kwargs)
    return wrapper



def require_role(*allowed_roles):
    """
    use just after the require_auth decorator
    Example:
        @require_role("admin")
        @require_role("admin", "student")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if g.current_user.role not in allowed_roles:
                return {"message": "Permission denied"}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator 




def require_club_role(*allowed_roles):
    """
    Checks the authenticated user's role inside a specific club.

    Supports:
        /clubs/<club_id>/...
        ?club_id=<club_id>
        /events/<event_id>/...
        /attendance/<record_id>
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            if not hasattr(g, "current_user"):
                return {
                    "message": "Authentication required"
                }, 401

            with get_session() as db:

                # -------------------------------------------------
                # Determine club_id
                # -------------------------------------------------

                # 1. From URL or query parameter
                club_id = (
                    kwargs.get("club_id")
                    or request.args.get("club_id")
                )

                # 2. From event_id
                if not club_id and kwargs.get("event_id"):

                    event = (
                        db.query(Event)
                        .filter(
                            Event.id == kwargs["event_id"]
                        )
                        .first()
                    )

                    if not event:
                        return {
                            "message": "Event not found"
                        }, 404

                    club_id = event.club_id

                # 3. From attendance record
                if not club_id and kwargs.get("record_id"):

                    attendance = (
                        db.query(AttendanceRecord)
                        .filter(
                            AttendanceRecord.id == kwargs["record_id"]
                        )
                        .first()
                    )

                    if not attendance:
                        return {
                            "message": "Attendance record not found"
                        }, 404

                    event = (
                        db.query(Event)
                        .filter(
                            Event.id == attendance.event_id
                        )
                        .first()
                    )

                    if not event:
                        return {
                            "message": "Event not found"
                        }, 404

                    club_id = event.club_id

                if not club_id:
                    return {
                        "message": "Club ID missing"
                    }, 400

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.user_id == g.current_user.id,
                        ClubMembership.club_id == int(club_id),
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                    .first()
                )

                if not membership:
                    return {
                        "message": "You are not a member of this club"
                    }, 403

                user_club_role = (
                    membership.role_in_club.value
                    if hasattr(membership.role_in_club, "value")
                    else membership.role_in_club
                )

                if user_club_role not in allowed_roles:
                    return {
                        "message": "Insufficient club permissions"
                    }, 403

                g.club_membership = membership
                g.club_role = user_club_role

            return fn(*args, **kwargs)

        return wrapper

    return decorator

