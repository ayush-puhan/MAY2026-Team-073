from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import Interest


# ---------------------------------------------------
# Blueprint Setup
# ---------------------------------------------------

interest_bp = Blueprint("interest", __name__)
api = Api(interest_bp)


# ---------------------------------------------------
# Serializer
# ---------------------------------------------------

def serialize_interest(interest):
    return {
        "id": interest.id,
        "name": interest.name,
        "created_at": (
            interest.created_at.isoformat()
            if interest.created_at
            else None
        )
    }


# ---------------------------------------------------
# GET /api/interests
# POST /api/interests
# ---------------------------------------------------

class InterestListResource(Resource):

    def get(self):
        try:
            with get_session() as db:

                interests = (
                    db.query(Interest)
                    .order_by(Interest.name.asc())
                    .all()
                )

                return [
                    serialize_interest(i)
                    for i in interests
                ], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500


    def post(self):
        try:
            data = request.get_json()

            if not data or not data.get("name"):
                return {
                    "message": "Interest name is required"
                }, 400


            with get_session() as db:

                existing = (
                    db.query(Interest)
                    .filter(
                        Interest.name == data["name"]
                    )
                    .first()
                )

                if existing:
                    return {
                        "message": "Interest already exists"
                    }, 409


                interest = Interest(
                    name=data["name"]
                )

                db.add(interest)
                db.commit()
                db.refresh(interest)


                return serialize_interest(interest), 201
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



# ---------------------------------------------------
# GET /api/interests/<id>
# PATCH /api/interests/<id>
# DELETE /api/interests/<id>
# ---------------------------------------------------

class InterestResource(Resource):

    def get(self, interest_id):
        try:
            with get_session() as db:

                interest = (
                    db.query(Interest)
                    .filter(
                        Interest.id == interest_id
                    )
                    .first()
                )

                if not interest:
                    return {
                        "message": "Interest not found"
                    }, 404


                return serialize_interest(interest), 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



    def patch(self, interest_id):
        try:
            data = request.get_json()

            with get_session() as db:

                interest = (
                    db.query(Interest)
                    .filter(
                        Interest.id == interest_id
                    )
                    .first()
                )

                if not interest:
                    return {
                        "message": "Interest not found"
                    }, 404


                if "name" in data:
                    interest.name = data["name"]


                db.commit()
                db.refresh(interest)


                return serialize_interest(interest), 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



    def delete(self, interest_id):
        try:
            with get_session() as db:

                interest = (
                    db.query(Interest)
                    .filter(
                        Interest.id == interest_id
                    )
                    .first()
                )

                if not interest:
                    return {
                        "message": "Interest not found"
                    }, 404


                db.delete(interest)
                db.commit()


                return {
                    "message": "Interest deleted successfully"
                }, 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500



# ---------------------------------------------------
# Routes
# ---------------------------------------------------

api.add_resource(
    InterestListResource,
    "/interests"
)


api.add_resource(
    InterestResource,
    "/interests/<int:interest_id>"
)