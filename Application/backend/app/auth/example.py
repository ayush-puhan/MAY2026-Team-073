from flask import request
from flask_restful import Resource

todos = {1:"Hello all"}
class sayHello(Resource):
    def get(self):
        return {'team' : 73, 'say' : 'hello'}
    
class TodoSimple(Resource):
    def get(self, todo_id):
        if todo_id in todos.keys():
            return {todo_id: todos[todo_id]}
        else:
            return { "message": "Todo is not present."}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}