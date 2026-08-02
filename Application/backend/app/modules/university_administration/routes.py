from flask import Blueprint, jsonify
from app.database.database import get_session
from app.database.models.university import UniversityDomain
from app.middleware.auth_middleware import require_auth ,require_role

university_bp = Blueprint('university', __name__)

@university_bp.route('/domains', methods=['GET'])
@require_auth
def get_university_domains():
    with get_session() as session:
        universities = session.query(UniversityDomain).all()
        return jsonify([
            {
                "university_id" : university.university_id,
                "domain" : university.domain
            } for university in universities
        ]) , 200