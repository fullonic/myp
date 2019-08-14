import os
import shutil
from glob import glob
from random import randrange

import pytest
import piexif
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import create_app, db
from app.auth.models import User
from app.main.utilities import utils


ROOT = os.getcwd()
TEST_FOLDER = os.path.join(ROOT, "app/tests/data")


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config.from_object("app.config.TestConfig")
    db.create_all()
    db.session.commit()

    # Set up flask client testing
    testing_client = app.test_client()
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield testing_client  # this is where the testing happens!
    ctx.pop()


##########################
# TEST APP PUBLIC ROUTES
##########################


@pytest.mark.skip
def test_static_files(client):
    """
    GIVEN a flask app
    WHEN the "/" is requested (GET)
    THEN check if the static files are loaded
    """

    response = client.get("/")
    assert response.status_code == 200
    assert b'src="/static/js/main.js"' in response.data
    assert b'href="/static/css/master.css"' in response.data


@pytest.mark.skip
def test_landing(client):
    """
    GIVEN a flask app
    WHEN the "/" is requested (GET)
    THEN check if the response is valid
    """

    response = client.get("/")

    assert response.status_code == 200
    assert b"Lets map!" in response.data
    assert b"How it works" in response.data


@pytest.mark.skip
def test_create_map(client):
    """
    GIVEN a flask app
    WHEN the "/create_map" is requested (GET)
    THEN check if the response is valid
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 100
    response = client.get("/create_map")
    assert response.status_code == 200
    assert b"Upload" in response.data


@pytest.mark.skip
def test_map_by_gpx(client):
    """
    GIVEN a flask app
    WHEN the "/map_by_track" is requested (POST)
    THEN check if the response is valid
    """

    # login

    test_email = "oficial@tester.tester"
    data = {"email": test_email, "password": "password"}
    client.post("auth/register", data=data, follow_redirects=True)
    response = client.post("auth/login", data=data, follow_redirects=True)
    # Get files to upload
    track = f"{TEST_FOLDER}/track.gpx"
    gallery = f"{TEST_FOLDER}/by_tag/gpx4.jpg"

    user_id = "testing_user"
    data = dict(
        project_name=user_id,
        photos=(open(gallery, "rb"), gallery),
        track=(open(track, "rb"), track),
    )
    response = client.post(
        "/map_by_track", data=data, content_type="multipart/form-data"
    )

    # follow_redirects=False in other to get 302
    assert response.status_code == 302

    # Check if GPS data was inserted

    test = os.path.join(ROOT, f"app/main/MYP/by_gpx/{user_id}/{user_id}")
    photo = glob(f"{test}/*.jpg")
    print("PHOTO", photo)
    img = piexif.load(photo[0])
    lat = utils.to_degrees(img["GPS"][piexif.GPSIFD.GPSLatitude])
    lng = utils.to_degrees(img["GPS"][piexif.GPSIFD.GPSLongitude])
    dt = utils.to_datetime(img["0th"][piexif.ImageIFD.DateTime].decode())
    date = str(dt.date())

    assert lat == 42.050001583333334
    assert lng == 2.516667638888889
    assert date == "2019-07-25"

    # Remove testing folder with all data
    shutil.rmtree(test)


@pytest.mark.skip
def test_photos_upload(client):
    """
    GIVEN a flask app
    WHEN the "/create_map" is requested (POST)
    THEN check if the response is valid
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 00

    gallery = f"{TEST_FOLDER}/mapping/mapping.jpg"
    data = {
        "project_name": "testing_user",
        "color": "red",
        "tiles": "openstreetmap",
        "files": (open(gallery, "rb"), gallery),
    }
    response = client.post(
        "/create_map",
        data=data,
        content_type="multipart/form-data",
        # follow_redirects=True,
    )
    assert response.status_code == 302


@pytest.mark.skip
def test_temporary_url(client):
    id_ = randrange(10, 133)
    with client.session_transaction() as sess:
        sess["user_id"] = id_
    gallery = f"{TEST_FOLDER}/mapping/mapping.jpg"
    # Create POST information
    data = {
        "project_name": "testing_user",
        "color": "red",
        "tiles": "openstreetmap",
        "files": (open(gallery, "rb"), gallery),
    }

    response = client.post(
        "/create_map",
        data=data,
        content_type="multipart/form-data",
        # follow_redirects=True,
    )

    assert response.status_code == 302

    with client.session_transaction() as sess:
        token = sess["token"]
    response = client.get(f"/get_file/{token}")
    s = Serializer("THISISONLYATEST")
    try:
        user_id = s.loads(token)["user_id"]
        s.loads(token)["project_name"] = "testing_user"
        name = s.loads(token)["project_name"]
        print(name)
    except:
        return None
    user = User.query.get(user_id)
    assert response.status_code == 200
    assert user.id == id_



@pytest.mark.skip
def test_create_map_from_gpx_tag(client):
    """
    GIVEN a flask app
    WHEN the "/create_map" is requested (POST)
    THEN check if the response is valid
    """
    pass

##################
# AUTHENTICATION TESTS


@pytest.fixture(scope="module")
def init_db():
    """DB SETUP."""
    # Create DB tables
    db.create_all()
    db.session.commit()
    yield db
    db.drop_all()


@pytest.mark.skip
def test_register_new_user(client, init_db):
    """
    GIVEN a new user
    WHEN the "/register" is called to create a new user (POST)
    THEN check if user was registered
    """

    test_email = "test@myp.zz"
    data = {"email": test_email, "password": "password", "confirm": "password"}
    response = client.post("auth/register", data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been successfully registered, please log in." in response.data
    user = User.query.filter_by(email=test_email).first()
    assert user.email == test_email
    init_db.session.delete(user)
    init_db.session.commit()


@pytest.mark.skip
def test_unique_email(client, init_db):
    """
    GIVEN a new user
    WHEN the "/register": create a new user with and the email already exist (POST)
    THEN check if no duplicate email is added to the database
    """
    test_email = "test@myp.zz"
    data = {"email": test_email, "password": "password", "confirm": "password"}
    user1 = client.post("auth/register", data=data, follow_redirects=True)

    assert b"You have been successfully registered, please log in." in user1.data
    user2 = client.post("auth/register", data=data, follow_redirects=True)

    assert b"User with that name already exists." in user2.data
    user = User.query.filter_by(email=test_email).first()
    init_db.session.delete(user)
    init_db.session.commit()


@pytest.mark.skip
def test_login_user(client, init_db):
    """
    GIVEN a login user
    WHEN "/login": checks the login validation system (POST)
    THEN checks if user is correctly authenticated
    """
    test_email = "test1@myp.zz"
    data = {"email": test_email, "password": "password", "confirm": "password"}
    response = client.post("auth/register", data=data, follow_redirects=True)

    response = client.post("auth/login", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been successfully logged in." in response.data

    # Clean up
    user = User.query.filter_by(email=test_email).first()
    init_db.session.delete(user)
    init_db.session.commit()


@pytest.mark.skip
def test_login_user_wrong_password(client, init_db):
    """
    GIVEN a login user
    WHEN "/login": checks for wrong password (POST)
    THEN checks if user is correctly authenticated
    """
    test_email = "test@myp.zz"
    data = {"email": test_email, "password": "password", "confirm": "password"}
    response = client.post("auth/register", data=data, follow_redirects=True)

    data["password"] = "pass"
    response = client.post("auth/login", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data

    # Clean up
    user = User.query.filter_by(email=test_email).first()
    init_db.session.delete(user)
    init_db.session.commit()
