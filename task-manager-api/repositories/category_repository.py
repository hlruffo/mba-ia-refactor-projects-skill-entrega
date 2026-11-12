from database import db
from sqlalchemy import func
from models.category import Category
from models.task import Task


class CategoryRepository:
    @staticmethod
    def list_with_task_counts():
        return db.session.query(Category, func.count(Task.id)).outerjoin(Task).group_by(Category.id).all()
