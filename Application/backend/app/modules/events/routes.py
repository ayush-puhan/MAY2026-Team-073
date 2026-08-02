"""
Event management module APIs.

Handles:
- Events
- Event registrations
- External participants
- Event sessions
- Attendance
"""

from datetime import datetime

from flask import Blueprint, request, g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import (
    Event,
    EventSession,
    EventRegistration,
    AttendanceRecord,
    ExternalParticipant,
)

from app.middleware.auth_middleware import require_auth, require_club_role


event_bp = Blueprint("events", __name__)
api = Api(event_bp)


# ============================================================
# SERIALIZERS
# ============================================================


def serialize_session(session):

    return {
        "id": session.id,
        "event_id": session.event_id,
        "title": session.title,
        "description": session.description,
        "venue": session.venue,
        "start_at": session.start_at.isoformat(),
        "end_at": session.end_at.isoformat(),
        "session_order": session.session_order
    }



def serialize_event(event):

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,

        "start_at": (
            event.start_at.isoformat()
            if event.start_at else None
        ),

        "end_at": (
            event.end_at.isoformat()
            if event.end_at else None
        ),

        "registration_deadline": (
            event.registration_deadline.isoformat()
            if event.registration_deadline
            else None
        ),

        "capacity": event.capacity,

        "status": (
            event.status.value
            if event.status
            else None
        ),

        "banner": event.banner,

        "club_id": event.club_id,

        "is_public": event.is_public,


        "club": {
            "id": event.club.id,
            "name": event.club.name,
            "logo_url": getattr(
                event.club,
                "logo_url",
                None
            ),

            "university_id": event.club.university_id,

            "university": {
                "id": event.club.university.id,
                "name": event.club.university.name
            }
            if event.club.university else None
        }
        if event.club else None,


        "event_sessions": [
            serialize_session(s)
            for s in event.event_sessions
        ]
    }




# ============================================================
# GET ALL EVENTS
# GET /api/events
# ============================================================


class EventListResource(Resource):

    @require_auth
    def get(self):

        club_id = request.args.get("club_id")


        with get_session() as session:

            query = session.query(Event)


            if club_id:
                query = query.filter(
                    Event.club_id == int(club_id)
                )


            events = query.all()


            return [
                serialize_event(event)
                for event in events
            ], 200


    @require_club_role("event_coordinator", "president")
    def post(self):

        data = request.json


        with get_session() as session:


            event = Event(

                club_id=data["club_id"],
                title=data["title"],
                description=data.get("description"),

                venue=data.get("venue"),


                start_at=datetime.fromisoformat(data["start_at"]),

                end_at=datetime.fromisoformat(data["end_at"]),


                registration_deadline=(
                    datetime.fromisoformat(
                        data["registration_deadline"]
                    )
                    if data.get(
                        "registration_deadline"
                    )
                    else None
                ),


                capacity=data.get(
                    "capacity"
                ),


                banner=data.get(
                    "banner"
                ),


                created_by=g.current_user.id,


                is_public=data.get(
                    "is_public",
                    False
                )
            )


            session.add(event)

            session.commit()

            session.refresh(event)


            return serialize_event(event), 201




# ============================================================
# GET EVENT BY ID
# GET /api/events/<id>
# ============================================================


class EventDetailResource(Resource):

    @require_auth
    def get(self, event_id):

        with get_session() as session:

            event = (
                session.query(Event)
                .filter(
                    Event.id == event_id
                )
                .first()
            )


            if not event:

                return {
                    "message":
                    "Event not found"
                },404



            return serialize_event(event),200





# ============================================================
# EVENT REGISTRATION
#
# POST   /api/events/<id>/register
# DELETE /api/events/<id>/register
# ============================================================


class EventRegistrationResource(Resource):


    @require_auth
    def post(self,event_id):

        with get_session() as session:


            existing = (
                session.query(EventRegistration)
                .filter_by(
                    event_id=event_id,
                    user_id=g.current_user.id
                )
                .first()
            )


            if existing:

                return {
                    "message":
                    "Already registered"
                },400



            registration = EventRegistration(

                event_id=event_id,

                user_id=g.current_user.id

            )


            session.add(registration)

            session.commit()



            return {

                "message":
                "Registered successfully",

                "id":
                registration.id

            },201




    @require_auth
    def delete(self,event_id):


        with get_session() as session:


            registration = (
                session.query(EventRegistration)
                .filter_by(
                    event_id=event_id,
                    user_id=g.current_user.id
                )
                .first()
            )


            if not registration:

                return {
                    "message":
                    "Registration not found"
                },404



            session.delete(registration)

            session.commit()



            return {
                "message":
                "Unregistered successfully"
            },200





# ============================================================
# EXTERNAL PARTICIPANTS
#
# POST /api/events/<id>/register-external
# ============================================================


class ExternalRegistrationResource(Resource):

    @require_auth
    def post(self,event_id):

        data=request.json


        with get_session() as session:


            participant = ExternalParticipant(

                event_id=event_id,

                full_name=data["full_name"],

                email=data.get("email"),

                affiliation=data.get(
                    "affiliation"
                ),

                participant_type=data[
                    "participant_type"
                ]

            )


            session.add(participant)

            session.commit()



            return {

                "message":
                "External participant registered",

                "id":
                participant.id

            },201




# ============================================================
# USER EVENTS
#
# GET /api/users/<user_id>/events
# ============================================================


class UserEventsResource(Resource):

    @require_auth
    def get(self,user_id):


        with get_session() as session:


            registrations = (
                session.query(EventRegistration)
                .filter_by(
                    user_id=user_id
                )
                .all()
            )


            return [
                serialize_event(
                    r.event
                )
                for r in registrations
            ],200





# ============================================================
# EVENT SESSIONS
#
# GET    /api/events/<id>/sessions
# POST   /api/events/<id>/sessions
# DELETE /api/events/<id>/sessions
# ============================================================


class EventSessionsResource(Resource):


    @require_auth
    def get(self,event_id):

        with get_session() as session:


            sessions = (
                session.query(EventSession)
                .filter_by(
                    event_id=event_id
                )
                .all()
            )


            return [
                serialize_session(s)
                for s in sessions
            ],200



    @require_club_role("event_coordinator", "president")
    def post(self,event_id):

        data=request.json


        with get_session() as session:


            session_obj = EventSession(

                event_id=event_id,

                title=data["title"],

                description=data.get(
                    "description"
                ),

                venue=data.get(
                    "venue"
                ),

                start_at=datetime.fromisoformat(
                    data["start_at"]
                ),

                end_at=datetime.fromisoformat(
                    data["end_at"]
                ),

                session_order=data.get(
                    "session_order",
                    1
                )
            )


            session.add(session_obj)

            session.commit()



            return {
                "message":
                "Session created",

                "id":
                session_obj.id
            },201




    @require_club_role("event_coordinator", "president")
    def delete(self,event_id):

        with get_session() as session:


            session.query(
                EventSession
            ).filter_by(
                event_id=event_id
            ).delete()


            session.commit()



            return {
                "message":
                "Sessions deleted"
            },200





# ============================================================
# ATTENDANCE
#
# GET  /api/events/<id>/attendance
# POST /api/events/<id>/attendance
# ============================================================


class EventAttendanceResource(Resource):


    @require_club_role(
        "member",
        "volunteer_coordinator",
        "event_coordinator",
        "secretary",
        "treasurer",
        "vice_president",
        "president"
    )
    def get(self,event_id):

        with get_session() as session:


            records = (
                session.query(AttendanceRecord)
                .filter_by(
                    event_id=event_id
                )
                .all()
            )


            return [

                {
                    "id":r.id,

                    "event_id":r.event_id,

                    "user_id":r.user_id,

                    "checked_in_at":
                    r.checked_in_at.isoformat()

                }

                for r in records

            ],200




    @require_club_role(
        "event_coordinator",
        "volunteer_coordinator",
        "president"
    )
    def post(self,event_id):

        data=request.json


        with get_session() as session:


            record=AttendanceRecord(

                event_id=event_id,

                user_id=data["user_id"],

                recorded_by=g.current_user.id

            )


            session.add(record)

            session.commit()



            return {

                "message":
                "Checked in",

                "id":
                record.id

            },201





# ============================================================
# DELETE ATTENDANCE
#
# DELETE /api/attendance/<record_id>
# ============================================================


class AttendanceDeleteResource(Resource):


    @require_club_role(
        "event_coordinator",
        "president"
    )
    def delete(self,record_id):

        with get_session() as session:


            record = (
                session.query(AttendanceRecord)
                .filter_by(
                    id=record_id
                )
                .first()
            )


            if not record:

                return {
                    "message":
                    "Attendance not found"
                },404



            session.delete(record)

            session.commit()



            return {
                "message":
                "Check-in removed"
            },200




# ============================================================
# ROUTE REGISTRATION
# ============================================================


api.add_resource(
    EventListResource,
    "/events"
)


api.add_resource(
    EventDetailResource,
    "/events/<int:event_id>"
)


api.add_resource(
    EventRegistrationResource,
    "/events/<int:event_id>/register"
)


api.add_resource(
    ExternalRegistrationResource,
    "/events/<int:event_id>/register-external"
)


api.add_resource(
    UserEventsResource,
    "/users/<int:user_id>/events"
)


api.add_resource(
    EventSessionsResource,
    "/events/<int:event_id>/sessions"
)


api.add_resource(
    EventAttendanceResource,
    "/events/<int:event_id>/attendance"
)


api.add_resource(
    AttendanceDeleteResource,
    "/attendance/<int:record_id>"
)