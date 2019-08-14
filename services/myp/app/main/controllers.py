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
)

from flask_login import current_user, login_required
from werkzeug.utils import secure_filename


from app import db
from .forms import ProjectForm, MapByGPXForm
from .models import TagGPX, Mapping
from ..auth.models import User
from .utilities.utils import (
    zip_folder,
    process_files,
    generate_map,
    allowed_photo_file,
    allowed_track_file,
)
from .utilities.service_by_gpx import insert_tag_photos

main_blueprint = Blueprint(
    "main",
    __name__,
    template_folder="./templates/main",
    static_folder="./static",
    url_prefix="/",
)

##########################
# APP PAGES
##########################


@main_blueprint.route("/", methods=["POST", "GET"])
@main_blueprint.route("/index", methods=["POST", "GET"])
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


@main_blueprint.route("/create_map", methods=["POST", "GET"])
def create_map():
    """Create basic project landing page."""
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
                flash("No file part")
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


# MAP BY GPX FILE
@main_blueprint.route("/map_by_track", methods=["POST", "GET"])
@login_required
def map_by_track():
    """Insert tags using gpx file service."""
    form = MapByGPXForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # Insert new project data into DB table
            project = TagGPX()
            project.project_name = request.form["project_name"]
            project.email = current_user.email
            project.time_difference = int(request.form["time_difference"])
            project.user_id = current_user.id
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
                map = Mapping()
                map.project_name = project.project_name
                map.user_id = project.user_id
                project.map = True
                map.create_folders(project.project_name)
                db.session.add(project)
                db.session.add(map)
                db.session.commit()

            # Insert gpx information into photos
            insert_tag_photos(folder, proj_id=project.id, map=project.map)
            return redirect(url_for("main.map_by_track", token="FUNNY"))
    return render_template("services/map_by_track.html", form=form, token="NONE")


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


# @main_blueprint.route("/get_file/<token>", methods=["GET"])
# def get_file(token):
#     """Send zip file to user for downloading."""
#     s = Serializer(current_app.config["SECRET_KEY"])
#     try:
#         user_id = s.loads(token)["user_id"]
#     except Exception() as e:
#         print(e)  # NOTE:  Needs to be logged.
#         return "None"
#     user = User.query.get(user_id)
#     if user:
#         # Do things with registered users
#         pass
#     file_root = f"{os.getcwd()}/{current_app.config['DELIVERY_FOLDER'][1:]}"
#     return send_from_directory(file_root, session["zip_file"], as_attachment=True)
@main_blueprint.route("/get_file/<token>/", methods=["GET", "POST"])
def get_file(token):
    """Send zip file to user for downloading."""
    if request.method == "POST":
        project = TagGPX.query.filter_by(project_name=token).first()

        return dict(status="success", message=project.)
    print("TOKEN", token)
    print("project", project)
    return send_from_directory(os.path.dirname(project.download_file),
                               os.path.basename(project.download_file),
                               as_attachment=True)
