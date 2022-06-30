"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
# https://flask.palletsprojects.com/en/2.0.x/testing/
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
# https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1

from pathlib import Path
import os
import pytest
from bs4 import BeautifulSoup

from conftest import app


def test_flask_client_creation(app):
    """Tests that the fixture for creating the Flask web app client returned a FlaskClient object for `nolcat.app`."""
    assert repr(app) == "<FlaskClient <Flask 'nolcat.app'>>"


def test_homepage(app):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    homepage = app.get('/')
    with open(Path(os.getcwd(), 'nolcat', 'templates', 'index.html'), 'r') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = soup.head.title
        HTML_file_page_title = soup.body.h1
    print(f"`homepage.data` is {homepage.data} of type {repr(type(homepage.data))}")
    with homepage.data as GET_response:
        soup = BeautifulSoup(GET_response, 'lxml')
        GET_response_title = soup.head.title
        GET_response_page_title = soup.body.h1
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_404_page(app):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistent_page = app.get('/404')
    with open(Path(os.getcwd(), 'nolcat', 'templates', '404.html'), 'br') as HTML_file:
        # Because the only Jinja markup on this page is a link to the homepage, replacing that Jinja with the homepage route and removing the Windows-exclusive carriage feed from the HTML file make it identical to the data returned from the GET request
        HTML_markup = HTML_file.read().replace(b"\r", b"")
        HTML_markup = HTML_markup.replace(b"{{ url_for(\'homepage\') }}", b"/")
    assert nonexistent_page.status == "404 NOT FOUND" and nonexistent_page.data == HTML_markup