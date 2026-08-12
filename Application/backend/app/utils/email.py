import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Sends an email using Gmail SMTP.
    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in the environment variables.
    """
    from app.config import Config
    sender = Config.GMAIL_ADDRESS
    password = Config.GMAIL_APP_PASSWORD

    if not sender or not password:
        print("ERROR: GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in environment.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"ClubConnect <{sender}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email to {to_email}: {e}")
        return False

def send_welcome_email(to_email: str, full_name: str) -> bool:
    """Sends a formatted Welcome email to new users."""
    subject = "Welcome to ClubConnect!"
    
    # Read the HTML template from the email_templates folder
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'welcome.html')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read welcome email template: {e}")
        return False
        
    # Replace the placeholder with the user's name
    html_body = html_template.replace("{{FULL_NAME}}", full_name)
    
    return send_email(to_email, subject, html_body)

def send_otp_email(to_email: str, full_name: str, otp_code: str) -> bool:
    """Sends an OTP email for account verification."""
    subject = "Your ClubConnect Verification Code"
    
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'otp.html')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read otp email template: {e}")
        return False
        
    html_body = html_template.replace("{{FULL_NAME}}", full_name).replace("{{OTP_CODE}}", otp_code)
    
    return send_email(to_email, subject, html_body)

def send_reset_password_email(to_email: str, full_name: str, reset_link: str) -> bool:
    """Sends a password reset/set email."""
    subject = "ClubConnect Password Request"
    
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'reset_password.html')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read reset password email template: {e}")
        return False
        
    html_body = html_template.replace("{{FULL_NAME}}", full_name).replace("{{RESET_LINK}}", reset_link)
    
    return send_email(to_email, subject, html_body)

def send_notification_email(user, subject: str, html_body: str) -> bool:
    """
    Sends an email to a user if their email_notifications preference is enabled.
    Parses user.accessibility_prefs JSON to check the preference.
    """
    if user.accessibility_prefs:
        try:
            prefs = json.loads(user.accessibility_prefs)
            if prefs.get("email_notifications") is False:
                # User has explicitly opted out of email notifications
                print(f"Skipping email to {user.email} (opted out).")
                return False
        except Exception:
            pass # Invalid JSON, fallback to default (True)
            
    return send_email(user.email, subject, html_body)

def send_announcement_email(user, club_name: str, announcement_title: str, content: str) -> bool:
    subject = f"New Announcement from {club_name}: {announcement_title}"
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'announcement.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read announcement template: {e}")
        return False
    html_body = html_template.replace("{{CLUB_NAME}}", club_name).replace("{{ANNOUNCEMENT_TITLE}}", announcement_title).replace("{{CONTENT}}", content)
    return send_notification_email(user, subject, html_body)

def send_membership_approved_email(user, club_name: str) -> bool:
    subject = f"Your membership to {club_name} was approved!"
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'membership_approved.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read membership approved template: {e}")
        return False
    html_body = html_template.replace("{{CLUB_NAME}}", club_name)
    return send_notification_email(user, subject, html_body)

def send_event_posted_email(user, club_name: str, event_title: str) -> bool:
    subject = f"New Event: {event_title} by {club_name}"
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'event_posted.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read event posted template: {e}")
        return False
    html_body = html_template.replace("{{CLUB_NAME}}", club_name).replace("{{EVENT_TITLE}}", event_title)
    return send_notification_email(user, subject, html_body)

def send_event_registration_email(user, event_title: str) -> bool:
    subject = f"Registration Confirmed: {event_title}"
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'event_registration.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read event registration template: {e}")
        return False
    html_body = html_template.replace("{{EVENT_TITLE}}", event_title)
    return send_notification_email(user, subject, html_body)

def send_event_reminder_email(user, event_title: str, start_time_str: str) -> bool:
    subject = f"Reminder: {event_title} is starting soon!"
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'event_reminder.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read event reminder template: {e}")
        return False
    html_body = html_template.replace("{{EVENT_TITLE}}", event_title).replace("{{START_TIME}}", start_time_str)
    return send_notification_email(user, subject, html_body)

def send_task_reminder_email(user, task_title: str, due_date_str: str) -> bool:
    subject = f"Task Deadline Approaching: {task_title}"
    template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'task_reminder.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        print(f"ERROR: Could not read task reminder template: {e}")
        return False
    html_body = html_template.replace("{{TASK_TITLE}}", task_title).replace("{{DUE_DATE}}", due_date_str)
    return send_notification_email(user, subject, html_body)
