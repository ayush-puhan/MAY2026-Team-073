from flask_restful import Api
from app.modules.auth import auth_bp
from app.modules.users import users_bp
from app.modules.student.routes import student_bp
from app.modules.clubs.core.routes import club_bp
from app.modules.helpdesk.routes import admin_support_bp,ticket_response_bp, support_ticket_bp
from app.modules.clubs.members.membership_routes import membership_bp
from app.modules.clubs.members.leave_club import leave_club_bp
from app.modules.clubs.members.application_routes import application_bp
from app.modules.notification_system.routes import notification_bp
from app.modules.clubs.management.committee_routes import committee_bp
from app.modules.clubs.management.volunteer_task_routes import volunteer_task_bp
from app.modules.events.routes import event_bp
from app.modules.student.rewards import rewards_bp
from app.modules.announcements.routes import announcement_bp
from app.modules.clubs.core.interests import interest_bp
from app.modules.student.certificates import certificate_bp
from app.modules.university_administration.university_routes import university_bp
from app.modules.university_administration.university_admin import university_admin_bp
from app.modules.system_admin.admin_routes import system_admin_bp
from app.modules.faculty.routes import  faculty_advisor_bp
from app.modules.faculty.faculty_advisors import faculty_bp
from app.modules.clubs.admin.club_creation_requests import club_creation_bp
from app.modules.clubs.management.club_resources import communication_bp

from app.modules.clubs.management.club_budget import budget_bp
from app.modules.clubs.members.transfer_presidency import transfer_presidency_bp
from app.modules.emergency_report.routes import  em_report
from app.modules.calendar.calendar_routes import calendar_bp
from flask import Blueprint

# ----------------------------------------------------
# Health Check Endpoint for Uptime Bots
# ----------------------------------------------------
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    return {"status": "awake", "database": "warm"}, 200

# ----------------------------------------------------
# ClubConnect AI Module
# Integrated by AI Backend
# Module Owner: AI Assistant / RAG Pipeline
# ----------------------------------------------------
from app.modules.ai_services import ai_bp

def register_api_paths(app):
    # Register the auth blueprint which contains its own Api setup
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    # Clubs-related api
    app.register_blueprint(club_bp, url_prefix="/api/clubs")
    app.register_blueprint(leave_club_bp, url_prefix="/api")
    app.register_blueprint(membership_bp,url_prefix="/api")
    app.register_blueprint(application_bp,url_prefix="/api")
    app.register_blueprint(volunteer_task_bp,url_prefix="/api")
    # Event api
    app.register_blueprint(event_bp,url_prefix="/api")
    # Ticket-related api for system-admin
    app.register_blueprint(admin_support_bp,url_prefix="/api/admin/support")
    app.register_blueprint(ticket_response_bp,url_prefix="/api")


    # Notification-related api
    app.register_blueprint(notification_bp, url_prefix="/api")

    app.register_blueprint(committee_bp,url_prefix="/api")

    # Student reward
    app.register_blueprint(rewards_bp, url_prefix="/api/rewards")
    app.register_blueprint(announcement_bp, url_prefix="/api")
    app.register_blueprint(interest_bp,url_prefix="/api")
    app.register_blueprint(certificate_bp,url_prefix="/api")    
    app.register_blueprint(support_ticket_bp,url_prefix="/api")

    app.register_blueprint(faculty_bp)
    app.register_blueprint(club_creation_bp,url_prefix="/api")
    app.register_blueprint(communication_bp,url_prefix="/api")
    app.register_blueprint(budget_bp,url_prefix="/api")
    app.register_blueprint(transfer_presidency_bp, url_prefix="/api")    # Faculty Advisor
    app.register_blueprint(faculty_advisor_bp, url_prefix='/api/faculty')
    
    # System admin
    app.register_blueprint(system_admin_bp, url_prefix='/api/admin')

    # University
    app.register_blueprint(university_bp, url_prefix='/api/universities')

    # University admin
    app.register_blueprint(university_admin_bp, url_prefix='/api/university-admin')

    # Emergency Report
    app.register_blueprint(em_report, url_prefix="/api/emergency-reports")

    # Calendar
    app.register_blueprint(calendar_bp, url_prefix="/api")

    # AI Services (ClubConnect Assistant) - url_prefix already set on the blueprint itself
    app.register_blueprint(ai_bp)

