from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.applications import ClubJoinApplication
from app.database.enums import MembershipStatus


application_bp = Blueprint(
    "club_join_applications",
    __name__
)

api = Api(application_bp)



def serialize_application(application):
    """
    Convert ClubJoinApplication object into JSON.
    """

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

        "skills": application.skills,

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
# GET /api/club_join_applications
#
# Examples:
#
# /club_join_applications
#
# /club_join_applications?club_id=1
#
# /club_join_applications?user_id=5
#
# /club_join_applications?status=pending
#
# /club_join_applications?club_id=1&status=pending
#
# -------------------------------------------------


class ClubJoinApplicationResource(Resource):

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



        with get_session() as db:


            query = db.query(
                ClubJoinApplication
            )



            if club_id:

                query = query.filter(
                    ClubJoinApplication.club_id
                    ==
                    int(club_id)
                )



            if user_id:

                query = query.filter(
                    ClubJoinApplication.user_id
                    ==
                    int(user_id)
                )



            if status:

                try:

                    query = query.filter(
                        ClubJoinApplication.status
                        ==
                        MembershipStatus(
                            status.lower()
                        )
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
# Route Registration
# -------------------------------------------------

api.add_resource(
    ClubJoinApplicationResource,
    "/club_join_applications"
)