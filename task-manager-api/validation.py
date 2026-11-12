import re
from datetime import datetime
from errors import APIError

VALID_STATUSES = {'pending', 'in_progress', 'done', 'cancelled'}
VALID_ROLES = {'user', 'admin', 'manager'}
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def require_object(data):
    if not isinstance(data, dict) or not data:
        raise APIError('Dados inválidos')
    return data


def parse_date(value, message='Data inválida'):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except (TypeError, ValueError):
        raise APIError(message)


def validate_email(value):
    if not isinstance(value, str) or not EMAIL_PATTERN.match(value):
        raise APIError('Email inválido')


def validate_role(value):
    if value not in VALID_ROLES:
        raise APIError('Role inválido')


def validate_task(data, creating=False):
    require_object(data)
    result = {}
    if creating and not data.get('title'):
        raise APIError('Título é obrigatório')
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str) or not title.strip():
            raise APIError('Título não pode ser vazio')
        if len(title.strip()) < 3:
            raise APIError('Título muito curto')
        if len(title.strip()) > 200:
            raise APIError('Título muito longo')
        result['title'] = title.strip()
    for field in ('description', 'status', 'priority', 'user_id', 'category_id', 'due_date', 'tags'):
        if field in data:
            result[field] = data[field]
    if 'status' in result and result['status'] not in VALID_STATUSES:
        raise APIError('Status inválido')
    if 'priority' in result:
        try:
            result['priority'] = int(result['priority'])
        except (ValueError, TypeError):
            raise APIError('Prioridade inválida')
        if not 1 <= result['priority'] <= 5:
            raise APIError('Prioridade deve ser entre 1 e 5')
    if 'due_date' in result:
        result['due_date'] = parse_date(result['due_date'], 'Formato de data inválido. Use YYYY-MM-DD')
    if isinstance(result.get('tags'), list):
        result['tags'] = ','.join(result['tags'])
    return result
