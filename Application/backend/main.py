import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from app.api import register_api_paths

# Load environment variables
load_dotenv()

from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-only-insecure-secret-do-not-use-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600 
jwt = JWTManager(app)

register_api_paths(app)

if __name__ == '__main__':
    app.run(debug=True)