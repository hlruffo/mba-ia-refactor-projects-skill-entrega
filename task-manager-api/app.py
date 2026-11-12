from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from config import Settings
from database import db
from errors import APIError
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Settings)
    if test_config:
        app.config.update(test_config)
    CORS(app)
    db.init_app(app)

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(500)
    def handle_internal_error(_error):
        db.session.rollback()
        return jsonify({'error': 'Erro interno'}), 500

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.get('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @app.get('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False), host=app.config.get('HOST', '0.0.0.0'),
            port=int(app.config.get('PORT', 5000)))
