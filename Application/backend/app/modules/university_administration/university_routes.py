from flask import Blueprint, request, jsonify
from app.database.database import get_session
from app.database.models.university import UniversityDomain
from app.middleware.auth_middleware import require_auth ,require_role

university_bp = Blueprint('university', __name__)

@university_bp.route('/domains', methods=['GET'])
def get_university_domains():
    with get_session() as session:
        universities = session.query(UniversityDomain).all()
        return jsonify([
            {
                "university_id" : university.university_id,
                "domain" : university.domain
            } for university in universities
        ]) , 200
    
university_admin_bp = Blueprint('university_admin', __name__)
