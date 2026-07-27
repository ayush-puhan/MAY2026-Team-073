import os

class Config:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-insecure-secret-do-not-use-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    FRONTEND_URL = os.environ.get("VITE_FRONTEND_URL", "http://localhost:5173")
    GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
