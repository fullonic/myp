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
    half_hour = db.Column(db.Integer())
    time_ref = db.Column(db.String(2))
    email = db.Column(db.String(256), nullable=False)
    created = db.Column(db.DateTime(128), default=func.now())
    download_file = db.Column(db.String(256))
    hash_url = db.Column(db.String(256))
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    send_by_email = db.Column(db.Boolean(), default=False)
    map = db.Column(db.Boolean(), default=False)

    @property
    def create_folder(self):
        """Create user project folder."""
        folder = f"{self.user.folder_gpx}/{self.project_name}"
        os.mkdir(folder)
        return folder

    def set_time_difference(self, _time, half_hour):
        """Clean form time difference user input and insert into db."""
        clean = _time.split(":")[0].split(" ")
        self.time_ref = clean[0]
        self.half_hour = half_hour
        self.time_difference = int(clean[-1])
        print(self.time_ref, half_hour, self.time_difference)

        db.session.add(self)
        db.session.commit()


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
    is_ready = db.Column(db.Boolean(), default=False)

    def ensure_unique_token(self):
        """Force unique token into download table."""
        while True:
            try:
                db.session.add(self)
                db.session.commit()
                break
            except Exception as e:  # Find error related with contains violation: use django UUID4
                print("DB ERROR\n", e)  # Must be logged into log file
                db.session.rollback()
                self.token = secrets.token_hex(16)

    def ready(self):
        """Make project available for download after celery job finished.

        User must be notify by profile private message or email.
        """
        print(f"Setting <{self.id}:{self.project_name}> project ready to download")
        self.is_ready = True
        db.session.add(self)
        db.session.commit()
