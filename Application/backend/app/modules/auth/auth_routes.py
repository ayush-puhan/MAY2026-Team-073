import os
import bcrypt
from flask import request, Blueprint
from flask_restful import Api, Resource
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from datetime import datetime, timedelta
import random

from app.database.database import get_session
from app.database.models.auth import User, UserOTP
from app.database.session_manager import generate_and_store_token, delete_token
from app.middleware.auth_middleware import require_auth
from app.utils.email import send_email, send_welcome_email, send_otp_email

auth_bp = Blueprint('auth', __name__)
auth_api = Api(auth_bp)

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        if not email or not password or not full_name:
            return {"message": "Email, password, and full_name are required."}, 400

        with get_session() as db:
            existing_user = db.query(User).filter_by(email=email).first()
            if existing_user:
                if existing_user.is_active:
                    return {"message": "User with this email already exists."}, 400
                else:
                    # User exists but not active (abandoned OTP registration), allow overwrite
                    user_to_update = existing_user
            else:
                user_to_update = User(email=email, auth_provider="LOCAL")
                db.add(user_to_update)

            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user_to_update.password_hash = hashed_pw.decode('utf-8')
            user_to_update.full_name = full_name
            user_to_update.is_active = False  # Must verify OTP to activate
            user_to_update.email_verified = False
            
            db.commit()

            # Generate OTP
            otp_code = str(random.randint(100000, 999999))
            expires_at = datetime.utcnow() + timedelta(minutes=2)

            # Invalidate old OTPs for this user
            db.query(UserOTP).filter_by(user_id=user_to_update.id).delete()
            
            new_otp = UserOTP(
                user_id=user_to_update.id,
                otp_code=otp_code,
                expires_at=expires_at
            )
            db.add(new_otp)
            db.commit()

            # Send OTP email in background
            try:
                import threading
                threading.Thread(target=send_otp_email, args=(user_to_update.email, user_to_update.full_name, otp_code)).start()
            except Exception as e:
                print(f"Background email error: {e}")

            return {"message": "OTP sent successfully.", "email": email}, 201


class VerifyOTPResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp_code')

        if not email or not otp_code:
            return {"message": "Email and OTP code are required."}, 400

        with get_session() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user:
                return {"message": "User not found."}, 404

            if user.is_active:
                return {"message": "User is already verified and active."}, 400

            # Find valid OTP
            otp_record = db.query(UserOTP).filter_by(
                user_id=user.id,
                otp_code=otp_code
            ).first()

            if not otp_record:
                return {"message": "Invalid OTP code."}, 400

            if otp_record.expires_at < datetime.utcnow():
                return {"message": "OTP has expired. Please request a new one."}, 400

            # OTP is valid!
            user.is_active = True
            user.email_verified = True
            
            # Delete the OTP record as it's been used
            db.delete(otp_record)
            
            # Generate session token (auto-login)
            token = generate_and_store_token(user.id, session=db)
            db.commit()

            # Send the Welcome email
            try:
                import threading
                threading.Thread(target=send_welcome_email, args=(user.email, user.full_name)).start()
            except Exception as e:
                print(f"Background email error: {e}")

            return {
                "message": "Email verified successfully.",
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value if hasattr(user.role, 'value') else user.role,
                    "auth_provider": user.auth_provider,
                    "has_password": bool(user.password_hash and user.password_hash != "GOOGLE_SSO")
                }
            }, 200


class ResendOTPResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')

        if not email:
            return {"message": "Email is required."}, 400

        with get_session() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user:
                return {"message": "User not found."}, 404

            if user.is_active:
                return {"message": "User is already verified and active."}, 400

            # Generate new OTP
            otp_code = str(random.randint(100000, 999999))
            expires_at = datetime.utcnow() + timedelta(minutes=2)

            # Delete old ones
            db.query(UserOTP).filter_by(user_id=user.id).delete()
            
            new_otp = UserOTP(
                user_id=user.id,
                otp_code=otp_code,
                expires_at=expires_at
            )
            db.add(new_otp)
            db.commit()

            # Send OTP email
            try:
                import threading
                threading.Thread(target=send_otp_email, args=(user.email, user.full_name, otp_code)).start()
            except Exception as e:
                print(f"Background email error: {e}")

            return {"message": "A new OTP has been sent to your email."}, 200

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"message": "Email and password are required."}, 400

        with get_session() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user or not user.is_active:
                return {"message": "Invalid credentials or inactive account."}, 401

            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return {"message": "Invalid credentials."}, 401

            # Generate and store session token
            token = generate_and_store_token(user.id, session=db)
            
            return {
                "message": "Login successful",
                "access_token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value if user.role else "STUDENT",
                    "auth_provider": user.auth_provider,
                    "has_password": bool(user.password_hash and user.password_hash != "GOOGLE_SSO")
                }
            }, 200


class LogoutResource(Resource):
    @require_auth
    def post(self):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            deleted = delete_token(token)
            if deleted:
                return {"message": "Successfully logged out."}, 200
        return {"message": "Failed to log out."}, 400


class GoogleAuthResource(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return {"message": "Google token is required."}, 400

        google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
        if not google_client_id:
            return {"message": "Server configuration error: GOOGLE_CLIENT_ID not set."}, 500

        try:
            # The frontend (useGoogleLogin) sends an access_token by default, not an id_token
            import requests
            response = requests.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}")
            
            if response.status_code != 200:
                return {"message": "Invalid Google token."}, 401
                
            idinfo = response.json()
            
            email = idinfo['email']
            full_name = idinfo.get('name', 'Google User')
            google_id = idinfo['sub']

            with get_session() as db:
                user = db.query(User).filter_by(email=email).first()
                if not user:
                    # Create new user for this Google account
                    user = User(
                        email=email,
                        password_hash="GOOGLE_SSO",
                        full_name=full_name,
                        google_id=google_id,
                        email_verified=True,
                        auth_provider="GOOGLE"
                    )
                    db.add(user)
                    db.commit()
                    
                    # Send welcome email in background
                    try:
                        import threading
                        from app.utils.email import send_welcome_email
                        threading.Thread(target=send_welcome_email, args=(user.email, user.full_name)).start()
                    except Exception as e:
                        print(f"Background email error: {e}")
                elif not user.google_id:
                    # Link existing account to Google
                    user.google_id = google_id
                    db.commit()
                
                # Issue JWT token
                jwt_token = generate_and_store_token(user.id, session=db)
                
                return {
                    "message": "Google Login successful",
                    "access_token": jwt_token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role.value if user.role else "STUDENT"
                    }
                }, 200

        except ValueError:
            # Invalid token
            return {"message": "Invalid Google token."}, 401


class ForgotPasswordResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return {"message": "Email is required."}, 400
            
        with get_session() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user:
                return {"message": "If that email exists, a reset link has been sent."}, 200
                
            # Generate a short-lived reset token (using standard PyJWT or just JWTManager)
            # Since we just need a random token, let's use generate_and_store_token but we would need to distinguish it.
            # For simplicity, we just generate a 15 min token. We can use create_access_token.
            from flask_jwt_extended import create_access_token
            reset_token = create_access_token(identity=str(user.id), expires_delta=False) # Wait, we need an expiration. Let's just create a raw JWT or standard UUID for now.
            import uuid
            # Using a simplified approach: just send an email with the frontend link. 
            # In a real app we'd store the token. We'll send a mock token for now that they can use.
            # Assuming we had a ResetToken table, but we'll use AuthSession as a hack, or a signed JWT.
            from flask import current_app
            import jwt
            from datetime import datetime, timedelta
            
            reset_token = jwt.encode(
                {"reset_password": user.id, "exp": datetime.utcnow() + timedelta(minutes=15)},
                current_app.config["JWT_SECRET_KEY"],
                algorithm="HS256"
            )
            
            reset_link = f"{os.environ.get('VITE_FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={reset_token}"
            
            from app.utils.email import send_reset_password_email
            send_reset_password_email(
                to_email=email,
                full_name=user.full_name,
                reset_link=reset_link
            )
            
            return {"message": "If that email exists, a reset link has been sent."}, 200

class ResetPasswordResource(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return {"message": "Token and new password are required."}, 400
            
        from flask import current_app
        import jwt
        
        try:
            decoded = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            user_id = decoded.get("reset_password")
            
            if not user_id:
                return {"message": "Invalid token."}, 400
                
            with get_session() as db:
                user = db.query(User).filter_by(id=user_id).first()
                if not user:
                    return {"message": "User not found."}, 404
                    
                user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.commit()
                
            return {"message": "Password reset successfully."}, 200
            
        except jwt.ExpiredSignatureError:
            return {"message": "Reset link has expired."}, 400
        except jwt.InvalidTokenError:
            return {"message": "Invalid reset link."}, 400

from flask_jwt_extended import get_jwt_identity

class SetPasswordResource(Resource):
    @require_auth
    def post(self):
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return {"message": "New password is required."}, 400
            
        # Get user ID from the validated JWT token
        user_id = get_jwt_identity()
        
        if not user_id:
            return {"message": "Invalid session identity."}, 401
            
        with get_session() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return {"message": "User not found."}, 404
                
            user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.commit()
            
            return {"message": "Password set successfully."}, 200

# Register the routes
auth_api.add_resource(RegisterResource, '/register')
auth_api.add_resource(VerifyOTPResource, '/verify-otp')
auth_api.add_resource(ResendOTPResource, '/resend-otp')
auth_api.add_resource(LoginResource, '/login')
auth_api.add_resource(LogoutResource, '/logout')
auth_api.add_resource(GoogleAuthResource, '/google')
auth_api.add_resource(ForgotPasswordResource, '/forgot-password')
auth_api.add_resource(ResetPasswordResource, '/reset-password')
auth_api.add_resource(SetPasswordResource, '/set-password')
