from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.applications import ClubJoinApplication
from app.database.enums import MembershipStatus
from app.middleware.auth_middleware import require_auth, require_role

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
    @require_role("student")
    def get(self, club_id):

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


# -------------------------------------------------
# GET /api/users/<user_id>/club-applications
# -------------------------------------------------

class UserClubApplicationsResource(Resource):

    def get(self, user_id):

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


# -------------------------------------------------
# POST /api/clubs/<club_id>/applications
# -------------------------------------------------

class ClubApplicationSubmissionResource(Resource):

    def post(self, club_id):

        data = request.get_json()

        if not data:

            return {
                "message":
                "Request body required."
            }, 400


        required = [

            "user_id",

            "motivation"

        ]

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

                user_id=data["user_id"],

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


# -------------------------------------------------
# PATCH /api/club-applications/<id>/review
# -------------------------------------------------

class ReviewApplicationResource(Resource):

    def patch(self, application_id):

        data = request.get_json()

        if not data:

            return {

                "message":
                "Request body required."

            }, 400


        with get_session() as db:

            application = (

                db.query(ClubJoinApplication)

                .filter_by(id=application_id)

                .first()

            )

            if not application:

                return {

                    "message":
                    "Application not found."

                }, 404


            if "status" in data:

                try:

                    application.status = MembershipStatus(
                        data["status"].lower()
                    )

                except ValueError:

                    return {

                        "message":
                        "Invalid application status."

                    }, 400


            application.reviewed_by = data.get(
                "reviewed_by"
            )

            application.review_comments = data.get(
                "review_comments"
            )

            application.reviewed_at = data.get(
                "reviewed_at"
            )

            db.commit()

            db.refresh(application)

            return {

                "message":
                "Application reviewed successfully.",

                "application":
                serialize_application(application)

            }, 200


# -------------------------------------------------
# Route Registration
# -------------------------------------------------

api.add_resource(ClubApplicationsResource,"/clubs/<int:club_id>/applications")
api.add_resource(UserClubApplicationsResource,"/users/<int:user_id>/club-applications")
api.add_resource(ClubApplicationSubmissionResource,"/clubs/<int:club_id>/applications")
api.add_resource(ReviewApplicationResource,"/club-applications/<int:application_id>/review")