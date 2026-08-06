"""
Transfer Presidency API

Endpoint:
PATCH /api/clubs/<club_id>/transfer-presidency

Only the current President can transfer the presidency.
After transfer:
- Current President -> Vice President
- Selected member -> President
"""

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import ClubMembership
from app.database.enums import ClubMemberRole, MembershipStatus
from app.middleware.auth_middleware import require_club_role, require_auth

# ---------------------------------------------------
# Blueprint Setup
# ---------------------------------------------------

transfer_presidency_bp = Blueprint("transfer_presidency", __name__)
api = Api(transfer_presidency_bp)


# ---------------------------------------------------
# Resource
# ---------------------------------------------------

class TransferPresidencyResource(Resource):
    @require_auth
    @require_club_role(ClubMemberRole.PRESIDENT)
    def patch(self, club_id):
        data = request.get_json() or {}

        current_membership_id = data.get("current_membership_id")
        successor_membership_id = data.get("successor_membership_id")

        if current_membership_id is None:
            return {
                "message": "current_membership_id is required"
            }, 400

        if successor_membership_id is None:
            return {
                "message": "successor_membership_id is required"
            }, 400

        with get_session() as session:

            current_membership = session.get(
                ClubMembership,
                current_membership_id
            )

            successor_membership = session.get(
                ClubMembership,
                successor_membership_id
            )

            if current_membership is None:
                return {
                    "message": "Current membership not found."
                }, 404

            if successor_membership is None:
                return {
                    "message": "Successor membership not found."
                }, 404

            if current_membership.club_id != club_id:
                return {
                    "message": "Current membership does not belong to this club."
                }, 400

            if successor_membership.club_id != club_id:
                return {
                    "message": "Successor membership does not belong to this club."
                }, 400

            if current_membership.role_in_club != ClubMemberRole.PRESIDENT:
                return {
                    "message": "Current member is not the President."
                }, 400

            if successor_membership.status != MembershipStatus.APPROVED:
                return {
                    "message": "Successor must be an approved member."
                }, 400

            if successor_membership.role_in_club == ClubMemberRole.PRESIDENT:
                return {
                    "message": "Selected member is already the President."
                }, 400

            # Transfer roles
            current_membership.role_in_club = ClubMemberRole.VICE_PRESIDENT
            successor_membership.role_in_club = ClubMemberRole.PRESIDENT

            session.commit()

            return {
                "message": "Presidency transferred successfully.",
                "previous_president_membership_id": current_membership.id,
                "new_president_membership_id": successor_membership.id,
            }, 200


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

api.add_resource(
    TransferPresidencyResource,
    "/clubs/<int:club_id>/transfer-presidency",
)