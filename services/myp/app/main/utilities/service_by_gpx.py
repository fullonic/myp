"""Create Service for Map by GPX.

# TODO:
- Create a list of photos not tag because are out of the time space of the gpx file
- Create a zip file to download photos
"""

import os
import secrets
from typing import NamedTuple, List
from datetime import datetime, timedelta
from functools import namedtuple
from glob import glob


import piexif
import gpxpy
import gpxpy.gpx

from app import db
from app.main.models import TagGPX, Download
from .service_mapping import map_photos

# Set up objects
GPSPoint = namedtuple("GPSPoint", ["id", "lat", "lng", "time"])
Photo = namedtuple("Photo", ["name", "time"])
PhotoTag = namedtuple("PhotoTag", ["name", "time", "lat", "lng"])
PROJECT_CONFIG = {}


##########################
# HELPER FUNCTIONS
##########################


def to_datetime(datetime_: str) -> datetime:
    """Convert exif.datetime string to python datetime with tzinfo."""
    dt = datetime.strptime(datetime_, "%Y:%m:%d %H:%M:%S")
    return dt.replace(tzinfo=PROJECT_CONFIG["TZ"])


def create_track_data(points):
    """Create track data points from track segments."""
    pass


def get_track_data(
    folder: os.path = None, time_difference: int = 0
) -> List[NamedTuple]:
    """Parser to data from GPX file."""
    track = glob(f"{folder}/*.gpx")
    gpx_file = open(track[0])
    gpx = gpxpy.parse(gpx_file)

    track_data = []
    for track in gpx.tracks:
        # TESTS ARE NEEDED TO CHECK IF THIS IF IS NECESSARY. IF TRUE, MUST BE IMPROVED TO DRY
        if len(track.segments) > 1:
            gpx = gpxpy.gpx.GPX()
            gpx_seg = gpxpy.gpx.GPXTrackSegment()
            for seg in track.segments:
                for point in seg.points:
                    gpx_seg.points.append(point)
            for i, point in enumerate(gpx_seg.points):
                track_data.append(
                    GPSPoint(
                        i,
                        point.latitude,
                        point.longitude,
                        point.time + timedelta(hours=time_difference),
                    )
                )
        else:
            for segment in track.segments:
                for i, point in enumerate(segment.points):
                    track_data.append(
                        GPSPoint(
                            i,
                            point.latitude,
                            point.longitude,
                            point.time + timedelta(hours=time_difference),
                        )
                    )
    PROJECT_CONFIG["TZ"] = track_data[0].time.tzinfo
    PROJECT_CONFIG["INTERVAL"] = (track_data[3].time - track_data[2].time).seconds
    return track_data


def get_photo_data(photos_folder: os.path = None) -> List[NamedTuple]:
    """Parser to get photos data: Name, Time."""
    # Get all photos
    # NOTE: needs to improve glob list files creation to avoid list compression
    photos = glob(f"{photos_folder}/*")
    photos = [photo for photo in photos if photo.split(".")[-1] != "gpx"]
    # Get name and time and add to a list
    photos_data = []
    for photo in photos:
        exif = piexif.load(photo)
        try:
            dt = to_datetime(exif["Exif"][36868].decode())
        except KeyError:
            dt = to_datetime(exif["0th"][306].decode())
        photos_data.append(Photo(os.path.basename(photo), dt))
    return sorted(photos_data, key=lambda x: x[1])


##########################
# CORE FUNCTIONS
##########################


def insert_tag_photos(folder: os.path = None, proj_id=None, map=False) -> None:
    """Service API to add GPS Data to Photos using gpx file."""
    from .utils import to_gms, zipper
    from time import perf_counter

    start = perf_counter()
    gpx_project = TagGPX.query.filter_by(id=proj_id).first()

    track = get_track_data(folder, time_difference=gpx_project.time_difference)
    photos = get_photo_data(folder)
    data = []

    # Loop throw all photo collection one by one
    for photo in photos:
        # For each photo check if photo timestamp is less than the interval of
        # gpx points. If it is, create a new object joining both data information.
        for i, point in enumerate(track):
            diff = (point.time - photo.time).seconds
            if (diff > 0) and (diff < PROJECT_CONFIG["INTERVAL"]):
                data.append(PhotoTag(photo.name, photo.time, point.lat, point.lng))
                del track[: i - 1]

    for obj in data:
        file_ = f"{folder}/{obj.name}"
        img = piexif.load(file_)
        # convert coordinates
        img["GPS"][piexif.GPSIFD.GPSLongitude] = to_gms(obj.lng)
        img["GPS"][piexif.GPSIFD.GPSLatitude] = to_gms(obj.lat)
        # set coord ref based on original coord point
        img["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" if obj.lng > 0 else b"W"
        img["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b"N" if obj.lng > 0 else b"S"
        # write new exif information to photo
        _bytes = piexif.dump(img)
        piexif.insert(_bytes, file_)

    # Insert project information inside mapping service table
    project_name = gpx_project.project_name
    gpx_project.download_file = (
        f"{gpx_project.user.folder_gpx}/{project_name}/{project_name}.zip"
    )
    hash = secrets.token_hex(16)
    gpx_project.hash_url = hash

    db.session.add(gpx_project)
    db.session.commit()
    end = perf_counter()
    print(f"total time: {end - start}")

    if map:
        map_photos(folder, proj_id, service_type="gpx_mapping")
    else:
        # NEEDS TO BE REFRACTED
        download = Download()
        download.file_path = (
            f"{gpx_project.user.folder_gpx}/{project_name}/{project_name}.zip"
        )
        download.token = hash
        download.user_id = gpx_project.user_id
        download.project_name = gpx_project.project_name

        db.session.add(download)
        db.session.commit()
        zipper(gpx_project_id=proj_id, service_type="gpx")
