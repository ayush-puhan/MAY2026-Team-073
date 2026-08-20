import os,pathlib
from datetime import timedelta

class Config:
    """Base configuration containing settings common to all environments."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-super-secret-key-replace-me')
    
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-insecure-secret-do-not-use-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7) # Long-lived JWT, actual expiration is enforced by AuthSession with sliding expiration

    FRONTEND_URL = os.environ.get("VITE_FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = [FRONTEND_URL]
    CORS_SUPPORTS_CREDENTIALS = True

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = "uploads"
    UNI_BANNER_UPLOAD_DIR = os.path.join(BASE_DIR,UPLOAD_FOLDER,"university_banner") 

    # ----------------------------------------------------
    # ClubConnect AI Module
    # Integrated by AI Backend
    # Module Owner: AI Assistant / RAG Pipeline
    # ----------------------------------------------------
    # Gemini is the only LLM provider wired up through the current roadmap;
    # Groq/OpenRouter fallback providers are explicitly deferred to a later
    # phase and are not referenced anywhere yet.
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    # Directory holding the always-injected System Documents and the
    # on-demand RAG Documents used by the AI module's prompt builder /
    # retriever.
    KNOWLEDGE_BASE_DIR = os.environ.get(
        "KNOWLEDGE_BASE_DIR",
        os.path.join(BASE_DIR, "modules", "ai_services", "knowledge_base"),
    )

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


