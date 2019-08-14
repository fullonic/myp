"""Run outside the flask app.

CMD python3 -m pytest ./services/myp/app/tests/functional/test_ui.py -s
"""

import os
from random import randrange
from time import sleep

import pytest
from selenium import webdriver


def log_in(driver, email="oficial@tester.tester", password="password"):
    """Log in helper function."""

    driver.get("http://localhost:5001/auth/login")
    field_email = driver.find_element_by_id("email")
    field_password = driver.find_element_by_id("password")
    sleep(3)
    field_submit = driver.find_element_by_id("submit")
    field_email.send_keys(email)
    field_password.send_keys(password)
    field_submit.click()
    return driver


@pytest.fixture()
def driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-Headless")
    driver = webdriver.Firefox(options=options)
    return driver


@pytest.mark.skip
def test_home_page(driver):
    driver.get("http://localhost:5001/")
    starting = driver.find_element_by_id("get_starting")
    assert starting.text == "Lets map!"


@pytest.mark.skip
def test_register_new_user(driver):
    driver.get("http://localhost:5001/auth/register")
    email = f"test{randrange(1, 500)}@test{randrange(1, 500)}.test"
    password = "password"
    field_email = driver.find_element_by_id("email")
    field_password = driver.find_element_by_id("password")
    field_confirm = driver.find_element_by_id("confirm")
    field_submit = driver.find_element_by_id("submit")
    field_email.send_keys(email)
    field_password.send_keys(password)
    field_confirm.send_keys(password)
    driver.implicitly_wait(1)
    field_submit.click()
    driver.implicitly_wait(1)
    assert "You have been successfully registered, please log in." in driver.page_source
    driver = log_in(driver, email, password)
    driver.implicitly_wait(2)
    assert "You have been successfully logged in." in driver.page_source


@pytest.mark.skip
def test_map_by_track(driver):
    driver = log_in(driver)
    root = "/home/somnium/Desktop/Projects/myp_project/services/myp/app/tests"
    driver.get("http://localhost:5001/map_by_track")
    name_field = driver.find_element_by_id("project_name")
    photos_field = driver.find_element_by_id("photos")
    track_field = driver.find_element_by_id("track")
    submit_field = driver.find_element_by_id("submitBtnGPX")
    name_field.send_keys("new_test")
    photos_field.send_keys(f"{root}/data/by_tag/gpx4.jpg")
    track_field.send_keys(f"{root}/data/track.gpx")
    submit_field.click()
