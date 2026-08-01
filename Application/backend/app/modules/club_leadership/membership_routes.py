from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.clubs import ClubMembership
from app.database.enums import MembershipStatus, ClubMemberRole


membership_bp = Blueprint(
    "club_memberships",
    __name__
)

api = Api(membership_bp)



def serialize_membership(membership):
    """
    Convert ClubMembership object into JSON.
    """

    return {
        "id": membership.id,

        "user_id": membership.user_id,

        "club_id": membership.club_id,

        # "club_name": (
        #     membership.club.name
        #     if membership.club
        #     else None
        # ),

        "user_name": (
            membership.user.full_name
            if membership.user
            else None
        ),

        "role_in_club": (
            membership.role_in_club.value.lower()
            if membership.role_in_club
            else None
        ),

        "status": (
            membership.status.value.lower()
            if membership.status
            else None
        ),

        "applied_at": (
            membership.applied_at.isoformat()
            if membership.applied_at
            else None
        ),

        "decided_at": (
            membership.decided_at.isoformat()
            if membership.decided_at
            else None
        ),

        "approved_by": membership.approved_by,

        "rejection_reason":
            membership.rejection_reason
    }



# -------------------------------------------------
# GET /api/users/<user_id>/clubs
# -------------------------------------------------

class UserClubResource(Resource):

    def get(self, user_id):

        with get_session() as db:

            memberships = (
                db.query(ClubMembership)
                .filter(
                    ClubMembership.user_id == user_id
                )
                .all()
            )


            if not memberships:

                return {
                    "message":
                    "No clubs found for this user."
                }, 200



            return [
                serialize_membership(membership)
                for membership in memberships
            ], 200




# -------------------------------------------------
# GET /api/club_memberships
#
# Filters:
#
# /club_memberships
#
# /club_memberships?club_id=1
#
# /club_memberships?user_id=5
#
# /club_memberships?status=pending
#
# /club_memberships?role=president
#
# -------------------------------------------------


class ClubMembershipResource(Resource):

    def get(self):

        club_id = request.args.get(
            "club_id"
        )

        user_id = request.args.get(
            "user_id"
        )

        status = request.args.get(
            "status"
        )

        role = request.args.get(
            "role"
        )


        with get_session() as db:


            query = db.query(
                ClubMembership
            )



            if club_id:

                query = query.filter(
                    ClubMembership.club_id
                    ==
                    int(club_id)
                )



            if user_id:

                query = query.filter(
                    ClubMembership.user_id
                    ==
                    int(user_id)
                )



            if status:

                try:

                    query = query.filter(
                        ClubMembership.status
                        ==
                        MembershipStatus(
                            status.lower()
                        )
                    )

                except ValueError:

                    return {
                        "message":
                        "Invalid membership status."
                    }, 400




            if role:

                try:

                    query = query.filter(
                        ClubMembership.role_in_club
                        ==
                        ClubMemberRole(
                            role.lower()
                        )
                    )


                except ValueError:

                    return {
                        "message":
                        "Invalid club role."
                    }, 400




            memberships = query.all()



            return [
                serialize_membership(membership)
                for membership in memberships
            ], 200





# -------------------------------------------------
# Route Registration
# -------------------------------------------------

api.add_resource(
    UserClubResource,
    "/users/<int:user_id>/clubs"
)


api.add_resource(
    ClubMembershipResource,
    "/club_memberships"
)