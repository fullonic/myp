"""Main app controllers.

# TODO:
- Fix Drag and Drop
"""


import os
import shutil
from random import randrange

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    current_app,
    send_from_directory,
    url_for,
    get_flashed_messages,
)

from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from flask_sqlalchemy import get_debug_queries

from app import db, cache
from .forms import ProjectForm, MapByGPXForm
from .models import TagGPX, Mapping, Download
from ..auth.models import User
from .utilities.utils import (
    zip_folder,
    process_files,
    generate_map,
    allowed_photo_file,
    allowed_track_file,
)
from .utilities.service_by_gpx import insert_tag_photos
from .utilities.service_mapping import map_photos
from ..main.main_tasks import map_it

main_blueprint = Blueprint(
    "main",
    __name__,
    template_folder="../templates/main",
    static_folder="./static",
    url_prefix="/",
)


##########################
# HELPER FUNCTIONS
##########################
@main_blueprint.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["MYP_SLOW_DB_QUERY_TIME"]:
            print(
                f"SLOWER {query.statement, query.parameters, query.duration, query.context}"
            )

    return response


def make_cache_keys(*args, **kwargs):
    """Cache key: only cache functions/views based on key_prefix."""
    path = request.path
    args = str(object=hash(frozenset(request.args.items())))
    messages = str(object=hash(frozenset(get_flashed_messages())))
    return (path + args + messages).encode("utf-8")


##########################
# APP PAGES
##########################


@main_blueprint.route("/", methods=["POST", "GET"])
@main_blueprint.route("/index", methods=["POST", "GET"])
# @cache.cached(timeout=72, key_prefix="home")
def index():
    """Landing page."""
    return render_template("home.html")


@main_blueprint.route("/how_works")
def how_works():
    """Help page."""
    return render_template("how_works.html")


##########################
# SERVICES
##########################


# MAPPING
import asyncio  # noqa
import time  # noqa


async def save_files_async(folder, id_, photos):
    """Save files to disk."""
    for file in photos:
        # if file and allowed_photo_file(file.filename):
        # filename = secure_filename(file.filename)
        file.save(os.path.join(folder, file.filename))
        await asyncio.sleep(0.01)
    map_it.delay(folder, id_, service_type="mapping")


def save_files(folder, id_, photos):
    """Save files to disk."""
    for file in photos:
        if file and allowed_photo_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))


@main_blueprint.route("/mapping", methods=["POST", "GET"])
@login_required
def mapping():
    """MAP SERVICE."""
    form = ProjectForm()
    if request.method == "POST" and form.validate_on_submit():
        start = time.perf_counter()
        project = Mapping()
        name = request.form["project_name"]
        project.project_name = name
        project.color = request.form["color"]
        project.tiles = request.form["tiles"]
        project.user_id = current_user.id
        # SET UP PROJECT FOLDERS
        project.create_folders(name)
        project.download_file = (
            f"{project.user.folder_mapping}/{name}/delivery/{name}.zip"
        )

        """MISSING SAVE THE PHOTOS TO FOLDER"""
        photos = request.files.getlist("files")
        folder = f"{current_user.folder_mapping}/{name}/requests"
        # ADD PROJECT TO DBync(folder, project.id, photos))
        db.session.add(project)
        db.session.commit()

        save_files(folder, project.id, photos)
        if request.form.get("bg_job", None):
            # asyncio.run(save_files_async(folder, project.id, photos))
            map_it.delay(folder, project.id, service_type="mapping")
        else:
            map_it(folder, project.id, service_type="mapping")

        end = time.perf_counter()
        print(f"total time: {end-start}")
        # map_photos(folder, project.id, ser5001vice_type="mapping")
    return render_template("services/mapping.html", form=form)


# MAP BY GPX FILE
@main_blueprint.route("/map_by_track", methods=["POST", "GET"])
@login_required
def map_by_track():
    """Insert tags using gpx file service."""
    form = MapByGPXForm()
    styling_form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # Insert new project data into DB table
            project = TagGPX()
            project.project_name = request.form["project_name"]
            project.email = current_user.email
            project.user_id = current_user.id
            half_hour = request.form.get("half_hour", 0)
            project.set_time_difference(request.form["time_difference"], int(half_hour))
            db.session.add(project)
            db.session.commit()

            # Save file to file system
            photos = request.files.getlist("photos")
            track_file = request.files.getlist("track")

            # NOTE: needs to handle same name project appending a number to avoid replacements
            folder = project.create_folder

            for file in track_file:
                if allowed_track_file(file.filename):
                    track_name = secure_filename(file.filename)
                    file.save(os.path.join(folder, track_name))
            for file in photos:
                if file and allowed_photo_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(folder, filename))
            mapping = request.form.get("mapping", None)

            if mapping:
                print("INSERTING MAP STYLING TABLE")
                map_ = Mapping()
                map_.project_name = project.project_name
                map_.user_id = project.user_id
                map_.tiles = session["tiles"]
                map_.color = session["color"]
                project.map = True  # Flag to decide how to build download url
                map_.create_folders(project.project_name)
                db.session.add(project)
                db.session.add(map_)
                db.session.commit()

            # Insert gpx information into photos
            insert_tag_photos(folder, proj_id=project.id, map=project.map)
            return redirect(url_for("main.map_by_track", token=""))
    return render_template(
        "services/map_by_track.html", styling_form=styling_form, form=form, token="NONE"
    )


@main_blueprint.route("/create_map", methods=["POST", "GET"])
def create_map():
    """Create basic map without be registered."""
    form = ProjectForm()
    try:
        user_id = current_user.id
    except AttributeError:
        user_id = session.get("user_id", randrange(10, 133))
    s = Serializer(current_app.config["SECRET_KEY"], 60 * 30)
    token = s.dumps({"user_id": user_id}).decode("utf-8")
    session["token"] = token
    if request.method == "POST":
        if form.validate_on_submit() or current_app.config["TESTING"]:
            # check if the post request has the files part
            if "files" not in request.files:
                flash("You missed add the files")
                return redirect(request.url)
            # Get user Form Data
            files = request.files.getlist("files")
            project_name = request.form["project_name"]
            session["color"] = request.form["color"]
            session["tiles"] = request.form["tiles"]

            # Set up session data
            session["project_name"] = project_name
            session["user"] = user_id
            project_folder = f"{user_id}_{project_name}"
            session["project_folder"] = project_folder
            gallery_folder = os.path.join(
                current_app.config["DELIVERY_FOLDER"], project_folder
            )
            session["gallery_folder"] = gallery_folder

            try:
                os.mkdir(gallery_folder)
            except FileExistsError:
                pass
            file_path = process_files(files, gallery_folder, project_folder)
            session["project_folder"] = project_folder
            session["html_file"] = generate_map(file_path, project_folder)

            # Compress folder
            zip_file = os.path.join(
                current_app.config["DELIVERY_FOLDER"],
                f"{session['project_folder']}.zip",
            )
            session["zip_file"] = zip_folder(zip_file, project_name, "mapping")
            # remove starter folder
            shutil.rmtree(gallery_folder)
            return redirect(url_for("main.create_map"))
    return render_template("services/upload_form.html", form=form)


##########################
# HELPERS ROUTES
##########################


@main_blueprint.route("/map")
def map():
    """Show user created map.

    # NOTE: will be deprecated
    """
    project_folder = session.get("project_folder")
    map_file = f"/maps/{project_folder}.html"
    return render_template(map_file)


@main_blueprint.route("/show_map", methods=["GET"])
def show_map():
    """Show map to test configurations."""
    return render_template("show_map.html")


@main_blueprint.route("/tiles/<tiles>/", methods=["GET"])
@cache.cached(timeout=7200, key_prefix=make_cache_keys)
def tiles(tiles):
    """Render map tiles examples based in user form input."""
    return render_template(f"/tiles/{tiles}.html")


#  FUTURE REST API ROUTES
@main_blueprint.route("/get_tiles/<tiles>/", methods=["POST"])
@cache.cached(timeout=7200, key_prefix=make_cache_keys)
def get_tiles(tiles):
    """Get user tiles key from form and redirect to tiles route."""
    options = {
        "OpenStreetMap": "osm",
        "CartoDB positron": "positron",
        "CartoDB dark_matter": "dark_matter",
        "Stamen Terrain": "stamen_terrain",
        "Stamen Toner": "stamen_toner",
        "Stamen Watercolor": "stamen_watercolor",
    }
    # return a url for selected tiles map provider
    return {"url": url_for("main.tiles", tiles=options[tiles])}


@main_blueprint.route("/setup_map_style/<tiles>&<color>/", methods=["POST"])
def setup_map_style(tiles, color):
    """Get user styling and add to session."""
    session["tiles"] = tiles
    session["color"] = color
    print(tiles, color)
    return dict(stats="success", msg="OK")


@main_blueprint.route("/get_file/<token>/", methods=["GET", "POST"])
def get_file(token):
    """Send zip file to user for downloading."""
    if request.method == "POST":
        project = Download.query.filter_by(project_name=token).first()
        return dict(status="success", url=project.token)
    project = Download.query.filter_by(token=token).first()

    print(project)
    print(project.file_path)
    return send_from_directory(
        os.path.dirname(project.file_path),
        os.path.basename(project.file_path),
        as_attachment=True,
    )


@main_blueprint.route("/one_time_url/<token>", methods=["GET"])
def one_time_url(token):
    """Send zip file to user for downloading."""
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        user_id = s.loads(token)["user_id"]
    except Exception() as e:
        print(e)  # NOTE:  Needs to be logged.
        return "None"
    user = User.query.get(user_id)
    if user:
        # Do things with registered users
        pass
    file_root = f"{os.getcwd()}/{current_app.config['DELIVERY_FOLDER'][1:]}"
    return send_from_directory(file_root, session["zip_file"], as_attachment=True)
