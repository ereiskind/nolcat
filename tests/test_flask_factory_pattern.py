"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
# https://flask.palletsprojects.com/en/2.0.x/testing/
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
# https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1

from pathlib import Path
import os
import pytest
from bs4 import BeautifulSoup
import pandas as pd

from conftest import app, session
from database_seeding_fixtures import vendors_relation


def test_flask_client_creation(app):
    """Tests that the fixture for creating the Flask web app client returned a FlaskClient object for `nolcat.app`."""
    assert repr(app) == "<FlaskClient <Flask 'nolcat.app'>>"


def test_homepage(app):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    homepage = app.get('/')
    with open(Path(os.getcwd(), 'nolcat', 'templates', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_404_page(app):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistent_page = app.get('/404')
    with open(Path(os.getcwd(), 'nolcat', 'templates', '404.html'), 'br') as HTML_file:
        # Because the only Jinja markup on this page is a link to the homepage, replacing that Jinja with the homepage route and removing the Windows-exclusive carriage feed from the HTML file make it identical to the data returned from the GET request
        HTML_markup = HTML_file.read().replace(b"\r", b"")
        HTML_markup = HTML_markup.replace(b"{{ url_for(\'homepage\') }}", b"/")
    assert nonexistent_page.status == "404 NOT FOUND" and nonexistent_page.data == HTML_markup


def test_loading_data_into_relation(app, vendors_relation):
    """Tests loading data into and querying data from a relation.
    
    This test takes a dataframe from a fixture and loads it into a relation, then performs a `SELECT *` query on that same relation to confirm that the database and program are connected to allow CRUD operations.
    """
    print(f"`vendors_relation` is {vendors_relation}")
    vendors_relation.to_sql(
        name='vendors',
        con=session,
        if_exists='replace',  # This removes the existing data and replaces it with the data from the fixture, ensuring that PK duplication and PK-FK matching problems don't arise; the rollback at the end of the test restores the original data
        chunksize=1000,
        index=True,
        index_label='vendor_ID',
    )

    retrieved_vendors_data = pd.read_sql(
        sql="SELECT * FROM vendors;",
        con=session,
        index_col='vendor_ID',
    )
    print(f"`retrieved_vendors_data` is {retrieved_vendors_data}")

    pd.assert_frame_equal(vendors_relation, retrieved_vendors_data)


def test_loading_data_into_relation(engine, vendors_relation, statisticsSources_fixture):
    """Test using the engine to load and query data.  #ToDo: Change to use Flask-SQLAlchemy connection
    
    This is a basic integration test, determining if dataframes can be loaded into the database and if data can be queried out of the database, not a StatisticsSources method test. All of those method tests, however, require the database I/O to be working and the existence of data in the `statisticsSources` and `vendors` relations; this test checks the former and ensures the latter.
    """
    ###ToDo: Confirm that the imported fixture can be used as an argument directly
    #ToDo: vendors_relation.to_sql(
        # name='vendors',
        # con=engine,
        # if_exists='replace',  # This removes the existing data and replaces it with the data from the fixture, ensuring that PK duplication and PK-FK matching problems don't arise; the rollback at the end of the test restores the original data
        # chunksize=1000,
        # index=True,
        # index_label='Vendor_ID',
    #ToDo: )
    #ToDo: statisticsSources_fixture.to_sql(
        # name='statisticsSources',
        # con=engine,
        # if_exists='replace',
        # chunksize=1000,
        # index=True,
        # index_label='Statistics_Source_ID',
    #ToDo: )

    #ToDo: retrieved_vendors_data = pd.read_sql(
        # sql="SELECT * FROM vendors;",
        # con=engine,
        # index_col='Vendor_ID',
    #ToDo: )
    #ToDo: retrieved_statisticsSources_data = pd.read_sql(
        # sql="SELECT * FROM statisticsSources;",
        # con=engine,
        # index_col='Statistics_Source_ID',
    #ToDo: )

    #ToDo: assert_frame_equal(vendors_relation, retrieved_vendors_data) and assert_frame_equal(statisticsSources_fixture, retrieved_statisticsSources_data)
    pass


#ToDo: Test loading data with foreign keys into the database