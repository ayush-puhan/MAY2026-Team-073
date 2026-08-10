from flask import Blueprint
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import Document
from app.database.enums import DocumentType


# ---------------------------------------------------
# Blueprint Setup
# ---------------------------------------------------

certificate_bp = Blueprint(
    "certificates",
    __name__
)

api = Api(certificate_bp)


# ---------------------------------------------------
# Serializer
# ---------------------------------------------------

def serialize_certificate(document):

    return {
        "id": document.id,
        "title": document.title,
        "file_url": document.file_url,
        "owner_id": document.owner_id,
        "club_id": document.club_id,
        "event_id": document.event_id,
        "committee_id": document.committee_id,
        "created_at": (
            document.created_at.isoformat()
            if document.created_at
            else None
        )
    }


# ---------------------------------------------------
# GET USER CERTIFICATES
# GET /api/users/<user_id>/certificates
# ---------------------------------------------------

class UserCertificatesResource(Resource):

    def get(self, user_id):
        try:
            with get_session() as db:

                certificates = (
                    db.query(Document)
                    .filter(
                        Document.owner_id == user_id,
                        Document.doc_type == DocumentType.CERTIFICATE
                    )
                    .order_by(
                        Document.created_at.desc()
                    )
                    .all()
                )


                return [
                    serialize_certificate(certificate)
                    for certificate in certificates
                ], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



# ---------------------------------------------------
# Routes
# ---------------------------------------------------

api.add_resource(
    UserCertificatesResource,
    "/users/<int:user_id>/certificates"
)