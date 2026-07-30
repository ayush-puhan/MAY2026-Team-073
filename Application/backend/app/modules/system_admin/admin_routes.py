from flask import Blueprint, jsonify, request
from app.database.database import get_session
from app.database.models.auth import User
from app.database.models.clubs import Club
from app.database.models.events import Event
from app.database.models.support import SupportTicket
from app.database.models.audit import AuditLog

from app.database.models.university import UniversityDomain
from app.middleware.auth_middleware import require_auth ,require_role
from app.database.enums import UserRole, TicketStatus

system_admin_bp = Blueprint('system_admin', __name__)

@system_admin_bp.route('/stats',methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def get_stats():
    try:
        with get_session() as db:
            total_users = db.query(User).count()
            active_users = db.query(User).filter_by(is_active = 1).count()
            total_clubs = db.query(Club).count()
            total_evetns = db.query(Event).count()
            open_tickets = db.query(SupportTicket).filter_by(status = TicketStatus.OPEN).count()

    except Exception as e:
        return {"message" : f"Error : {e}"}, 500
    
    return jsonify({
        "totalUsers" : total_users,
        "activeUsers" : active_users,
        "totalClubs" : total_clubs,
        "totalEvents" : total_evetns,
        "openTickets" : open_tickets
    }), 200




@system_admin_bp.route('/audit-logs',methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def get_audit_logs():
    limit = request.args.get("limit", default=10, type=int)

    try:
        with get_session() as db:
            audit_logs = db.query(AuditLog).limit(limit).all()
    except Exception as e:
        return {"message" : f"Error : {e}"}, 500
    
    return jsonify([
        {
            "id": audit.id,
            "user_id": audit.user_id,
            "university_id": audit.university_id,
            "action": audit.action,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
            "details": audit.details
        } for audit in audit_logs
    ]), 200