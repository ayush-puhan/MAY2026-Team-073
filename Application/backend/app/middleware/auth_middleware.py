from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from app.database.session_manager import validate_stored_token

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
