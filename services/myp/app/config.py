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

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = True
    DEBUG_TB_ENABLED = True

class ProdConfig(Config):
    """Development app configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = False
    DEBUG_TB_ENABLED = False


class TestConfig(Config):
    """Development app configuration."""

    # Disable CSRF tokens in the Forms (only for testing purposes!)
    WTF_CSRF_ENABLED = False
    TESTING = True
    DEBUG = True
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
