"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
# https://flask.palletsprojects.com/en/2.0.x/testing/
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
# https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1

from pathlib import Path
import os
import pytest
from bs4 import BeautifulSoup
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app


def test_flask_app_creation(app):
    """Tests that the fixture for creating the Flask web app object returns a Flask object for `nolcat.app`."""
    assert repr(app) == "<Flask 'nolcat.app'>"


def test_flask_client_creation(client):
    """Tests that the fixture for creating the Flask client returned a FlaskClient object for `nolcat.app`."""
    assert repr(client) == "<FlaskClient <Flask 'nolcat.app'>>"


def test_GET_request_for_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    
    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'templates', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_404_page(client):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistent_page = client.get('/404')
    with open(Path(os.getcwd(), 'nolcat', 'templates', '404.html'), 'br') as HTML_file:
        # Because the only Jinja markup on this page is a link to the homepage, replacing that Jinja with the homepage route and removing the Windows-exclusive carriage feed from the HTML file make it identical to the data returned from the GET request
        HTML_markup = HTML_file.read().replace(b"\r", b"")
        HTML_markup = HTML_markup.replace(b"{{ url_for(\'homepage\') }}", b"/")
    assert nonexistent_page.status == "404 NOT FOUND" and nonexistent_page.data == HTML_markup


def test_loading_data_into_relation(app, session, vendors_relation):
    """Tests loading data into and querying data from a relation.
    
    This test takes a dataframe from a fixture and loads it into a relation, then performs a `SELECT *` query on that same relation to confirm that the database and program are connected to allow CRUD operations.
    """
    print(f"`vendors_relation`:\n{vendors_relation}")
    vendors_relation.to_sql(
        name='vendors',
        con=session,
        #ToDo: `if_exists='replace',` was used to remove the existing data and replace it with the data from the fixture, ensuring no PK duplication and PK-FK matching problems would come out of adding the test data to the existing production data, with a rollback at the end of the test restoring the original data. The table dropping that causes, however, creates PK-FK integrity problems that cause the database to return an error; how should the situation be handled?
        if_exists='append',
        chunksize=1000,
        index=True,
        index_label='vendor_ID',
    )

    retrieved_vendors_data = pd.read_sql(
        sql="SELECT * FROM vendors;",
        con=session,
        index_col='vendor_ID',
    )
    print(f"`retrieved_vendors_data`:\n{retrieved_vendors_data}")

    pd.assert_frame_equal(vendors_relation, retrieved_vendors_data)


def test_loading_connected_data_into_other_relation(app, session, statisticsSources_relation):
    """Tests loading data into a second relation connected with foreign keys and performing a joined query.

    This test uses second dataframe to load data into a relation that has a foreign key field that corresponds to the primary keys of the relation loaded with data in `test_loading_data_into_relation`, then tests that the data load and the primary key-foreign key connection worked by performing a `JOIN` query and comparing it to a manually constructed dataframe containing that same data.
    """
    print(f"`statisticsSources_relation`:\n{statisticsSources_relation}")
    statisticsSources_relation.to_sql(
        name='statisticsSources',
        con=session,
        if_exists='append',  #ToDo: See above about handling databases and fixtures
        chunksize=1000,
        index=True,
        index_label='statistics_source_ID',
    )

    retrieved_data = pd.read_sql(
        sql="SELECT statisticsSources.statistics_source_ID, statisticsSources.statistics_source_name, statisticsSources.statistics_source_vendor_code, vendors.vendor_name, vendors.alma_vendor_code FROM statisticsSources JOIN vendors ON statisticsSources.vendor_ID=vendors.vendor_ID;",
        con=session,
        index_col='statisticsSources.statistics_source_ID'  # Each stats source appears only once, so the PKs can still be used--remember that pandas doesn't have a problem with duplication in the index
    )
    print(f"`retrieved_JOIN_query_data`:\n{retrieved_data}")

    expected_output_data = pd.DataFrame(
        [
            ["ProQuest", None, "ProQuest", None],
            ["EBSCOhost", None, "EBSCO", None],
            ["Gale Cengage Learning", None, "Gale", None],
            ["iG Library/Business Expert Press (BEP)", None, "iG Publishing/BEP", None],
            ["DemographicsNow", None, "Gale", None],
            ["Ebook Central", None, "ProQuest", None],
            ["Peterson's Career Prep", None, "Gale", None],
            ["Peterson's Test Prep", None, "Gale", None],
            ["Peterson's Prep", None, "Gale", None],
            ["Pivot", None, "ProQuest", None],
            ["Ulrichsweb", None, "ProQuest", None],
        ],
        columns=["statistics_source_name", "statistics_source_retrieval_code", "vendor_name", "alma_vendor_code"]
    )
    expected_output_data.index.name = "statistics_source_ID"

    pd.assert_frame_equal(retrieved_data, expected_output_data)