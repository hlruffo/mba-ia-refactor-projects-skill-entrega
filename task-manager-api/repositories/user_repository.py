from database import db
from sqlalchemy import func
from models.user import User
from models.task import Task


class UserRepository:
    @staticmethod
    def get(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def list_with_task_counts():
        rows = db.session.query(User, func.count(Task.id)).outerjoin(Task).group_by(User.id).all()
        return rows
