from datetime import datetime

from flask import Blueprint, request, g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import (
    VolunteerAssignment,
    Event,
    ClubMembership,
    User,
)

from app.database.enums import (
    MembershipStatus,
    VolunteerTaskStatus,
)

from app.middleware.auth_middleware import (
    require_auth,
    require_club_role,
)


volunteer_task_bp = Blueprint(
    "volunteer_tasks",
    __name__,
)

api = Api(volunteer_task_bp)



def serialize_task(task):

    assignee_membership = task.assignee_membership
    assignee_user = assignee_membership.user

    return {
        "id": task.id,
        "event_id": task.event_id,
        "assignee_membership_id": task.assignee_membership_id,
        "task_description": task.task_description,

        "status": (
            task.status.value
            if hasattr(task.status, "value")
            else task.status
        ),

        "due_at": (
            task.due_at.isoformat()
            if task.due_at
            else None
        ),

        "event": {
            "id": task.event.id,
            "title": task.event.title,
        }
        if task.event
        else None,


        "assigner": {
            "id": task.assigner.id,
            "full_name": task.assigner.full_name,
        }
        if task.assigner
        else None,


        "assignee": {
            "id": assignee_user.id,
            "full_name": assignee_user.full_name,
            "role": (
                assignee_user.role.value
                if hasattr(
                    assignee_user.role,
                    "value"
                )
                else assignee_user.role
            )
        }
        if assignee_user
        else None
    }



# -------------------------------------------------
# GET MY TASKS
# /api/clubs/<club_id>/tasks?user_id=X
# -------------------------------------------------

class ClubTasksResource(Resource):

    method_decorators = [
        require_auth
    ]


    def get(self, club_id):
        try:
            user_id = request.args.get("user_id")


            with get_session() as db:


                # -----------------------------------------
                # CASE 1:
                # Member checking own tasks
                # /clubs/2/tasks?user_id=1
                # -----------------------------------------

                if user_id:


                    membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.club_id == club_id,
                            ClubMembership.user_id == int(user_id),
                            ClubMembership.status ==
                            MembershipStatus.APPROVED
                        )
                        .first()
                    )


                    if not membership:
                        return {
                            "message":
                            "Membership not found"
                        },404



                    from sqlalchemy.orm import joinedload

                    tasks = (
                        db.query(VolunteerAssignment)
                        .options(
                            joinedload(VolunteerAssignment.assignee_membership).joinedload(ClubMembership.user),
                            joinedload(VolunteerAssignment.event),
                            joinedload(VolunteerAssignment.assigner),
                        )
                        .filter(
                            VolunteerAssignment.assignee_membership_id
                            ==
                            membership.id
                        )
                        .all()
                    )


                    return [
                        serialize_task(task)
                        for task in tasks
                    ],200



                # -----------------------------------------
                # CASE 2:
                # Coordinator viewing all tasks
                # /clubs/2/tasks
                # -----------------------------------------


                current_user = g.current_user


                from sqlalchemy.orm import joinedload

                tasks = (
                    db.query(VolunteerAssignment)
                    .options(
                        joinedload(VolunteerAssignment.assignee_membership).joinedload(ClubMembership.user),
                        joinedload(VolunteerAssignment.event),
                        joinedload(VolunteerAssignment.assigner),
                    )
                    .join(Event)
                    .filter(
                        Event.club_id == club_id
                    )
                    .all()
                )


                return [
                    serialize_task(task)
                    for task in tasks
                ],200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500



# -------------------------------------------------
# CREATE TASK
# POST /api/volunteer-tasks
# -------------------------------------------------

class CreateVolunteerTaskResource(Resource):

    method_decorators = [
        require_auth
    ]

    @require_club_role(
        "event_coordinator",
        "volunteer_coordinator",
        "president",
        "vice_president",
        "secretary"
    )
    def post(self):
        try:
            data = request.get_json()

            print("REQUEST DATA:", data)

            if not data:
                return {
                    "message": "Request body is required"
                }, 400


            required_fields = [
                "event_id",
                "assignee_membership_id",
                "task_description"
            ]

            for field in required_fields:
                if field not in data:
                    print("MISSING FIELD:", field)

                    return {
                        "message": f"{field} is required"
                    }, 400


            with get_session() as db:

                event = (
                    db.query(Event)
                    .filter(
                        Event.id == data["event_id"]
                    )
                    .first()
                )


                print("EVENT:", event)


                if not event:
                    return {
                        "message": "Event not found"
                    }, 404



                membership = (
                    db.query(ClubMembership)
                    .filter(
                        ClubMembership.id == data["assignee_membership_id"]
                    )
                    .first()
                )


                print(
                    "ASSIGNEE MEMBERSHIP:",
                    membership
                )


                if not membership:
                    return {
                        "message":
                        "Membership ID does not exist"
                    },400



                print(
                    "MEMBERSHIP CLUB:",
                    membership.club_id
                )

                print(
                    "EVENT CLUB:",
                    event.club_id
                )


                if membership.club_id != event.club_id:

                    return {
                        "message":
                        "Assignee does not belong to event club"
                    },400



                if membership.status != MembershipStatus.APPROVED:

                    return {
                        "message":
                        "Assignee membership is not approved"
                    },400



                due_at = None

                if data.get("due_at"):

                    try:
                        due_at = datetime.fromisoformat(
                            data["due_at"]
                        )

                    except ValueError:

                        return {
                            "message":
                            "Invalid due_at format"
                        },400



                task = VolunteerAssignment(

                    event_id=data["event_id"],

                    assignee_membership_id=
                    data["assignee_membership_id"],

                    assigned_by=
                    g.current_user.id,

                    task_description=
                    data["task_description"],

                    due_at=due_at,

                    committee_id=
                    data.get("committee_id")
                )


                db.add(task)

                db.commit()

                db.refresh(task)


                print("TASK CREATED:", task.id)


                return serialize_task(task), 201
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500


    method_decorators = [
        require_auth
    ]

    @require_club_role(
        "event_coordinator",
        "volunteer_coordinator",
        "president",
        "vice_president",
        "secretary"
    )
    def patch(self, taskId):
        try:
            data = request.get_json()

            print("UPDATE TASK REQUEST:", data)

            if not data:
                return {
                    "message": "Request body is required"
                }, 400

            with get_session() as db:

                # --------------------------------------------
                # Find existing task
                # --------------------------------------------
                task = (
                    db.query(VolunteerAssignment)
                    .filter(
                        VolunteerAssignment.id == taskId
                    )
                    .first()
                )

                print("TASK:", task)

                if not task:
                    return {
                        "message": "Volunteer task not found"
                    }, 404


                # --------------------------------------------
                # Update assignee if provided
                # --------------------------------------------
                if "assignee_membership_id" in data:

                    membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.id ==
                            data["assignee_membership_id"]
                        )
                        .first()
                    )

                    print(
                        "NEW ASSIGNEE MEMBERSHIP:",
                        membership
                    )

                    if not membership:
                        return {
                            "message":
                            "Membership ID does not exist"
                        }, 400

                    # Get event associated with task
                    event = (
                        db.query(Event)
                        .filter(
                            Event.id == task.event_id
                        )
                        .first()
                    )

                    if not event:
                        return {
                            "message": "Event not found"
                        }, 404

                    # Assignee must belong to same club
                    if membership.club_id != event.club_id:
                        return {
                            "message":
                            "Assignee does not belong to event club"
                        }, 400

                    # Assignee membership must be approved
                    if membership.status != MembershipStatus.APPROVED:
                        return {
                            "message":
                            "Assignee membership is not approved"
                        }, 400

                    task.assignee_membership_id = (
                        data["assignee_membership_id"]
                    )


                # --------------------------------------------
                # Update task description
                # --------------------------------------------
                if "task_description" in data:

                    if not data["task_description"]:
                        return {
                            "message":
                            "task_description cannot be empty"
                        }, 400

                    task.task_description = (
                        data["task_description"]
                    )


                # --------------------------------------------
                # Update due date
                # --------------------------------------------
                if "due_at" in data:

                    # Allow clearing due date
                    if data["due_at"] is None:
                        task.due_at = None

                    else:
                        try:
                            task.due_at = datetime.fromisoformat(
                                data["due_at"]
                            )

                        except (ValueError, TypeError):
                            return {
                                "message":
                                "Invalid due_at format"
                            }, 400


                # --------------------------------------------
                # Update committee
                # --------------------------------------------
                if "committee_id" in data:
                    task.committee_id = data["committee_id"]


                # --------------------------------------------
                # Update event
                # --------------------------------------------
                if "event_id" in data:

                    event = (
                        db.query(Event)
                        .filter(
                            Event.id == data["event_id"]
                        )
                        .first()
                    )

                    if not event:
                        return {
                            "message": "Event not found"
                        }, 404

                    # If assignee is not being changed, validate
                    # existing assignee against the new event.
                    membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.id ==
                            task.assignee_membership_id
                        )
                        .first()
                    )

                    if membership and (
                        membership.club_id != event.club_id
                    ):
                        return {
                            "message":
                            "Assignee does not belong to event club"
                        }, 400

                    task.event_id = data["event_id"]


                # --------------------------------------------
                # Save changes
                # --------------------------------------------
                db.commit()
                db.refresh(task)

                print("TASK UPDATED:", task.id)

                return serialize_task(task), 200

        except Exception as e:
            print("UPDATE TASK ERROR:", e)

            return {
                "message": f"Error: {e}"
            }, 500


    method_decorators = [
        require_auth
    ]

    @require_club_role(
        "event_coordinator",
        "volunteer_coordinator",
        "president",
        "vice_president",
        "secretary"
    )
    def delete(self, taskId):
        try:
            with get_session() as db:

                task = (
                    db.query(VolunteerAssignment)
                    .filter(
                        VolunteerAssignment.id == taskId
                    )
                    .first()
                )

                if not task:
                    return {
                        "message": "Volunteer task not found"
                    }, 404

                db.delete(task)
                db.commit()

                return {
                    "message": "Volunteer task deleted successfully"
                }, 200

        except Exception as e:
            return {
                "message": f"Error: {e}"
            }, 500

# -------------------------------------------------
# UPDATE TASK STATUS
# PATCH /api/volunteer-tasks/<id>/status
# -------------------------------------------------

class VolunteerTaskStatusResource(Resource):
    @require_auth
    @require_club_role(
        "member",
        "event_coordinator",
        "volunteer_coordinator",
        "president"
    )


    def patch(self, taskId):
        try:
            data = request.get_json()
            new_status = data.get("status")

            if not new_status:
                return {
                    "message":
                    "status required"
                },400



            with get_session() as db:

                task = (
                    db.query(VolunteerAssignment)
                    .filter(
                        VolunteerAssignment.id==taskId
                    )
                    .first()
                )


                if not task:
                    return {
                        "message":
                        "Task not found"
                    },404



                membership = task.assignee_membership


                if membership.user_id != g.current_user.id:

                    return {
                        "message":
                        "You can update only your task"
                    },403



                try:

                    task.status = VolunteerTaskStatus(
                        new_status
                    )

                except ValueError:

                    return {
                        "message":
                        "Invalid status"
                    },400



                db.commit()


                return serialize_task(task),200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500




# -------------------------------------------------
# CHECK OVERDUE TASKS
# POST /api/volunteer-tasks/check-overdue
# -------------------------------------------------

class CheckOverdueTasksResource(Resource):

    method_decorators = [
        require_auth
    ]


    def post(self):
        try:
            updated = 0
            with get_session() as db:

                tasks = (
                    db.query(VolunteerAssignment)
                    .filter(
                        VolunteerAssignment.due_at
                        < datetime.utcnow(),

                        VolunteerAssignment.status
                        !=
                        VolunteerTaskStatus.COMPLETED
                    )
                    .all()
                )


                for task in tasks:

                    task.status = (
                        VolunteerTaskStatus.MISSED
                    )

                    updated +=1



                db.commit()


            return {
                "updated":updated
            },200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500





api.add_resource(
    ClubTasksResource,
    "/clubs/<int:club_id>/tasks"
)


api.add_resource(
    CreateVolunteerTaskResource,
    "/volunteer-tasks",
    "/volunteer-tasks/<int:taskId>"
)


api.add_resource(
    VolunteerTaskStatusResource,
    "/volunteer-tasks/<int:taskId>/status"
)


api.add_resource(
    CheckOverdueTasksResource,
    "/volunteer-tasks/check-overdue"
)
