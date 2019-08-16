"""Application core data base models."""

import os
import secrets

from flask import current_app
from sqlalchemy.sql import func

from .. import db


class TagGPX(db.Model):
    """Model to have information about Tag by GPX jobs."""

    __tablename__ = "taggpx"
    id = db.Column(db.Integer(), primary_key=True)
    project_name = db.Column(db.String(64), nullable=False)
    time_difference = db.Column(db.Integer(), default=0)
    email = db.Column(db.String(256), nullable=False)
    created = db.Column(db.DateTime(128), default=func.now())
    download_file = db.Column(db.String(256))
    hash_url = db.Column(db.String(256))
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    send_by_email = db.Column(db.Boolean(), default=False)
    map = db.Column(db.Boolean(), default=False)
    finished = db.Column(db.Boolean(), default=False, nullable=False)

    @property
    def create_folder(self):
        """Create user project folder."""
        folder = f"{self.user.folder_gpx}/{self.project_name}"
        os.mkdir(folder)
        return folder


class Mapping(db.Model):
    """Model to have information about Tag by GPX jobs."""

    __tablename__ = "mapping"
    id = db.Column(db.Integer(), primary_key=True)
    project_name = db.Column(db.String(64), nullable=False)
    tiles = db.Column(db.String(64), default="OpenStreetMap")
    color = db.Column(db.String(64), default="Green")
    created = db.Column(db.DateTime(128), default=func.now())
    download_file = db.Column(db.String(256))
    hash_url = db.Column(db.String(256))
    send_by_email = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    finished = db.Column(db.Boolean(), default=False, nullable=False)

    def create_folders(self, project_name):
        """Create folders for mapping service using project name as root."""
        os.mkdir(
            f'{current_app.config["USERS_FOLDER"]}/{self.user_id}/mapping/{project_name}'
        )
        os.mkdir(
            f'{current_app.config["USERS_FOLDER"]}/{self.user_id}/mapping/{project_name}/delivery'  # noqa
        )
        os.mkdir(
            f'{current_app.config["USERS_FOLDER"]}/{self.user_id}/mapping/{project_name}/geo_files'  # noqa
        )
        os.mkdir(
            f'{current_app.config["USERS_FOLDER"]}/{self.user_id}/mapping/{project_name}/requests'  # noqa
        )

        db.session.add(self)
        db.session.commit()


class Download(db.Model):
    """Model to have information about file saved place."""

    __tablename__ = "download"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    project_name = db.Column(db.String(64))
    file_path = db.Column(db.String(128))
    token = db.Column(db.String(128), unique=True)

    def ensure_unique_token(self):
        """Force unique token into download table."""
        while True:
            try:
                db.session.add(self)
                db.session.commit()
                break
            except Exception as e:
                print("DB ERROR\n", e)  # Must be logged into log file
                db.session.rollback()
                self.token = secrets.token_hex(16)
# download = Download()
# download.file_path = '("{gpx_project.user.folder_gpx}/{project_name}/{project_name}.zip")'
# download.token = "TOKEN"
# download.user_id = 10
# download.project_name = "gpx_project.project_name"
# download.ensure_unique_token()
