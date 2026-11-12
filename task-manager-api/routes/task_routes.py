from flask import Blueprint, jsonify, request
from controllers.task_controller import TaskController

task_bp = Blueprint('tasks', __name__)

@task_bp.get('/tasks')
def get_tasks():
    return jsonify(TaskController.list_tasks()), 200

@task_bp.get('/tasks/<int:task_id>')
def get_task(task_id):
    return jsonify(TaskController.get_task(task_id)), 200

@task_bp.post('/tasks')
def create_task():
    body, status = TaskController.create_task(request.get_json(silent=True))
    return jsonify(body), status

@task_bp.put('/tasks/<int:task_id>')
def update_task(task_id):
    return jsonify(TaskController.update_task(task_id, request.get_json(silent=True))), 200

@task_bp.delete('/tasks/<int:task_id>')
def delete_task(task_id):
    return jsonify(TaskController.delete_task(task_id)), 200

@task_bp.get('/tasks/search')
def search_tasks():
    return jsonify(TaskController.search(request.args.get('q', ''), request.args.get('status', ''),
                                        request.args.get('priority', ''), request.args.get('user_id', ''))), 200

@task_bp.get('/tasks/stats')
def task_stats():
    return jsonify(TaskController.stats()), 200
