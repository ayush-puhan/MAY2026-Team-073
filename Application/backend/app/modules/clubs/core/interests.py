"""
Interest APIs for ClubConnect.

This module handles:

1. Master Interest CRUD
   GET    /api/interests
   POST   /api/interests
   GET    /api/interests/<interest_id>
   PATCH  /api/interests/<interest_id>
   DELETE /api/interests/<interest_id>

2. Club Interests
   GET    /api/clubs/<club_id>/interests
   POST   /api/clubs/<club_id>/interests
   DELETE /api/clubs/<club_id>/interests/<interest_id>

3. User Interests
   GET    /api/users/<user_id>/interests
   POST   /api/users/<user_id>/interests
   DELETE /api/users/<user_id>/interests/<interest_id>

4. Event Interests
   GET    /api/events/<event_id>/interests
   POST   /api/events/<event_id>/interests
   DELETE /api/events/<event_id>/interests/<interest_id>

The Interest table is the centralized master list.

UserInterest, ClubInterest and EventInterest are
many-to-many association tables.
"""

from flask import Blueprint, request
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import (Interest,UserInterest,ClubInterest,EventInterest,User,Club,Event)

from app.middleware.auth_middleware import require_club_role,require_auth


# ============================================================
# BLUEPRINT
# ============================================================

interest_bp = Blueprint("interest", __name__)
api = Api(interest_bp)


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_interest(interest):
    """Serialize a master Interest object."""

    return {
        "id": interest.id,
        "name": interest.name,
        "created_at": (
            interest.created_at.isoformat()
            if interest.created_at
            else None
        ),
    }


def serialize_user_interest(link):
    """Serialize UserInterest mapping."""

    return {
        "id": link.id,
        "user_id": link.user_id,
        "interest_id": link.interest_id,
        "interest": serialize_interest(link.interest),
        "created_at": (
            link.created_at.isoformat()
            if link.created_at
            else None
        ),
    }


def serialize_club_interest(link):
    """Serialize ClubInterest mapping."""

    return {
        "id": link.id,
        "club_id": link.club_id,
        "interest_id": link.interest_id,
        "interest": serialize_interest(link.interest),
        "created_at": (
            link.created_at.isoformat()
            if link.created_at
            else None
        ),
    }


def serialize_event_interest(link):
    """Serialize EventInterest mapping."""

    return {
        "id": link.id,
        "event_id": link.event_id,
        "interest_id": link.interest_id,
        "interest": serialize_interest(link.interest),
        "created_at": (
            link.created_at.isoformat()
            if link.created_at
            else None
        ),
    }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_interest(db, interest_id):
    """Return an Interest or None."""

    return (
        db.query(Interest)
        .filter(Interest.id == interest_id)
        .first()
    )


def get_club(db, club_id):
    """Return a Club or None."""

    return (
        db.query(Club)
        .filter(Club.id == club_id)
        .first()
    )


def get_user(db, user_id):
    """Return a User or None."""

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_event(db, event_id):
    """Return an Event or None."""

    return (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )


# ============================================================
# MASTER INTERESTS
# ============================================================
#
# GET  /api/interests
# POST /api/interests
#
# ============================================================

class InterestListResource(Resource):

    @require_auth
    def get(self):
        """
        Get all available interests.
        GET /api/interests
        """
        try:
            with get_session() as db:
                interests = (db.query(Interest).order_by(Interest.name.asc()).all())
                return [serialize_interest(interest)for interest in interests], 200
        except Exception as e:
                    return {'message'  :  f"ERROR  :  {e}"}, 500
        
    @require_auth
    def post(self):
        """
        Create a new master interest.
        POST /api/interests
        Body:
        {"name": "Photography"}
        """
        try:
            data = request.get_json(silent=True) or {}
            name = data.get("name")
            if not name:
                return {"message": "Interest name is required"}, 400
            name = name.strip()
            if not name:
                return {"message": "Interest name cannot be empty"}, 400
            with get_session() as db:
                existing = (db.query(Interest).filter(Interest.name.ilike(name)).first())
                if existing:
                    return {"message": "Interest already exists","interest": serialize_interest(existing)}, 409
            interest = Interest(name=name)
            db.add(interest)
            db.commit()
            db.refresh(interest)
            return serialize_interest(interest), 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        

# ============================================================
# SINGLE MASTER INTEREST
# ============================================================
#
# GET    /api/interests/<interest_id>
# PATCH  /api/interests/<interest_id>
# DELETE /api/interests/<interest_id>
#
# ============================================================

class InterestResource(Resource):

    @require_auth
    def get(self, interest_id):
        """
        Get one master interest.
        """
        try:
            with get_session() as db:
                interest = get_interest(db, interest_id)
                if not interest:
                    return {"message": "Interest not found"}, 404
                return serialize_interest(interest), 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        
    @require_auth
    def patch(self, interest_id):
        """
        Update a master interest.
        PATCH /api/interests/<interest_id>
        Body:{"name": "Photography & Editing"}
        """
        try:
            data = request.get_json(silent=True) or {}

            if "name" not in data:
                return {"message": "Nothing to update"}, 400
            name = data.get("name")
            if not isinstance(name, str) or not name.strip():
                return {"message": "Interest name cannot be empty"}, 400
            name = name.strip()

            with get_session() as db:
                interest = get_interest(db, interest_id)
                if not interest:
                    return {"message": "Interest not found"}, 404
                duplicate = (db.query(Interest).filter(Interest.name.ilike(name),Interest.id != interest_id).first())
                if duplicate:
                    return {"message": "Interest already exists"}, 409
                interest.name = name
                db.commit()
                db.refresh(interest)
                return serialize_interest(interest), 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500

    @require_auth
    def delete(self, interest_id):
        """
        Delete a master interest.

        Because the relationship tables use cascade delete,
        associated user/club/event mappings will also be removed
        when the database is configured correctly.
        """
        try:
            with get_session() as db:

                interest = get_interest(db, interest_id)
                if not interest:
                    return {"message": "Interest not found"}, 404
            db.delete(interest)
            db.commit()
            return {"message": "Interest deleted successfully"}, 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        

# ============================================================
# CLUB INTERESTS
# ============================================================
#
# GET
# /api/clubs/<club_id>/interests
#
# POST
# /api/clubs/<club_id>/interests
#
# DELETE
# /api/clubs/<club_id>/interests/<interest_id>
#
# ============================================================

class ClubInterestListResource(Resource):

    @require_auth
    def get(self, club_id):
        """
        Get all interests associated with a club.
        """

        with get_session() as db:

            club = get_club(db, club_id)

            if not club:
                return {
                    "message": "Club not found"
                }, 404

            links = (
                db.query(ClubInterest)
                .filter(
                    ClubInterest.club_id == club_id
                )
                .join(Interest)
                .order_by(Interest.name.asc())
                .all()
            )

            return [
                serialize_club_interest(link)
                for link in links
            ], 200

    @require_club_role(
        "president",
        "vice_president",
        "secretary"
    )
    def post(self, club_id):
        """
        Add interests to a club.

        POST /api/clubs/<club_id>/interests

        Supported body:

        {
            "interest_ids": [1, 2, 3]
        }

        OR:

        {
            "interest_id": 1
        }
        """
        try:
            data = request.get_json(silent=True) or {}

            interest_ids = data.get("interest_ids")

            if interest_ids is None:

                single_interest_id = data.get("interest_id")

                if single_interest_id is None:
                    return {
                        "message": "interest_id or interest_ids is required"
                    }, 400

                interest_ids = [single_interest_id]

            if not isinstance(interest_ids, list):
                return {
                    "message": "interest_ids must be a list"
                }, 400

            if not interest_ids:
                return {
                    "message": "At least one interest is required"
                }, 400

            # Remove duplicates
            interest_ids = list(set(interest_ids))

            with get_session() as db:

                club = get_club(db, club_id)

                if not club:
                    return {
                        "message": "Club not found"
                    }, 404

                added = []
                already_exists = []

                for interest_id in interest_ids:

                    interest = get_interest(
                        db,
                        interest_id
                    )

                    if not interest:
                        return {
                            "message": f"Interest {interest_id} not found"
                        }, 404

                    existing = (
                        db.query(ClubInterest)
                        .filter(
                            ClubInterest.club_id == club_id,
                            ClubInterest.interest_id == interest_id
                        )
                        .first()
                    )

                    if existing:
                        already_exists.append(
                            interest_id
                        )
                        continue

                    link = ClubInterest(
                        club_id=club_id,
                        interest_id=interest_id
                    )

                    db.add(link)
                    added.append(interest_id)

                db.commit()

                return {
                    "message": "Club interests updated successfully",
                    "club_id": club_id,
                    "added_interest_ids": added,
                    "already_exists": already_exists
                }, 201

        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        
class ClubInterestResource(Resource):

    @require_club_role(
        "president",
        "vice_president",
        "secretary"
    )
    def delete(self, club_id, interest_id):
        """
        Remove one interest from a club.

        DELETE
        /api/clubs/<club_id>/interests/<interest_id>
        """
        try:
            with get_session() as db:

                club = get_club(db, club_id)

                if not club:
                    return {
                        "message": "Club not found"
                    }, 404

                link = (
                    db.query(ClubInterest)
                    .filter(
                        ClubInterest.club_id == club_id,
                        ClubInterest.interest_id == interest_id
                    )
                    .first()
                )

                if not link:
                    return {
                        "message": "Interest is not associated with this club"
                    }, 404

                db.delete(link)
                db.commit()

                return {
                    "message": "Interest removed from club successfully"
                }, 200

        except Exception as e:
                    return {'message'  :  f"ERROR  :  {e}"}, 500
        
# ============================================================
# USER INTERESTS
# ============================================================
#
# GET
# /api/users/<user_id>/interests
#
# POST
# /api/users/<user_id>/interests
#
# DELETE
# /api/users/<user_id>/interests/<interest_id>
#
# ============================================================

class UserInterestListResource(Resource):

    @require_auth
    def get(self, user_id):
        """
        Get all interests of a user.
        """
        try:
            with get_session() as db:

                user = get_user(db, user_id)

                if not user:
                    return {
                        "message": "User not found"
                    }, 404

                links = (
                    db.query(UserInterest)
                    .filter(
                        UserInterest.user_id == user_id
                    )
                    .join(Interest)
                    .order_by(Interest.name.asc())
                    .all()
                )

                return [
                    serialize_user_interest(link)
                    for link in links
                ], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        
    @require_auth
    def post(self, user_id):
        """
        Add interests to a user.

        POST /api/users/<user_id>/interests

        Body:

        {
            "interest_ids": [1, 2, 3]
        }
        """
        try:
            data = request.get_json(silent=True) or {}

            interest_ids = data.get("interest_ids")

            if interest_ids is None:

                single_interest_id = data.get("interest_id")

                if single_interest_id is None:
                    return {
                        "message": "interest_id or interest_ids is required"
                    }, 400

                interest_ids = [single_interest_id]

            if not isinstance(interest_ids, list):
                return {
                    "message": "interest_ids must be a list"
                }, 400

            if not interest_ids:
                return {
                    "message": "At least one interest is required"
                }, 400

            interest_ids = list(set(interest_ids))

            with get_session() as db:

                user = get_user(db, user_id)

                if not user:
                    return {
                        "message": "User not found"
                    }, 404

                added = []
                already_exists = []

                for interest_id in interest_ids:

                    interest = get_interest(
                        db,
                        interest_id
                    )

                    if not interest:
                        return {
                            "message": f"Interest {interest_id} not found"
                        }, 404

                    existing = (
                        db.query(UserInterest)
                        .filter(
                            UserInterest.user_id == user_id,
                            UserInterest.interest_id == interest_id
                        )
                        .first()
                    )

                    if existing:
                        already_exists.append(
                            interest_id
                        )
                        continue

                    link = UserInterest(
                        user_id=user_id,
                        interest_id=interest_id
                    )

                    db.add(link)
                    added.append(interest_id)

                db.commit()

                return {
                    "message": "User interests updated successfully",
                    "user_id": user_id,
                    "added_interest_ids": added,
                    "already_exists": already_exists
                }, 201
        except Exception as e:
                    return {'message'  :  f"ERROR  :  {e}"}, 500
        

class UserInterestResource(Resource):

    @require_auth
    def delete(self, user_id, interest_id):
        """
        Remove one interest from a user.
        """
        try:
            with get_session() as db:

                user = get_user(db, user_id)

                if not user:
                    return {
                        "message": "User not found"
                    }, 404

                link = (
                    db.query(UserInterest)
                    .filter(
                        UserInterest.user_id == user_id,
                        UserInterest.interest_id == interest_id
                    )
                    .first()
                )

                if not link:
                    return {
                        "message": "Interest is not associated with this user"
                    }, 404

                db.delete(link)
                db.commit()

                return {
                    "message": "Interest removed from user successfully"
                }, 200

        except Exception as e:
                    return {'message'  :  f"ERROR  :  {e}"}, 500
        
# ============================================================
# EVENT INTERESTS
# ============================================================
#
# GET
# /api/events/<event_id>/interests
#
# POST
# /api/events/<event_id>/interests
#
# DELETE
# /api/events/<event_id>/interests/<interest_id>
#
# ============================================================

class EventInterestListResource(Resource):

    @require_auth
    def get(self, event_id):
        """
        Get all interests associated with an event.
        """
        try:
            with get_session() as db:

                event = get_event(db, event_id)

                if not event:
                    return {
                        "message": "Event not found"
                    }, 404

                links = (
                    db.query(EventInterest)
                    .filter(
                        EventInterest.event_id == event_id
                    )
                    .join(Interest)
                    .order_by(Interest.name.asc())
                    .all()
                )

                return [
                    serialize_event_interest(link)
                    for link in links
                ], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        
    @require_auth
    def post(self, event_id):
        """
        Add interests to an event.

        POST /api/events/<event_id>/interests

        Body:

        {
            "interest_ids": [1, 2, 3]
        }
        """
        try:
            data = request.get_json(silent=True) or {}

            interest_ids = data.get("interest_ids")

            if interest_ids is None:

                single_interest_id = data.get("interest_id")

                if single_interest_id is None:
                    return {
                        "message": "interest_id or interest_ids is required"
                    }, 400

                interest_ids = [single_interest_id]

            if not isinstance(interest_ids, list):
                return {
                    "message": "interest_ids must be a list"
                }, 400

            if not interest_ids:
                return {
                    "message": "At least one interest is required"
                }, 400

            interest_ids = list(set(interest_ids))

            with get_session() as db:

                event = get_event(db, event_id)

                if not event:
                    return {
                        "message": "Event not found"
                    }, 404

                added = []
                already_exists = []

                for interest_id in interest_ids:

                    interest = get_interest(db,interest_id)
                    if not interest:
                        return {"message": f"Interest {interest_id} not found"}, 404

                    existing = (db.query(EventInterest).filter(EventInterest.event_id == event_id,EventInterest.interest_id == interest_id).first())
                    if existing:
                        already_exists.append(interest_id)
                        continue
                    link = EventInterest(event_id=event_id,interest_id=interest_id)
                    db.add(link)
                    added.append(interest_id)
                db.commit()
                return {
                    "message": "Event interests updated successfully",
                    "event_id": event_id,
                    "added_interest_ids": added,
                    "already_exists": already_exists
                }, 201

        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        
class EventInterestResource(Resource):

    @require_auth
    def delete(self, event_id, interest_id):
        """
        Remove one interest from an event.
        """
        try:
            with get_session() as db:

                event = get_event(db, event_id)

                if not event:
                    return {"message": "Event not found"}, 404
                link = (
                    db.query(EventInterest)
                    .filter(
                        EventInterest.event_id == event_id,
                        EventInterest.interest_id == interest_id
                    )
                    .first()
                )

                if not link:
                    return {
                        "message": "Interest is not associated with this event"
                    }, 404

                db.delete(link)
                db.commit()

                return {
                    "message": "Interest removed from event successfully"
                }, 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500
        

# ============================================================
# ROUTES
# ============================================================

# ------------------------------------------------------------
# Master Interest Routes
# ------------------------------------------------------------

api.add_resource(
    InterestListResource,
    "/interests"
)

api.add_resource(
    InterestResource,
    "/interests/<int:interest_id>"
)


# ------------------------------------------------------------
# Club Interest Routes
# ------------------------------------------------------------

api.add_resource(
    ClubInterestListResource,
    "/clubs/<int:club_id>/interests"
)

api.add_resource(
    ClubInterestResource,
    "/clubs/<int:club_id>/interests/<int:interest_id>"
)


# ------------------------------------------------------------
# User Interest Routes
# ------------------------------------------------------------

api.add_resource(
    UserInterestListResource,
    "/users/<int:user_id>/interests"
)

api.add_resource(
    UserInterestResource,
    "/users/<int:user_id>/interests/<int:interest_id>"
)


# ------------------------------------------------------------
# Event Interest Routes
# ------------------------------------------------------------

api.add_resource(
    EventInterestListResource,
    "/events/<int:event_id>/interests"
)

api.add_resource(
    EventInterestResource,
    "/events/<int:event_id>/interests/<int:interest_id>"
)

