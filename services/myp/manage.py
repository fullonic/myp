import sys

from flask.cli import FlaskGroup

from app import create_app, db

import coverage


# COV = coverage.Coverage(
#     branch=True,
#     include="project/*",
#     omit=["project/tests/*", "project/config.py"],
#     # concurrency=True,
# )
# COV.start()
app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command("recreate_db")
def recreate_db():
    """Create command for recreate db."""
    db.drop_all()
    print("CREATING DB")
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    cli()
