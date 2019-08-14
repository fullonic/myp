import os

import pytest

from app import create_app
from app.main.utilities.utils import get_gps_exif, to_gms, to_degrees

ROOT = os.getcwd()
TEST_FOLDER = os.path.join(ROOT, "app/tests/data")


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config.from_object("app.config.TestConfig")

    # Set up flask client testing
    testing_client = app.test_client()
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield testing_client  # this is where the testing happens!
    ctx.pop()


@pytest.mark.skip
def test_get_gps_exif(client):
    """
    GIVEN core functionality
    WHEN extract gps tags when present
    THEN check if data valid
    """

    img = get_gps_exif(f"{TEST_FOLDER}/mapping/mapping.jpg", "testing")
    assert isinstance(img[1], float)
    assert isinstance(img[2], float)
    assert isinstance(img[0], str)


@pytest.mark.skip
def test_to_gm():
    """
    GIVEN core functionality
    WHEN extract to_gm is called to convert coords
    THEN check if return a dms coordinate point in tuple(tuple) format
    """
    result = ((2, 1), (27, 1), (23, 10000))
    test = to_gms(2.45656)

    assert test == result


@pytest.mark.skip
def test_to_degres():
    """
    GIVEN core functionality
    WHEN extract to_gm is called to convert coords
    THEN check if returns a float number
    """
    result = 2.450000638888889
    test = to_degrees(((2, 1), (27, 1), (23, 10000)))

    assert test == result
