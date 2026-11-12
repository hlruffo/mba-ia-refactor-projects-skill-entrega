from database import db
from datetime import datetime
from sqlalchemy import func
from models.task import Task


class TaskRepository:
    @staticmethod
    def get(task_id):
        return db_get(Task, task_id)

    @staticmethod
    def list_all():
        return Task.query.all()

    @staticmethod
    def search(query='', status='', priority='', user_id=''):
        tasks = Task.query
        if query:
            pattern = f'%{query}%'
            tasks = tasks.filter(Task.title.like(pattern) | Task.description.like(pattern))
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))
        return tasks.all()

    @staticmethod
    def counts_by_status():
        return dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())

    @staticmethod
    def counts_by_priority():
        return dict(db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all())


def db_get(model, key):
    return db.session.get(model, key)
