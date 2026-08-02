from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy import func, case


from app.database.database import get_session
from app.database.models.auth import User
from app.database.models.clubs import Club, ClubCreationRequest
from app.database.models.events import Event
from app.database.models.support import SupportTicket
from app.database.models.audit import AuditLog
from app.database.models.academics import Department
from app.database.models.university import UniversityDomain, University
from app.database.enums import UserRole, TicketStatus,ClubRequestStatus,EventStatus,ExpenseStatus
from app.database.models.finance import Expense

from app.middleware.auth_middleware import require_auth ,require_role

faculty_advisor_bp = Blueprint('faculty_advisor', __name__)

@faculty_advisor_bp.route('/<int:id>/stats', methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_stats_of_id(id):
    token_user_id = get_jwt_identity()
    if id != int(token_user_id):
        return {"message" : "Forbidden : You are not advisor of this club"}, 404
    try:
        with get_session() as db:
            clubs_adv = db.query(Club).filter_by(faculty_advisor_id=id).count()
            pending_club_prop = db.query(ClubCreationRequest).filter(
                ClubCreationRequest.faculty_advisor_id ==id,
                ClubCreationRequest.status != ClubRequestStatus.APPROVED,
                ClubCreationRequest.status != ClubRequestStatus.REJECTED
            ).count()

            pending_event_approv = db.query(Event).filter_by(
                status=EventStatus.PENDING_APPROVAL
            ).count()

            pending_expenses = db.query(Expense).filter_by(
                status=ExpenseStatus.PENDING
            ).count()
                

            result = {
                "totalAdvisedClubs": clubs_adv,
                "pendingEventApprovals": pending_event_approv,
                "pendingProposals": pending_club_prop,
                "pendingExpenses": pending_expenses,
                "clubsTrend": "+1",
                "eventsTrend": "-2",
                "proposalsTrend": "0",
                "expensesTrend": "+3"
            }
    except Exception as e:
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    
    return jsonify(result), 200


@faculty_advisor_bp.route('/<int:user_id>/clubs',methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_clubs_of_id(user_id):
    token_user_id = get_jwt_identity()
    if user_id != int(token_user_id):
        return {"message" : "Forbidden : You are not advisor of this club"}, 404
    try:
        with get_session() as db:
            rows = (
                db.query(
                    Club,
                    func.sum(
                        case((Event.status == EventStatus.SCHEDULED, 1), else_=0)
                    ).label("scheduled_count"),
                    func.sum(
                        case((Event.status == EventStatus.PENDING_APPROVAL, 1), else_=0)
                    ).label("pending_count"),
                )
                .outerjoin(Event, Event.club_id == Club.id)
                .filter(Club.faculty_advisor_id == user_id)
                .group_by(Club.id)
                .all()
            )


            result = [
                {
                    "id": club.id,
                    "name": club.name,
                    "category": club.category,
                    "scheduled_events": scheduled_count or 0,
                    "pending_events": pending_count or 0,
                }
                for club, scheduled_count, pending_count in rows
            ]

    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200
    



@faculty_advisor_bp.route('/clubs/<int:club_id>',methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_club_detail_by_id(club_id):
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            club = db.query(Club).filter_by(faculty_advisor_id=user_id, id=club_id).first()
            if not club:
                return {"message" : "Not Found any club for faculty."},404
            result = {
                "id": "1",
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
            }

    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200
    


@faculty_advisor_bp.route('/<int:user_id>/events',methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_events_detail_by(user_id):
    token_user_id = get_jwt_identity()
    if user_id != int(token_user_id):
        return {"message" : "Forbidden : You are not advisor of this club."}, 404
    try:
        status_flag = request.args.get('status', default=EventStatus.SCHEDULED, type=str)
        with get_session() as db:
            events = (
                db.query(Event)
                .join(Club, Event.club_id == Club.id)
                .filter(Club.faculty_advisor_id == user_id, Event.status == status_flag)
                .all()
            )

            result = [
                {
                    "id": event.id,
                    "club_id": event.club_id,
                    "title": event.title,
                    "description": event.description,
                    "venue": event.venue,
                    "start_at": event.start_at,
                    "end_at": event.end_at,
                    "registration_deadline": event.registration_deadline,
                    "capacity": event.capacity,
                    "status": event.status,
                    "banner": event.banner,
                    "created_by": event.created_by,
                    "requires_external_participants": event.requires_external_participants,
                    "is_public": event.is_public,
                    "created_at": event.created_at
                } for event in events
            ]
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200



@faculty_advisor_bp.route('/events/<int:event_id>/decision',methods=['PATCH'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def let_faculty_decide_events(user_id):   
    try:
        data = request.get_json()
        print(data)
        result = {}
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200



@faculty_advisor_bp.route('/<int:user_id>/expenses',methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_faculty_expenses(user_id):   
    try:
        status_flag = request.args.get('status', default=ExpenseStatus.PENDING, type=str)

        print(status_flag)
        result = {}
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200


@faculty_advisor_bp.route('/expenses/<int:expenses_id>/decision',methods=['PATCH'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def let_faculty_decide_expenses(user_id):   
    try:
        data = request.get_json()
        print(data)
        result = {}
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200


