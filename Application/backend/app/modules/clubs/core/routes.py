from flask import Blueprint, request, g
from flask_restful import Api, Resource
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from app.database.database import get_session
from app.database.models import (Club,ClubMembership)
from app.database.models.interests import ClubInterest
from app.database.enums import MembershipStatus
from app.middleware.auth_middleware import (require_auth, require_role)


club_bp = Blueprint("club",__name__)
api = Api(club_bp)

# ---------------------------------------------------
# Serializer
# ---------------------------------------------------
def serialize_club(club, db, member_count_map=None):

    # Approved student members count
    if member_count_map is not None:
        member_count = member_count_map.get(club.id, 0)
    else:
        member_count = (
            db.query(ClubMembership)
            .filter(
                ClubMembership.club_id == club.id,
                ClubMembership.status == MembershipStatus.APPROVED
            )
            .count()
        )
    # Interests
    interests = []
    if hasattr(club, "interest_links"):
        for link in club.interest_links:
            interests.append(
                link.interest.name
            )
    # University
    university = None
    if club.university:
        university = {"id": club.university.id,"name": club.university.name}

    return {
        "id": club.id,
        "name": club.name,
        "slug": getattr(club,"slug",None),
        "category": getattr(club,"category",None),
        "description": club.description,
        "logo_url": getattr(club,"logo_url",None),
        "banner": getattr(club,"banner",None),
        "status":
            club.status.value
            if hasattr(club.status, "value")
            else club.status,
        "members": member_count,
        "interests": interests,
        "university": university,
        "faculty_advisor_id": club.faculty_advisor_id
    }
# ---------------------------------------------------
# GET ALL CLUBS
# GET /api/clubs
# ---------------------------------------------------
class ClubListResource(Resource):

    @require_auth
    
    def get(self):
        try:
            # Always scope to the current user's university
            user_university_id = g.current_user.university_id
            status = request.args.get("status")
            
            with get_session() as db:
                query = db.query(Club).options(
                    joinedload(Club.university),
                    selectinload(Club.interest_links).joinedload(ClubInterest.interest)
                ).filter(Club.university_id == user_university_id)
                
                if status:
                    from app.database.enums import ClubStatus
                    try:
                        query = query.filter(Club.status == ClubStatus[status.upper()])
                    except KeyError:
                        pass

                clubs = query.all()

                # Batch member counts in a single query
                count_rows = (
                    db.query(ClubMembership.club_id, func.count(ClubMembership.id))
                    .filter(ClubMembership.status == MembershipStatus.APPROVED)
                    .group_by(ClubMembership.club_id)
                    .all()
                )
                member_count_map = dict(count_rows)

                return [
                    serialize_club(club, db, member_count_map)
                    for club in clubs
                ], 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

# ---------------------------------------------------
# GET CLUB BY ID
# GET /api/clubs/<club_id>
# ---------------------------------------------------

class ClubDetailResource(Resource):

    @require_auth
    def get(self,club_id):
        try:
            with get_session() as db:
                club = (db.query(Club).filter(Club.id == club_id).first())
                if not club:
                    return {
                        "message":
                        "Club not found"
                    },404

                return serialize_club(
                    club,
                    db
                ),200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500




# ---------------------------------------------------
# Routes
# ---------------------------------------------------

api.add_resource(ClubListResource,"")
api.add_resource(ClubDetailResource,"/<int:club_id>")