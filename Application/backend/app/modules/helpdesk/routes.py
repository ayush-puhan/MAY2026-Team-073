from flask import Blueprint, request
from flask_restful import Api, Resource
from app.middleware.auth_middleware import require_auth ,require_role
from flask import g

from app.database import get_session
from app.database.models.support import (
    SupportTicket,
    TicketResponse,
    EmergencyReport
)
from app.database.models.auth import User
from app.database.models.clubs import ClubMembership
from app.database.enums import TicketStatus, TicketPriority, TicketType, UserRole, ClubMemberRole, MembershipStatus


admin_support_bp = Blueprint("admin_support", __name__)
api = Api(admin_support_bp)


class AdminSupportResource(Resource):
    @require_auth
    @require_role("system_admin")
    def get(self, ticket_id=None):
        try:
            with get_session() as db:

                # GET /api/admin/support/<id>
                if ticket_id is not None:

                    ticket = (
                        db.query(SupportTicket)
                        .filter_by(id=ticket_id)
                        .first()
                    )

                    if not ticket:
                        return {
                            "message": "Ticket not found."
                        }, 404


                    responses = (
                        db.query(TicketResponse)
                        .filter_by(ticket_id=ticket.id)
                        .all()
                    )


                    return {
                            "id": str(ticket.id),
                            "raised_by": ticket.raised_by,
                            "club_id": ticket.club_id,
                            "title": ticket.title,
                            "description": ticket.description,
                            "ticket_type": ticket.ticket_type.value,
                            "priority": ticket.priority.value,
                            "status": ticket.status.value,
                            "assigned_agent_id": ticket.assigned_agent_id,
                            "is_offensive": ticket.is_offensive,
                            "resolution_rating": ticket.resolution_rating,
                            "university_id": ticket.university_id,
                            "created_at": ticket.created_at.strftime(
                                "%Y-%m-%d %H:%M:%S"
                                )
                        }, 200


                # GET /api/admin/support
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 100, type=int)
                tickets = db.query(SupportTicket).limit(per_page).offset((page - 1) * per_page).all()

                return [
                    {
                        "id": str(ticket.id),
                        "raised_by": ticket.raised_by,
                        "club_id": ticket.club_id,
                        "title": ticket.title,
                        "description": ticket.description,
                        "ticket_type": ticket.ticket_type.value,
                        "priority": ticket.priority.value,
                        "status": ticket.status.value,
                        "assigned_agent_id": ticket.assigned_agent_id,
                        "is_offensive": ticket.is_offensive,
                        "resolution_rating": ticket.resolution_rating,
                        "university_id": ticket.university_id,
                        "created_at": ticket.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ) if ticket.created_at else None
                    }
                    for ticket in tickets
                ], 200
        except Exception as e:
            return {'message' : 'Uncaught Error'}, 500
            

    @require_auth
    @require_role("system_admin")
    def patch(self, ticket_id):
        try:

            data = request.get_json()
            
            with get_session() as db:

                ticket = (
                    db.query(SupportTicket)
                    .filter_by(id=ticket_id)
                    .first()
                )


                if not ticket:
                    return {
                        "message": "Ticket not found."
                    }, 404


                if "status" in data:
                    ticket.status = TicketStatus(
                        data["status"]
                    )


                if "priority" in data:
                    ticket.priority = TicketPriority(
                        data["priority"].upper()
                    )


                if "assigned_agent_id" in data:
                    ticket.assigned_agent_id = data["assigned_agent_id"]


                if "is_offensive" in data:
                    ticket.is_offensive = data["is_offensive"]


                if "resolution_rating" in data:
                    ticket.resolution_rating = data["resolution_rating"]


                db.commit()


                return {
                    "message": "Ticket updated successfully."
                }, 200
        except Exception as e:
            return {'message' : 'Uncaught Error'}, 500



class TicketResponseResource(Resource):
    
    @require_auth
    @require_role("system_admin")
    
    def post(self, ticket_id):
        try:
            data = request.get_json()

            print("Received data:", data)

            # Accept both "body" and "message"
            body = data.get("body") or data.get("message")

            # Get responder from authenticated user
            responder_id = g.current_user.id

            is_resolution = data.get(
                "is_resolution",
                False
            )

            if not body:
                return {
                    "message": "Response message is required."
                }, 400


            with get_session() as db:

                ticket = (
                    db.query(SupportTicket)
                    .filter_by(id=ticket_id)
                    .first()
                )


                if not ticket:
                    return {
                        "message": "Ticket not found."
                    }, 404


                response = TicketResponse(
                    ticket_id=ticket_id,
                    responder_id=responder_id,
                    body=body,
                    is_resolution=is_resolution
                )


                db.add(response)


                if is_resolution:
                    ticket.status = TicketStatus.CLOSED
                else:
                    ticket.status = TicketStatus.IN_PROGRESS


                db.commit()


                return {
                    "message": "Response added successfully.",
                    "response_id": response.id
                }, 201
        except Exception as e:
            return {'message' : 'Uncaught Error'}, 500

#====================================================================
ticket_response_bp = Blueprint("ticket_response", __name__)
ticket_response_api = Api(ticket_response_bp)
class TicketResponsesListResource(Resource):

    @require_auth
    def get(self):
        try:
            ticket_id = request.args.get("ticket_id")

            if not ticket_id:
                return {
                    "message": "ticket_id is required"
                }, 400

            with get_session() as db:

                ticket = (
                    db.query(SupportTicket)
                    .filter_by(id=ticket_id)
                    .first()
                )

                if not ticket:
                    return {
                        "message": "Ticket not found"
                    }, 404

                # ---------- Authorization ----------

                if g.current_user.role.value != "system_admin":

                    if ticket.raised_by != g.current_user.id:
                        return {
                            "message": "Permission denied"
                        }, 403

                responses = (
                    db.query(TicketResponse)
                    .filter_by(ticket_id=ticket_id)
                    .all()
                )

                return [
                    {
                        "id": r.id,
                        "message": r.body,
                        "responder_id": r.responder_id,
                        "is_resolution": r.is_resolution,
                        "created_at": (
                            r.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if r.created_at else None
                        )
                    }
                    for r in responses
                ], 200
        except Exception as e:
            return {'message' : 'Uncaught Error'}, 500
#=================================================================
support_ticket_bp = Blueprint("support_ticket", __name__)
support_ticket_api = Api(support_ticket_bp)


class SupportTicketResource(Resource):

    @require_auth
    def get(self):
        try:
            with get_session() as db:
                from sqlalchemy.orm import joinedload

                tickets = (
                    db.query(SupportTicket)
                    .options(joinedload(SupportTicket.assigned_agent))
                    .filter(
                        SupportTicket.raised_by == g.current_user.id
                    )
                    .all()
                )

                return [
                    {
                        "id": ticket.id,
                        "raised_by": ticket.raised_by,
                        "title": ticket.title,
                        "description": ticket.description,
                        "ticket_type": ticket.ticket_type.value,
                        "priority": ticket.priority.value,
                        "status": ticket.status.value,
                        "club_id": ticket.club_id,
                        "assigned_agent_id": ticket.assigned_agent_id,
                        "assigned_agent_name": (
                            ticket.assigned_agent.full_name
                            if ticket.assigned_agent else None
                        ),
                        "created_at": (
                            ticket.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if ticket.created_at else None
                        )
                    }
                    for ticket in tickets
                ], 200
        except Exception as e:
            return {'message' : 'Uncaught Error'}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()

            if not data or not data.get('title') or not data.get('description'):
                return {'message': 'title and description are required'}, 400

            with get_session() as db:
                assigned_agent_id = None
                assigned_role = data.get("assigned_role")
                university_id = data.get("university_id")
                club_id = data.get("club_id")

                if assigned_role:
                    # 1. System Admin
                    if assigned_role == UserRole.SYSTEM_ADMIN.value:
                        admin = db.query(User).filter(User.role == UserRole.SYSTEM_ADMIN).first()
                        if admin:
                            assigned_agent_id = admin.id
                    
                    # 2. University Staff (Dean or Student Affairs)
                    elif assigned_role in [UserRole.DEAN_STUDENT_WELFARE.value, UserRole.STUDENT_AFFAIRS_OFFICE.value] and university_id:
                        staff = db.query(User).filter(
                            User.role == UserRole(assigned_role),
                            User.university_id == university_id
                        ).first()
                        if staff:
                            assigned_agent_id = staff.id
                            
                    # 3. Faculty Advisor for a club
                    elif assigned_role == UserRole.FACULTY_ADVISOR.value and club_id:
                        from app.database.models.clubs import Club
                        club = db.query(Club).filter_by(id=club_id).first()
                        if club and club.faculty_advisor_id:
                            assigned_agent_id = club.faculty_advisor_id
                            
                    # 4. Club Officer
                    elif club_id:
                        # Find member with that role in that club
                        membership = db.query(ClubMembership).filter(
                            ClubMembership.club_id == club_id,
                            ClubMembership.role_in_club == ClubMemberRole(assigned_role),
                            ClubMembership.status == MembershipStatus.APPROVED
                        ).first()
                        if membership:
                            assigned_agent_id = membership.user_id

                ticket = SupportTicket(
                    raised_by=g.current_user.id,
                    club_id=club_id,
                    title=data["title"],
                    description=data["description"],
                    ticket_type=TicketType(data.get("ticket_type", "Support")),
                    priority=TicketPriority(data.get("priority", "Medium")),
                    university_id=university_id,
                    assigned_agent_id=assigned_agent_id
                )

                db.add(ticket)
                db.commit()
                db.refresh(ticket)

                return {
                    "id": ticket.id,
                    "raised_by": ticket.raised_by,
                    "title": ticket.title,
                    "description": ticket.description,
                    "ticket_type": ticket.ticket_type.value,
                    "priority": ticket.priority.value,
                    "status": ticket.status.value,
                    "club_id": ticket.club_id,
                    "created_at": (
                        ticket.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        if ticket.created_at else None
                    )
                }, 201
        except Exception as e:
            return {'message' : 'Uncaught Error'}, 500
api.add_resource(
    AdminSupportResource,
    "",
    "/<int:ticket_id>"
)


api.add_resource(
    TicketResponseResource,
    "/<int:ticket_id>/respond"
)
ticket_response_api.add_resource(
    TicketResponsesListResource,
    "/ticket_responses"
)
support_ticket_api.add_resource(
    SupportTicketResource,
    "/support_tickets"
)