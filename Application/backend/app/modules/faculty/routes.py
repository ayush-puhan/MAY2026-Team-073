from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy import func, case


from app.database.database import get_session
from app.database.models import (User,
 Club, ClubMembership,Committee,Announcement,
 Event,
 SupportTicket,
 AuditLog,
 Department,
 UniversityDomain, University,
 Expense,Budget
)
from app.database.enums import UserRole, TicketStatus,ClubRequestStatus,EventStatus,ExpenseStatus,MembershipStatus

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
            club_stats = (
                db.query(
                    func.count(Club.id).label('total_clubs'),
                    func.sum(Club.member_count_cache).label('total_members')
                )
                .filter(Club.faculty_advisor_id == token_user_id)
                .first()
            )
            pending_event = (
                db.query(Event)
                .join(Club, Event.club_id == Club.id)
                .filter(
                    Event.status == EventStatus.PENDING_APPROVAL,
                    Club.faculty_advisor_id == token_user_id 
                )
                .count()
            )

            pending_expenses = (
                db.query(Expense)
                .join(Budget, Expense.budget_id == Budget.id)
                .join(Club, Budget.club_id == Club.id)
                .filter(
                    Expense.status == ExpenseStatus.PENDING,
                    Club.faculty_advisor_id == token_user_id 
                )
                .count()
            )
            
            result = {
                "advisedClubs": club_stats.total_clubs,
                "pendingEvents": pending_event,
                "totalMembers" : club_stats.total_members,
                "pendingExpenses": pending_expenses
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
            clubs = db.query(Club).filter_by(faculty_advisor_id=user_id).all()

            result = [
                {
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
                }
                for club in clubs
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
                return {"message" : "Aunothorize or Not Found any club for faculty."}, 403
            
            memberships_query = (
                db.query(ClubMembership, User.full_name.label('user_name'))
                .join(User, ClubMembership.user_id == User.id)
                .filter(
                    ClubMembership.club_id == club_id,
                    # If using an Enum, use MembershipStatus.APPROVED instead of 'approved'
                    ClubMembership.status == MembershipStatus.APPROVED 
                )
                .all()
            )
            committees = db.query(Committee).filter(Committee.club_id == club_id).all()
            main_budget = (
                db.query(Budget)
                .filter(
                    Budget.club_id == club_id,
                    Budget.committee_id.is_(None),
                    Budget.parent_budget_id.is_(None)
                )
                .first()
            )
            
            members_data=[{
                "id": membership.id,
                "user_id": membership.user_id,
                "club_id": membership.club_id,
                "role_in_club": membership.role_in_club,
                "status": membership.status.upper(),
                "user_name": user_name or 'Unknown'  # Map the name from the joined User table
            } for membership, user_name in memberships_query]
            
            committees_data = [{
                "id": c.id,
                "club_id": c.club_id,
                "name": c.name,
                "description": c.description
            } for c in committees]

            main_budget_data = None
            if main_budget:
                main_budget_data = {
                    "id": main_budget.id,
                    "title": main_budget.title,
                    "allocated_amount": main_budget.allocated_amount
                }
            result = {
                "id" : club.id,
                "name": club.name,
                "description": club.description,
                "status": club.status,
                "category": club.category,
                "mainBudget" : main_budget_data,
                "members" : members_data,
                "committees" : committees_data
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
        status_flag = request.args.get('status', default=None, type=str)
        with get_session() as db:
            query = (
                db.query(Event, Club.name.label('club_name'))
                .join(Club, Event.club_id == Club.id)
                .filter(Club.faculty_advisor_id == user_id)
            )
            if status_flag:
                query = query.filter(Event.status == EventStatus(status_flag))
            events = query.all()

            result = [
                {
                    "id": event.id,
                    "club_id": event.club_id,
                    "club_name": club_name,
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
                } for event,club_name in events
            ]
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200



@faculty_advisor_bp.route('/events/<int:event_id>/decision',methods=['PATCH'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def let_faculty_decide_events(event_id):  
    token_user_id = get_jwt_identity() 
    try:
        data = request.get_json()
        approval_status = data.get('approval_status')
        review_comments = data.get('review_comments')
        reviewed_by = data.get('reviewed_by')
        print(data)
        with get_session() as db:
            event_to_approve = (
                db.query(Event)
                .join(Club, Event.club_id == Club.id)
                .filter(
                    Event.id == event_id,
                    Club.faculty_advisor_id == token_user_id
                )
                .first()
            )
            if not event_to_approve:
                return {'message' : 'Forbidden : Can not update event of other clubs.'}, 403
            decision_status_map = {'approved': EventStatus.SCHEDULED, 'rejected': EventStatus.REJECTED}
            new_status = decision_status_map.get(approval_status)
            if new_status is None:
                return {'message': f"Invalid approval_status '{approval_status}'"}, 400
            event_to_approve.status = new_status
            db.commit()
            result = {
                "created_by" : event_to_approve.created_by,
                "title" : event_to_approve.title
            }
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200



@faculty_advisor_bp.route('/<int:user_id>/expenses',methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_faculty_expenses(user_id):   
    token_user_id = get_jwt_identity()
    if user_id != int(token_user_id):
        return {'message' : "Forbidden : Can not see expenses of other clubs."}, 403
    try:
        status_filter = request.args.get('status', default=None, type=str)
        with get_session() as db:
            query = (
                db.query(Expense, Budget.title.label('budget_title'))
                .join(Budget, Expense.budget_id == Budget.id)
                .join(Club, Budget.club_id == Club.id)
                .filter(Club.faculty_advisor_id == user_id)
            )
            if status_filter:
                query = query.filter(Expense.approval_status == status_filter)
            all_expenses = query.all()
            result = [
                {
                    "id": expense.id,
                    "budget_id": expense.budget_id,
                    "budget_title": budget_title,
                    "description": expense.description,
                    "amount": expense.amount,
                    "category": expense.category,
                    "receipt_document_id": expense.receipt_document_id,
                    "submitted_by": expense.submitted_by,
                    "status": expense.status,
                    "approval_status": expense.approval_status,
                    "approved_by": expense.approved_by,
                    "approval_date": expense.approval_date,
                    "approval_remarks": expense.approval_remarks,
                    "created_at": expense.created_at
                } for expense, budget_title in all_expenses
            ]

    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200


@faculty_advisor_bp.route('/expenses/<int:expense_id>/decision',methods=['PATCH'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def let_faculty_decide_expenses(expense_id):  
    token_user_id = get_jwt_identity() 
    try:
        data = request.get_json()
        approval_status = data.get('approval_status')
        approval_remarks = data.get('approval_remarks')
        approved_by = data.get('approved_by')
        if approval_status not in ('approved', 'rejected'):
            return {'message': f"Invalid approval_status '{approval_status}'"}, 400
        with get_session() as db:
            expense = (
                db.query(Expense)
                .join(Budget, Expense.budget_id == Budget.id)
                .join(Club, Budget.club_id == Club.id)
                .filter(
                    Expense.id == expense_id,
                    Club.faculty_advisor_id == token_user_id  # <-- SECURITY CHECK ENFORCED HERE
                )
                .first()
            )
            if not expense:
                return {'message' : 'Expense not found or unauthorized access'}, 403
            expense.approval_status = approval_status.upper()
            expense.status = approval_status.upper()
            expense.approval_remarks = approval_remarks
            expense.approved_by = approved_by
            expense.approval_date = datetime.now()
            db.commit()
            result = {
                "description" : expense.description,
                "submitted_by" : expense.submitted_by
            }
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200

@faculty_advisor_bp.route('/<int:user_id>/announcements',methods=['GET'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def get_faculty_announcements(user_id): 
    token_user_id = get_jwt_identity()
    if user_id != int(token_user_id):
        return {'message' : "Forbidden : Can not see expenses of other clubs."}, 403
    
    try:
        with get_session() as db:
            all_anns = (
                db.query(Announcement, Club.name.label('club_name'))
                .join(Club, Club.id == Announcement.club_id)
                .filter(Announcement.posted_by == user_id)
                .all()
            )
            result = [
                {
                    "id" : ann.id,
                    "club_id" : ann.club_id,
                    "club_name" : club_name,
                    "posted_by" : ann.posted_by,
                    "title" : ann.title,
                    "body" : ann.body,
                    "target_audience" : ann.target_audience.upper(),
                    "created_at" : ann.created_at
                } for ann, club_name in all_anns
            ]
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200

# post announcement
@faculty_advisor_bp.route('/announcements',methods=['POST'])
@require_auth
@require_role(UserRole.FACULTY_ADVISOR)
def make_faculty_announcements(): 
    try:
        data = request.get_json()
        club_id = data.get('club_id')
        posted_by = data.get('posted_by')
        title = data.get('title')
        body = data.get('body')
        target_audience = data.get('target_audience')
        created_at = data.get('created_at')
        if not club_id and not posted_by and not title and not body and not target_audience and not created_at:
            return {"message" : "Request field can not be empty."}, 400
        with get_session() as db:
            new_ann = Announcement(
                club_id=club_id,
                posted_by=posted_by,
                title=title,body=body,
                target_audience=target_audience.upper(),
                created_at=created_at
            )
            db.add(new_ann)
            db.commit()
            result = {
                'messge' : "Announcement published successfully"
            }
    except Exception as e :
        msg = {"message" : f"Error : {e}"}
        print(msg)
        return msg, 500
    return jsonify(result), 200