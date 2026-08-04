from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.auth import User
from app.database.models.support import EmergencyReport
from app.database.enums import EmergencyCategory, EmergencyStatus, UserRole
from app.database.database import get_session

from app.middleware.auth_middleware import require_auth, require_role


em_report = Blueprint('emergency_reports', __name__)


@em_report.route('',methods=['POST'])
@require_auth
def make_emergency_report():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    category = data.get("category")
    description = data.get("description")
    event_id = data.get("event_id")

    if not category or not description:
        return jsonify({
            "message": "category and description are required"
        }), 400

    try:
        with get_session() as db:
            report = EmergencyReport(
                reported_by=user_id,     # set from JWT
                event_id=event_id,
                category=EmergencyCategory(category),
                description=description,
                status=EmergencyStatus.REPORTED
            )

            db.add(report)
            db.flush()
            db.commit(report)

            return jsonify({
                "message": "Emergency report submitted successfully",
                "report": {
                    "id": report.id,
                    "reported_by": report.reported_by,
                    "event_id": report.event_id,
                    "category": report.category.value,
                    "description": report.description,
                    "status": report.status.value,
                    "handled_by": report.handled_by,
                    "created_at": report.created_at.isoformat(),
                    "resolved_at": None
                }
            }), 201

    except ValueError:
        return jsonify({"message": "Invalid emergency category"}), 400

    except SQLAlchemyError:
        return jsonify({"message": "Failed to submit emergency report"}), 500


@em_report.route("", methods=["GET"])
@require_auth
def get_emergency_reports():
    status = request.args.get("status")
    category = request.args.get("category")
    reported_by = request.args.get("reported_by", type=int)

    Reporter = aliased(User)
    Handler = aliased(User)

    try:
        with get_session() as db:
            query = (
                db.query(
                    EmergencyReport,
                    Reporter.full_name.label("reporter_name"),
                    Handler.full_name.label("handler_name")
                )
                .outerjoin(
                    Reporter,
                    EmergencyReport.reported_by == Reporter.id
                )
                .outerjoin(
                    Handler,
                    EmergencyReport.handled_by == Handler.id
                )
            )

            if status:
                query = query.filter(
                    EmergencyReport.status == EmergencyStatus(status)
                )

            if category:
                query = query.filter(
                    EmergencyReport.category == EmergencyCategory(category)
                )

            if reported_by:
                query = query.filter(
                    EmergencyReport.reported_by == reported_by
                )

            reports = (
                query.order_by(EmergencyReport.created_at.desc())
                .all()
            )

            result = []

            for report, reporter_name, handler_name in reports:
                result.append({
                    "id": report.id,
                    "reported_by": report.reported_by,
                    "reporter_name": reporter_name or "Unknown",
                    "event_id": report.event_id,
                    "category": report.category.value,
                    "description": report.description,
                    "status": report.status.value,
                    "handled_by": report.handled_by,
                    "handler_name": handler_name or "Unassigned",
                    "created_at": report.created_at.isoformat(),
                    "resolved_at": (
                        report.resolved_at.isoformat()
                        if report.resolved_at
                        else None
                    )
                })
            print(len(result))
            return jsonify(result), 200

    except ValueError:
        return jsonify({"message": "Invalid filter value"}), 400

    except Exception:
        return jsonify({"message": "Failed to fetch emergency reports"}), 500


@em_report.route("/<int:report_id>/status",methods=['PATCH'])
@require_auth
#@require_role(UserRole.SYSTEM_ADMIN)
def admin_update_emergency_report(report_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    if not data or "status" not in data:
        return jsonify({"message": "status is required"}), 400

    try:
        new_status = EmergencyStatus(data["status"])
    except ValueError:
        return jsonify({"message": "Invalid emergency status"}), 400

    handled_by = data.get("handled_by")

    try:
        with get_session() as db:
            report = db.get(EmergencyReport, report_id)

            if not report:
                return jsonify({"message": "Emergency report not found"}), 404

            previously_resolved = (
                report.status == EmergencyStatus.RESOLVED
            )

            report.status = new_status

            # If handled_by is not supplied, use the authenticated user.
            report.handled_by = handled_by or user_id

            if (
                new_status == EmergencyStatus.RESOLVED
                and not previously_resolved
            ):
                report.resolved_at = datetime.utcnow()
            
            db.commit()

            return jsonify({
                "message": "Emergency report updated successfully",
                "report": {
                    "id": report.id,
                    "reported_by": report.reported_by,
                    "event_id": report.event_id,
                    "category": report.category.value,
                    "description": report.description,
                    "status": report.status.value,
                    "handled_by": report.handled_by,
                    "created_at": report.created_at.isoformat(),
                    "resolved_at": (
                        report.resolved_at.isoformat()
                        if report.resolved_at
                        else None
                    )
                }
            }), 200

    except Exception as e :
        return jsonify({"message": f"Failed to update emergency report : {e}"}), 500

@em_report.route("/active",methods=['GET'])
@require_auth
@require_role(UserRole.SYSTEM_ADMIN)
def admin_get_active_emergency_report():
    Reporter = aliased(User)
    Handler = aliased(User)

    try:
        with get_session() as db:
            reports = (
                db.query(
                    EmergencyReport,
                    Reporter.full_name.label("reporter_name"),
                    Handler.full_name.label("handler_name")
                )
                .outerjoin(
                    Reporter,
                    EmergencyReport.reported_by == Reporter.id
                )
                .outerjoin(
                    Handler,
                    EmergencyReport.handled_by == Handler.id
                )
                .filter(
                    EmergencyReport.status != EmergencyStatus.RESOLVED
                )
                .order_by(EmergencyReport.created_at.desc())
                .all()
            )

            result = [
                {
                    "id": report.id,
                    "reported_by": report.reported_by,
                    "reporter_name": reporter_name or "Unknown",
                    "event_id": report.event_id,
                    "category": report.category.value,
                    "description": report.description,
                    "status": report.status.value,
                    "handled_by": report.handled_by,
                    "handler_name": handler_name or "Unassigned",
                    "created_at": report.created_at.isoformat(),
                    "resolved_at": (
                        report.resolved_at.isoformat()
                        if report.resolved_at
                        else None
                    )
                }
                for report, reporter_name, handler_name in reports
            ]

            return jsonify(result), 200

    except Exception:
        return jsonify({
            "message": "Failed to fetch active emergency reports"
        }), 500



