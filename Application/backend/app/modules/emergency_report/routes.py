from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime

from app.database.models.support import EmergencyReport
from app.database.enums import EmergencyCategory, EmergencyStatus, UserRole
from app.database.database import get_session

from app.middleware.auth_middleware import require_auth, require_role


em_report = Blueprint('emergency_reports', __name__)


@em_report.route("",methods=['POST'])
@require_auth
def make_emergency_report():
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        category = data.get('category')
        description = data.get('description')
        status = data.get('status')
        handled_by = data.get('handled_by')
        created_at = data.get('created_at')
        resolved_at = data.get('resolved_at')
        if not event_id and not category and not description and not status and not created_at:
            return {'message' : 'Required field can not be empty or null value.'}, 400
        with get_session() as db:
            new_em_report = EmergencyReport(
                reported_by=user_id,
                event_id=event_id,
                category=category,
                description=description,
                status=status.upper(),
                created_at = datetime.utcnow(),
                resolved_at = resolved_at if resolved_at else None
            )

            result={
                'message' : 'Reported Successfully.' 
            }

    except Exception as e:
        msg = {'message' : f'Error : {e}'}
        print(msg)
        return msg, 500
    return result, 200


@em_report.route("",methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_get_emergency_report():
    user_id = get_jwt_identity()
    try:
        status = request.args.get('status',type=str)
        category = request.args.get('category',type=str)
        if not status and not category:
            return {'message' : 'Required args can not be empty or null value.'}, 400
        with get_session() as db:
            all_em_reports = db.query(EmergencyReport).filter_by(status=status,category=category).all()

            result = [
                {
                    "id": rep.id,
                    "reported_by": rep.reported_by,
                    "event_id": rep.event_id,
                    "category": rep.category.upper(),
                    "description": rep.description,
                    "status": rep.status.upper(),
                    "handled_by": None,
                    "created_at": rep.created_at,
                    "resolved_at": None
                } for rep in all_em_reports
            ]
    except Exception as e:
        msg = {'message' : f'Error : {e}'}
        print(msg)
        return msg, 500
    return jsonify(result), 200


@em_report.route("/<int:report_id>/status",methods=['PATCH'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_update_emergency_report(report_id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        status = data.get('status')
        handled_by = data.get('handled_by')
        #resolved_at = data.get('resolved_at')
        if not status and not handled_by:
            return {"message" : "Required field can not be empty."}, 400
        with get_session() as db:
            report = db.query(EmergencyReport).filter_by(id=report_id).first()
            if not report :
                return {"message" : "Not Found particular resource."}, 400
            report.status = status.upper()
            report.handled_by = handled_by if handled_by else user_id
            report.resolved_at = datetime.utcnow()

            db.add(report)
            db.commit()

            result={
                'message' : 'Updated Successfully.' 
            }
    except Exception as e:
        msg = {'message' : f'Error : {e}'}
        print(msg)
        return msg, 500
    return jsonify(result), 200

@em_report.route("/active",methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_get_active_emergency_report():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            all_em_reports = db.query(EmergencyReport).filter(EmergencyReport.status != EmergencyStatus.RESOLVED).all()
            result = [
                {
                    "id": rep.id,
                    "reported_by": rep.reported_by,
                    "event_id": rep.event_id,
                    "category": rep.category.upper(),
                    "description": rep.description,
                    "status": rep.status.upper(),
                    "handled_by": None,
                    "created_at": rep.created_at,
                    "resolved_at": None
                } for rep in all_em_reports
            ]
    except Exception as e:
        msg = {'message' : f'Error : {e}'}
        print(msg)
        return msg, 500
    return jsonify(result), 200



