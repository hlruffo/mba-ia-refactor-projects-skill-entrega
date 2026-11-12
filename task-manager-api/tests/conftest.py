import pytest
from app import create_app
from database import db
from models.category import Category
from models.task import Task
from models.user import User


@pytest.fixture()
def app(tmp_path):
    database_file = tmp_path / 'test.sqlite'
    application = create_app({'TESTING': True, 'SECRET_KEY': 'pytest-only-key',
                              'SQLALCHEMY_DATABASE_URI': f'sqlite:///{database_file}'})
    with application.app_context():
        db.drop_all()
        db.create_all()
        user = User(name='Test User', email='test@example.com', role='admin')
        user.set_password('pytest-password')
        category = Category(name='Testing', description='Fixture category', color='#123456')
        db.session.add_all([user, category])
        db.session.flush()
        db.session.add(Task(title='Fixture task', status='pending', priority=2,
                            user_id=user.id, category_id=category.id))
        db.session.commit()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
