"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Data in no relations ##########

from pathlib import Path
import os
import pytest
from bs4 import BeautifulSoup
import pandas as pd
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.app import first_new_PK_value


def test_flask_app_creation(app):
    """Tests that the fixture for creating the Flask web app object returns a Flask object for `nolcat.app`."""
    assert repr(app) == "<Flask 'nolcat.app'>"


def test_flask_client_creation(client):
    """Tests that the fixture for creating the Flask client returned a FlaskClient object for `nolcat.app`."""
    assert repr(client) == "<FlaskClient <Flask 'nolcat.app'>>"


def test_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    page = client.get('/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    
    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'templates', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_404_page(client):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistent_page = client.get('/404')
    with open(Path(os.getcwd(), 'nolcat', 'templates', '404.html'), 'br') as HTML_file:
        # Because the only Jinja markup on this page is a link to the homepage, replacing that Jinja with the homepage route and removing the Windows-exclusive carriage feed from the HTML file make it identical to the data returned from the GET request
        HTML_markup = HTML_file.read().replace(b"\r", b"")
        HTML_markup = HTML_markup.replace(b"{{ url_for(\'homepage\') }}", b"/")
    assert nonexistent_page.status == "404 NOT FOUND"
    assert nonexistent_page.data == HTML_markup


@pytest.mark.dependency()
def test_loading_data_into_relation(engine, vendors_relation):
    """Tests loading data into and querying data from a relation.
    
    This test takes a dataframe from a fixture and loads it into a relation, then performs a `SELECT *` query on that same relation to confirm that the database and program are connected to allow CRUD operations.
    """
    print(f"\n`vendors_relation` dataframe:\n{vendors_relation}")
    vendors_relation.to_sql(
        name='vendors',
        con=engine,
        if_exists='append',
        # `if_exists='replace',` raises the error `sqlalchemy.exc.IntegrityError: (MySQLdb.IntegrityError) (1217, 'Cannot delete or update a parent row: a foreign key constraint fails')`
        chunksize=1000,
        index_label='vendor_ID',
    )

    retrieved_vendors_data = pd.read_sql(
        sql="SELECT * FROM vendors;",
        con=engine,
        index_col='vendor_ID',
    )
    retrieved_vendors_data = retrieved_vendors_data.astype({
        "vendor_name": 'string',
        "alma_vendor_code": 'string',
    })
    print(f"`retrieved_vendors_data`:\n{retrieved_vendors_data}")

    assert_frame_equal(vendors_relation, retrieved_vendors_data)


@pytest.mark.dependency(depends=['test_loading_data_into_relation'])  # If the data load into the `vendors` relation fails, this test is skipped
def test_loading_connected_data_into_other_relation(engine, statisticsSources_relation):
    """Tests loading data into a second relation connected with foreign keys and performing a joined query.

    This test uses second dataframe to load data into a relation that has a foreign key field that corresponds to the primary keys of the relation loaded with data in `test_loading_data_into_relation`, then tests that the data load and the primary key-foreign key connection worked by performing a `JOIN` query and comparing it to a manually constructed dataframe containing that same data.
    """
    print(f"\n`statisticsSources_relation` dataframe:\n{statisticsSources_relation}")
    statisticsSources_relation.to_sql(
        name='statisticsSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='statistics_source_ID',
    )

    retrieved_data = pd.read_sql(
        sql="SELECT statisticsSources.statistics_source_ID, statisticsSources.statistics_source_name, statisticsSources.statistics_source_retrieval_code, vendors.vendor_name, vendors.alma_vendor_code FROM statisticsSources JOIN vendors ON statisticsSources.vendor_ID=vendors.vendor_ID ORDER BY statisticsSources.statistics_source_ID;",
        con=engine,
        index_col='statistics_source_ID'
        # Each stats source appears only once, so the PKs can still be used--remember that pandas doesn't have a problem with duplication in the index
    )
    retrieved_data = retrieved_data.astype({
        "statistics_source_name": 'string',
        "statistics_source_retrieval_code": 'string',
        "vendor_ID": 'int',
    })
    print(f"`retrieved_JOIN_query_data`:\n{retrieved_data}")

    expected_output_data = pd.DataFrame(
        [
            ["ProQuest", None, "ProQuest", None],
            ["EBSCOhost", None, "EBSCO", None],
            ["Gale Cengage Learning", None, "Gale", None],
            ["Duke UP", None, "Duke UP", None],
            ["iG Library/Business Expert Press (BEP)", None, "iG Publishing/BEP", None],
            ["DemographicsNow", None, "Gale", None],
            ["Ebook Central", None, "ProQuest", None],
            ["Peterson's Career Prep", None, "Gale", None],
            ["Peterson's Test Prep", None, "Gale", None],
            ["Peterson's Prep", None, "Gale", None],
            ["Pivot", None, "ProQuest", None],
            ["Ulrichsweb", None, "ProQuest", None],
        ],
        columns=["statistics_source_name", "statistics_source_retrieval_code", "vendor_name", "alma_vendor_code"],
    )
    expected_output_data.index.name = "statistics_source_ID"

    assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes


@pytest.mark.dependency(depends=['test_loading_data_into_relation'])  # If the data load into the `vendors` relation fails, this test is skipped
def test_first_new_PK_value():
    """Tests the retrieval of a relation's next primary key value."""
    assert first_new_PK_value('vendors') == 8