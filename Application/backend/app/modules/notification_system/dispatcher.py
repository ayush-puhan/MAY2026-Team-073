import threading
from app.database.database import SessionLocal
from app.database.models import (
    Notification,
    User,
    ClubMembership,
    EventRegistration,
    ExternalParticipant,
    Club
)
from app.database.enums import NotificationType, NotificationChannel, MembershipStatus, UserRole
from app.utils.email import (
    send_announcement_email,
    send_membership_approved_email,
    send_event_posted_email,
    send_event_registration_email
)

def _dispatch_announcement_notifications(announcement_id, title, body, club_id, audience, current_user_id):
    """Background task to send announcement notifications"""
    with SessionLocal() as db:
        users_to_notify = []
        club_name = "University Administration"
        
        if club_id:
            club = db.query(Club).filter(Club.id == club_id).first()
            if club:
                club_name = club.name
            # Notify club members
            memberships = db.query(ClubMembership).filter(
                ClubMembership.club_id == club_id,
                ClubMembership.status == MembershipStatus.APPROVED
            ).all()
            for m in memberships:
                if m.user_id != current_user_id:
                    user = db.query(User).filter(User.id == m.user_id).first()
                    if user:
                        users_to_notify.append(user)
        else:
            # University / System wide
            if audience == "SYSTEM_WIDE":
                users_to_notify = db.query(User).filter(User.id != current_user_id).all()
            else:
                # UNIVERSITY_WIDE
                sender = db.query(User).filter(User.id == current_user_id).first()
                if sender and sender.university_id:
                    users_to_notify = db.query(User).filter(
                        User.university_id == sender.university_id,
                        User.id != current_user_id
                    ).all()

        for user in users_to_notify:
            # Create in-app notification
            notif = Notification(
                user_id=user.id,
                type=NotificationType.ANNOUNCEMENT,
                channel=NotificationChannel.IN_APP,
                title=f"New Announcement: {title}",
                body=f"{club_name} posted an announcement."
            )
            db.add(notif)
            
            # Send Email
            send_announcement_email(user, club_name, title, body)
            
        db.commit()

def dispatch_announcement_notifications(announcement):
    """Starts a background thread to send announcement notifications"""
    # Need to extract enums to strings to avoid threading detached instance issues
    audience = announcement.target_audience.name if hasattr(announcement.target_audience, 'name') else str(announcement.target_audience)
    thread = threading.Thread(
        target=_dispatch_announcement_notifications,
        args=(announcement.id, announcement.title, announcement.body, announcement.club_id, audience, announcement.posted_by)
    )
    thread.daemon = True
    thread.start()

def _dispatch_membership_approved(user_id, club_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        club = db.query(Club).filter(Club.id == club_id).first()
        if user and club:
            notif = Notification(
                user_id=user.id,
                type=NotificationType.SYSTEM_ALERT, # Changed from CLUB_INVITE
                channel=NotificationChannel.IN_APP,
                title="Membership Approved",
                body=f"Your membership for {club.name} was approved."
            )
            db.add(notif)
            send_membership_approved_email(user, club.name)
            db.commit()

def dispatch_membership_approved(user_id, club_id):
    thread = threading.Thread(target=_dispatch_membership_approved, args=(user_id, club_id))
    thread.daemon = True
    thread.start()

def _dispatch_event_posted(event_id, title, club_id):
    with SessionLocal() as db:
        club = db.query(Club).filter(Club.id == club_id).first()
        if not club:
            return
            
        memberships = db.query(ClubMembership).filter(
            ClubMembership.club_id == club_id,
            ClubMembership.status == MembershipStatus.APPROVED
        ).all()
        
        for m in memberships:
            user = db.query(User).filter(User.id == m.user_id).first()
            if user:
                notif = Notification(
                    user_id=user.id,
                    type=NotificationType.EVENT_REMINDER,
                    channel=NotificationChannel.IN_APP,
                    title="New Event Posted",
                    body=f"{club.name} posted a new event: {title}"
                )
                db.add(notif)
                send_event_posted_email(user, club.name, title)
                
        db.commit()

def dispatch_event_posted(event):
    thread = threading.Thread(target=_dispatch_event_posted, args=(event.id, event.title, event.club_id))
    thread.daemon = True
    thread.start()

def _dispatch_event_registration(user_id, event_id, is_external, external_email=None):
    with SessionLocal() as db:
        from app.database.models import Event
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return
            
        if not is_external:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                notif = Notification(
                    user_id=user.id,
                    type=NotificationType.SYSTEM_ALERT,
                    channel=NotificationChannel.IN_APP,
                    title="Event Registration Confirmed",
                    body=f"You successfully registered for {event.title}."
                )
                db.add(notif)
                send_event_registration_email(user, event.title)
        else:
            # External users don't have in-app accounts, just send email if possible
            if external_email:
                from app.utils.email import send_email, _get_generic_template
                body = _get_generic_template(
                    title="Registration Confirmed!",
                    message=f"You are successfully registered for <strong>{event.title}</strong> as an external participant."
                )
                send_email(external_email, f"Registration Confirmed: {event.title}", body)
                
        db.commit()

def dispatch_event_registration(user_id, event_id, is_external=False, external_email=None):
    thread = threading.Thread(target=_dispatch_event_registration, args=(user_id, event_id, is_external, external_email))
    thread.daemon = True
    thread.start()
