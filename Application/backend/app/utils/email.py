import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Sends an email using Gmail SMTP.
    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in the environment variables.
    """
    sender = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")

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
