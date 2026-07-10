from flask import Flask
from app.api import  register_api_paths


app = Flask(__name__)
register_api_paths(app)


if __name__ == '__main__':
    app.run(debug=True)