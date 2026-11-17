import jwt

from models.user import User
from database import db


def test_health_and_root(client):
    assert client.get('/health').status_code == 200
    assert client.get('/health').json['status'] == 'ok'
    assert client.get('/').json == {'message': 'Task Manager API', 'version': '1.0'}


def test_task_endpoints(client):
    tasks = client.get('/tasks')
    assert tasks.status_code == 200 and len(tasks.json) == 1
    assert tasks.json[0]['user_name'] == 'Test User'
    task_id = tasks.json[0]['id']
    assert client.get(f'/tasks/{task_id}').status_code == 200
    assert client.get('/tasks/search?q=Fixture').json[0]['title'] == 'Fixture task'
    assert client.get('/tasks/stats').json['total'] == 1
    created = client.post('/tasks', json={'title': 'New task', 'priority': 1})
    assert created.status_code == 201
    assert client.put(f"/tasks/{created.json['id']}", json={'status': 'done'}).status_code == 200
    assert client.delete(f"/tasks/{created.json['id']}").status_code == 200


def test_user_endpoints_and_password_safety(client, app):
    listed = client.get('/users')
    assert listed.status_code == 200 and listed.json[0]['task_count'] == 1
    created = client.post('/users', json={'name': 'New User', 'email': 'new@example.com', 'password': 'safe-test-password'})
    assert created.status_code == 201
    assert 'password' not in created.json
    with app.app_context():
        user = db.session.get(User, created.json['id'])
        assert user.password != 'safe-test-password'
        assert not user.password.startswith('d41d8cd98f00b204e9800998ecf8427e')
    user_id = created.json['id']
    assert client.get(f'/users/{user_id}').status_code == 200
    assert client.get(f'/users/{user_id}/tasks').status_code == 200
    login = client.post('/login', json={'email': 'new@example.com', 'password': 'safe-test-password'})
    assert login.status_code == 200
    token = login.json['token']
    assert not token.startswith('fake-jwt-token-')
    claims = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    assert claims['sub'] == str(user_id)
    assert claims['role'] == 'user'
    assert claims['exp'] > claims['iat']
    assert client.post('/login', json={'email': 'new@example.com', 'password': 'bad'}).status_code == 401
    assert client.put(f'/users/{user_id}', json={'name': 'Updated'}).status_code == 200
    assert client.delete(f'/users/{user_id}').status_code == 200


def test_reports_and_categories(client):
    assert client.get('/reports/summary').status_code == 200
    assert client.get('/reports/user/1').status_code == 200
    categories = client.get('/categories')
    assert categories.status_code == 200 and categories.json[0]['task_count'] == 1
    created = client.post('/categories', json={'name': 'Another'})
    assert created.status_code == 201
    category_id = created.json['id']
    assert client.put(f'/categories/{category_id}', json={'name': 'Updated'}).status_code == 200
    assert client.delete(f'/categories/{category_id}').status_code == 200


def test_validation_errors_are_consistent(client):
    response = client.post('/tasks', json={'title': 'a'})
    assert response.status_code == 400 and response.json == {'error': 'Título muito curto'}
    assert client.post('/users', json={}).json == {'error': 'Dados inválidos'}
