"""Tests the routes in the `ingest_usage` blueprint."""

import pytest
import json
from random import choice
from pathlib import Path
import os
from bs4 import BeautifulSoup
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.models import PATH_TO_CREDENTIALS_FILE
from nolcat.ingest_usage import *


@pytest.fixture(scope='module')
def StatisticsSources_primary_key_fixture(engine, most_recent_month_with_usage):
    """A fixture selecting a random `StatisticsSources` primary key value to perpetuate a real SUSHI call.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. The `test_harvest_SUSHI_statistics()` tests a POST request sending data from a form that's ultimately used to make a SUSHI call; one of those fields is the primary key value of the `statisticsSources` record for which the call should be made, and this fixture serves to randomly select one such value. Because the `_harvest_R5_SUSHI()` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics are filtered out to prevent their use.

    Args:
        PATH_TO_CREDENTIALS_FILE (str): the file path for "R5_SUSHI_credentials.json"
        most_recent_month_with_usage (tuple): the first and last days of the most recent month for which COUNTER data is available

    Yields:
        int: the primary key value for a StatisticsSources object connected to valid SUSHI data
    """
    retrieval_codes_as_interface_IDs = []  # The list of `StatisticsSources.statistics_source_retrieval_code` values from the JSON, which are labeled as `interface_id` in the JSON
    with open(PATH_TO_CREDENTIALS_FILE()) as JSON_file:
        SUSHI_data_file = json.load(JSON_file)
        for vendor in SUSHI_data_file:
            for stats_source in vendor['interface']:
                if "interface_id" in list(stats_source.keys()):
                        retrieval_codes_as_interface_IDs.append(stats_source['interface_id'])
    print(f"Possible retrieval code choices:\n{retrieval_codes_as_interface_IDs}")
    
    retrieval_codes = []
    for interface in retrieval_codes_as_interface_IDs:
        query_result = pd.read_sql(
            sql=f"SELECT COUNT(*) FROM statisticsSources JOIN COUNTERData ON statisticsSources.statistics_source_ID=COUNTERData.statistics_source_ID WHERE statisticsSources.statistics_source_retrieval_code={interface} AND COUNTERData.usage_date={most_recent_month_with_usage[0].strftime('%Y-%m-%d')}",
            con=engine,
        )
        if not query_result.empty or not query_result.isnull().all().all():  # `empty` returns Boolean based on if the dataframe contains data elements; `isnull().all().all()` returns a Boolean based on a dataframe of Booleans based on if the value of the data element is null or not
            retrieval_codes.append(interface)
    print(f"Retrieval code choices:\n{retrieval_codes}")
    
    primary_key = pd.read_sql(
        sql=f"SELECT statistics_source_ID FROM statisticsSources WHERE statistics_source_retrieval_code={choice(retrieval_codes)};",
        con=engine,
    )
    print(primary_key)
    yield primary_key.iloc[0][0]


def test_ingest_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    page = client.get('/ingest_usage/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_upload_COUNTER_reports():
    """Tests adding data to the `COUNTERData` relation by uploading files with the `ingest_usage.COUNTERReportsForm` form."""
    #ToDo: Write test
    pass


def test_GET_request_for_harvest_SUSHI_statistics(client, engine):
    """Tests that the page for making custom SUSHI calls can be successfully GET requested and that the response properly populates with the requested data."""
    #Section: Get Data from `GET` Requested Page
    page = client.get('/ingest_usage/harvest')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    GET_select_field_options = []
    for child in GET_soup.find(name='select', id='statistics_source').children:
        GET_select_field_options.append((
            int(child['value']),
            str(child.string),
        ))

    #Section: Get Data from HTML File and Database
    with open(Path(os.getcwd(), 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'make-SUSHI-call.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    db_select_field_options = pd.read_sql(
        sql="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
        con=engine,
    )
    db_select_field_options = list(db_select_field_options.itertuples(index=False, name=None))

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    assert GET_select_field_options == db_select_field_options


def test_harvest_SUSHI_statistics(StatisticsSources_primary_key_fixture, most_recent_month_with_usage, client, header_value):
    """Tests making a SUSHI API call based on data entered into the `ingest_usage.SUSHIParametersForm` form."""
    form_input = {
        'statistics_source': StatisticsSources_primary_key_fixture,
        'begin_date': most_recent_month_with_usage[0],
        'end_date': most_recent_month_with_usage[1],
    }
    POST_response = client.post(
        '/ingest_usage/harvest',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    #ToDo: Find a way to assert that `POST_response` includes the message `The load was a success.` to be flashed on the redirect destination page
    print(f"`POST_response.content` (type {type(POST_response.content)}): {POST_response.content}")
    print(f"`POST_response.headers` (type {type(POST_response.headers)}): {POST_response.headers}")
    print(f"`POST_response.text` (type {type(POST_response.text)}): {POST_response.text}")
    print(f"`POST_response.next` (type {type(POST_response.next)}): {POST_response.next}")
    assert POST_response.status == "302 FOUND"
    assert b'<a href="/ingest_usage">' in POST_response.data  # The `in` operator checks that the redirect location is correct


def test_GET_request_for_upload_non_COUNTER_reports(client):
    """Tests that the page for uploading and saving non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    #Section: Get Data from `GET` Requested Page
    page = client.get('/ingest_usage/upload-non-COUNTER')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Get the values from the SQL query in the best way for the purpose of comparison

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'upload-non-COUNTER-usage.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
        #ToDo: Get the list of AUCT options presented for populating the drop-down

    #ToDo: `assert page.status == "200 OK"` when route is completed
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_upload_non_COUNTER_reports():
    """Tests saving files uploaded to `ingest_usage.UsageFileForm` and updating the corresponding AUCT record."""
    #ToDo: Write test
    #ToDo: Make one of the `assert` conditions the appearance of the flashed message
    pass