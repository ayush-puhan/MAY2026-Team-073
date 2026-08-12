from datetime import datetime

from flask import Blueprint, request, g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import Club, ClubCreationRequest
from app.database.enums import ClubRequestStatus, ClubStatus
from app.middleware.auth_middleware import require_auth, require_role


club_creation_bp = Blueprint("club_creation_requests", __name__)
api = Api(club_creation_bp)


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _json_data():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _to_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _slugify(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("&", "and")
        .replace(" ", "-")
        .replace("_", "-")
    )


def _make_unique_slug(db, base_slug: str) -> str:
    slug = base_slug
    suffix = 1
    while db.query(Club).filter_by(slug=slug).first() is not None:
        suffix += 1
        slug = f"{base_slug}-{suffix}"
    return slug


def _format_dt(dt):
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def serialize_request(req):
    return {
        "id": str(req.id),
        "proposed_name": req.proposed_name,
        "proposed_category": req.proposed_category,
        "proposal_description": req.proposal_description,
        "requested_by": req.requested_by,
        "status": req.status.value if req.status else None,
        "reviewed_by": req.reviewed_by,
        "review_comments": req.review_comments,
        "resulting_club_id": req.resulting_club_id,
        "created_at": _format_dt(req.created_at),
        "decided_at": _format_dt(req.decided_at),
        "faculty_advisor_id": req.faculty_advisor_id,
    }


# -------------------------------------------------
# 1. POST /api/club-creation-requests
# Student creates request
# -------------------------------------------------

class CreateClubRequestResource(Resource):
    @require_auth
    @require_role("student")
    def post(self):
        try:
            data = _json_data()
            if not data:
                return {"message": "Request body required."}, 400

            required = ["name", "description"]
            missing = [x for x in required if not data.get(x)]
            if missing:
                return {"message": f"Missing fields: {', '.join(missing)}"}, 400

            faculty_advisor_id = _to_int(data.get("faculty_advisor_id"))

            with get_session() as db:
                req = ClubCreationRequest(
                    proposed_name=data.get("name").strip(),
                    proposed_category=data.get("category") or None,
                    proposal_description=data.get("description").strip(),
                    requested_by=g.current_user.id,
                    faculty_advisor_id=faculty_advisor_id,
                    status=ClubRequestStatus.SUBMITTED,
                    created_at=datetime.utcnow(),
                )
                db.add(req)
                db.commit()
                db.refresh(req)

                return {
                    "message": "Club creation request submitted.",
                    "request": serialize_request(req),
                }, 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# 2. GET /api/club-creation-requests/admin
# Admin views requests
# -------------------------------------------------

class AdminClubRequestsResource(Resource):
    @require_auth
    @require_role("student_affairs_office", "dean_student_welfare")
    def get(self):
        try:
            status = request.args.get("status")

            with get_session() as db:
                query = db.query(ClubCreationRequest)

                if status:
                    try:
                        query = query.filter(
                            ClubCreationRequest.status == ClubRequestStatus(status.lower())
                        )
                    except ValueError:
                        return {"message": "Invalid status"}, 400

                requests = query.order_by(ClubCreationRequest.created_at.desc()).all()
                return [serialize_request(x) for x in requests], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# 3. GET /api/club-creation-requests/faculty
# Faculty views assigned proposals
# -------------------------------------------------

class FacultyClubRequestsResource(Resource):
    @require_auth
    @require_role("faculty_advisor")
    def get(self):
        try:
            faculty_id = request.args.get("faculty_advisor_id") or g.current_user.id
            faculty_id = _to_int(faculty_id)
            if faculty_id is None:
                return {"message": "Invalid faculty_advisor_id"}, 400

            with get_session() as db:
                requests = (
                    db.query(ClubCreationRequest)
                    .filter(ClubCreationRequest.faculty_advisor_id == faculty_id)
                    .order_by(ClubCreationRequest.created_at.desc())
                    .all()
                )
                return [serialize_request(x) for x in requests], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# 4. PATCH /api/club-creation-requests/<id>/recommend
# Faculty recommends
# -------------------------------------------------

class RecommendClubRequestResource(Resource):
    @require_auth
    @require_role("faculty_advisor")
    def patch(self, request_id):
        try:
            data = _json_data()

            with get_session() as db:
                req = db.query(ClubCreationRequest).filter_by(id=request_id).first()
                if not req:
                    return {"message": "Request not found"}, 404

                if req.status not in (
                    ClubRequestStatus.SUBMITTED,
                    ClubRequestStatus.FACULTY_RECOMMENDED,
                ):
                    return {"message": "Request cannot be recommended in its current state."}, 400

                if req.faculty_advisor_id and req.faculty_advisor_id != g.current_user.id:
                    return {"message": "You are not assigned to this request"}, 403

                req.status = ClubRequestStatus.FACULTY_RECOMMENDED
                req.review_comments = data.get("review_comments")
                req.reviewed_by = g.current_user.id
                req.decided_at = datetime.utcnow()

                db.commit()
                db.refresh(req)

                return {
                    "message": "Club proposal recommended.",
                    "request": serialize_request(req),
                }, 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# 5. PATCH /api/club-creation-requests/<id>/approve
# Dean approves and creates Club
# -------------------------------------------------

class ApproveClubRequestResource(Resource):
    @require_auth
    @require_role("dean_student_welfare")
    def patch(self, request_id):
        try:
            with get_session() as db:
                req = db.query(ClubCreationRequest).filter_by(id=request_id).first()
                if not req:
                    return {"message": "Request not found"}, 404

                if req.status != ClubRequestStatus.FACULTY_RECOMMENDED:
                    return {"message": "Request not recommended."}, 400

                base_slug = _slugify(req.proposed_name)
                if not base_slug:
                    return {"message": "Invalid proposed club name"}, 400

                unique_slug = _make_unique_slug(db, base_slug)

                club = Club(
                    name=req.proposed_name.strip(),
                    slug=unique_slug,
                    category=req.proposed_category,
                    description=req.proposal_description,
                    faculty_advisor_id=req.faculty_advisor_id,
                    status=ClubStatus.ACTIVE,
                    university_id=g.current_user.university_id,
                    created_at=datetime.utcnow(),
                )

                db.add(club)
                db.flush()

                req.status = ClubRequestStatus.APPROVED
                req.resulting_club_id = club.id
                req.reviewed_by = g.current_user.id
                req.decided_at = datetime.utcnow()

                db.commit()
                db.refresh(req)
                db.refresh(club)

                return {
                    "message": "Club approved and created.",
                    "club_id": club.id,
                    "request": serialize_request(req),
                }, 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# 6. PATCH /api/club-creation-requests/<id>/reject
# Faculty/Dean reject
# -------------------------------------------------

class RejectClubRequestResource(Resource):
    @require_auth
    @require_role("faculty_advisor", "dean_student_welfare")
    def patch(self, request_id):
        try:
            data = _json_data()

            with get_session() as db:
                req = db.query(ClubCreationRequest).filter_by(id=request_id).first()
                if not req:
                    return {"message": "Request not found"}, 404

                if req.status in (ClubRequestStatus.APPROVED, ClubRequestStatus.REJECTED):
                    return {"message": "Request cannot be rejected in its current state."}, 400

                if (
                    g.current_user.role == "faculty_advisor"
                    and req.faculty_advisor_id
                    and req.faculty_advisor_id != g.current_user.id
                ):
                    return {"message": "You are not assigned to this request"}, 403

                req.status = ClubRequestStatus.REJECTED
                req.review_comments = data.get("review_comments")
                req.reviewed_by = g.current_user.id
                req.decided_at = datetime.utcnow()

                db.commit()
                db.refresh(req)

                return {
                    "message": "Club request rejected.",
                    "request": serialize_request(req),
                }, 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500


# -------------------------------------------------
# Route registration
# -------------------------------------------------

api.add_resource(CreateClubRequestResource, "/club-creation-requests")
api.add_resource(AdminClubRequestsResource, "/club-creation-requests/admin")
api.add_resource(FacultyClubRequestsResource, "/club-creation-requests/faculty")
api.add_resource(RecommendClubRequestResource, "/club-creation-requests/<int:request_id>/recommend")
api.add_resource(ApproveClubRequestResource, "/club-creation-requests/<int:request_id>/approve")
api.add_resource(RejectClubRequestResource, "/club-creation-requests/<int:request_id>/reject")