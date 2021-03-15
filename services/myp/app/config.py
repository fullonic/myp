"""APP CONFIG."""

import os


class Config:
    """Basic app configuration."""

    SECRET_KEY = "THISISONLYATEST"
    TESTING = False
    DEBUG = False
    # Set up maximum total upload size
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1 GB
    # Mapping service
    BASE_DIR = "./app/main/MYP"
    MAPPING_FOLDER = "./app/main/MYP/mapping"
    UPLOAD_FOLDER = "./app/main/MYP/mapping/requests"
    GEOJSON_FOLDER = "./app/main/MYP/mapping/geo_files"
    DELIVERY_FOLDER = "./app/main/MYP/mapping/delivery"

    # By GPX Service
    USERS_FOLDER = f"{os.getcwd()}/app/main/MYP/users"
    GEOTAG_FOLDER = f"{os.getcwd()}/app/main/MYP/by_gpx"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    WTF_CSRF_ENABLED = True


class DevConfig(Config):
    """Development app configuration."""

    CACHE_TYPE = "simple"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = True
    DEBUG_TB_ENABLED = True
    SQLALCHEMY_RECORD_QUERIES = True
    MYP_SLOW_DB_QUERY_TIME = 0.5

    # CELERY CONFIG
    CELERY_IMPORTS = ("app.main.main_tasks",)
    CELERY_BROKER_URL = "amqp://rabbitmq:rabbitmq@localhost//"
    CELERY_RESULT_BACKEND = "amqp://rabbitmq:rabitmq@localhost//"


class ProdConfig(Config):
    """Development app configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = False
    DEBUG_TB_ENABLED = False


class TestConfig(Config):
    """Development app configuration."""

    CACHE_TYPE = "null"

    # Disable CSRF tokens in the Forms (only for testing purposes!)
    WTF_CSRF_ENABLED = False
    TESTING = True
    DEBUG = True
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
