from flask import Blueprint, request, g
from flask_restful import Api, Resource
from datetime import datetime
from app.database.database import get_session
from app.database.models import (Club,Committee,CommitteeMembership,ClubMembership,User)
from app.database.enums import (CommitteeRole,MembershipStatus,ClubMemberRole,)
from app.middleware.auth_middleware import (require_auth,require_club_role,)


committee_bp = Blueprint("committee", __name__)
api = Api(committee_bp)


# -------------------------------------------------------
# Serializers
# -------------------------------------------------------

def serialize_committee(committee):
    return {
        "id": committee.id,
        "club_id": committee.club_id,
        "name": committee.name,
        "description": committee.description,
        "created_at": (
            committee.created_at.isoformat(sep=" ")
            if committee.created_at
            else None
        ),
    }


def serialize_committee_membership(link):
    return {
        "id": link.id,
        "committee_id": link.committee_id,
        "membership_id": link.membership_id,
        "role": (
            link.role.value
            if hasattr(link.role, "value")
            else link.role
        ),
        "joined_at": (
            link.joined_at.isoformat(sep=" ")
            if link.joined_at
            else None
        ),
    }

def return_db_error(e):
    return {'message' : f"Error : {e}"},500

# -------------------------------------------------------
# /clubs/<club_id>/committees
# -------------------------------------------------------

class CommitteeListResource(Resource):

    @require_auth
    @require_club_role(
        ClubMemberRole.MEMBER.value,
        ClubMemberRole.SECRETARY.value,
        ClubMemberRole.TREASURER.value,
        ClubMemberRole.EVENT_COORDINATOR.value,
        ClubMemberRole.VOLUNTEER_COORDINATOR.value,
        ClubMemberRole.VICE_PRESIDENT.value,
        ClubMemberRole.PRESIDENT.value,
    )
    def get(self, club_id=None):
        try:
            if club_id is None:
                club_id = request.args.get("club_id")

            if not club_id:
                return {
                    "message": "Club ID missing"
                }, 400

            club_id = int(club_id)

            with get_session() as db:

                club = (
                    db.query(Club)
                    .filter_by(id=club_id)
                    .first()
                )

                if not club:
                    return {
                        "message": "Club not found"
                    }, 404

                committees = (
                    db.query(Committee)
                    .filter_by(club_id=club_id)
                    .order_by(Committee.name)
                    .all()
                )

                return [
                        serialize_committee(c)
                        for c in committees
                    ], 200
        except Exception as e:
            return return_db_error(e)
    @require_auth
    @require_club_role(
        ClubMemberRole.PRESIDENT.value
    )
    def post(self, club_id):
        try:
            data = request.get_json() or {}
            name = data.get("name")
            description = data.get("description")
            if not name:
                return {
                    "message": "Committee name is required"
                }, 400
            with get_session() as db:
                club = db.query(Club).filter_by(id=club_id).first()
                if not club:
                    return {
                        "message": "Club not found"
                    }, 404
                existing = (
                    db.query(Committee)
                    .filter(
                        Committee.club_id == club_id,
                        Committee.name == name,
                    )
                    .first()
                )
                if existing:
                    return {
                        "message": "Committee already exists"
                    }, 409
                committee = Committee(
                    club_id=club_id,
                    name=name,
                    description=description,
                    created_at=datetime.utcnow(),
                )
                db.add(committee)
                db.commit()
                db.refresh(committee)
                return {
                    "message": "Committee created successfully",
                    "committee": serialize_committee(
                        committee
                    ),
                }, 201
        except Exception as e:
            return return_db_error(e)

# -------------------------------------------------------
# /committees/<committee_id>/members
# -------------------------------------------------------

class CommitteeMemberResource(Resource):

    @require_auth
    def get(self, committeeId=None):
        try:
            # Case 1:
            # /committee_memberships?committeeId=3
            if committeeId is None:
                committeeId = request.args.get("committeeId")

            club_id = request.args.get("club_id")


            with get_session() as db:

                # --------------------------------------------
                # Get members of a specific committee
                # --------------------------------------------
                if committeeId:

                    committee_id = int(committeeId)

                    committee = (
                        db.query(Committee)
                        .filter_by(id=committee_id)
                        .first()
                    )

                    if not committee:
                        return {
                            "message": "Committee not found"
                        }, 404


                    # Check user belongs to club
                    membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.club_id == committee.club_id,
                            ClubMembership.user_id == g.current_user.id,
                            ClubMembership.status == MembershipStatus.APPROVED
                        )
                        .first()
                    )

                    if not membership:
                        return {
                            "message": "You are not a member of this club"
                        }, 403


                    links = (
                        db.query(CommitteeMembership)
                        .filter_by(
                            committee_id=committee_id
                        )
                        .all()
                    )


                # --------------------------------------------
                # Get members of all committees in a club
                # --------------------------------------------
                elif club_id:

                    club_id = int(club_id)

                    # Check user belongs to club
                    membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.club_id == club_id,
                            ClubMembership.user_id == g.current_user.id,
                            ClubMembership.status == MembershipStatus.APPROVED
                        )
                        .first()
                    )

                    if not membership:
                        return {
                            "message": "You are not a member of this club"
                        }, 403


                    committee_ids = (
                        db.query(Committee.id)
                        .filter_by(club_id=club_id)
                        .all()
                    )

                    committee_ids = [
                        c[0]
                        for c in committee_ids
                    ]


                    links = (
                        db.query(CommitteeMembership)
                        .filter(
                            CommitteeMembership.committee_id.in_(committee_ids)
                        )
                        .all()
                    )


                else:
                    return {
                        "message": "committee_id or club_id required"
                    }, 400



                # --------------------------------------------
                # Serialize response
                # --------------------------------------------

                # Batch fetch all memberships and users in one query
                membership_ids = [link.membership_id for link in links]
                if membership_ids:
                    club_members = (
                        db.query(ClubMembership)
                        .filter(ClubMembership.id.in_(membership_ids))
                        .all()
                    )
                    membership_map = {cm.id: cm for cm in club_members}

                    user_ids = [cm.user_id for cm in club_members]
                    users = (
                        db.query(User)
                        .filter(User.id.in_(user_ids))
                        .all()
                    )
                    user_map = {u.id: u for u in users}
                else:
                    membership_map = {}
                    user_map = {}

                members = []

                for link in links:

                    club_member = membership_map.get(link.membership_id)

                    if not club_member:
                        continue

                    user = user_map.get(club_member.user_id)

                    members.append({
                        "committee_membership": (
                            serialize_committee_membership(link)
                        ),

                        "membership": {
                            "id": club_member.id,
                            "user_id": club_member.user_id,
                            "club_id": club_member.club_id,
                            "role_in_club": (
                                club_member.role_in_club.value
                            ),
                            "status": (
                                club_member.status.value
                            ),
                        },
                        
                        "user": {
                            "id": user.id if user else None,
                            "first_name": user.full_name if user else "Member",
                            "last_name": "",
                            "email": user.email if user else ""
                        } if user else None
                    })


                return members, 200
        except Exception as e:
            return return_db_error(e)


    @require_auth
    def post(self, committeeId):
        try:
            data = request.get_json() or {}

            membership_id = data.get("membership_id")
            role = data.get("role", CommitteeRole.MEMBER.value)

            if not membership_id:
                return {
                    "message": "membership_id is required"
                }, 400

            with get_session() as db:

                committee = (
                    db.query(Committee)
                    .filter_by(id=committeeId)
                    .first()
                )

                if not committee:
                    return {
                        "message": "Committee not found"
                    }, 404

                current_user_membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.club_id == committee.club_id,
                        ClubMembership.user_id == g.current_user.id,
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                    .first()
                )

                if not current_user_membership:
                    return {
                        "message": "You are not a member of this club"
                    }, 403

                if current_user_membership.role_in_club not in [
                    ClubMemberRole.PRESIDENT,
                    ClubMemberRole.VICE_PRESIDENT
                ]:
                    return {
                        "message": "Insufficient permissions"
                    }, 403

                club_membership = (
                    db.query(ClubMembership)
                    .filter_by(id=membership_id)
                    .first()
                )

                if not club_membership:
                    return {
                        "message": "Membership not found"
                    }, 404

                if club_membership.club_id != committee.club_id:
                    return {
                        "message": "Member does not belong to this club"
                    }, 400

                existing = (
                    db.query(CommitteeMembership)
                    .filter(
                        CommitteeMembership.committee_id == committeeId,
                        CommitteeMembership.membership_id == membership_id
                    )
                    .first()
                )

                if existing:
                    return {
                        "message": "Member already exists in committee"
                    }, 409

                try:
                    role_enum = CommitteeRole(role)
                except ValueError:
                    return {
                        "message": "Invalid committee role"
                    }, 400

                committee_member = CommitteeMembership(
                    committee_id=committeeId,
                    membership_id=membership_id,
                    role=role_enum,
                    joined_at=datetime.utcnow()
                )

                db.add(committee_member)
                db.commit()
                db.refresh(committee_member)

                return {
                    "message": "Member added successfully",
                    "committee_membership":
                        serialize_committee_membership(
                            committee_member
                        )
                }, 201
        except Exception as e:
            return return_db_error(e)


# -------------------------------------------------------
# /committee-memberships/<membership_id>
# -------------------------------------------------------

class CommitteeMembershipResource(Resource):

    @require_auth
    @require_club_role(
        "president",
        "vice_president",
    )
    def patch(self, membership_id):
        try:
            data = request.get_json() or {}

            role = data.get("role")

            if not role:
                return {
                    "message": "role is required"
                }, 400

            with get_session() as db:

                committee_member = (
                    db.query(CommitteeMembership)
                    .filter_by(id=membership_id)
                    .first()
                )

                if not committee_member:
                    return {
                        "message": "Committee membership not found"
                    }, 404

                committee = (
                    db.query(Committee)
                    .filter_by(id=committee_member.committee_id)
                    .first()
                )

                current_user_membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.club_id == committee.club_id,
                        ClubMembership.user_id == g.current_user.id,
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                    .first()
                )

                if not current_user_membership:
                    return {
                        "message": "You are not a member of this club"
                    }, 403

                

                try:
                    committee_member.role = CommitteeRole(role)
                except ValueError:
                    return {
                        "message": "Invalid committee role"
                    }, 400

                db.commit()
                db.refresh(committee_member)

                return {
                    "message": "Committee member role updated successfully",
                    "committee_membership": serialize_committee_membership(
                        committee_member
                    )
                }, 200
            
        except Exception as e :
            return return_db_error(e)


    @require_auth
    @require_club_role(
        "president",
        "vice_president",
    )
    def delete(self, membership_id):
        try:
            with get_session() as db:

                committee_member = (
                    db.query(CommitteeMembership)
                    .filter_by(id=membership_id)
                    .first()
                )

                if not committee_member:
                    return {
                        "message": "Committee membership not found"
                    }, 404

                committee = (
                    db.query(Committee)
                    .filter_by(id=committee_member.committee_id)
                    .first()
                )

                current_user_membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.club_id == committee.club_id,
                        ClubMembership.user_id == g.current_user.id,
                        ClubMembership.status == MembershipStatus.APPROVED
                    )
                    .first()
                )

                if not current_user_membership:
                    return {
                        "message": "You are not a member of this club"
                    }, 403

                

                db.delete(committee_member)
                db.commit()

                return {
                    "message": "Committee member removed successfully"
                }, 200
        except Exception as e:
            return return_db_error(e)


# -------------------------------------------------------
# Route Registration
# -------------------------------------------------------

api.add_resource(
    CommitteeListResource,
    "/committees",
    "/clubs/<int:club_id>/committees"
)

api.add_resource(
    CommitteeMemberResource,
    "/committees/<int:committeeId>/members",
    "/committee_memberships"
)

api.add_resource(
    CommitteeMembershipResource,
    "/committee-memberships/<int:committeeMembershipId>"
)
