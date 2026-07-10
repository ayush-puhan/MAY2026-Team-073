from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

todos = {1:"Hello all"}

class TodoSimple(Resource):
    def get(self, todo_id):
        if todo_id in todos.keys():
            return {todo_id: todos[todo_id]}
        else:
            return { "message": "Todo is not present."}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}

api.add_resource(TodoSimple, '/<string:todo_id>')

if __name__ == '__main__':
    app.run(debug=True)