from flask import Blueprint, g, request
from datetime import datetime
from flask_restful import Api, Resource
from app.database.models.clubs import ClubMembership
from app.database import get_session
from app.database.models.applications import ClubJoinApplication
from app.database.enums import MembershipStatus, ClubMemberRole
from app.middleware.auth_middleware import require_auth, require_club_role, require_role

application_bp = Blueprint(
    "club_join_applications",
    __name__
)

api = Api(application_bp)


# -------------------------------------------------
# Serializers
# -------------------------------------------------

def serialize_application(application):

    return {

        "id": application.id,

        "user_id": application.user_id,

        "club_id": application.club_id,

        "club_name": (
            application.club.name
            if application.club
            else None
        ),

        "user_name": (
            application.user.full_name
            if application.user
            else None
        ),

        "user": (
            {
                "id": application.user.id,
                "full_name": application.user.full_name,
                "email": application.user.email,
                "profile_photo_url": application.user.profile_photo_url,
            }
            if application.user
            else None
        ),

        "motivation": application.motivation,

        "contribution": application.contribution,

        "previous_experience":
            application.previous_experience,

        "skills":
            application.skills,

        "portfolio_url":
            application.portfolio_url,

        "resume_document_id":
            application.resume_document_id,

        "weekly_availability":
            application.weekly_availability,

        "status": (
            application.status.value.lower()
            if application.status
            else None
        ),

        "reviewed_by":
            application.reviewed_by,

        "review_comments":
            application.review_comments,

        "applied_at": (
            application.applied_at.isoformat()
            if application.applied_at
            else None
        ),

        "reviewed_at": (
            application.reviewed_at.isoformat()
            if application.reviewed_at
            else None
        )
    }


# -------------------------------------------------
# GET /api/clubs/<club_id>/applications
# -------------------------------------------------

class ClubApplicationsResource(Resource):
    @require_auth
    @require_club_role("president", "vice_president")
    def get(self, club_id):
        try:
            status = request.args.get("status")

            with get_session() as db:

                query = (
                    db.query(ClubJoinApplication)
                    .filter(
                        ClubJoinApplication.club_id == club_id
                    )
                )

                if status:

                    try:

                        query = query.filter(
                            ClubJoinApplication.status ==
                            MembershipStatus(status.lower())
                        )

                    except ValueError:

                        return {
                            "message":
                            "Invalid application status."
                        }, 400

                applications = query.all()

                return [

                    serialize_application(application)

                    for application in applications

                ], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# GET /api/users/<user_id>/club-applications
# -------------------------------------------------

class UserClubApplicationsResource(Resource):
    @require_auth
    def get(self, user_id):
        try:
            with get_session() as db:

                applications = (

                    db.query(ClubJoinApplication)

                    .filter(
                        ClubJoinApplication.user_id == user_id
                    )

                    .all()

                )

                return [

                    serialize_application(application)

                    for application in applications

                ], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# POST /api/clubs/<club_id>/applications
# -------------------------------------------------

class ClubApplicationSubmissionResource(Resource):
    @require_auth
    @require_role("student")
    def post(self, club_id):
        try:
            data = request.get_json()

            if not data:

                return {
                    "message":
                    "Request body required."
                }, 400


            required = ["motivation"]

            missing = [

                field

                for field in required

                if not data.get(field)

            ]

            if missing:

                return {

                    "message":

                    f"Missing fields: {', '.join(missing)}"

                }, 400


            with get_session() as db:

                application = ClubJoinApplication(

                    user_id=g.current_user.id,

                    club_id=club_id,

                    motivation=data["motivation"],

                    contribution=data.get("contribution"),

                    previous_experience=data.get(
                        "previous_experience"
                    ),

                    skills=data.get("skills"),

                    portfolio_url=data.get(
                        "portfolio_url"
                    ),

                    resume_document_id=data.get(
                        "resume_document_id"
                    ),

                    weekly_availability=data.get(
                        "weekly_availability"
                    )

                )

                db.add(application)

                db.commit()

                db.refresh(application)

                return {

                    "message":
                    "Application submitted successfully.",

                    "application":
                    serialize_application(application)

                }, 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# PATCH /api/club-applications/<id>/review
# -------------------------------------------------

class ReviewApplicationResource(Resource):

    @require_auth
    @require_club_role(
        "president",
        "vice_president"
    )
    def patch(self, application_id):
        try:
            data = request.get_json()

            if not data:
                return {
                    "message": "Request body required."
                }, 400


            # Support frontend field name: decision
            # Also support API field name: status
            new_status = (
                data.get("status")
                or data.get("decision")
            )


            if not new_status:
                return {
                    "message": "Status/decision is required."
                }, 400


            try:
                new_status = MembershipStatus(
                    new_status.lower()
                )

            except ValueError:
                return {
                    "message": "Invalid application status."
                }, 400



            with get_session() as db:

                application = (
                    db.query(ClubJoinApplication)
                    .filter(
                        ClubJoinApplication.id == application_id
                    )
                    .first()
                )


                if not application:
                    return {
                        "message": "Application not found."
                    }, 404



                if application.status != MembershipStatus.PENDING:

                    return {
                        "message":
                        "Application already reviewed."
                    }, 400



                club_id = application.club_id


                if not club_id:
                    return {
                        "message":
                        "Application has no club assigned."
                    }, 400



                # -----------------------------
                # APPROVE APPLICATION
                # -----------------------------

                if new_status == MembershipStatus.APPROVED:


                    existing_membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.user_id ==
                            application.user_id,

                            ClubMembership.club_id ==
                            club_id
                        )
                        .first()
                    )


                    if existing_membership:

                        return {
                            "message":
                            "User already has membership."
                        }, 400



                    membership = ClubMembership(

                        user_id=application.user_id,

                        # Required field
                        club_id=club_id,

                        role_in_club=ClubMemberRole.MEMBER,

                        status=MembershipStatus.APPROVED,

                        applied_at=application.applied_at,

                        decided_at=datetime.utcnow(),

                        approved_by=g.current_user.id
                    )


                    db.add(membership)



                # -----------------------------
                # REJECT APPLICATION
                # -----------------------------

                elif new_status == MembershipStatus.REJECTED:

                    application.review_comments = (
                        data.get("review_comments")
                    )



                # -----------------------------
                # UPDATE APPLICATION
                # -----------------------------

                application.status = new_status

                application.reviewed_by = (
                    g.current_user.id
                )

                application.review_comments = (
                    data.get("review_comments")
                )

                application.reviewed_at = datetime.utcnow()



                db.commit()

                db.refresh(application)


                return {

                    "message":
                    "Application reviewed successfully.",

                    "application":
                    serialize_application(application)

                }, 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# Route Registration
# -------------------------------------------------

api.add_resource(ClubApplicationsResource,"/clubs/<int:club_id>/applications")
api.add_resource(UserClubApplicationsResource,"/users/<int:user_id>/club-applications")
api.add_resource(ClubApplicationSubmissionResource,"/clubs/<int:club_id>/applications")
api.add_resource(ReviewApplicationResource,"/club-applications/<int:application_id>/review")