import unittest
import sys

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import User

import coverage


COV = coverage.Coverage(
    branch=True,
    include="project/*",
    omit=["project/tests/*", "project/config.py"],
    # concurrency=True,
)
COV.start()
app = create_app()
cli = FlaskGroup(create_app=create_app)


def add_user(username, email):
    """Helper function to add new user."""
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


@cli.command("recreate_db")
def recreate_db():
    """Create command for recreate db."""
    db.drop_all()
    print("CREATING DB")
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover("project/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)


@cli.command("seed_db")
def seed_db():
    """Populate data base with data."""
    add_user("mike", "mike@nonx.org")
    add_user("jenny", "jen@nonx.org")


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover("project/tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == "__main__":
    cli()
