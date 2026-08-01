from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from app.database.session_manager import validate_stored_token
from app.database.database import get_session
from app.database.models import User
from app.database.models import ClubMembership

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
        # current_user_id = get_jwt_identity()
            
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
            # Verify JWT exists
            try:
                verify_jwt_in_request()
            except Exception as e:
                return {"message": f"Authentication failed: {str(e)}"}, 401

            # User ID stored as JWT identity
            user_id = get_jwt_identity()

            with get_session() as db:
                user = db.query(User).filter_by(id=user_id).first()
                if user is None:
                    return {"message": "User not found"}, 404

                if user.role not in allowed_roles:
                    return {"message": "Permission denied"}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator 


def require_club_role(*allowed_roles):
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





