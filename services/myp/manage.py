import os
from pathlib import Path

from flask.cli import FlaskGroup

from app import create_app, db

import coverage

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
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
    logger.info("RECREATING DB")
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("create_db")
def create_db():
    """Create command for recreate db."""
    logger.info("CREATING DB")
    db.create_all()
    db.session.commit()


@cli.command("create_folders")
def create_folders():
    logger.info(">> Creating project folders")

    folders = [
        "BASE_DIR",
        "MAPPING_FOLDER",
        "UPLOAD_FOLDER",
        "GEOJSON_FOLDER",
        "DELIVERY_FOLDER",
        "USERS_FOLDER",
        "GEOTAG_FOLDER",
    ]
    for folder in folders:
        try:
            os.mkdir(f"{app.config[folder]}")
            logger.info(f"  >> {folder} created")
        except FileExistsError:
            logger.warning(f"  >> {folder} already exist")
            continue


if __name__ == "__main__":
    cli()
