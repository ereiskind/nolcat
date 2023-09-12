"""Tests the routes in the `ingest_usage` blueprint."""
########## Failing 2023-09-08 ##########

import pytest
import logging
from random import choice
from pathlib import Path
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
from requests_toolbelt.multipart.encoder import MultipartEncoder

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.ingest_usage import *

log = logging.getLogger(__name__)


def test_ingest_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    page = client.get('/ingest_usage/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'index.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_upload_COUNTER_reports(engine, client, header_value, COUNTERData_relation, caplog):
    """Tests adding data to the `COUNTERData` relation by uploading files with the `ingest_usage.COUNTERReportsForm` form."""
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    form_submissions = MultipartEncoder(  #Test: This field is a MultipleFileField, but current setup, which passes, only accepts a single file
        #ToDo: Create a variable/fixture that simulates multiple files being added to the MultipleFileField field
            # Multiple items in the value of a MultipartEncoder.fields key-value pair doesn't work
            # Should a MultipleFileField object be instantiated?
            # Could the classes in "test_UploadCOUNTERReports.py" be used?
            # Can a direct list of Werkzeug FileStorage object(s) be used?
        fields={
            'COUNTER_reports': ('0_2017.xlsx', open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('tests')+1]) / 'bin' / 'COUNTER_workbooks_for_tests' / '0_2017.xlsx', 'rb')),
        },
        encoding='utf-8',
    )
    header_value['Content-Type'] = form_submissions.content_type
    POST_response = client.post(
        '/ingest_usage/upload-COUNTER',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_submissions,  #ToDo: Find a way to make this simulate multiple files
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    # This is the HTML file of the page the redirect goes to
    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'index.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    COUNTERData_relation_data = pd.read_sql(
        sql=f"SELECT * FROM COUNTERData ORDER BY COUNTER_data_ID DESC LIMIT {COUNTERData_relation.shape[0]};",
        con=engine,
        index_col='COUNTER_data_ID',
    )

    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert b'Successfully loaded the data from the tabular COUNTER reports into the `COUNTERData` relation' in POST_response.data  # This confirms the flash message indicating success appears; if there's an error, the error message appears instead, meaning this statement will fail
    #TEST: Because only one of the test data files is being loaded, ``assert_frame_equal(COUNTERData_relation, COUNTERData_relation_data)  # `first_new_PK_value` is part of the view function, but if it was used, this statement will fail`` won't pass


def test_GET_request_for_harvest_SUSHI_statistics(engine, client,):
    """Tests that the page for making custom SUSHI calls can be successfully GET requested and that the response properly populates with the requested data."""
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

    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'make-SUSHI-call.html'), 'br') as HTML_file:
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


def test_harvest_SUSHI_statistics(engine, client, most_recent_month_with_usage, header_value, caplog):
    """Tests making a SUSHI API call based on data entered into the `ingest_usage.SUSHIParametersForm` form.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. Since the data in the form being submitted with the POST request is ultimately used to make a SUSHI call, the `StatisticsSources.statistics_source_retrieval_code` values used in the test data--`1`, `2`, and `3`--must correspond to values in the SUSHI credentials JSON; for testing purposes, these values don't need to make SUSHI calls to the statistics source designated by the test data's StatisticsSources record--any valid credential set will work. The limited number of possible SUSHI credentials means statistics sources current with the available usage statistics are not filtered out, meaning this test may fail because it fails the check preventing SUSHI calls to stats source/date combos already in the database.
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()` called in `StatisticsSources.collect_usage_statistics()`
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()` called in `StatisticsSources._harvest_R5_SUSHI()` called in `StatisticsSources.collect_usage_statistics()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `StatisticsSources._harvest_single_report()` called in `StatisticsSources._harvest_R5_SUSHI()` called in `StatisticsSources.collect_usage_statistics()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `StatisticsSources._check_if_data_in_database()` called in `StatisticsSources._harvest_single_report()` called in `StatisticsSources._harvest_R5_SUSHI()` called in `StatisticsSources.collect_usage_statistics()`
    primary_key_list = pd.read_sql(
        sql="SELECT statistics_source_ID FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
        con=engine,
    )
    primary_key_list = change_single_field_dataframe_into_series(primary_key_list).astype('string').to_list()
    form_input = {
        'statistics_source': choice(primary_key_list),
        'begin_date': most_recent_month_with_usage[0],
        'end_date': most_recent_month_with_usage[1],
    }
    POST_response = client.post(
        '/ingest_usage/harvest',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    # This is the HTML file of the page the redirect goes to
    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'index.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    log.info(POST_response.data)
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert re.search(rb'Successfully loaded \d* records into the database.', string=POST_response.data) is not None   # This confirms the flash message indicating success appears; if there's an error, the error message appears instead, meaning this statement will fail  #TEST: tests/test_bp_ingest_usage.py:146: The SUSHI request form submission failed due to the error 'NoneType' object has no attribute 'get'.


def test_GET_request_for_upload_non_COUNTER_reports(engine, client, caplog):
    """Tests that the page for uploading and saving non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `change_single_field_dataframe_into_series()`
    page = client.get('/ingest_usage/upload-non-COUNTER')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Uncomment below when "ingest_usage/upload-non-COUNTER-usage.html" is finished
    #GET_select_field_options = []
    #for child in GET_soup.find(name='select', id='statistics_source').children:
    #    GET_select_field_options.append((
    #        int(child['value']),
    #        str(child.string),
    #    ))

    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'upload-non-COUNTER-usage.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    db_select_field_options = pd.read_sql(
        sql="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
        con=engine,
    )
    db_select_field_options = list(db_select_field_options.itertuples(index=False, name=None))

    #ToDo: `assert page.status == "200 OK"` when route is completed
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    #ToDo: `assert GET_select_field_options == db_select_field_options` when "ingest_usage/upload-non-COUNTER-usage.html" is finished


def test_upload_non_COUNTER_reports():
    """Tests saving files uploaded to `ingest_usage.UsageFileForm` and updating the corresponding AUCT record."""
    #ToDo: caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    #ToDo: Write test
    #ToDo: Make one of the `assert` conditions the appearance of the flashed message
    pass