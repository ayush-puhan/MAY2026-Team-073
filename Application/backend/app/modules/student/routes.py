from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from app.database.database import get_session
from app.database.models.academics import Department, Program
from app.database.models.interests import Interest
from app.middleware.auth_middleware import require_auth ,require_role

from app.database.enums import UserRole

student_bp = Blueprint('student', __name__)
student_api = Api(student_bp)

@student_bp.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    try:
        with get_session() as session:
            departments = session.query(Department).all()
            return jsonify([
                {
                    "id": dept.id,
                    "name": dept.name,
                    "code": dept.code,
                    "university_id": dept.university_id
                } for dept in departments
            ]), 200
    except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

@student_bp.route('/programs', methods=['GET'])
@require_auth
def get_programs():
    try:
        with get_session() as session:
            programs = session.query(Program).all()
            return jsonify([
                {
                    "id": prog.id,
                    "department_id": prog.department_id,
                    "name": prog.name
                } for prog in programs
            ]), 200
    except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

@student_bp.route('/interests', methods=['GET'])
@require_auth
def get_interests():
    try:
        with get_session() as session:
            interests = session.query(Interest).all()
            return jsonify([
                {
                    "id": interest.id,
                    "name": interest.name
                } for interest in interests
            ]), 200
    except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500
