"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Passing 2023-07-19 ##########

import pytest
import logging
from pathlib import Path
import os
from random import choice
from bs4 import BeautifulSoup
import pandas as pd
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal
import botocore.exceptions  # `botocore` is a dependency of `boto3`
import sqlalchemy
import flask

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *

log = logging.getLogger(__name__)


@pytest.fixture(params=[Path(os.getcwd(), 'tests', 'data', 'COUNTER_JSONs_for_tests'), Path(os.getcwd(), 'tests', 'bin', 'sample_COUNTER_R4_reports')])
def files_to_upload_to_S3_bucket(request):
    """Handles the selection and removal of files for testing uploads to a S3 bucket.
    
    This fixture uses parameterization to randomly select two files--one text and one binary--to upload into a S3 bucket, then, upon completion of the test, removes those files from the bucket. The `sample_COUNTER_R4_reports` folder is used for binary data because all of the files within are under 30KB; there is no similar way to limit the file size for text data, as the files in `COUNTER_JSONs_for_tests` can be over 6,000KB.
    """
    file_path = request.param
    list_of_file_names = tuple(os.walk(file_path))[0][2]
    file_name = choice(list_of_file_names)
    file_to_upload = file_path / file_name  # Adding prefix in fixture prevents matching to files required in `upload_file_to_S3_bucket()`
    yield file_to_upload
    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=f"{PATH_WITHIN_BUCKET}test_{file_name}"
        )
    except botocore.exceptions as error:
        log.error(f"Trying to remove the test data files from the S3 bucket raised {error}.")


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
    retrieved_vendors_data = retrieved_vendors_data.astype(Vendors.state_data_types())
    assert_frame_equal(vendors_relation, retrieved_vendors_data)


@pytest.mark.dependency(depends=['test_loading_data_into_relation'])  # If the data load into the `vendors` relation fails, this test is skipped
def test_loading_connected_data_into_other_relation(engine, statisticsSources_relation):
    """Tests loading data into a second relation connected with foreign keys and performing a joined query.

    This test uses second dataframe to load data into a relation that has a foreign key field that corresponds to the primary keys of the relation loaded with data in `test_loading_data_into_relation`, then tests that the data load and the primary key-foreign key connection worked by performing a `JOIN` query and comparing it to a manually constructed dataframe containing that same data.
    """
    df_dtypes = {
        "statistics_source_name": StatisticsSources.state_data_types()['statistics_source_name'],
        "statistics_source_retrieval_code": StatisticsSources.state_data_types()['statistics_source_retrieval_code'],
        "vendor_name": Vendors.state_data_types()['vendor_name'],
        "alma_vendor_code": Vendors.state_data_types()['alma_vendor_code'],
    }

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


#Section: Test Helper Functions
@pytest.mark.dependency(depends=['test_loading_data_into_relation'])  # If the data load into the `vendors` relation fails, this test is skipped
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


def test_upload_file_to_S3_bucket(files_to_upload_to_S3_bucket):
    """Tests uploading files to a S3 bucket."""
    upload_file_to_S3_bucket(  # The function returns a string serving as a logging statement, but all error statements also feature a logging statement within the function
        files_to_upload_to_S3_bucket,
        f"test_{files_to_upload_to_S3_bucket.name}",  # The prefix will allow filtering that prevents the test from failing
    )
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}test_",
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET}test_", "") for file_name in bucket_contents]
    assert files_to_upload_to_S3_bucket.name in bucket_contents