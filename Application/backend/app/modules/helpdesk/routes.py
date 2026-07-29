from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.support import (
    SupportTicket,
    TicketResponse,
    EmergencyReport
)
from app.database.enums import TicketStatus, TicketPriority


admin_support_bp = Blueprint("admin_support", __name__)
api = Api(admin_support_bp)


class AdminSupportResource(Resource):

    def get(self, ticket_id=None):
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
            tickets = db.query(SupportTicket).all()

            responses = db.query(TicketResponse).all()

            emergency_reports = db.query(EmergencyReport).all()

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
            


    def patch(self, ticket_id):

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



class TicketResponseResource(Resource):

    def post(self, ticket_id):

        data = request.get_json()

        print("Received data:", data)

        # Accept both "body" and "message"
        body = data.get("body") or data.get("message")

        # Optional for now if authentication is not implemented
        responder_id = data.get("responder_id")

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

api.add_resource(
    AdminSupportResource,
    "",
    "/<int:ticket_id>"
)


api.add_resource(
    TicketResponseResource,
    "/<int:ticket_id>/respond"
)