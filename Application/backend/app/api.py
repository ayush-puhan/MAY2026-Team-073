from flask_restful import Api
from app.modules.auth import auth_bp
from app.modules.users import users_bp
from app.modules.student.routes import student_bp
from app.modules.university_administration.routes import university_bp
from app.modules.system_admin.admin_routes import system_admin_bp


def register_api_paths(app):
    # Register the auth blueprint which contains its own Api setup
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(university_bp, url_prefix='/api/universities')
    app.register_blueprint(system_admin_bp, url_prefix='/api/admin')


