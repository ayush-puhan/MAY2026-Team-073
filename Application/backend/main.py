import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from app.api import register_api_paths

# Load environment variables
load_dotenv()

from flask_cors import CORS

from app.config import Config

from app.database.database import init_engine
init_engine()

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": "*"}})

jwt = JWTManager(app)

register_api_paths(app)

if __name__ == '__main__':
    app.run(debug=True)
