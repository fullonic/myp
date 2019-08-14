import os
from . import bcrypt


from flask import current_app
from sqlalchemy.sql import func
from flask_login import AnonymousUserMixin

from app import db


class User(db.Model):
    """User model."""

    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    folder_mapping = db.Column(db.String(64), default="", nullable=False)
    folder_gpx = db.Column(db.String(64), default="", nullable=False)
    by_gpx = db.relationship("TagGPX", backref="user", lazy="dynamic")
    by_mapping = db.relationship("Mapping", backref="user", lazy="dynamic")
    plan = db.Column(db.String(16), default="free")

    def __init__(self, email):  # noqa
        self.email = email

    def __repr__(self):  # noqa
        return f"<User {self.email}>"

    def set_password(self, password):
        """Password hash generator."""
        pwrd = bcrypt.generate_password_hash(password).decode("utf-8")
        self.password = pwrd

    def check_password(self, password):
        """Check and validation of the password."""
        return bcrypt.check_password_hash(self.password, password)

    @property
    def is_authenticated(self):
        """Check if user is authenticated."""
        if isinstance(self, AnonymousUserMixin):
            return False
        return True

    @property
    def is_active(self):
        """Check if user is active.

        Used by flask_login
        """
        return True

    def get_id(self):
        """To easily get user id."""
        return self.id

    def create_folder(self):
        """Create all folder for the different services."""
        # Create main folder
        os.mkdir(f'{current_app.config["USERS_FOLDER"]}/{self.id}')
        # Create folder for TagGPX
        os.mkdir(f'{current_app.config["USERS_FOLDER"]}/{self.id}/by_gpx')
        # Create folder for mapping
        os.mkdir(f'{current_app.config["USERS_FOLDER"]}/{self.id}/mapping')

        self.folder_gpx = f'{current_app.config["USERS_FOLDER"]}/{self.id}/by_gpx'
        self.folder_mapping = f'{current_app.config["USERS_FOLDER"]}/{self.id}/mapping'
        db.session.add(self)
        db.session.commit()
