"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
# https://flask.palletsprojects.com/en/2.0.x/testing/
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
# https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1

from pathlib import Path
import os
import pytest

from nolcat.app import create_app
from conftest import app


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


def test_flask_client_creation(flask_client):
    """Tests that the flask_client fixture creates a FlaskClient object for `nolcat.app`."""
    assert repr(flask_client) == "<FlaskClient <Flask 'nolcat.app'>>"


def test_flask_client_creation2(app):
    """Tests that the flask_client fixture creates a FlaskClient object for `nolcat.app`."""
    assert repr(app) == "<FlaskClient <Flask 'nolcat.app'>>"


def test_homepage(flask_client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    homepage = flask_client.get('/')
    HTML_file = open(Path(os.getcwd(), 'nolcat', 'templates', 'index.html'), 'rb')  # CWD is where the tests are being run (root for this suite)
    HTML_markup = HTML_file.read().replace(b"\r", b"")  # This removes the carriage return so the HTML file written on Windows matches the line feed-only Flask response
    HTML_file.close()
    #ToDo: HTML_markup shows the Jinja, data attribute shows what's rendered by Jinja--if necessary, find way to resolve
    assert homepage.status == "200 OK" and homepage.data == HTML_markup


def test_404_page(flask_client):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistant_page = flask_client.get('/404')
    HTML_file = open(Path(os.getcwd(), 'nolcat', 'templates', '404.html'), 'rb')
    HTML_markup = HTML_file.read().replace(b"\r", b"")
    HTML_file.close()
    HTML_markup = HTML_markup.replace(b"{{ url_for(\'homepage\') }}", b"/")  # This replaces the Jinja with what it renders to--this replacement is safe because it replaces the homepage function with the homepage/root route
    assert nonexistant_page.status == "404 NOT FOUND" and nonexistant_page.data == HTML_markup