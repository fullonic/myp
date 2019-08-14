"""Test Case basic set up."""

from flask_testing import TestCase

from myp import create_app, db

app = create_app()


class BaseTestCase(TestCase):
    """Test Case basic set up."""

    def create_app(self):
        """Instantiate app."""
        app.config.from_object("app.config.TestConfig")
        return app

    def setUp(self):
        """Create basic set up."""
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """Clean up basic set up."""
        db.session.remove()
        db.drop_all()
