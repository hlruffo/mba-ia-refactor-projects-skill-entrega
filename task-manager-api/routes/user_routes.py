from flask import Blueprint, jsonify, request
from controllers.user_controller import UserController

user_bp = Blueprint('users', __name__)

@user_bp.get('/users')
def get_users():
    return jsonify(UserController.list_users()), 200

@user_bp.get('/users/<int:user_id>')
def get_user(user_id):
    return jsonify(UserController.get_user(user_id)), 200

@user_bp.post('/users')
def create_user():
    body, status = UserController.create_user(request.get_json(silent=True))
    return jsonify(body), status

@user_bp.put('/users/<int:user_id>')
def update_user(user_id):
    return jsonify(UserController.update_user(user_id, request.get_json(silent=True))), 200

@user_bp.delete('/users/<int:user_id>')
def delete_user(user_id):
    return jsonify(UserController.delete_user(user_id)), 200

@user_bp.get('/users/<int:user_id>/tasks')
def get_user_tasks(user_id):
    return jsonify(UserController.get_user_tasks(user_id)), 200

@user_bp.post('/login')
def login():
    return jsonify(UserController.login(request.get_json(silent=True))), 200
