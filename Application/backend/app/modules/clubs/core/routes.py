from flask import Blueprint, request, g
from flask_restful import Api, Resource
from app.database.database import get_session
from app.database.models import (Club,ClubMembership)
from app.database.enums import MembershipStatus
from app.middleware.auth_middleware import (require_auth, require_role)


club_bp = Blueprint("club",__name__)
api = Api(club_bp)

# ---------------------------------------------------
# Serializer
# ---------------------------------------------------
def serialize_club(club, db):

    # Approved student members count
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
                query = db.query(Club).filter(Club.university_id == user_university_id)
                
                if status:
                    from app.database.enums import ClubStatus
                    try:
                        query = query.filter(Club.status == ClubStatus[status.upper()])
                    except KeyError:
                        pass
                        
                clubs = query.all()
                return [
                    serialize_club(club,db)
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