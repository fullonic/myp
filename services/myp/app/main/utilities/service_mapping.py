"""Create Service for mapping geo tagged photos."""

import os
import json
import secrets
import operator
from math import floor
from typing import Any
from glob import glob

import folium
from folium.plugins import MarkerCluster
import piexif

from app import db
from app.main.models import TagGPX, Mapping, Download
from .utils import to_degrees, to_datetime, zipper


def to_json(
    project_name: str,
    lat: float,
    lng: float,
    name: str,
    alt: float,
    date: str,
    time_: str,
):
    """Turn data into json format."""
    return {
        "geometry": {"type": "Point", "coordinates": [lng, lat]},
        "type": "Feature",
        "properties": {
            "photo_location": os.path.join(f"photos_{project_name}", name),
            "alt": alt,
            "date": date,
            "time_": time_,
        },
    }


def to_geojson(collections: list, _file: os.path) -> os.path:
    """Create a geojson file with all photography data."""
    with open(_file, "w") as f:
        json.dump({"type": "FeatureCollection", "features": collections}, f)


def map_photos(gallery_folder: os.path, project_id: int, service_type: str = "mapping"):
    """Create map from list of tagged photos.

    Generate a map with photos tagged from tag by gpx service.
    """
    # NOTE: needs to improve glob list files creation to avoid list compression
    photos = glob(f"{gallery_folder}/*")
    photos = [photo for photo in photos if photo.split(".")[-1] != "gpx"]

    if service_type == "gpx_mapping":
        project = TagGPX.query.filter_by(id=project_id).one()
    else:
        project = Mapping.query.filter_by(id=project_id).one()

    data = []
    project_name = project.project_name
    for photo in photos:
        img = piexif.load(photo)
        name = os.path.basename(photo)

        try:
            print("GETTING DATA FROM PHOTOS")
            # Extract and convert exif data
            lat = to_degrees(img["GPS"][piexif.GPSIFD.GPSLatitude])
            lng = to_degrees(img["GPS"][piexif.GPSIFD.GPSLongitude])
            dt = to_datetime(img["0th"][piexif.ImageIFD.DateTime].decode())
            date = str(dt.date())
            time_ = str(dt.time())
            # get altitude, Meters,Decimal
            m, d = img["GPS"][piexif.GPSIFD.GPSAltitude]
            alt = operator.truediv(m, d)
            data.append(to_json(project_name, lat, lng, name, floor(alt), date, time_))
        except Exception as e:
            print(e) # NOTE: Needs to be logged
            print(f"Photo{name} doesn't contains GPS DATA") 
    geojson_file = (
        f"{project.user.folder_mapping}/{project_name}/geo_files/{project_name}.geojson"
    )
    # CREATE GEOJSON FILE
    to_geojson(data, geojson_file)
    # GENERATE MAP
    generate_map(geojson_file, project_name, project.user_id, project_id, service_type)


def generate_map(
    file_path: os.path,
    project_name: str,
    user_id: int,
    project_id: int,
    service_type: str = "mapping",
) -> Any:
    """Create final map with geo tagged photos."""
    # Open json file
    with open(file_path) as f:
        _file = json.load(f)

    # create map zoom point

    try:
        lng, lat = _file["features"][0]["geometry"]["coordinates"]
    except IndexError:
        lng, lat = [3, 43]

    # Get info to generate map
    map_project = Mapping.query.filter_by(
        project_name=project_name, user_id=user_id
    ).first()

    map_ = folium.Map(tiles=map_project.tiles, location=[lat, lng], zoom_start=6)

    mc = MarkerCluster()

    for i in range(len(_file["features"])):
        lng, lat = _file["features"][i]["geometry"]["coordinates"]

        photo = _file["features"][i]["properties"]["photo_location"]

        # Create Icon
        photo_location = f"<a href='{photo}' target='_blank'><img src='{photo}' height='250' width='250'></a>"  # noqa
        photo_location += f"""<p style="text-align:center;">
        alt. {_file["features"][i]["properties"]["alt"]} mts |
        {_file["features"][i]["properties"]["date"]}</p>"""
        popup = folium.Popup(html=photo_location)
        # folium.()
        folium.CircleMarker(
            [lat, lng],
            popup=popup,
            radius=6,
            fill=True,
            fill_opacity=1,
            color=map_project.color,
            class_name="circle",
        ).add_to(mc)

    mc.add_to(map_)

    map_.save(
        f"{map_project.user.folder_mapping}/{project_name}/delivery/{project_name}.html"
    )
    # REMOVE GEOJSON FILE AFTER CREATE MAP
    # os.remove(file_path)
    map_project.download_file = (
        f"{map_project.user.folder_mapping}/{project_name}/delivery/{project_name}.zip"
    )
    db.session.add(map_project)
    db.session.commit()
    return prepare_to_download(service_type, project_name, project_id, map_project)


def prepare_to_download(service_type, project_name, project_id, map_project):
    # NEEDS TO BE REFRACTED
    download = Download()
    download.file_path = (
        f"{map_project.user.folder_mapping}/{project_name}/delivery/{project_name}.zip"
    )
    download.token = secrets.token_hex(16)
    download.user_id = map_project.user_id
    download.project_name = map_project.project_name
    # Ensure unique and commit changes into db
    download.ensure_unique_token()

    if service_type == "mapping":
        return zipper(mapping_project_id=map_project.id, service_type="mapping")
    elif service_type == "gpx_mapping":

        return zipper(
            mapping_project_id=map_project.id,
            gpx_project_id=project_id,
            service_type="gpx_mapping",
        )
