"""Test case for each possible app stage."""

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from app import create_app, config

app = create_app()


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object(config.TestConfig)
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config["SECRET_KEY"] == "THISISONLYATEST")
        self.assertTrue(app.config["TESTING"])
        self.assertTrue(app.config["DEBUG"])
        self.assertTrue(
            app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get("DATABASE_TEST_URL")
        )
        self.assertFalse(app.config["WTF_CSRF_ENABLED"])
        self.assertFalse(app.config["DEBUG_TB_ENABLED"])
        self.assertFalse(app.config["PRESERVE_CONTEXT_ON_EXCEPTION"])


class TestDevConfig(TestCase):
    def create_app(self):
        app.config.from_object(config.DevConfig)
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config["SECRET_KEY"] == "THISISONLYATEST")
        self.assertTrue(app.config["DEBUG_TB_ENABLED"])
        self.assertTrue(app.config["DEBUG"])
        self.assertTrue(app.config["WTF_CSRF_ENABLED"])
        self.assertTrue(app.config["MAX_CONTENT_LENGTH"] == 1024 * 1024 * 1024)
        self.assertFalse(current_app is None)
