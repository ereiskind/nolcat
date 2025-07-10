"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Passing 2025-06-12 ##########

import pytest
from datetime import datetime
from random import choice
from filecmp import cmp
from bs4 import BeautifulSoup
import sqlalchemy
import flask

# `conftest.py` fixtures are imported automatically
from conftest import prepare_HTML_page_for_comparison
from nolcat.logging_config import *
from nolcat.app import *
from nolcat.models import *
from nolcat.statements import *

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


# Testing of `nolcat.app.check_if_data_already_in_COUNTERData()` in `tests.test_StatisticsSources.test_check_if_data_already_in_COUNTERData()`


#Section: Test Helper Functions
def test_upload_file_to_S3_bucket(tmp_path, path_to_sample_file, remove_file_from_S3):  # `remove_file_from_S3()` not called but used to remove file loaded during test
    """Tests uploading files to a S3 bucket."""
    logging_message = upload_file_to_S3_bucket(
        path_to_sample_file,
        path_to_sample_file.name,
        bucket_path=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    log.debug(logging_message)
    if not upload_file_to_S3_bucket_success_regex().fullmatch(logging_message):
        assert False  # Entering this block means the function that's being tested raised an error, so continuing with the test won't provide anything meaningful
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    log.debug(f"Raw contents of `{BUCKET_NAME}/{PATH_WITHIN_BUCKET_FOR_TESTS}` (type {type(list_objects_response)}):\n{format_list_for_stdout(list_objects_response)}.")
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET_FOR_TESTS}", "") for file_name in bucket_contents]
    assert path_to_sample_file.name in bucket_contents
    download_location = tmp_path / path_to_sample_file.name
    s3_client.download_file(
        Bucket=BUCKET_NAME,
        Key=PATH_WITHIN_BUCKET_FOR_TESTS + path_to_sample_file.name,
        Filename=download_location,
    )
    assert cmp(path_to_sample_file, download_location)


# `test_check_if_data_already_in_COUNTERData()` and its related fixtures are in `tests.test_StatisticsSources` because the test requires the test data to be loaded into the `COUNTERData` relation while every other test function in this module relies upon the test suite starting with an empty database.


def test_prepare_HTML_page_for_comparison():
    """Tests creating an Unicode string from HTML page data."""
    assert prepare_HTML_page_for_comparison(b'<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Ingest Usage</title>\n</head>\n<body>\n    <h1>Ingest Usage Homepage</h1>\n\n    \n        \n            <p>[{&#39;DR&#39;: [], &#39;IR&#39;: [], &#39;PR&#39;: [], &#39;reports&#39;: [], &#39;status&#39;: []}]</p>\n        \n    \n\n    <ul>\n        <li>To upload a tabular COUNTER report, <a href="/ingest_usage/upload-COUNTER">click here</a>.</li>\n        <li>To make a SUSHI call, <a href="/ingest_usage/harvest">click here</a>.</li>\n        <li>To save a non-COUNTER usage file, <a href="/ingest_usage/upload-non-COUNTER">click here</a>.</li>\n    </ul>\n\n    <p>To return to the homepage, <a href="/">click here</a>.</p>\n</body>\n</html>') == '<!DOCTYPE html>\\n<html lang="en">\\n<head>\\n    <meta charset="UTF-8">\\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\\n    <title>Ingest Usage</title>\\n</head>\\n<body>\\n    <h1>Ingest Usage Homepage</h1>\\n\\n    \\n        \\n            <p>[{\'DR\': [], \'IR\': [], \'PR\': [], \'reports\': [], \'status\': []}]</p>\\n        \\n    \\n\\n    <ul>\\n        <li>To upload a tabular COUNTER report, <a href="/ingest_usage/upload-COUNTER">click here</a>.</li>\\n        <li>To make a SUSHI call, <a href="/ingest_usage/harvest">click here</a>.</li>\\n        <li>To save a non-COUNTER usage file, <a href="/ingest_usage/upload-non-COUNTER">click here</a>.</li>\\n    </ul>\\n\\n    <p>To return to the homepage, <a href="/">click here</a>.</p>\\n</body>\\n</html>'


@pytest.fixture(params=[
    {'Report_Header': {'Created': '2023-10-17T21:13:26Z','Created_By': 'ProQuest','Customer_ID': '0000','Report_ID': 'PR','Release': '5','Report_Name': 'Platform Master Report','Institution_Name': 'FLORIDA STATE UNIVERSITY','Institution_ID': [{'Type': 'Proprietary','Value': 'ProQuest:0000'}],'Report_Filters': [{'Name': 'Platform','Value': 'ProQuest'},{'Name': 'Begin_Date','Value': '2022-07-01'},{'Name': 'End_Date','Value': '2023-08-31'},{'Name': 'Data_Type','Value': 'Book|Journal'}],'Report_Attributes': [{'Name': 'Attributes_To_Show','Value': 'Data_Type|Access_Method'}]},'Report_Items': [{'Platform': 'ProQuest','Data_Type': 'Book','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 8},{'Metric_Type': 'Total_Item_Requests','Count': 9}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 2},{'Metric_Type': 'Total_Item_Requests','Count': 12}]}]},{'Platform': 'ProQuest','Data_Type': 'Journal','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 53},{'Metric_Type': 'Total_Item_Requests','Count': 89}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 77},{'Metric_Type': 'Total_Item_Requests','Count': 92}]}]}]},
    "{'Report_Header': {'Created': '2023-10-17T21:13:26Z','Created_By': 'ProQuest','Customer_ID': '0000','Report_ID': 'PR','Release': '5','Report_Name': 'Platform Master Report','Institution_Name': 'FLORIDA STATE UNIVERSITY','Institution_ID': [{'Type': 'Proprietary','Value': 'ProQuest:0000'}],'Report_Filters': [{'Name': 'Platform','Value': 'ProQuest'},{'Name': 'Begin_Date','Value': '2022-07-01'},{'Name': 'End_Date','Value': '2023-08-31'},{'Name': 'Data_Type','Value': 'Book|Journal'}],'Report_Attributes': [{'Name': 'Attributes_To_Show','Value': 'Data_Type|Access_Method'}]},'Report_Items': [{'Platform': 'ProQuest','Data_Type': 'Book','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 8},{'Metric_Type': 'Total_Item_Requests','Count': 9}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 2},{'Metric_Type': 'Total_Item_Requests','Count': 12}]}]},{'Platform': 'ProQuest','Data_Type': 'Journal','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 53},{'Metric_Type': 'Total_Item_Requests','Count': 89}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 77},{'Metric_Type': 'Total_Item_Requests','Count': 92}]}]}]}",
])
def file_name_stem_and_data(request, most_recent_month_with_usage):
    """Provides the contents and name stem for the file in `test_save_unconverted_data_via_upload()`, then removes that file from S3 after the test runs.

    Args:
        request (dict or str): the contents of the file that will be saved to S3

    Yields:
        tuple: the stem of the name under which the file will be saved in S3 (str); the data that will be in the file saved to S3 (dict or str)
    """
    data = request.param
    log.debug(f"In `remove_file_from_S3_with_yield()`, the `data` is {data}.")
    file_name_stem = f"{choice(('P', 'D', 'T', 'I'))}R_{most_recent_month_with_usage[0].strftime('%Y-%m')}_{most_recent_month_with_usage[1].strftime('%Y-%m')}_{datetime.now().strftime(AWS_timestamp_format())}"  # This is the format used for usage reports, which are the most frequently type of saved report
    log.info(f"In `remove_file_from_S3_with_yield()`, the `file_name_stem` is {file_name_stem}.")
    yield (file_name_stem, data)
    if isinstance(data, dict):
        file_name = file_name_stem + '.json'
    else:
        file_name = file_name_stem + '.txt'
    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=PATH_WITHIN_BUCKET_FOR_TESTS + file_name
        )
    except botocore.exceptions as error:
        log.error(f"Trying to remove file `{file_name}` from the S3 bucket raised {error}.")


def test_save_unconverted_data_via_upload(file_name_stem_and_data):
    """Tests saving data that can't be transformed for loading into the database to a file in S3."""
    file_name_stem, data = file_name_stem_and_data
    logging_message = save_unconverted_data_via_upload(
        data=data,
        file_name_stem=file_name_stem,
        bucket_path=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    if not upload_file_to_S3_bucket_success_regex().fullmatch(logging_message):
        assert False  # Entering this block means the function that's being tested raised an error, so continuing with the test won't provide anything meaningful
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(PATH_WITHIN_BUCKET_FOR_TESTS, "") for file_name in bucket_contents]
    if isinstance(data, dict):
        assert f"{file_name_stem}.json" in bucket_contents
    else:
        assert f"{file_name_stem}.txt" in bucket_contents