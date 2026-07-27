import os
from flask import Flask
from .config import DevelopmentConfig,ProductionConfig
from app.core.jwt import jwt
from app.core.cors import cors
from app.api import register_api_paths
def create_app():
    app = Flask(__name__)
    
    # Load Config
    app.config.from_object(DevelopmentConfig)
    
    # Initialize Extensions with the app
    cors.init_app(
        app, 
        origins=app.config['CORS_ORIGINS'], 
        supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS']
    )
    jwt.init_app(app)

    # Register RESTful Routes 
    register_api_paths(app)
    
    
    return app