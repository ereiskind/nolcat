"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Passing 2023-09-08 ##########

import pytest
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal
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
    assert str(engine.__dict__['url']) == f'mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}'


def test_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    page = client.get('/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    
    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'templates', 'index.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_404_page(client):
    """Tests that the unassigned route '/404' goes to the 404 page."""
    nonexistent_page = client.get('/404')
    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'templates', '404.html'), 'br') as HTML_file:
        # Because the only Jinja markup on this page is a link to the homepage, replacing that Jinja with the homepage route and removing the Windows-exclusive carriage feed from the HTML file make it identical to the data returned from the GET request
        HTML_markup = HTML_file.read().replace(b"\r", b"")
        HTML_markup = HTML_markup.replace(b"{{ url_for(\'homepage\') }}", b"/")
    assert nonexistent_page.status == "404 NOT FOUND"
    assert nonexistent_page.data == HTML_markup


@pytest.mark.dependency()
def test_load_data_into_database(engine, vendors_relation):
    """Tests loading data into a relation.

    Testing the helper function for loading data into the database also confirms that the database and program are connected.
    """
    result = load_data_into_database(
        df=vendors_relation,
        relation='vendors',
        engine=engine,
        index_field_name='vendor_ID',
    )
    assert result == "Successfully loaded 8 records into the vendors relation."


@pytest.mark.dependency(depends=['test_load_data_into_database'])
def test_query_database(engine, vendors_relation):
    """Tests getting data from the database through a SQL query.

    This test performs a `SELECT *` query on the relation that had data loaded into it in the previous test, confirming that the function works and that the database and program are connected to allow CRUD operations.
    """
    retrieved_vendors_data = query_database(
        query="SELECT * FROM vendors;",
        engine=engine,
        index='vendor_ID',
    )
    if isinstance(retrieved_vendors_data, str):
        #SQLErrorReturned
    retrieved_vendors_data = retrieved_vendors_data.astype(Vendors.state_data_types())
    assert_frame_equal(vendors_relation, retrieved_vendors_data)


@pytest.mark.dependency(depends=['test_query_database'])
def test_loading_connected_data_into_other_relation(engine, statisticsSources_relation, caplog):
    """Tests loading data into a second relation connected with foreign keys and performing a joined query.

    This test uses second dataframe to load data into a relation that has a foreign key field that corresponds to the primary keys of the relation loaded with data in `test_load_data_into_database`, then tests that the data load and the primary key-foreign key connection worked by performing a `JOIN` query and comparing it to a manually constructed dataframe containing that same data.
    """
    df_dtypes = {
        "statistics_source_name": StatisticsSources.state_data_types()['statistics_source_name'],
        "statistics_source_retrieval_code": StatisticsSources.state_data_types()['statistics_source_retrieval_code'],
        "vendor_name": Vendors.state_data_types()['vendor_name'],
        "alma_vendor_code": Vendors.state_data_types()['alma_vendor_code'],
    }

    load_data_into_database(
        df=statisticsSources_relation,
        relation='statisticsSources',
        engine=engine,
        index_field_name='statistics_source_ID',
    )
    retrieved_data = query_database(
        query="""
            SELECT
                statisticsSources.statistics_source_ID,
                statisticsSources.statistics_source_name,
                statisticsSources.statistics_source_retrieval_code,
                vendors.vendor_name,
                vendors.alma_vendor_code
            FROM statisticsSources
            JOIN vendors ON statisticsSources.vendor_ID=vendors.vendor_ID
            ORDER BY statisticsSources.statistics_source_ID;
        """,
        engine=engine,
        index='statistics_source_ID'
        # Each stats source appears only once, so the PKs can still be used--remember that pandas doesn't have a problem with duplication in the index
    )
    if isinstance(retrieved_data, str):
        #SQLErrorReturned
    retrieved_data = retrieved_data.astype(df_dtypes)

    expected_output_data = pd.DataFrame(
        [
            ["ProQuest", "1", "ProQuest", None],
            ["EBSCOhost", "2", "EBSCO", None],
            ["Gale Cengage Learning", None, "Gale", None],
            ["Duke UP", "3", "Duke UP", None],
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
    expected_output_data = expected_output_data.astype(df_dtypes)
    assert_frame_equal(retrieved_data, expected_output_data)


def test_download_file(client, path_to_sample_file):  #ToDo: If method for interacting with host workstation's file system can be established, add `default_download_folder`
    """Tests the route enabling file downloads."""
    log.info(f"At start of `test_download_file()`, `path_to_sample_file` is {path_to_sample_file} (type {type(path_to_sample_file)})")  #FileIO
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


#Section: Test Helper Functions
@pytest.mark.dependency(depends=['test_load_data_into_database'])
def test_first_new_PK_value():
    """Tests the retrieval of a relation's next primary key value."""
    assert first_new_PK_value('vendors') == 8


def test_change_single_field_dataframe_into_series():
    """Tests the transformation of a dataframe with a single field into a series."""
    mx = pd.MultiIndex.from_frame(
        pd.DataFrame(
            [
                [0, "a"],
                [0, "b"],
                [1, "a"],
                [1, "c"],
            ],
            columns=["numbers", "letters"],
        )
    )
    df = pd.DataFrame(
        [[1], [2], [3], [4]],
        index=mx,
        dtype='int64',
        columns=["test"],
    )
    s = pd.Series(
        [1, 2, 3, 4],
        index=mx,
        dtype='int64',
        name="test",
    )
    assert_series_equal(change_single_field_dataframe_into_series(df), s)


def test_restore_boolean_values_to_boolean_field():
    """Tests the replacement of MySQL's single-bit int data type with pandas's `boolean` data type."""
    tinyint_s = pd.Series(
        [1, 0, pd.NA, 1],
        dtype='Int8',  # pandas' single-bit int data type is used because it allows nulls; using the Python data type raises an error
        name="boolean_values",
    )
    boolean_s = pd.Series(
        [True, False, pd.NA, True],
        dtype='boolean',
        name="boolean_values",
    )
    assert_series_equal(restore_boolean_values_to_boolean_field(tinyint_s), boolean_s)


def test_S3_bucket_connection():
    """Tests that the S3 bucket created by the instantiated client exists and can be accessed by NoLCAT."""
    bucket_header = s3_client.head_bucket(Bucket=BUCKET_NAME)
    assert bucket_header['ResponseMetadata']['HTTPStatusCode'] == 200


def test_upload_file_to_S3_bucket(path_to_sample_file):
    """Tests uploading files to a S3 bucket."""
    upload_file_to_S3_bucket(  # The function returns a string serving as a logging statement, but all error statements also feature a logging statement within the function
        path_to_sample_file,
        f"test_{path_to_sample_file.name}",  # The prefix will allow filtering that prevents the test from failing
    )
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}test_",
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET}test_", "") for file_name in bucket_contents]
    assert path_to_sample_file.name in bucket_contents


def test_create_AUCT_SelectField_options():
    """Tests the transformation of a dataframe with four fields into a list for the `SelectField.choices` attribute with the characteristics described in the docstring of the function being tested."""
    df = pd.DataFrame(
        [
            [1, 1, "First Statistics Source", "2017"],
            [2, 1, "Second Statistics Source", "2017"],
            [1, 2, "First Statistics Source", "2018"],
            [3, 2, "Third Statistics Source", "2018"],
        ],
        columns=["AUCT_statistics_source", "AUCT_fiscal_year", "statistics_source_name", "fiscal_year"],
    )
    result_list = [
        (
            (1, 1),
            "First Statistics Source--FY 2017",
        ),
        (
            (2, 1),
            "Second Statistics Source--FY 2017",
        ),
        (
            (1, 2),
            "First Statistics Source--FY 2018",
        ),
        (
            (3, 2),
            "Third Statistics Source--FY 2018",
        ),
    ]
    assert create_AUCT_SelectField_options(df) == result_list


@pytest.fixture
def partially_duplicate_COUNTER_data():
    """COUNTER data, some of which is in the `COUNTERData_relation` dataframe.

    Yields:
        dataframe: data formatted for loading into the `COUNTERData` relation
    """
    df = pd.DataFrame(
        [
            [3, "TR", "Empires of Vision<subtitle>A Reader</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822378976", "Silverchair:417", "978-0-8223-7897-6", None, None, None, "Book", "Chapter", 2013, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-01-01", 4, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-01-01", 4, None],
            [3, "TR", "Pikachu's Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822385813", "Silverchair:891", "978-0-8223-8581-3", None, None, None, "Book", "Book", 2004, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-03-01", 2, None],
            [3, "TR", "Pikachu's Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822385813", "Silverchair:891", "978-0-8223-8581-3", None, None, None, "Book", "Book", 2004, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Item_Investigations", "2020-03-01", 2, None],
            [3, "TR", "Pikachu's Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822385813", "Silverchair:891", "978-0-8223-8581-3", None, None, None, "Book", None, 2004, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Title_Investigations", "2020-03-01", 2, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 16, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 4, None],
        ],
        columns=["statistics_source_ID", "report_type", "resource_name", "publisher", "publisher_ID", "platform", "authors", "publication_date", "article_version", "DOI", "proprietary_ID", "ISBN", "print_ISSN", "online_ISSN", "URI", "data_type", "section_type", "YOP", "access_type", "access_method",  "parent_title", "parent_authors", "parent_publication_date", "parent_article_version", "parent_data_type", "parent_DOI", "parent_proprietary_ID", "parent_ISBN", "parent_print_ISSN", "parent_online_ISSN", "parent_URI", "metric_type", "usage_date", "usage_count", "report_creation_date"],
    )
    df.index.name = "COUNTER_data_ID"
    df = df.astype(COUNTERData.state_data_types())
    df["publication_date"] = pd.to_datetime(df["publication_date"])
    df["parent_publication_date"] = pd.to_datetime(df["parent_publication_date"])
    df["usage_date"] = pd.to_datetime(df["usage_date"])
    df["report_creation_date"] = pd.to_datetime(df["report_creation_date"])
    yield df


@pytest.fixture
def non_duplicate_COUNTER_data():
    """The COUNTER data from `partially_duplicate_COUNTER_data`not in the `COUNTERData_relation` dataframe.

    Yields:
        dataframe: data formatted for loading into the `COUNTERData` relation
    """
    df = pd.DataFrame(
        [
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 16, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 4, None],
        ],
        columns=["statistics_source_ID", "report_type", "resource_name", "publisher", "publisher_ID", "platform", "authors", "publication_date", "article_version", "DOI", "proprietary_ID", "ISBN", "print_ISSN", "online_ISSN", "URI", "data_type", "section_type", "YOP", "access_type", "access_method",  "parent_title", "parent_authors", "parent_publication_date", "parent_article_version", "parent_data_type", "parent_DOI", "parent_proprietary_ID", "parent_ISBN", "parent_print_ISSN", "parent_online_ISSN", "parent_URI", "metric_type", "usage_date", "usage_count", "report_creation_date"],
    )
    df.index.name = "COUNTER_data_ID"
    df = df.astype(COUNTERData.state_data_types())
    df["publication_date"] = pd.to_datetime(df["publication_date"])
    df["parent_publication_date"] = pd.to_datetime(df["parent_publication_date"])
    df["usage_date"] = pd.to_datetime(df["usage_date"])
    df["report_creation_date"] = pd.to_datetime(df["report_creation_date"])
    yield df


def test_check_if_data_already_in_COUNTERData(partially_duplicate_COUNTER_data, non_duplicate_COUNTER_data):
    """Tests the check for statistics source/report type/usage date combinations already in the database."""
    #TEST: Because there's no data loaded in the `COUNTERData` relation at this point, this test won't pass
    df, message = check_if_data_already_in_COUNTERData(partially_duplicate_COUNTER_data)
    assert_frame_equal(df, non_duplicate_COUNTER_data)
    assert message == f"Usage statistics for the report type, usage date, and statistics source combination(s) below, which were included in the upload, are already in the database; as a result, it wasn't uploaded to the database. If the data needs to be re-uploaded, please remove the existing data from the database first.\nTR  | 2020-01-01 | Duke UP (ID 3)\nTR  | 2020-03-01 | Duke UP (ID 3)\nBR2 | 2018-04-01 | Gale Cengage Learning (ID 2)\nBR2 | 2018-08-01 | Gale Cengage Learning (ID 2)"


#ToDo: test_match_direct_SUSHI_harvest_result()
# Function itself in `tests.conftest`


#ToDo: test_COUNTER_reports_offered_by_statistics_source()
# Function itself in `tests.conftest`