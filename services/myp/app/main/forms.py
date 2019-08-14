"""Projects Forms."""

from wtforms import StringField, MultipleFileField, SelectField, FileField, BooleanField

from wtforms.validators import DataRequired
from flask_wtf import FlaskForm as Form


#########################
# Authentication
class RegistrationForm(Form):
    """User register."""

    email = StringField("Your email", validators=[DataRequired()])


class ProjectForm(Form):
    """Basic Project Form."""

    files = MultipleFileField(
        label="Upload your files", id="upload", validators=[DataRequired()]
    )
    project_name = StringField("Project name", validators=[DataRequired()])
    color = SelectField(
        "color",
        validators=[DataRequired()],
        choices=[
            ("Blue", "Blue"),
            ("Red", "Red"),
            ("Purple", "Purple"),
            ("Orange", "Orange"),
            ("Green", "Green"),
        ],
    )
    tiles = SelectField(
        "tiles",
        validators=[DataRequired()],
        choices=[
            ("OpenStreetMap", "OSM"),
            ("CartoDB positron", "CartoDB Positron"),
            ("CartoDB dark_matter", "CartoDB Dark Matter"),
            ("Stamen Terrain", "Stamen Terrain"),
            ("Stamen Toner", "Stamen Toner"),
            ("Stamen Watercolor", "Stamen Watercolor"),
        ],
    )


class MapByGPXForm(Form):
    """Form for tag photos by gpx file."""

    project_name = StringField("Project name", validators=[DataRequired()])
    photos = MultipleFileField(
        label="Upload your photos", id="photos", validators=[DataRequired()]
    )
    track = FileField(
        label="Upload your track file", id="track", validators=[DataRequired()]
    )
    time_difference = StringField("Project name", validators=[DataRequired()])
    mapping = BooleanField(
        label="Would like to map your photos? ", id="map-or-not",
    )
