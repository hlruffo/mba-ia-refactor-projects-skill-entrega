from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

from database import db
from errors import APIError
from models.user import User
from models.task import Task
from repositories.user_repository import UserRepository
from validation import require_object, validate_email, validate_role


class UserController:
    @staticmethod
    def list_users():
        return [{'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role,
                 'active': user.active, 'created_at': str(user.created_at), 'task_count': count}
                for user, count in UserRepository.list_with_task_counts()]

    @staticmethod
    def get_user(user_id):
        user = UserRepository.get(user_id)
        if not user:
            raise APIError('Usuário não encontrado', 404)
        result = user.to_dict()
        result['tasks'] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
        return result

    @staticmethod
    def create_user(data):
        data = require_object(data)
        name, email, password = data.get('name'), data.get('email'), data.get('password')
        if not name:
            raise APIError('Nome é obrigatório')
        if not email:
            raise APIError('Email é obrigatório')
        if not password:
            raise APIError('Senha é obrigatória')
        validate_email(email)
        if len(password) < 4:
            raise APIError('Senha deve ter no mínimo 4 caracteres')
        role = data.get('role', 'user')
        validate_role(role)
        if UserRepository.by_email(email):
            raise APIError('Email já cadastrado', 409)
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao criar usuário', 500)
        return user.to_dict(), 201

    @staticmethod
    def update_user(user_id, data):
        user = UserRepository.get(user_id)
        if not user:
            raise APIError('Usuário não encontrado', 404)
        data = require_object(data)
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            validate_email(data['email'])
            existing = UserRepository.by_email(data['email'])
            if existing and existing.id != user_id:
                raise APIError('Email já cadastrado', 409)
            user.email = data['email']
        if 'password' in data:
            if len(data['password']) < 4:
                raise APIError('Senha muito curta')
            user.set_password(data['password'])
        if 'role' in data:
            validate_role(data['role'])
            user.role = data['role']
        if 'active' in data:
            user.active = data['active']
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao atualizar', 500)
        return user.to_dict()

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get(user_id)
        if not user:
            raise APIError('Usuário não encontrado', 404)
        try:
            Task.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise APIError('Erro ao deletar', 500)
        return {'message': 'Usuário deletado com sucesso'}

    @staticmethod
    def get_user_tasks(user_id):
        user = UserRepository.get(user_id)
        if not user:
            raise APIError('Usuário não encontrado', 404)
        tasks = Task.query.filter_by(user_id=user_id).all()
        return [{'id': task.id, 'title': task.title, 'description': task.description, 'status': task.status,
                 'priority': task.priority, 'created_at': str(task.created_at),
                 'due_date': str(task.due_date) if task.due_date else None, 'overdue': task.is_overdue()}
                for task in tasks]

    @staticmethod
    def login(data):
        data = require_object(data)
        email, password = data.get('email'), data.get('password')
        if not email or not password:
            raise APIError('Email e senha são obrigatórios')
        user = UserRepository.by_email(email)
        if not user or not user.check_password(password):
            raise APIError('Credenciais inválidas', 401)
        if not user.active:
            raise APIError('Usuário inativo', 403)
        now = datetime.now(timezone.utc)
        expires_minutes = current_app.config.get('JWT_EXPIRES_MINUTES', 60)
        token = jwt.encode(
            {
                'sub': str(user.id),
                'email': user.email,
                'role': user.role,
                'iat': now,
                'exp': now + timedelta(minutes=expires_minutes),
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256',
        )
        return {'message': 'Login realizado com sucesso', 'user': user.to_dict(), 'token': token}
