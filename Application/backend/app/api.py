from flask_restful import Api
from app.modules.auth import auth_bp
from app.modules.users import users_bp
from app.modules.student.routes import student_bp
from app.modules.club_leadership.routes import club_bp
from app.modules.helpdesk.routes import admin_support_bp

def register_api_paths(app):
    # Register the auth blueprint which contains its own Api setup
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(club_bp, url_prefix="/api/clubs")
    app.register_blueprint(admin_support_bp,url_prefix="/api/admin/support")
    
