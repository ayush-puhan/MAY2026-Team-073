from flask_restful import Api
from app.auth.example import TodoSimple,sayHello

def register_api_paths(app):
    api = Api(app)
    api.add_resource(TodoSimple, '/<string:todo_id>')
    api.add_resource(sayHello, '/')
