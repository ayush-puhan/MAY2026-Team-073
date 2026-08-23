from datetime import datetime

from flask import Blueprint, g, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.clubs import ClubMembership, CommitteeMembership
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
        "role_in_club": ( member.role_in_club.value.lower() if member.role_in_club else None),
        "status": ( member.status.value.lower() if member.status else None),
        "applied_at": ( member.applied_at.isoformat() if member.applied_at else None),
        "decided_at": ( member.decided_at.isoformat() if member.decided_at else None),
        "approved_by": member.approved_by,
        "rejection_reason": member.rejection_reason,
        "user": ({
                "id": member.user.id,
                "full_name": member.user.full_name,
                "email": member.user.email,
                "profile_photo_url": member.user.profile_photo_url,
                "role": ( member.user.role.value.lower() if member.user.role else None)
            } if member.user else None)
    }



def serialize_user_club(member, db=None):
    """
    Response format:
    GET /api/users/<user_id>/clubs
    """

    club = member.club

    # derived member count
    def _get_count(session):
        return (
            session.query(ClubMembership)
            .filter(
                ClubMembership.club_id == club.id,
                ClubMembership.status == MembershipStatus.APPROVED
            )
            .count()
        )

    if db is not None:
        member_count = _get_count(db)
    else:
        with get_session() as session:
            member_count = _get_count(session)



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
                    serialize_user_club(member, db=db)
                    for member in memberships
                ], 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500



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
            return {'message'  :  f"Error  :  {e}"}, 500
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
            return {'message'  :  f"Error  :  {e}"}, 500



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
            return {'message'  :  f"Error  :  {e}"}, 500

# -------------------------------------------------
# PATCH /api/memberships/<id>/role
# -------------------------------------------------

class UpdateMemberRoleResource(Resource):

    @require_auth
    @require_club_role(
        "president",
        "vice_president",
        "secretary",
        "event_coordinator",
        "volunteer_coordinator"
    )
    def patch(self, club_id, id):
        try:
            data = request.get_json(silent=True)

            if not data:
                return {"message": "Request body required."}, 400

            new_role = data.get("role") or data.get("role_in_club")

            if not new_role:
                return {"message": "role (or role_in_club) is required."}, 400

            with get_session() as db:

                membership = (
                    db.query(ClubMembership)
                    .filter(ClubMembership.id == id)
                    .first()
                )

                if not membership:
                    return {"message": "Membership not found."}, 404

                try:
                    membership.role_in_club = ClubMemberRole(new_role)
                except ValueError:
                    return {
                        "message": f"Invalid club role: {new_role}"
                    }, 400

                db.commit()
                db.refresh(membership)

                return {
                    "message": "Member role updated successfully.",
                    "membership": serialize_membership(membership)
                }, 200

        except Exception as e:
            import traceback
            traceback.print_exc()

            return {
                "message": f"ERROR: {str(e)}"
            }, 500     
# -------------------------------------------------
# POST /api/clubs/<club_id>/join
# API 7: Join Club
# -------------------------------------------------

class JoinClubResource(Resource):

    @require_auth
    @require_role("student")
    def post(self, club_id):
        try:
            data = request.get_json(silent=True) or {}

            # The frontend may send role_in_club and reason.
            # We intentionally do NOT trust the role from the frontend.
            # A newly joining student always starts as MEMBER.
            with get_session() as db:

                # Check whether the club exists
                from app.database.models.clubs import Club

                club = (
                    db.query(Club)
                    .filter(Club.id == club_id)
                    .first()
                )

                if not club:
                    return {
                        "message": "Club not found."
                    }, 404

                # Get the authenticated student
                user_id = g.current_user.id

                # Check existing membership
                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.user_id == user_id,
                        ClubMembership.club_id == club_id
                    )
                    .first()
                )

                # -------------------------------------------------
                # Already has a membership
                # -------------------------------------------------

                if membership:

                    if membership.status == MembershipStatus.APPROVED:
                        return {
                            "message": "You are already a member of this club."
                        }, 400

                    if membership.status == MembershipStatus.PENDING:
                        return {
                            "message": "Your membership request is already pending."
                        }, 400

                    # Allow a rejected/withdrawn student to apply again
                    if membership.status in (
                        MembershipStatus.REJECTED,
                        MembershipStatus.WITHDRAWN
                    ):
                        membership.status = MembershipStatus.PENDING
                        membership.role_in_club = ClubMemberRole.MEMBER
                        membership.applied_at = datetime.utcnow()
                        membership.decided_at = None
                        membership.approved_by = None
                        membership.rejection_reason = None

                        db.commit()
                        db.refresh(membership)

                        return {
                            "message": "Club membership request submitted successfully.",
                            "membership": serialize_membership(membership)
                        }, 201

                # -------------------------------------------------
                # Create new membership request
                # -------------------------------------------------

                membership = ClubMembership(
                    user_id=user_id,
                    club_id=club_id,
                    role_in_club=ClubMemberRole.MEMBER,
                    status=MembershipStatus.PENDING,
                    applied_at=datetime.utcnow()
                )

                db.add(membership)
                db.commit()
                db.refresh(membership)

                return {
                    "message": "Club membership request submitted successfully.",
                    "membership": serialize_membership(membership)
                }, 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        

# -------------------------------------------------
# PATCH /api/memberships/<membership_id>/approve
# API 8: Approve Membership
# -------------------------------------------------

class ApproveMembershipResource(Resource):

    @require_auth
    @require_club_role(
        "president",
        "vice_president"
    )
    def patch(self, membership_id):
        try:
            with get_session() as db:

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.id == membership_id
                    )
                    .first()
                )

                if not membership:
                    return {
                        "message": "Membership not found."
                    }, 404

                # Only pending requests can be approved
                if membership.status != MembershipStatus.PENDING:
                    return {
                        "message": (
                            "Only pending membership requests "
                            "can be approved."
                        )
                    }, 400

                # Approve membership
                membership.status = MembershipStatus.APPROVED
                membership.role_in_club = ClubMemberRole.MEMBER
                membership.decided_at = datetime.utcnow()
                membership.approved_by = g.current_user.id
                membership.rejection_reason = None

                db.commit()
                db.refresh(membership)

                return {
                    "message": "Membership approved successfully.",
                    "membership": serialize_membership(membership)
                }, 200
        except Exception as e:
                    return {'message'  :  f"ERROR  :  {e}"}, 500
        

# -------------------------------------------------
# PATCH /api/memberships/<membership_id>/reject
# API 9: Reject Membership
# -------------------------------------------------

class RejectMembershipResource(Resource):

    @require_auth
    @require_club_role(
        "president",
        "vice_president"
    )
    def patch(self, membership_id):
        try:
            data = request.get_json(silent=True) or {}

            reason = data.get("reason")

            with get_session() as db:

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.id == membership_id
                    )
                    .first()
                )

                if not membership:
                    return {
                        "message": "Membership not found."
                    }, 404

                # Only pending requests can be rejected
                if membership.status != MembershipStatus.PENDING:
                    return {
                        "message": (
                            "Only pending membership requests "
                            "can be rejected."
                        )
                    }, 400

                # Reject membership
                membership.status = MembershipStatus.REJECTED
                membership.decided_at = datetime.utcnow()
                membership.approved_by = None
                membership.rejection_reason = reason

                db.commit()
                db.refresh(membership)

                return {
                    "message": "Membership rejected successfully.",
                    "membership": serialize_membership(membership)
                }, 200
        except Exception as e:
                    return {'message'  :  f"ERROR  :  {e}"}, 500
        
# -------------------------------------------------
# DELETE /api/memberships/<membership_id>
# -------------------------------------------------

class RemoveMemberResource(Resource):

    @require_auth
    @require_club_role("president")
    def delete(self, membershipId):
        try:
            with get_session() as db:

                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.id == membershipId
                    )
                    .first()
                )

                if not membership:
                    return {
                        "message": "Membership not found."
                    }, 404

                # Prevent removing a non-approved member
                if membership.status != MembershipStatus.APPROVED:
                    return {
                        "message": "Only approved members can be removed."
                    }, 400

                # Prevent President from removing themselves
                if membership.role_in_club == ClubMemberRole.PRESIDENT:
                    return {
                        "message": "The President cannot be removed from the club."
                    }, 400

                # Remove committee memberships first
                # because CommitteeMembership references ClubMembership
                # and this also keeps the relationship clean.
                db.query(CommitteeMembership).filter(
                    CommitteeMembership.membership_id == membership.id
                ).delete(
                    synchronize_session=False
                )

                db.delete(membership)
                db.commit()

                return {
                    "message": "Member removed successfully."
                }, 200

        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
# -------------------------------------------------
# DELETE /api/clubs/<club_id>/memberships/<id>
# -------------------------------------------------

class RemoveMemberResource(Resource):
    @require_auth
    @require_club_role("president", "vice_president")
    def delete(self, club_id, id):
        try:
            with get_session() as db:
                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.id == id,
                        ClubMembership.club_id == club_id
                    )
                    .first()
                )

                if not membership:
                    return {"message": "Membership not found."}, 404

                if membership.role_in_club == ClubMemberRole.PRESIDENT:
                    return {"message": "Cannot remove the president."}, 400

                db.delete(membership)
                db.commit()

                return {"message": "Member removed successfully."}, 200
        except Exception as e:
            return {'message': f"Error: {e}"}, 500

# -------------------------------------------------
# Route Registration
# -------------------------------------------------

api.add_resource(JoinClubResource,"/clubs/<int:club_id>/join")
api.add_resource(ApproveMembershipResource,"/memberships/<int:membership_id>/approve")
api.add_resource(RejectMembershipResource,"/memberships/<int:membership_id>/reject")
api.add_resource(UserClubResource,"/users/<int:user_id>/clubs")
api.add_resource(ClubMembersResource,"/clubs/<int:club_id>/members","/club_memberships")
api.add_resource(ClubMembershipRequestsResource,"/clubs/<int:club_id>/membership-requests")
api.add_resource(UserRoleInClubResource,"/clubs/<int:club_id>/members/<int:user_id>/role")
api.add_resource(UpdateMemberRoleResource,"/clubs/<int:club_id>/memberships/<int:id>/role")
api.add_resource(RemoveMemberResource,"/clubs/<int:club_id>/memberships/<int:id>")
