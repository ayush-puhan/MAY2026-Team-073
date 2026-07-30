from datetime import datetime

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.clubs import Club, ClubCreationRequest
from app.database.enums import ClubStatus


club_bp = Blueprint("clubs", __name__)
api = Api(club_bp)


def serialize_club(club):
    """
    Convert Club model object into JSON response.
    """

    return {
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "category": club.category,
        "university_id": club.university_id,
        "status": club.status.value.lower()
        if club.status else None,
        "logo_url": club.logo_url,
        "banner": club.banner,
        "member_count_cache": club.member_count_cache,
        "slug": club.slug,
        "objectives": club.objectives,
        "faculty_advisor_id": club.faculty_advisor_id,
        "created_at": (
            club.created_at.isoformat()
            if club.created_at
            else None
        ),
        "updated_at": (
            club.updated_at.isoformat()
            if club.updated_at
            else None
        ),
    }


class ClubResource(Resource):

    def get(self, club_id=None):

        with get_session() as db:

            # GET /clubs/<club_id>
            if club_id:

                club = (
                    db.query(Club)
                    .filter_by(id=club_id)
                    .first()
                )

                if not club:
                    return {
                        "message": "Club not found."
                    }, 404

                return serialize_club(club), 200


            # GET /clubs
            clubs = db.query(Club).all()

            return [
                serialize_club(club)
                for club in clubs
            ], 200



    def patch(self, club_id):

        data = request.get_json()

        if not data:
            return {
                "message": "Request body required."
            }, 400


        with get_session() as db:

            club = (
                db.query(Club)
                .filter_by(id=club_id)
                .first()
            )

            if not club:
                return {
                    "message": "Club not found."
                }, 404


            allowed_fields = [
                "name",
                "description",
                "category",
                "objectives",
                "logo_url",
                "banner",
                "faculty_advisor_id",
                "member_count_cache",
                "slug",
                "university_id",
            ]


            for field in allowed_fields:

                if field in data:
                    setattr(
                        club,
                        field,
                        data[field]
                    )


            if "status" in data:

                try:
                    club.status = ClubStatus(
                        data["status"].upper()
                    )

                except ValueError:
                    return {
                        "message":
                        "Invalid club status."
                    }, 400


            db.commit()


            return {
                "message": "Club updated successfully.",
                "club": serialize_club(club)
            }, 200



    def delete(self, club_id):

        with get_session() as db:

            club = (
                db.query(Club)
                .filter_by(id=club_id)
                .first()
            )

            if not club:
                return {
                    "message": "Club not found."
                }, 404


            club.deleted_at = datetime.utcnow()
            club.status = ClubStatus.ARCHIVED


            db.commit()


            return {
                "message": "Club archived successfully."
            }, 200


class ClubProposalResource(Resource):

    def post(self):

        data = request.get_json()


        required_fields = [
            "proposed_name",
            "proposal_description",
            "requested_by"
        ]


        missing = [
            field
            for field in required_fields
            if not data.get(field)
        ]


        if missing:
            return {
                "message":
                f"Missing fields: {', '.join(missing)}"
            }, 400



        with get_session() as db:


            proposal = ClubCreationRequest(

                proposed_name=data["proposed_name"],

                proposed_category=data.get(
                    "proposed_category"
                ),

                proposal_description=data[
                    "proposal_description"
                ],

                requested_by=data[
                    "requested_by"
                ],

                faculty_advisor_id=data.get(
                    "faculty_advisor_id"
                )
            )


            db.add(proposal)

            db.commit()

            db.refresh(proposal)



            return {

                "message":
                "Club proposal submitted successfully.",

                "proposal_id":
                proposal.id

            }, 201



# -----------------------
# Route Registration
# -----------------------

api.add_resource(
    ClubResource,
    "",
    "/<int:club_id>"
)


api.add_resource(
    ClubProposalResource,
    "/propose"
)