"""App core utilities for data processing."""

import os
import shutil
import json
import random
from datetime import datetime
from math import floor
from zipfile import ZipFile
from typing import Tuple, Iterable
from glob import glob

import folium
from flask import flash, session, current_app
from werkzeug.utils import secure_filename
import piexif

from app import db
from app.auth.models import User
from app.main.models import Mapping, TagGPX


ALLOWED_PHOTO = set(["png", "jpg", "jpeg", "gif", "tiff"])
ALLOWED_TRACK_FILE = set(["gpx", "kml"])
collections = []


##########################
# HELPER FUNCTIONS
##########################


def allowed_photo_file(filename):
    """Check function to validate photo extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PHOTO


def allowed_track_file(filename):
    """Check function to validate track file extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_TRACK_FILE


def to_degrees(gps_tag: Tuple[str]) -> float:
    """Convert coordinates from Degrees, Minutes, Seconds Decimal Degrees."""
    d, m, s = gps_tag
    return d[0] + (m[0] / 60) + (s[0] / 10000 / 3600)


def to_gms(dm: float) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """Convert coordinates from Decimal Degrees to Degrees, Minutes, Seconds."""
    # dm = 42.063106
    d = floor(dm)
    d
    _m = dm % 1 * 60
    m = floor(_m)
    m
    s = floor(_m % 1 * 60 * 10000)
    floor(s * 10000)
    return ((d, 1), (m, 1), (s, 10000))


def to_datetime(datetime_: str) -> datetime:
    """Convert exif.datetime string to python datetime with tzinfo."""
    dt = datetime.strptime(datetime_, "%Y:%m:%d %H:%M:%S")
    return dt.replace(tzinfo=None)


##########################
# LEGACY FUNCTIONS TO BE USED WITH GUEST USERS
##########################


def process_files(files: Iterable, gallery_folder: str, project_folder: os.path):
    """Get all uploads files and extract all meta data."""
    for file in files:
        if file and allowed_photo_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(gallery_folder, filename))
            get_gps_exif(os.path.join(gallery_folder, filename), filename)
            os.remove(os.path.join(gallery_folder, filename))
    flash("File(s) successfully uploaded", "info")
    # Save everything in a geojson file
    _file = to_geojson(collections, project_folder)
    # Move geojson file to map creation directory
    # Delete photo directory
    # Add DB row with information about user request, geojson file name, email
    return _file
    # Generate map


def get_gps_exif(file_path: os.path, name: str):
    """Grab the GPS information from photography if exists.

    # TODO:
    - It needs a list of photos without GPS
    - Ask to user if wants manually insert the data for each photo [MISSING SERVICE]
    """
    if current_app.config["TESTING"]:
        project_name = "testing"
    else:
        project_name = session["project_name"]
    img = piexif.load(file_path)
    try:
        lat = to_degrees(img["GPS"][piexif.GPSIFD.GPSLatitude])
        lng = to_degrees(img["GPS"][piexif.GPSIFD.GPSLongitude])
        dt = to_datetime(img["0th"][piexif.ImageIFD.DateTime].decode())
        date = str(dt.date())
        time_ = str(dt.time())
        to_json(project_name, lat, lng, name, date, time_)
        if current_app.config["TESTING"]:
            return (project_name, lat, lng, name, date, time_)
    except AttributeError:
        print(f"Photo{name} doesn't contains GPS DATA")  # NOTE: Needs to be logged


def to_json(
    project_name: str, lat: float, lng: float, name: str, date: str, time_: str
):
    """Turn data into json format."""
    collections.append(
        {
            "geometry": {"type": "Point", "coordinates": [lng, lat]},
            "type": "Feature",
            "properties": {
                "photo_location": os.path.join(f"photos_{project_name}", name),
                "date": date,
                "time_": time_,
            },
        }
    )


def to_geojson(collections: list, project_folder: os.path) -> os.path:
    """Create a geojson file with all photography data."""
    _file = os.path.join(
        current_app.config["GEOJSON_FOLDER"], f"{project_folder}.geojson"
    )
    with open(_file, "w") as f:
        json.dump({"type": "FeatureCollection", "features": collections}, f)
    return _file


def zip_folder(zip_file, project_name, service_type=None, gallery_folder=None):
    """Generate a zip file to be send to the user with folder structure."""
    # Location of zip to be send

    # Create photos folder
    photos = os.path.join(session["gallery_folder"], f"photos_{project_name}")
    try:
        os.mkdir(photos)
    except Exception as e:
        print(f"Error photos {e}")  # NOTE: Needs to be logged

    # Set root base dir
    origin = os.getcwd()
    # Zip photos folder and html map
    if service_type == "mapping":
        with ZipFile(zip_file, "w") as zip:
            os.chdir(session["gallery_folder"])
            zip.write(f"photos_{project_name}")
            zip.write(f"{session['html_file']}")
            os.chdir(origin)

        return f"{session['project_folder']}.zip"
    else:
        pass


def generate_map(file_path, project_name):
    """Create final map with geo tagged photos."""
    map = folium.Map(tiles=session["tiles"], location=[41, 2], zoom_start=8)
    # Open json file
    with open(file_path) as f:
        _file = json.load(f)

    for i in range(len(_file["features"])):
        lng, lat = _file["features"][i]["geometry"]["coordinates"]
        # date = _file["features"][i]["properties"]["date"]
        # time_ = _file["features"][i]["properties"]["time_"]
        photo = _file["features"][i]["properties"]["photo_location"]

        # Create Icon
        photo_location = f"<a href='{photo}' target='_blank'><img src='{photo}' height='50' width='50'></a>"  # noqa
        popup = folium.Popup(html=photo_location)
        # folium.()
        folium.CircleMarker(
            [lat, lng],
            popup=popup,
            radius=6,
            fill=True,
            fill_opacity=1,
            color=session["color"],
            class_name="circle",
        ).add_to(map)

    map_name = f"{project_name.split('_')[1]}.html"
    map.save(os.path.join(f"{session['gallery_folder']}", map_name))
    os.remove(file_path)
    return map_name


def show_map():
    """Create a show map to give the user the ability to choose some map styling."""
    map = folium.Map([41, 4], zoom_start=6, tiles=None)
    folium.TileLayer("openstreetmap", name="OSM").add_to(map)
    folium.TileLayer("CartoDB positron", name="CartoDB Positron").add_to(map)
    folium.TileLayer("CartoDB dark_matter", name="CartoDB Dark Matter").add_to(map)
    folium.TileLayer("Stamen Terrain", name="Stamen Terrain").add_to(map)
    folium.TileLayer("Stamen Toner", name="Stamen Toner").add_to(map)
    folium.TileLayer("Stamen Watercolor", name="Stamen Watercolor").add_to(map)
    colors = "blue purple red green orange".split(" ")
    for i, color in enumerate(colors):
        folium.CircleMarker(
            [41 + i, 4 - i],
            popup=f"I'm {color}",
            color=color,
            radius=6,
            fill=True,
            fill_opacity=1,
        ).add_to(map)
        i += i * random.random() * 2

    folium.LayerControl().add_to(map)
    map.save("app/main/templates/main/show_map.html")


def zipper(mapping_project_id=None, gpx_project_id=None, service_type=None):
    """Generate a zip file to be send to the user with folder structure."""
    origin = os.getcwd()

    def service_gpx(origin, gpx_project_id, _):
        project = TagGPX.query.filter_by(id=gpx_project_id).first()
        zip_file = project.download_file
        gallery_folder = os.path.dirname(project.download_file)
        os.chdir(gallery_folder)
        files = glob("./*")
        with ZipFile(zip_file, "w") as zip:
            for file in files:
                zip.write(file)
        # return gallery_folder

    def service_mapping(origin, _, mapping_project_id, type_=None):
        project = Mapping.query.filter_by(id=mapping_project_id).first()
        zip_file = project.download_file.split(".")[0]
        base = os.path.dirname(zip_file)
        gallery_folder = f"{base}/photos_{project.project_name}"
        os.mkdir(gallery_folder)
        if not type_:
            source = f"{project.user.folder_mapping}/{project.project_name}/delivery"
            zip_file = f"{source}/{project.project_name}"
            shutil.make_archive(zip_file, "zip", source)

        else:
            source = os.listdir(f"{project.user.folder_gpx}/{project.project_name}/")
            destination = f"{base}/photos_{project.project_name}"
            for file in source:
                if file.endswith(".jpg"):
                    # Move photos to mapping delivery folder
                    shutil.move(file, destination)
            shutil.make_archive(zip_file, "zip", base)

    def service_gpx_mapping(origin, gpx_project_id, mapping_project_id):
        # CREATE ZIP FOLDER WITH TAGGED PHOTOS
        service_gpx(origin, gpx_project_id, None)
        # ZIP MAP AND PHOTO GALLERY FOLDER
        service_mapping(origin, None, mapping_project_id, type_="mixed")

    service = {
        "gpx": service_gpx,
        "gpx_mapping": service_gpx_mapping,
        "mapping": service_mapping,
    }
    service[service_type](origin, gpx_project_id, mapping_project_id)
