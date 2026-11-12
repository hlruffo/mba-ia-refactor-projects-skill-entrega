"""Application factory for the Loja MVC API."""

import logging
import sqlite3

from flask import Flask
from flask_cors import CORS

from config import Config
from .database import init_app as init_database, init_schema, migrate_passwords, seed_if_empty
from .errors import register_error_handlers
from .routes import api


def create_app(config=None):
    app = Flask(__name__)
    settings = config if isinstance(config, Config) else Config(**(config or {}))
    app.config.update(settings.as_flask_mapping())
    app.logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if settings.CORS_ORIGINS:
        CORS(app, origins=settings.CORS_ORIGINS)
    app.register_blueprint(api)
    init_database(app)
    register_error_handlers(app)

    if settings.AUTO_INIT_DB:
        connection = sqlite3.connect(settings.DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        try:
            init_schema(connection)
            migrate_passwords(connection)
            seed_if_empty(connection)
        finally:
            connection.close()
    return app
