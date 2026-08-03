from flask_restful import Api
from app.modules.auth import auth_bp
from app.modules.users import users_bp
from app.modules.student.routes import student_bp
from app.modules.club_leadership.routes import club_bp
from app.modules.helpdesk.routes import admin_support_bp,ticket_response_bp, support_ticket_bp
from app.modules.club_leadership.routes import club_bp
from app.modules.club_leadership.membership_routes import membership_bp
from app.modules.club_leadership.application_routes import application_bp
from app.modules.notification_system.routes import notification_bp
from app.modules.club_leadership.committee_routes import committee_bp
from app.modules.club_leadership.volunteer_task_routes import volunteer_task_bp
from app.modules.events.routes import event_bp
from app.modules.student.rewards import rewards_bp
from app.modules.announcements.routes import announcement_bp
from app.modules.club_leadership.interests import interest_bp
from app.modules.student.certificates import certificate_bp
from app.modules.university_administration.routes import university_bp
from app.modules.system_admin.admin_routes import system_admin_bp


def register_api_paths(app):
    # Register the auth blueprint which contains its own Api setup
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    # Clubs-related api
    app.register_blueprint(club_bp, url_prefix="/api/clubs")
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
    app.register_blueprint(university_bp, url_prefix='/api/universities')
    app.register_blueprint(system_admin_bp, url_prefix='/api/admin')#from akash
    app.register_blueprint(support_ticket_bp,url_prefix="/api")

