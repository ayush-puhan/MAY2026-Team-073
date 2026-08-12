"""
Club/Committee Resources APIs
"""

from datetime import datetime

from flask import Blueprint, g, request
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models.communication import Document
from app.database.models.clubs import Committee
from app.database.enums import DocumentType
from app.middleware.auth_middleware import require_auth, require_club_role


communication_bp = Blueprint(
    "communication",
    __name__,
)

api = Api(communication_bp)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def serialize_document(document: Document):
    return {
        "id": document.id,
        "owner_id": document.owner_id,
        "club_id": document.club_id,
        "committee_id": document.committee_id,
        "event_id": document.event_id,
        "doc_type": document.doc_type.value,
        "title": document.title,
        "file_url": document.file_url,
        "created_at": document.created_at.isoformat(),
    }


# =========================================================
# GET / POST Club Resources
# =========================================================

class ClubResourcesResource(Resource):

    @require_auth
    @require_club_role(
        "member",
        "secretary",
        "volunteer_coordinator",
        "event_coordinator",
        "treasurer",
        "vice_president",
        "president",
    )
    def get(self, club_id):
        try:
            with get_session() as db:

                resources = (
                    db.query(Document)
                    .filter(
                        Document.club_id == club_id,
                        Document.committee_id == None
                    )
                    .order_by(Document.created_at.desc())
                    .all()
                )
                return [serialize_document(r) for r in resources], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


    @require_auth
    @require_club_role(
        "president",
        "vice_president",
        "secretary",
        "treasurer",
        "event_coordinator",
        "volunteer_coordinator"
    )
    def post(self, club_id):
        try:
            print("Current user:", getattr(g, "current_user", None))
            print("Current user id:", getattr(getattr(g, "current_user", None), "id", None))

            data = request.get_json()
            
            title = data.get("title")
            file_url = data.get("file_url")
            owner_id = g.current_user.id

            if not title:
                return {"message": "title is required"}, 400

            if not file_url:
                return {"message": "file_url is required"}, 400

            doc_type = data.get("doc_type", "GENERAL")

            try:
                document = Document(
                    owner_id=owner_id,
                    club_id=club_id,
                    committee_id=None,
                    event_id=None,
                    title=title,
                    file_url=file_url,
                    doc_type=DocumentType(doc_type.lower()),
                    created_at=datetime.utcnow(),
                )

            except ValueError:
                return {"message": "Invalid document type"}, 400

            with get_session() as db:

                db.add(document)
                db.commit()
                db.refresh(document)

                return serialize_document(document), 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# =========================================================
# DELETE Club Resource
# =========================================================

class ClubResourceDeleteResource(Resource):

    @require_auth
    @require_club_role(
        "president",
        "vice_president",
        "secretary",
        "treasurer",
        "event_coordinator",
        "volunteer_coordinator"
    )
    def delete(self, club_id, id):
        try:
            with get_session() as db:

                document = (
                    db.query(Document)
                    .filter(
                        Document.id == id,
                        Document.club_id == club_id,
                    )
                    .first()
                )

                if not document:
                    return {"message": "Resource not found"}, 404

                db.delete(document)
                db.commit()

                return {
                    "message": "Resource deleted successfully"
                }, 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500

# =========================================================
# Committee Resources
# =========================================================
class CommitteeResourcesResource(Resource):
    @require_auth
    @require_club_role(
        "member",
        "secretary",
        "president",
        "faculty_advisor",
    )
    def get(self, id):
        try:
            with get_session() as db:

                committee = (
                    db.query(Committee)
                    .filter(Committee.id == id)
                    .first()
                )
                if not committee:
                    return {"message": "Committee not found"}, 404

                resources = (
                    db.query(Document)
                    .filter(Document.committee_id == id)
                    .order_by(Document.created_at.desc())
                    .all()
                )
                return [serialize_document(r) for r in resources], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# =========================================================
# Routes
# =========================================================

api.add_resource(
    ClubResourcesResource,
    "/clubs/<int:club_id>/resources",
)

api.add_resource(
    ClubResourceDeleteResource,
    "/clubs/<int:club_id>/resources/<int:id>",
)

api.add_resource(
    CommitteeResourcesResource,
    "/committees/<int:id>/resources",
)