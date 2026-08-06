from flask import Blueprint
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.auth import User
from app.database.enums import UserRole
from app.middleware.auth_middleware import require_auth


faculty_bp = Blueprint(
    "faculty",
    __name__,
    url_prefix="/api/faculty-advisors"
)

api = Api(faculty_bp)


class FacultyAdvisorListResource(Resource):

    method_decorators = [require_auth]

    def get(self):
        try:
            with get_session() as session:

                faculty = (
                    session.query(User)
                    .filter(
                        User.role == UserRole.FACULTY_ADVISOR,
                        User.is_active == True
                    )
                    .order_by(User.full_name)
                    .all()
                )

                return [
                    {
                        "id": f.id,
                        "full_name": f.full_name,
                        "email": f.email,
                        "department_id": f.department_id,
                        "university_id": f.university_id
                    }
                    for f in faculty
                ], 200

        except Exception as e:
            return {
                "message": str(e)
            }, 500


api.add_resource(
    FacultyAdvisorListResource,
    ""
)