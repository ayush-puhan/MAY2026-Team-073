from datetime import datetime

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.clubs import Club, ClubCreationRequest
from app.database.enums import ClubStatus

club_bp = Blueprint("clubs", __name__)
api = Api(club_bp)


class ClubResource(Resource):
    def get(self, club_id=None):
        with get_session() as db:

            # Get single club
            if club_id is not None:
                club = db.query(Club).filter_by(id=club_id).first()

                if not club:
                    return {"message": "Club not found."}, 404

                return {
                    "id": str(club.id),
                    "name": club.name,
                    "description": club.description,
                    "category": club.category,
                    "university_id": club.university_id,
                    "status": club.status.value.lower(),
                    "logo_url": club.logo_url,
                    "banner": club.banner,
                    "member_count_cache": club.member_count_cache,
                    "slug": club.slug,
                    "objectives": club.objectives,
                    "faculty_advisor_id": club.faculty_advisor_id,
                    "created_at": club.created_at.isoformat() if club.created_at else None,
                    "updated_at": club.updated_at.isoformat() if club.updated_at else None,
                }, 200

            # Get all clubs
            clubs = db.query(Club).all()

            return [
                {
                    "id": str(club.id),
                    "name": club.name,
                    "description": club.description,
                    "category": club.category,
                    "university_id": club.university_id,
                    "status": club.status.value.lower(),
                    "logo_url": club.logo_url,
                    "banner": club.banner,
                    "member_count_cache": club.member_count_cache,
                    "slug": club.slug,
                    "objectives": club.objectives,
                    "faculty_advisor_id": club.faculty_advisor_id,
                    "created_at": club.created_at.isoformat() if club.created_at else None,
                    "updated_at": club.updated_at.isoformat() if club.updated_at else None,
                }
                for club in clubs
            ], 200

    def patch(self, club_id):
        data = request.get_json()

        with get_session() as db:
            club = db.query(Club).filter_by(id=club_id).first()

            if not club:
                return {"message": "Club not found."}, 404

            updatable_fields = [
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

            for field in updatable_fields:
                if field in data:
                    setattr(club, field, data[field])

            if "status" in data:
                club.status = ClubStatus(data["status"].upper())

            db.commit()

            return {
                "message": "Club updated successfully."
            }, 200

    def delete(self, club_id):
        with get_session() as db:
            club = db.query(Club).filter_by(id=club_id).first()

            if not club:
                return {"message": "Club not found."}, 404

            # Soft delete (adjust according to your SoftDeleteMixin)
            club.deleted_at = datetime.utcnow()

            db.commit()

            return {
                "message": "Club archived successfully."
            }, 200


class ClubProposalResource(Resource):
    def post(self):
        data = request.get_json()

        proposed_name = data.get("proposed_name")
        proposed_category = data.get("proposed_category")
        proposal_description = data.get("proposal_description")
        requested_by = data.get("requested_by")
        faculty_advisor_id = data.get("faculty_advisor_id")

        if not proposed_name or not proposal_description or not requested_by:
            return {
                "message": "proposed_name, proposal_description and requested_by are required."
            }, 400

        with get_session() as db:
            proposal = ClubCreationRequest(
                proposed_name=proposed_name,
                proposed_category=proposed_category,
                proposal_description=proposal_description,
                requested_by=requested_by,
                faculty_advisor_id=faculty_advisor_id,
            )

            db.add(proposal)
            db.commit()

            return {
                "message": "Club proposal submitted successfully.",
                "proposal_id": proposal.id
            }, 201


api.add_resource(
    ClubResource,
    "",
    "/<int:club_id>"
)

api.add_resource(
    ClubProposalResource,
    "/propose"
)