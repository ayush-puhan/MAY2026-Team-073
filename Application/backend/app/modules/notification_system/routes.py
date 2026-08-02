from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from app.database.enums import (NotificationType,NotificationChannel)
from flask import Blueprint, request, g
from flask_restful import Api, Resource

from app.database import get_session
from app.database.models.communication import Notification
from app.middleware.auth_middleware import require_auth


notification_bp = Blueprint("notifications", __name__)
api = Api(notification_bp)


class NotificationListResource(Resource):

    @require_auth
    def get(self):

        is_read = request.args.get("is_read")

        with get_session() as session:

            query = session.query(Notification).filter(
                Notification.user_id == g.current_user.id
            )

            if is_read is not None:
                query = query.filter(
                    Notification.is_read == (is_read.lower() == "true")
                )
            else:
                # Default: return only unread notifications
                query = query.filter(
                    Notification.is_read == False
                )

            notifications = (
                query.order_by(Notification.created_at.desc())
                .all()
            )

            return [
                {
                    "id": n.id,
                    "user_id": n.user_id,
                    "type": n.type.value,
                    "title": n.title,
                    "body": n.body,
                    "channel": n.channel.value,
                    "is_read": n.is_read,
                    "sent_via_resend": n.sent_via_resend,
                    "related_entity_type": n.related_entity_type,
                    "related_entity_id": n.related_entity_id,
                    "created_at": n.created_at.isoformat(),
                }
                for n in notifications
            ], 200
            
    @require_auth
    def post(self):

        data = request.get_json()

        with get_session() as session:

            notification = Notification(
                user_id=g.current_user.id,
                type=NotificationType(data["type"]),
                title=data["title"],
                body=data["body"],
                channel=NotificationChannel(
                    data.get("channel", "in_app")
                ),
                related_entity_type=data.get("related_entity_type"),
                related_entity_id=data.get("related_entity_id")
            )

            session.add(notification)
            session.commit()
            session.refresh(notification)

            return {
                "message": "Notification created.",
                "id": notification.id
            }, 201
class NotificationReadResource(Resource):
    
    @require_auth
    def post(self):
        with get_session() as session:
            # Mark all notifications as read
            updated = (
                session.query(Notification)
                .filter(
                    Notification.user_id == g.current_user.id,
                    Notification.is_read == False
                )
                .update(
                    {"is_read": True},
                    synchronize_session=False
                )
            )

            session.commit()

            return {
                "message": "All notifications marked as read.",
                "updated_count": updated
            }, 200

    @require_auth
    def patch(self, notification_id):

        with get_session() as session:

            notification = (
                session.query(Notification)
                .filter(
                    Notification.id == notification_id,
                    Notification.user_id == g.current_user.id
                )
                .first()
            )

            if not notification:
                return {
                    "message": "Notification not found."
                }, 404

            notification.is_read = True

            session.commit()

            return {
                "message": "Notification marked as read."
            }, 200

class NotificationEmailResource(Resource):

    method_decorators = [require_auth]

    def post(self):

        data = request.get_json()

        recipient = data["email"]
        subject = data["title"]
        body = data["body"]

        sender = os.getenv("GMAIL_ADDRESS")
        password = os.getenv("GMAIL_APP_PASSWORD")

        try:

            message = MIMEMultipart()
            message["From"] = sender
            message["To"] = recipient
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:

                server.starttls()

                server.login(sender, password)

                server.sendmail(
                    sender,
                    recipient,
                    message.as_string()
                )

            with get_session() as session:

                notification = Notification(

                    user_id=g.current_user.id,

                    type=NotificationType.ANNOUNCEMENT
                        if "type" not in data
                        else NotificationType(data["type"]),

                    title=subject,

                    body=body,

                    channel=NotificationChannel.EMAIL,

                    sent_via_resend=True,

                    related_entity_type=data.get(
                        "related_entity_type"
                    ),

                    related_entity_id=data.get(
                        "related_entity_id"
                    )
                )

                session.add(notification)

                session.commit()

            return {
                "message": "Email sent successfully."
            }, 200

        except Exception as e:

            return {
                "message": "Failed to send email.",
                "error": str(e)
            }, 500


api.add_resource(NotificationListResource, "/notifications")
api.add_resource(NotificationReadResource,"/notifications/read-all","/notifications/<int:notification_id>/read")
api.add_resource(NotificationEmailResource,"/notifications/email")