from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import bcrypt

from app.database.database import get_session
from app.database.models.auth import User
from app.database.models.clubs import Club
from app.database.models.events import Event
from app.database.models.support import SupportTicket
from app.database.models.audit import AuditLog
from app.database.models.academics import Department
from app.database.models.university import UniversityDomain, University
from app.database.enums import UserRole, TicketStatus


from app.utils.email import send_email
from app.utils.helpers import save_base64_image
from app.middleware.auth_middleware import require_auth ,require_role

club_bp = Blueprint('clubs', __name__)


@club_bp.route('/',methods=['GET'])
@require_auth
def get_all_clubs():
    try:
        with get_session() as db:
            clubs = db.query(Club).all()
            if not clubs:
                return {"message": "No club founds"}, 404
            result = [{
                "id": club.id,
                "name": club.name,
                "description": club.description,
                "category": club.category,
                "university_id": club.university_id,
                "status": club.status,
                "logo_url": club.logo_url,
                "banner": club.banner,
                "member_count_cache": club.member_count_cache,
                "slug": club.slug,
                "objectives": club.objectives,
                "faculty_advisor_id": club.faculty_advisor_id,
                "created_at": club.created_at,
                "updated_at": club.updated_at
            } for club in clubs ]

    except Exception as e:
        print(e)
        return {"message" : f"Error : {e}"}, 500
    
    return jsonify(result)
