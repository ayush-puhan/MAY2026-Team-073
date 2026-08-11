from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.clubs import ClubMembership
from app.database.enums import ClubMemberRole, MembershipStatus
from app.middleware.auth_middleware import require_auth, require_role, require_club_role

membership_bp = Blueprint(
    "club_memberships",
    __name__
)

api = Api(membership_bp)


# -------------------------------------------------
# Serializers
# -------------------------------------------------

def serialize_membership(member):
    """
    Response format:
    GET /api/clubs/<club_id>/members
    GET /api/clubs/<club_id>/membership-requests
    """

    return {

        "id": member.id,

        "user_id": member.user_id,

        "club_id": member.club_id,

        "role_in_club": (
            member.role_in_club.value.lower()
            if member.role_in_club
            else None
        ),

        "status": (
            member.status.value.lower()
            if member.status
            else None
        ),

        "applied_at": (
            member.applied_at.isoformat()
            if member.applied_at
            else None
        ),

        "decided_at": (
            member.decided_at.isoformat()
            if member.decided_at
            else None
        ),

        "approved_by": member.approved_by,

        "rejection_reason": member.rejection_reason,

        "user": (
            {
                "id": member.user.id,

                "full_name": member.user.full_name,

                "email": member.user.email,

                "role": (
                    member.user.role.value.lower()
                    if member.user.role
                    else None
                )
            }
            if member.user
            else None
        )
    }



def serialize_user_club(member):
    """
    Response format:
    GET /api/users/<user_id>/clubs
    """

    club = member.club


    # derived member count
    member_count = 0

    with get_session() as db:

        member_count = (
            db.query(ClubMembership)
            .filter(
                ClubMembership.club_id == club.id,
                ClubMembership.status == MembershipStatus.APPROVED
            )
            .count()
        )


    return {

        "id": club.id,

        "name": club.name,

        "slug": club.slug,

        "category": club.category,

        "description": club.description,

        "logo_url": club.logo_url,

        "banner": club.banner,

        "status": (
            club.status.value.lower()
            if club.status
            else None
        ),

        "role_in_club": (
            member.role_in_club.value.lower()
            if member.role_in_club
            else None
        ),

        "membership_id": member.id,

        "members": member_count,

        "university": (
            {
                "id": club.university.id,

                "name": club.university.name
            }
            if club.university
            else None
        )
    }



# -------------------------------------------------
# GET /api/users/<user_id>/clubs
# -------------------------------------------------

class UserClubResource(Resource):
    @require_auth
    def get(self, user_id):
        try:
            with get_session() as db:

                memberships = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.user_id == user_id,
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                    .all()
                )


                return [
                    serialize_user_club(member)
                    for member in memberships
                ], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



# -------------------------------------------------
# GET /api/clubs/<club_id>/members
# -------------------------------------------------

class ClubMembersResource(Resource):

    @require_auth
    def get(self, club_id=None):

        # Support:
        # /clubs/<club_id>/members
        # /club_memberships?club_id=2
        # /club_memberships
        try:
            if club_id is None:
                club_id = request.args.get("club_id")


            with get_session() as db:

                query = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                )


                # If club_id is provided, filter that club only
                if club_id:
                    query = query.filter(
                        ClubMembership.club_id == int(club_id)
                    )


                members = query.all()


                return [
                    serialize_membership(member)
                    for member in members
                ], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500
# -------------------------------------------------
# GET /api/clubs/<club_id>/membership-requests
# -------------------------------------------------

class ClubMembershipRequestsResource(Resource):
    @require_auth
    @require_role("student")
    def get(self, club_id):
        try:
            with get_session() as db:

                requests = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.club_id == club_id,
                        ClubMembership.status == MembershipStatus.PENDING
                    )
                    .all()
                )


                return [
                    serialize_membership(member)
                    for member in requests
                ], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



# -------------------------------------------------
# GET /api/clubs/<club_id>/members/<user_id>/role
# -------------------------------------------------

class UserRoleInClubResource(Resource):
    @require_auth
    def get(self, club_id, user_id):
        try:
            with get_session() as db:

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.club_id == club_id,
                        ClubMembership.user_id == user_id,
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                    .first()
                )


                if not membership:

                    return {
                        "message": "Membership not found."
                    }, 404



                return {

                    "club_id": club_id,

                    "user_id": user_id,

                    "role_in_club": (
                        membership.role_in_club.value.lower()
                        if membership.role_in_club
                        else None
                    )

                }, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

# -------------------------------------------------
# PATCH /api/memberships/<id>/role
# -------------------------------------------------

class UpdateMemberRoleResource(Resource):

    @require_auth
    @require_club_role("president")
    def patch(self, id):
        try:
            data = request.get_json()

            if not data:
                return {
                    "message": "Request body required."
                }, 400


            new_role = data.get("role_in_club")

            if not new_role:
                return {
                    "message": "role_in_club is required."
                }, 400


            with get_session() as db:

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.id == id
                    )
                    .first()
                )


                if not membership:
                    return {
                        "message": "Membership not found."
                    }, 404


                try:

                    membership.role_in_club = ClubMemberRole(
                        new_role
                    )

                except ValueError:

                    return {
                        "message": "Invalid club role."
                    }, 400


                db.commit()
                db.refresh(membership)


                return {
                    "message": "Member role updated successfully.",
                    "membership": serialize_membership(membership)
                }, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

# -------------------------------------------------
# Route Registration
# -------------------------------------------------

api.add_resource(UserClubResource,"/users/<int:user_id>/clubs")
api.add_resource(ClubMembersResource,"/clubs/<int:club_id>/members","/club_memberships")
api.add_resource(ClubMembershipRequestsResource,"/clubs/<int:club_id>/membership-requests")
api.add_resource(UserRoleInClubResource,"/clubs/<int:club_id>/members/<int:user_id>/role")
api.add_resource(UpdateMemberRoleResource,"/memberships/<int:id>/role")