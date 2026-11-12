from utils.time import utcnow
from datetime import datetime, timedelta
from sqlalchemy import case, func
from database import db
from errors import APIError
from models.task import Task
from models.user import User
from models.category import Category
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from validation import require_object


class ReportController:
    @staticmethod
    def summary():
        counts_status = TaskRepository.counts_by_status()
        counts_priority = TaskRepository.counts_by_priority()
        now = utcnow()
        seven_days_ago = now - timedelta(days=7)
        overdue_tasks = Task.query.filter(Task.due_date < now, Task.status.notin_(['done', 'cancelled'])).all()
        productivity = db.session.query(
            User.id, User.name, func.count(Task.id),
            func.sum(case((Task.status == 'done', 1), else_=0))
        ).outerjoin(Task).group_by(User.id).all()
        user_stats = []
        for user_id, name, total, completed in productivity:
            total, completed = total or 0, completed or 0
            user_stats.append({'user_id': user_id, 'user_name': name, 'total_tasks': total,
                               'completed_tasks': completed,
                               'completion_rate': round(completed / total * 100, 2) if total else 0})
        return {
            'generated_at': str(now),
            'overview': {'total_tasks': sum(counts_status.values()), 'total_users': User.query.count(), 'total_categories': Category.query.count()},
            'tasks_by_status': {status: counts_status.get(status, 0) for status in ('pending', 'in_progress', 'done', 'cancelled')},
            'tasks_by_priority': {label: counts_priority.get(priority, 0) for label, priority in
                                  (('critical', 1), ('high', 2), ('medium', 3), ('low', 4), ('minimal', 5))},
            'overdue': {'count': len(overdue_tasks), 'tasks': [
                {'id': task.id, 'title': task.title, 'due_date': str(task.due_date), 'days_overdue': (now - task.due_date).days}
                for task in overdue_tasks]},
            'recent_activity': {
                'tasks_created_last_7_days': Task.query.filter(Task.created_at >= seven_days_ago).count(),
                'tasks_completed_last_7_days': Task.query.filter(Task.status == 'done', Task.updated_at >= seven_days_ago).count()},
            'user_productivity': user_stats,
        }

    @staticmethod
    def user_report(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise APIError('Usuário não encontrado', 404)
        tasks = Task.query.filter_by(user_id=user_id).all()
        counts = {status: sum(task.status == status for task in tasks)
                  for status in ('done', 'pending', 'in_progress', 'cancelled')}
        now = utcnow()
        total = len(tasks)
        return {'user': {'id': user.id, 'name': user.name, 'email': user.email},
                'statistics': {'total_tasks': total, **counts,
                    'overdue': sum(task.is_overdue() for task in tasks),
                    'high_priority': sum(task.priority <= 2 for task in tasks),
                    'completion_rate': round(counts['done'] / total * 100, 2) if total else 0}}

    @staticmethod
    def categories():
        return [{**category.to_dict(), 'task_count': count}
                for category, count in CategoryRepository.list_with_task_counts()]

    @staticmethod
    def create_category(data):
        data = require_object(data)
        name = data.get('name')
        if not name:
            raise APIError('Nome é obrigatório')
        category = Category(name=name, description=data.get('description', ''), color=data.get('color', '#000000'))
        try:
            db.session.add(category)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao criar categoria', 500)
        return category.to_dict(), 201

    @staticmethod
    def update_category(cat_id, data):
        category = db.session.get(Category, cat_id)
        if not category:
            raise APIError('Categoria não encontrada', 404)
        data = require_object(data)
        for field in ('name', 'description', 'color'):
            if field in data:
                setattr(category, field, data[field])
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao atualizar', 500)
        return category.to_dict()

    @staticmethod
    def delete_category(cat_id):
        category = db.session.get(Category, cat_id)
        if not category:
            raise APIError('Categoria não encontrada', 404)
        try:
            db.session.delete(category)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao deletar', 500)
        return {'message': 'Categoria deletada'}
