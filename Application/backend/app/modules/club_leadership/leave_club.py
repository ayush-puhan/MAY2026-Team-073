from datetime import datetime

from flask import Blueprint, g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.enums import MembershipStatus
from app.database.models import ClubMembership
from app.middleware.auth_middleware import require_auth

memberships_bp = Blueprint("memberships", __name__)
api = Api(memberships_bp)


def _format_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def serialize_membership(membership):
    return {
        "id": membership.id,
        "user_id": membership.user_id,
        "club_id": membership.club_id,
        "role_in_club": (
            membership.role_in_club.value
            if membership.role_in_club
            else None
        ),
        "status": (
            membership.status.value
            if membership.status
            else None
        ),
        "applied_at": _format_dt(membership.applied_at),
        "decided_at": _format_dt(membership.decided_at),
        "approved_by": membership.approved_by,
        "rejection_reason": membership.rejection_reason,
    }


class LeaveClubResource(Resource):

    @require_auth
    def options(self, membership_id):
        return {}, 200

    @require_auth
    def post(self, membership_id):
        with get_session() as db:

            membership = (
                db.query(ClubMembership)
                .filter_by(id=membership_id)
                .first()
            )

            if membership is None:
                return {"message": "Membership not found."}, 404

            if membership.user_id != g.current_user.id:
                return {
                    "message": "You can only leave your own club membership."
                }, 403

            if membership.status != MembershipStatus.APPROVED:
                return {
                    "message": "Only approved members can leave a club."
                }, 400

            membership.status = MembershipStatus.WITHDRAWN
            membership.decided_at = datetime.utcnow()

            db.commit()
            db.refresh(membership)

            return {
                "message": "Successfully left the club.",
                "membership": serialize_membership(membership),
            }, 200


api.add_resource(
    LeaveClubResource,
    "/memberships/<int:membership_id>/leave",
)