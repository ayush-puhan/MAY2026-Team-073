import json
from flask import request, Blueprint
from flask_restful import Api, Resource
from flask_jwt_extended import get_jwt_identity

from app.database.database import get_session
from app.database.models.auth import User
from app.database.models.academics import StudentProfile
from app.database.models.interests import UserInterest
from app.middleware.auth_middleware import require_auth
# ----------------------------------------------------
# ClubConnect AI Module
# Integrated by AI Backend
# Module Owner: AI Assistant / RAG Pipeline
# ----------------------------------------------------
from app.modules.ai_services.cache import invalidate_user_cache

users_bp = Blueprint('users', __name__)
user_api = Api(users_bp)

class ProfileResource(Resource):
    @require_auth
    def get(self):
        user_id = get_jwt_identity()
        if not user_id:
            return {"message": "Invalid session identity."}, 401
            
        with get_session() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return {"message": "User not found."}, 404
                
            # Base payload
            payload = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
                "auth_provider": user.auth_provider.value if hasattr(user.auth_provider, 'value') else user.auth_provider,
                "has_password": bool(user.password_hash and user.password_hash != "GOOGLE_SSO"),
                "phone": user.phone,
                "roll_number": user.roll_number,
                "profile_photo_url": user.profile_photo_url,
                "color_blind_mode": user.color_blind_mode,
                "department_id": user.department_id,
                "email_verified": user.email_verified,
                "dob": user.dob.isoformat() if user.dob else None,
                "gender": user.gender.value if hasattr(user.gender, 'value') else user.gender,
                "accessibility_prefs": user.accessibility_prefs
            }
            
            # Append nested student profile if it exists
            if user.student_profile:
                payload["student_profile"] = {
                    "program_id": user.student_profile.program_id,
                    "academic_year": user.student_profile.academic_year,
                    "semester": user.student_profile.semester,
                    "batch": user.student_profile.batch,
                    "section": user.student_profile.section,
                    "institutional_email": user.student_profile.institutional_email,
                    "is_verified": user.student_profile.is_verified
                }
            
            # Append nested interests
            payload["interests"] = [ui.interest_id for ui in user.interest_links]
            
            return payload, 200

    @require_auth
    def patch(self):
        user_id = get_jwt_identity()
        if not user_id:
            return {"message": "Invalid session identity."}, 401
            
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400
            
        with get_session() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return {"message": "User not found."}, 404
                
            # 1. Update basic scalar fields on User
            allowed_fields = [
                'full_name', 'phone', 'dob', 'gender', 'roll_number', 
                'profile_photo_url', 'color_blind_mode', 'department_id',
                'accessibility_prefs'
            ]
            from datetime import datetime
            
            for field in allowed_fields:
                if field in data:
                    value = data[field]
                    if field == 'dob':
                        if value:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                return {"message": "Invalid DOB format. Use YYYY-MM-DD."}, 400
                        else:
                            value = None
                    elif field == 'department_id':
                        if value == '':
                            value = None
                        elif value is not None:
                            try:
                                value = int(value)
                            except ValueError:
                                return {"message": "Invalid department ID format."}, 400
                    elif field in ['gender', 'roll_number']:
                        if value == '':
                            value = None
                    setattr(user, field, value)
                    
            # 2. Update or create nested StudentProfile
            if 'student_profile' in data:
                sp_data = data['student_profile']
                
                # Check if we have a valid program_id before trying to create a new profile
                prog_id = sp_data.get('program_id')
                has_prog_id = prog_id is not None and prog_id != ''
                
                if not user.student_profile and has_prog_id:
                    user.student_profile = StudentProfile(user_id=user.id)
                
                if user.student_profile:
                    sp_fields = [
                        'program_id', 'academic_year', 'semester', 
                        'batch', 'section', 'institutional_email'
                    ]
                    for field in sp_fields:
                        if field in sp_data:
                            val = sp_data[field]
                            if field in ['program_id', 'academic_year', 'semester']:
                                if val == '':
                                    val = None
                                elif val is not None:
                                    try:
                                        val = int(val)
                                    except ValueError:
                                        return {"message": f"Invalid {field} format."}, 400
                            
                            # program_id is NOT NULL in db, don't set it to None
                            if field == 'program_id' and val is None:
                                continue
                                
                            setattr(user.student_profile, field, val)
            
            # 3. Update Interests (complete replacement)
            if 'interests' in data:
                # Clear old interests
                db.query(UserInterest).filter_by(user_id=user.id).delete()
                # Insert new interests
                for interest_id in data['interests']:
                    try:
                        parsed_interest_id = int(interest_id)
                        db.add(UserInterest(user_id=user.id, interest_id=parsed_interest_id))
                    except ValueError:
                        return {"message": "Invalid interest ID format."}, 400
            
            from sqlalchemy.exc import IntegrityError
            try:
                db.commit()
                # Phase 6A (AI module): profile changed, so this user's
                # cached AI responses (e.g. "Profile & Account" answers)
                # could be stale - invalidate only this user's entries,
                # never a full cache flush.
                invalidate_user_cache(user.id)
                return {"message": "Profile updated successfully"}, 200
            except IntegrityError as e:
                db.rollback()
                return {"message": "A database integrity error occurred (e.g. duplicate roll number or email, or invalid ID)."}, 400
    @require_auth
    def delete(self):
        user_id = get_jwt_identity()
        if not user_id:
            return {"message": "Invalid session identity."}, 401
            
        with get_session() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return {"message": "User not found."}, 404
                
            db.delete(user)
            db.commit()
            return {"message": "User account permanently deleted."}, 200

user_api.add_resource(ProfileResource, '/profile')
