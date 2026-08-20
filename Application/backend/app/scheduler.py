import threading
import time
from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.database.models import (
    Event, EventRegistration, User, Notification, VolunteerAssignment, ClubMembership
)
from app.database.enums import NotificationType, NotificationChannel, VolunteerTaskStatus
from app.utils.email import send_event_reminder_email, send_task_reminder_email

def _check_upcoming_events():
    with SessionLocal() as db:
        now = datetime.utcnow()
        next_24h = now + timedelta(hours=24)
        
        # Find events starting within 24 hours
        events = db.query(Event).filter(
            Event.start_at > now,
            Event.start_at <= next_24h
        ).all()
        
        for event in events:
            # Find registrations
            registrations = db.query(EventRegistration).filter(
                EventRegistration.event_id == event.id
            ).all()
            
            for reg in registrations:
                # Check if reminder already sent for this user + event
                existing = db.query(Notification).filter(
                    Notification.user_id == reg.user_id,
                    Notification.type == NotificationType.EVENT_REMINDER,
                    Notification.related_entity_type == "Event",
                    Notification.related_entity_id == event.id
                ).first()
                
                if not existing:
                    user = db.query(User).filter(User.id == reg.user_id).first()
                    if user:
                        # Send notification and email
                        notif = Notification(
                            user_id=user.id,
                            type=NotificationType.EVENT_REMINDER,
                            channel=NotificationChannel.IN_APP,
                            title=f"Reminder: {event.title} is starting soon!",
                            body=f"Your event '{event.title}' starts at {event.start_at.strftime('%Y-%m-%d %H:%M')}.",
                            related_entity_type="Event",
                            related_entity_id=event.id
                        )
                        db.add(notif)
                        send_event_reminder_email(user, event.title, event.start_at.strftime('%Y-%m-%d %H:%M'))
        
        db.commit()

def _check_upcoming_tasks():
    with SessionLocal() as db:
        now = datetime.utcnow()
        next_24h = now + timedelta(hours=24)
        
        # Find tasks due within 24 hours that are not completed
        tasks = db.query(VolunteerAssignment).filter(
            VolunteerAssignment.due_at > now,
            VolunteerAssignment.due_at <= next_24h,
            VolunteerAssignment.status != VolunteerTaskStatus.COMPLETED
        ).all()
        
        for task in tasks:
            # Task assigns to a membership, not directly to user. We need the user_id.
            membership = db.query(ClubMembership).filter(
                ClubMembership.id == task.assignee_membership_id
            ).first()
            
            if not membership:
                continue
                
            # Check if reminder already sent
            existing = db.query(Notification).filter(
                Notification.user_id == membership.user_id,
                Notification.type == NotificationType.SYSTEM_ALERT, # Use SYSTEM_ALERT or TASK_ALERT
                Notification.related_entity_type == "VolunteerAssignment",
                Notification.related_entity_id == task.id
            ).first()
            
            if not existing:
                user = db.query(User).filter(User.id == membership.user_id).first()
                if user:
                    # Short title
                    task_title = (task.task_description[:30] + '..') if len(task.task_description) > 30 else task.task_description
                    notif = Notification(
                        user_id=user.id,
                        type=NotificationType.SYSTEM_ALERT,
                        channel=NotificationChannel.IN_APP,
                        title=f"Task Deadline Approaching: {task_title}",
                        body=f"Your assigned task is due at {task.due_at.strftime('%Y-%m-%d %H:%M')}.",
                        related_entity_type="VolunteerAssignment",
                        related_entity_id=task.id
                    )
                    db.add(notif)
                    send_task_reminder_email(user, task_title, task.due_at.strftime('%Y-%m-%d %H:%M'))
        
        db.commit()

def scheduler_loop():
    """Continuously polls for upcoming events and tasks every 5 minutes."""
    while True:
        try:
            _check_upcoming_events()
            _check_upcoming_tasks()
        except Exception as e:
            print(f"Scheduler error: {e}")
            
        # Sleep for 5 minutes
        time.sleep(300)

def start_scheduler():
    thread = threading.Thread(target=scheduler_loop)
    thread.daemon = True
    thread.start()
    print("Background notification scheduler started.")
