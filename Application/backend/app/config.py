import os
from datetime import timedelta

class Config:
    """Base configuration containing settings common to all environments."""
    
    # ---------------------------------------------------------
    # FLASK CORE CONFIGURATION
    # ---------------------------------------------------------
    # Secret key for signing cookies and other cryptographic operations.
    # ALWAYS override this with a strong, random environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-super-secret-key-replace-me')
    
    # ---------------------------------------------------------
    # JWT & AUTHENTICATION CONFIGURATION
    # ---------------------------------------------------------
    # Secret key specifically for encoding/decoding JWT tokens. 
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-insecure-secret-do-not-use-in-production")
    
    # Token expiration times. Adjust according to your security requirements.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # ---------------------------------------------------------
    # CORS CONFIGURATION (Frontend Restriction)
    # ---------------------------------------------------------
    # Define the URL of your frontend server. 
    # Defaulting to localhost:3000 for standard local React/Vue/Angular development.
    FRONTEND_URL = os.environ.get('FRONTEND_URL',"http://localhost:5173")
    CORS_ORIGINS = [FRONTEND_URL]
    # Allow credentials (cookies, authorization headers) to be included in cross-origin requests
    CORS_SUPPORTS_CREDENTIALS = True


class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True
    TESTING = True
    # You can add development-specific overrides here


class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False
    TESTING = False
    
    # In production, enforce that security keys are set in the environment
    @classmethod
    def init_app(cls, app):
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY environment variable is missing!'
        assert os.environ.get('JWT_SECRET_KEY'), 'JWT_SECRET_KEY environment variable is missing!'

