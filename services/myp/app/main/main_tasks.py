"""Main app background tasks."""

import os

from werkzeug.utils import secure_filename

from .. import celery
from .utilities.utils import allowed_photo_file
from .utilities.service_mapping import map_photos


@celery.task()
def multiply(x, y):
    return x * y


@celery.task()
def log(msg):
    return msg


@celery.task()
def save_files(folder, photos):
    """Save files to disk."""
    print("DOING IN BACKGROUND")
    for file in photos:
        if file and allowed_photo_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))


@celery.task()
def map_it(folder, id_, service_type="mapping"):
    """Make photo mapping a celery task."""
    print("DOING IN BACKGROUND")
    map_photos(folder, id_, service_type="mapping")
    print("DONE")
