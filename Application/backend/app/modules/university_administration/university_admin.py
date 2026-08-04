from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from app.database.database import get_session
from datetime import datetime

from app.database.models.auth import User
from app.database.models.clubs import Club,ClubMembership,ClubCreationRequest
from app.database.models.events import Event 
from app.database.enums import UserRole,MembershipStatus, ClubRequestStatus, ClubStatus
from app.middleware.auth_middleware import require_auth ,require_role


university_admin_bp = Blueprint('university_admin', __name__)

@university_admin_bp.get("/stats")
@require_auth
@require_role(
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE
)
def get_stats():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            current_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if current_user is None:
                return jsonify({"message": "User not found"}), 404

            university_id = current_user.university_id

            # Total active clubs
            total_clubs = (
                db.query(func.count(Club.id))
                .filter(
                    Club.university_id == university_id,
                    Club.status == "active"
                )
                .scalar()
            )

            # Total approved memberships
            total_memberships = (
                db.query(func.count(ClubMembership.id))
                .join(Club, ClubMembership.club_id == Club.id)
                .filter(
                    Club.university_id == university_id,
                    ClubMembership.status == "approved"
                )
                .scalar()
            )

            # Total scheduled events
            active_events = (
                db.query(func.count(Event.id))
                .join(Club, Event.club_id == Club.id)
                .filter(
                    Club.university_id == university_id,
                    Event.status == "scheduled"
                )
                .scalar()
            )

            # Total pending club creation requests
            pending_approvals = (
                db.query(func.count(ClubCreationRequest.id))
                .join(User, ClubCreationRequest.requested_by == User.id)
                .filter(
                    User.university_id == university_id,
                    ClubCreationRequest.status == "submitted"
                )
                .scalar()
            )
            result={
                "totalClubs": total_clubs,
                "totalMemberships": total_memberships,
                "activeEvents": active_events,
                "pendingApprovals": pending_approvals
            }
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    return jsonify(result), 200

@university_admin_bp.get("/club-requests")
@require_auth
@require_role(
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE
)
def get_club_creation_requests():
    user_id = get_jwt_identity()
    try:
        status = request.args.get("status")
        with get_session() as db:
            current_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if current_user is None:
                return jsonify({"message": "User not found"}), 404

            query = (
                db.query(
                    ClubCreationRequest,
                    User.full_name.label("requested_by_name")
                )
                .join(User, ClubCreationRequest.requested_by == User.id)
                .filter(User.university_id == current_user.university_id)
            )

            if status:
                query = query.filter(ClubCreationRequest.status == status)

            requests = (
                query
                .order_by(ClubCreationRequest.created_at.desc())
                .all()
            )
            result=[
                {
                    "id": req.id,
                    "proposed_name": req.proposed_name,
                    "proposed_category": req.proposed_category,
                    "proposal_description": req.proposal_description,
                    "requested_by": req.requested_by,
                    "requested_by_name": requested_by_name,
                    "status": req.status,
                    "reviewed_by": req.reviewed_by,
                    "review_comments": req.review_comments,
                    "resulting_club_id": req.resulting_club_id,
                    "created_at": req.created_at.isoformat() if req.created_at else None,
                    "decided_at": req.decided_at.isoformat() if req.decided_at else None,
                }
                for req, requested_by_name in requests
            ]
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500

    return jsonify(result), 200


@university_admin_bp.route('/club-requests/<int:req_id>/decision', methods=['PATCH'])
@require_auth
@require_role(UserRole.STUDENT_AFFAIRS_OFFICE, UserRole.DEAN_STUDENT_WELFARE)
def decide_ua_club_request(req_id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        id = data.get('id')
        status = data.get('status')
        reviewed_by = data.get('reviewed_by')
        review_comments = data.get('review_comments')
        faculty_advisor_id = data.get('faculty_advisor_id')
        with get_session() as db:
            req = db.query(ClubCreationRequest).filter_by(id=req_id).first()
            if not req:
                return {'message' : 'Required Resource not found or empty resource'}, 400
            
            
            if status.upper() == ClubRequestStatus.APPROVED:
                new_club = Club(
                    name = req.proposed_name,
                    slug = "_".join(req.proposed_name.split(" ")),
                    category = req.proposed_category,
                    description = req.proposal.description,
                    objectives = None,
                    logo_url = None,
                    status = ClubStatus.ACTIVE,
                    faculty_advisor_id = faculty_advisor_id,
                    university_id = 1, 
                    member_count_cache = 0,
                    created_at = datetime.utcnow()
                )
                db.add(new_club)
                db.flush()
                req.resulting_club_id =new_club.id
            req.status = status.upper()
            req.faculty_advisor_id = faculty_advisor_id
            req.review_comments = review_comments
            req.reviewed_by = reviewed_by
            req.decided_at = datetime.utcnow()
             
            db.commit()
            result = {
                "message": f"Request {status}",
                "club_id": req.resulting_club_id
            } 

    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    
    return jsonify(result), 200




@university_admin_bp.route('/clubs/pending-activation', methods=['GET'])
@require_auth
@require_role(UserRole.STUDENT_AFFAIRS_OFFICE, UserRole.DEAN_STUDENT_WELFARE)
def get_ud_pending_activation():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if user is None:
                return jsonify({"message": "User not found"}), 404

            clubs = (
                db.query(Club)
                .filter(
                    Club.university_id == user.university_id,
                    Club.status == "pending",
                    Club.faculty_advisor_id.is_(None)
                )
                .all()
            )

            result = [
                {
                    "id": club.id,
                    "name": club.name,
                    "slug": club.slug,
                    "category": club.category,
                    "description": club.description,
                    "status": club.status,
                    "university_id": club.university_id,
                    "created_at": club.created_at.isoformat() if club.created_at else None
                }
                for club in clubs
            ]
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    
    return jsonify(result), 200



@university_admin_bp.patch("/clubs/<int:club_id>/activate")
@require_auth
@require_role(UserRole.STUDENT_AFFAIRS_OFFICE, UserRole.DEAN_STUDENT_WELFARE)
def activate_club(club_id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json() or {}
        faculty_advisor_id = data.get("faculty_advisor_id")
        if faculty_advisor_id is None:
            return jsonify({"message": "faculty_advisor_id is required"}), 400
        with get_session() as db:
            admin = db.query(User).filter(User.id == user_id).first()
            if admin is None:
                return jsonify({"message": "User not found"}), 404
            club = (
                db.query(Club)
                .filter(
                    Club.id == club_id,
                    Club.university_id == admin.university_id
                )
                .first()
            )
            if club is None:
                return jsonify({"message": "Club not found"}), 404
            if club.status != ClubStatus.PENDING:
                return jsonify({"message": "Club is not pending activation"}), 400
            advisor = (
                db.query(User)
                .filter(
                    User.id == faculty_advisor_id,
                    User.university_id == admin.university_id
                )
                .first()
            )
            if advisor is None:
                return jsonify({"message": "Faculty advisor not found"}), 404
            club.status = ClubStatus.ACTIVE
            club.faculty_advisor_id = faculty_advisor_id
            club.updated_at = datetime.utcnow()

            db.commit()
            result = {
                "message": "Club activated successfully",
                "club": {
                    "id": club.id,
                    "status": club.status,
                    "faculty_advisor_id": club.faculty_advisor_id
                }
            }
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    
    return jsonify(result), 200


@university_admin_bp.get("/faculty-advisors")
@require_auth
@require_role(
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE
)
def get_faculty__ua_advisors():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            current_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if current_user is None:
                return jsonify({"message": "User not found"}), 404

            advisors = (
                db.query(User)
                .filter(
                    User.role == UserRole.FACULTY_ADVISOR,
                    User.university_id == current_user.university_id,
                    User.is_active.is_(True)
                )
                .order_by(User.full_name)
                .all()
            )
            result = [
                {
                    "value": advisor.id,
                    "label": advisor.full_name
                }
                for advisor in advisors
            ]
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    
    return jsonify(result), 200



@university_admin_bp.get("/clubs")
@require_auth
@require_role(
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE
)
def get_all_ua_clubs():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            current_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if current_user is None:
                return jsonify({"message": "User not found"}), 404

            clubs = (
                db.query(Club)
                .filter(Club.university_id == current_user.university_id)
                .order_by(Club.name)
                .all()
            )
            result = [
                {
                    "id": club.id,
                    "name": club.name,
                    "slug": club.slug,
                    "category": club.category,
                    "description": club.description,
                    "status": club.status,
                    "faculty_advisor_id": club.faculty_advisor_id,
                    "university_id": club.university_id,
                    "member_count_cache": club.member_count_cache,
                    "created_at": club.created_at.isoformat() if club.created_at else None,
                    "updated_at": club.updated_at.isoformat() if club.updated_at else None,
                    "deleted_at": club.deleted_at.isoformat() if club.deleted_at else None,
                }
                for club in clubs
            ]
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    return jsonify(result), 200



@university_admin_bp.get("/events")
@require_auth
@require_role(
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE
)
def get_all_events():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            current_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if current_user is None:
                return jsonify({"message": "User not found"}), 404

            results = (
                db.query(Event, Club.name.label("club_name"))
                .join(Club, Event.club_id == Club.id)
                .filter(Club.university_id == current_user.university_id)
                .order_by(Event.start_at.desc())
                .all()
            )

            events = [
                {
                    "id": event.id,
                    "club_id": event.club_id,
                    "club_name": club_name,
                    "title": event.title,
                    "description": event.description,
                    "venue": event.venue,
                    "start_at": event.start_at.isoformat() if event.start_at else None,
                    "end_at": event.end_at.isoformat() if event.end_at else None,
                    "status": event.status,
                    "created_at": event.created_at.isoformat() if event.created_at else None,
                    "updated_at": event.updated_at.isoformat() if event.updated_at else None,
                }
                for event, club_name in results
            ]
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    return jsonify(events), 200



@university_admin_bp.get("/analytics")
@require_auth
@require_role(
    UserRole.STUDENT_AFFAIRS_OFFICE,
    UserRole.DEAN_STUDENT_WELFARE
)
def get_analytics():
    user_id = get_jwt_identity()
    try:
        with get_session() as db:
            current_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if current_user is None:
                return jsonify({"message": "User not found"}), 404

            university_id = current_user.university_id

            # -------- Category Distribution --------
            category_distribution = (
                db.query(
                    Club.category,
                    func.count(Club.id).label("count")
                )
                .filter(Club.university_id == university_id)
                .group_by(Club.category)
                .all()
            )

            # -------- Club Growth --------
            club_growth = (
                db.query(
                    func.strftime("%Y-%m", Club.created_at).label("month"),
                    func.count(Club.id).label("count")
                )
                .filter(Club.university_id == university_id)
                .group_by("month")
                .order_by("month")
                .all()
            )

            # -------- Membership Growth --------
            membership_growth = (
                db.query(
                    func.strftime("%Y-%m", ClubMembership.applied_at).label("month"),
                    func.count(ClubMembership.id).label("count")
                )
                .join(Club, Club.id == ClubMembership.club_id)
                .filter(
                    Club.university_id == university_id,
                    ClubMembership.status == "approved"
                )
                .group_by("month")
                .order_by("month")
                .all()
            )
            result={
                "categoryDistribution": [
                    {
                        "category": category,
                        "count": count
                    }
                    for category, count in category_distribution
                ],
                "clubGrowth": [
                    {
                        "month": month,
                        "count": count
                    }
                    for month, count in club_growth
                ],
                "membershipGrowth": [
                    {
                        "month": month,
                        "count": count
                    }
                    for month, count in membership_growth
                ]
            }
    except Exception as e:
        msg = {'message' : f"Error : {e}"}
        print(msg)
        return jsonify(msg), 500
    return jsonify(result), 200