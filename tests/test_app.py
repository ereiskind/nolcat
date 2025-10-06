"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Passing 2025-09-29 ##########

import pytest
from bs4 import BeautifulSoup
import sqlalchemy
import flask

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *

log = logging.getLogger(__name__)


#Section: Test Flask Factory Pattern
def test_flask_app_creation(app):
    """Tests that the fixture for creating the Flask web app object returns a Flask object for `nolcat.app`."""
    assert isinstance(app, flask.app.Flask)
    assert app.__dict__['name'] == 'nolcat.app'


def test_flask_client_creation(client):
    """Tests that the fixture for creating the Flask client returned a FlaskClient object for `nolcat.app`."""
    assert isinstance(client, flask.testing.FlaskClient)
    assert isinstance(client.__dict__['application'], flask.app.Flask)
    assert client.__dict__['application'].__dict__['name'] == 'nolcat.app'


def test_SQLAlchemy_engine_creation(engine):
    """Tests that the fixture for creating the SQLAlchemy engine returned an engine object for connecting to the NoLCAT database."""
    assert isinstance(engine, sqlalchemy.engine.base.Engine)
    assert isinstance(engine.__dict__['url'], sqlalchemy.engine.url.URL)
    assert str(engine.__dict__['url']) == f'mysql://{DATABASE_USERNAME}:***@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}'  # The `sqlalchemy.engine.url.URL` changes the password to `***` for stdout


def test_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    page = client.get('/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    
    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'templates' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_404_page(client):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistent_page = client.get('/404')
    GET_soup = BeautifulSoup(nonexistent_page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    
    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'templates' / '404.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert nonexistent_page.status == "404 NOT FOUND"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_download_file(client, path_to_sample_file):  #ToDo: If method for interacting with host workstation's file system can be established, add `default_download_folder`
    """Tests the route enabling file downloads."""
    page = client.get(
        f'/download/{path_to_sample_file}',
        follow_redirects=True,
    )
    #ToDo: If method for interacting with host workstation's file system can be established, `with Path(default_download_folder, path_to_sample_file.name) as file: downloaded_file = file.read()`

    assert page.status == "200 OK"
    assert page.history[0].status == "308 PERMANENT REDIRECT"
    assert page.headers.get('Content-Disposition') == f'attachment; filename={path_to_sample_file.name}'
    assert page.headers.get('Content-Type') == file_extensions_and_mimetypes()[path_to_sample_file.suffix]
    #ToDo: If method for interacting with host workstation's file system can be established, `assert path_to_sample_file.name in [file_name for file_name in default_download_folder.iterdir()]
    #ToDo: If method for interacting with host workstation's file system can be established,
    #if "bin" in path_to_sample_file.parts:
    #    with path_to_sample_file.open('rb') as file:
    #        assert file.read() == downloaded_file
    #else:
    #    with path_to_sample_file.open('rt') as file:
    #        assert file.read() == downloaded_file