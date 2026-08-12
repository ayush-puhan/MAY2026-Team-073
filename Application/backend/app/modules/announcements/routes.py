from flask import Blueprint, request,g
from flask_restful import Api, Resource

from app.database.database import get_session
from app.database.models import Announcement, ClubMembership
from app.database.enums import AnnouncementAudience,ClubMemberRole,MembershipStatus, UserRole
from app.middleware.auth_middleware import require_auth

announcement_bp = Blueprint("announcements", __name__)
api = Api(announcement_bp)


def serialize_announcement(a):
    return {
        "id": a.id,
        "club_id": a.club_id,
        "posted_by": a.posted_by,
        "title": a.title,
        "body": a.body,
        "target_audience": a.target_audience.value,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


class AnnouncementListResource(Resource):
    @require_auth
    def get(self):
        try:
            club_id = request.args.get("club_id")
            announcement_type = request.args.get("type")

            with get_session() as db:

                query = db.query(Announcement)

                if club_id:
                    query = query.filter(
                        Announcement.club_id == int(club_id)
                    )

                elif announcement_type == "university":
                    query = query.filter(
                        Announcement.target_audience.in_([
                            AnnouncementAudience.UNIVERSITY_WIDE,
                            AnnouncementAudience.SYSTEM_WIDE,
                            AnnouncementAudience.ALL_MEMBERS,
                        ])
                    )

                elif announcement_type == "system":
                    query = query.filter(
                        Announcement.target_audience ==
                        AnnouncementAudience.SYSTEM_WIDE
                    )

                announcements = (
                    query.order_by(Announcement.created_at.desc())
                    .all()
                )

                return [serialize_announcement(a) for a in announcements], 200
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500

    @require_auth
    def post(self):
        try:
            data = request.get_json()

            with get_session() as db:

                club_id = data.get("club_id")
                audience = AnnouncementAudience(
                    data.get("target_audience", "all_members")
                )

                # -------------------------------
                # Club announcement
                # -------------------------------
                if club_id:

                    membership = (
                        db.query(ClubMembership)
                        .filter(
                            ClubMembership.user_id == g.current_user.id,
                            ClubMembership.club_id == club_id,
                            ClubMembership.status == MembershipStatus.APPROVED,
                        )
                        .first()
                    )

                    if (
                        membership is None
                        or membership.role_in_club
                        not in (
                            ClubMemberRole.PRESIDENT,
                            ClubMemberRole.SECRETARY,
                        )
                    ):
                        return {
                            "message": "Only club President or Secretary can post announcements."
                        }, 403

                # --------------------------------
                # University/System announcement
                # --------------------------------
                else:

                    if audience not in (
                        AnnouncementAudience.UNIVERSITY_WIDE,
                        AnnouncementAudience.SYSTEM_WIDE,
                    ):
                        return {
                            "message": "club_id is required for club announcements."
                        }, 400

                    if g.current_user.role not in (
                        UserRole.STUDENT_AFFAIRS_OFFICE,
                        UserRole.DEAN_STUDENT_WELFARE,
                    ):
                        return {
                            "message": "Permission denied."
                        }, 403

                announcement = Announcement(
                    club_id=club_id,
                    posted_by=g.current_user.id,
                    title=data["title"],
                    body=data["body"],
                    target_audience=audience,
                )
                
                db.add(announcement)
                db.commit()
                db.refresh(announcement)

                return serialize_announcement(announcement), 201
        except Exception as e:
            return {'message'  :  f"ERROR  :  {e}"}, 500

api.add_resource(AnnouncementListResource, "/announcements")