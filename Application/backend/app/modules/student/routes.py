from flask import Blueprint, jsonify
from app.database.database import get_session
from app.database.models.academics import Department, Program
from app.database.models.interests import Interest

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

@student_bp.route('/departments', methods=['GET'])
def get_departments():
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

@student_bp.route('/programs', methods=['GET'])
def get_programs():
    with get_session() as session:
        programs = session.query(Program).all()
        return jsonify([
            {
                "id": prog.id,
                "department_id": prog.department_id,
                "name": prog.name
            } for prog in programs
        ]), 200

@student_bp.route('/interests', methods=['GET'])
def get_interests():
    with get_session() as session:
        interests = session.query(Interest).all()
        return jsonify([
            {
                "id": interest.id,
                "name": interest.name
            } for interest in interests
        ]), 200
