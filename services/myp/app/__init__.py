"""Create Map Your Photos Application."""

import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_celery import Celery

# from app.config import DevConfig


# instantiate of app dependencies
toolbar = DebugToolbarExtension()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
celery = Celery()


def create_app(config=None):
    """Flask app."""
    app = Flask(__name__)

    # APP configuration
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # Set up dependencies
    toolbar.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    celery.init_app(app)

    from .main import create_module as main_create_module
    from .auth import create_module as auth_create_module

    main_create_module(app)
    auth_create_module(app)

    # Set up shell context for flask client
    from .auth.models import User
    from .main.models import TagGPX, Mapping, Download

    @app.shell_context_processor
    def ctx():
        import app.main.main_tasks as tasks  # noqa

        return {
            "app": app,
            "db": db,
            "User": User,
            "TagGPX": TagGPX,
            "Mapping": Mapping,
            "Download": Download,
            "tasks": tasks,
        }

    return app
