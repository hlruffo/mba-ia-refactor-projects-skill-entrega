from utils.time import utcnow
from datetime import datetime
from sqlalchemy.orm import joinedload
from database import db
from errors import APIError
from models.task import Task
from models.user import User
from models.category import Category
from repositories.task_repository import TaskRepository
from validation import validate_task


class TaskController:
    @staticmethod
    def list_tasks():
        result = []
        for task in Task.query.options(joinedload(Task.user), joinedload(Task.category)).all():
            item = task.to_dict()
            item['overdue'] = task.is_overdue()
            item['user_name'] = task.user.name if task.user else None
            item['category_name'] = task.category.name if task.category else None
            result.append(item)
        return result

    @staticmethod
    def get_task(task_id):
        task = TaskRepository.get(task_id)
        if not task:
            raise APIError('Task não encontrada', 404)
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data

    @staticmethod
    def create_task(data):
        values = validate_task(data, creating=True)
        TaskController._validate_relations(values)
        task = Task(**values)
        try:
            db.session.add(task)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao criar task', 500)
        return task.to_dict(), 201

    @staticmethod
    def update_task(task_id, data):
        task = TaskRepository.get(task_id)
        if not task:
            raise APIError('Task não encontrada', 404)
        values = validate_task(data)
        TaskController._validate_relations(values)
        for key, value in values.items():
            setattr(task, key, value)
        task.updated_at = utcnow()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao atualizar', 500)
        return task.to_dict()

    @staticmethod
    def delete_task(task_id):
        task = TaskRepository.get(task_id)
        if not task:
            raise APIError('Task não encontrada', 404)
        try:
            db.session.delete(task)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao deletar', 500)
        return {'message': 'Task deletada com sucesso'}

    @staticmethod
    def search(query, status, priority, user_id):
        return [task.to_dict() for task in TaskRepository.search(query, status, priority, user_id)]

    @staticmethod
    def stats():
        counts = TaskRepository.counts_by_status()
        total = sum(counts.values())
        overdue = Task.query.filter(Task.due_date < utcnow(), Task.status.notin_(['done', 'cancelled'])).count()
        return {'total': total, 'pending': counts.get('pending', 0), 'in_progress': counts.get('in_progress', 0),
                'done': counts.get('done', 0), 'cancelled': counts.get('cancelled', 0), 'overdue': overdue,
                'completion_rate': round(counts.get('done', 0) / total * 100, 2) if total else 0}

    @staticmethod
    def _validate_relations(values):
        if values.get('user_id') and not db.session.get(User, values['user_id']):
            raise APIError('Usuário não encontrado', 404)
        if values.get('category_id') and not db.session.get(Category, values['category_id']):
            raise APIError('Categoria não encontrada', 404)
