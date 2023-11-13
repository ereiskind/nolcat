"""Tests the routes in the `ingest_usage` blueprint."""
########## Passing 2023-10-12 ##########

import pytest
import logging
from random import choice
from pathlib import Path
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
from pandas.testing import assert_frame_equal
from requests_toolbelt.multipart.encoder import MultipartEncoder

# `conftest.py` fixtures are imported automatically
from conftest import prepare_HTML_page_for_comparison
from nolcat.app import *
from nolcat.statements import *
from nolcat.ingest_usage import *

log = logging.getLogger(__name__)


def test_ingest_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    page = client.get('/ingest_usage/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_upload_COUNTER_reports(engine, client, header_value, COUNTERData_relation, caplog):
    """Tests adding data to the `COUNTERData` relation by uploading files with the `ingest_usage.COUNTERReportsForm` form."""
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()` and `query_database()`
    
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
    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    COUNTERData_relation_data = query_database(
        query=f"SELECT * FROM COUNTERData ORDER BY COUNTER_data_ID DESC LIMIT {COUNTERData_relation.shape[0]};",
        engine=engine,
        index='COUNTER_data_ID',
    )
    if isinstance(COUNTERData_relation_data, str):
        pytest.skip(database_function_skip_statements(COUNTERData_relation_data))

    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert str(HTML_file_title)[2:-1] in prepare_HTML_page_for_comparison(POST_response.data)
    assert str(HTML_file_page_title)[2:-1] in prepare_HTML_page_for_comparison(POST_response.data)
    assert load_data_into_database_success_regex().search(prepare_HTML_page_for_comparison(POST_response.data))  # This confirms the flash message indicating success appears; if there's an error, the error message appears instead, meaning this statement will fail
    #Test: Because only one of the test data files is being loaded, ``assert_frame_equal(COUNTERData_relation, COUNTERData_relation_data)  # `first_new_PK_value` is part of the view function, but if it was used, this statement will fail`` won't pass


def test_GET_request_for_harvest_SUSHI_statistics(engine, client, caplog):
    """Tests that the page for making custom SUSHI calls can be successfully GET requested and that the response properly populates with the requested data."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`
    
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

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'make-SUSHI-call.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    db_select_field_options = query_database(
        query="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
        engine=engine,
    )
    if isinstance(db_select_field_options, str):
        pytest.skip(database_function_skip_statements(db_select_field_options))
    db_select_field_options = list(db_select_field_options.itertuples(index=False, name=None))

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    assert GET_select_field_options == db_select_field_options


def test_harvest_SUSHI_statistics(engine, client, most_recent_month_with_usage, header_value, caplog):
    """Tests making a SUSHI API call based on data entered into the `ingest_usage.SUSHIParametersForm` form.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. Since the data in the form being submitted with the POST request is ultimately used to make a SUSHI call, the `StatisticsSources.statistics_source_retrieval_code` values used in the test data--`1`, `2`, and `3`--must correspond to values in the SUSHI credentials JSON; for testing purposes, these values don't need to make SUSHI calls to the statistics source designated by the test data's StatisticsSources record--any valid credential set will work. The limited number of possible SUSHI credentials means statistics sources current with the available usage statistics are not filtered out, meaning this test may fail because it fails the check preventing SUSHI calls to stats source/date combos already in the database.
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()` called in `StatisticsSources.collect_usage_statistics()` and for `query_database()`
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()` called in `StatisticsSources._harvest_R5_SUSHI()` called in `StatisticsSources.collect_usage_statistics()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `StatisticsSources._harvest_single_report()` called in `StatisticsSources._harvest_R5_SUSHI()` called in `StatisticsSources.collect_usage_statistics()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `StatisticsSources._check_if_data_in_database()` called in `StatisticsSources._harvest_single_report()` called in `StatisticsSources._harvest_R5_SUSHI()` called in `StatisticsSources.collect_usage_statistics()`
    
    primary_key_list = query_database(
        query="SELECT statistics_source_ID FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
        engine=engine,
    )
    if isinstance(primary_key_list, str):
        pytest.skip(database_function_skip_statements(primary_key_list))
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
    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert str(HTML_file_title)[2:-1] in prepare_HTML_page_for_comparison(POST_response.data)
    assert str(HTML_file_page_title)[2:-1] in prepare_HTML_page_for_comparison(POST_response.data)
    assert load_data_into_database_success_regex().search(prepare_HTML_page_for_comparison(POST_response.data))  # This confirms the flash message indicating success appears; if there's an error, the error message appears instead, meaning this statement will fail


def test_GET_request_for_upload_non_COUNTER_reports(engine, client, caplog):
    """Tests that the page for uploading and saving non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `change_single_field_dataframe_into_series()` and `query_database()`
    
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

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'upload-non-COUNTER-usage.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    db_select_field_options = query_database(
        query="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
        engine=engine,
    )
    if isinstance(db_select_field_options, str):
        pytest.skip(database_function_skip_statements(db_select_field_options))
    db_select_field_options = list(db_select_field_options.itertuples(index=False, name=None))

    #ToDo: `assert page.status == "200 OK"` when route is completed
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    #ToDo: `assert GET_select_field_options == db_select_field_options` when "ingest_usage/upload-non-COUNTER-usage.html" is finished


def test_upload_non_COUNTER_reports(engine, client, header_value, non_COUNTER_AUCT_object_before_upload, path_to_sample_file, remove_file_from_S3, caplog):  # `remove_file_from_S3()` not called but used to remove file loaded during test
    """Tests saving files uploaded to `ingest_usage.UsageFileForm` and updating the corresponding AUCT record."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`

    #Section: Create Form Submission
    #Subsection: Create `AUCT_options` Index
    statistics_source_name = query_database(
        query=f"SELECT statistics_source_name FROM statisticsSources WHERE statistics_source_ID={non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source};",
        engine=engine,
    )
    if isinstance(statistics_source_name, str):
        pytest.skip(f"Unable to run test because it relied on {statistics_source_name[0].lower()}{statistics_source_name[1:].replace(' raised', ', which raised')}")
    fiscal_year = query_database(
        query=f"SELECT fiscal_year FROM fiscalYears WHERE fiscal_year_ID={non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year};",
        engine=engine,
    )
    if isinstance(fiscal_year, str):
        pytest.skip(f"Unable to run test because it relied on {fiscal_year[0].lower()}{fiscal_year[1:].replace(' raised', ', which raised')}")
    df = pd.DataFrame(
        [
            non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source,
            non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year,
            statistics_source_name,
            fiscal_year,
        ],
        columns=['AUCT_statistics_source', 'AUCT_fiscal_year', 'statistics_source_name', 'fiscal_year'],
    )

    #Subsection: Create MultipartEncoder
    if path_to_sample_file.suffix == '.json':
        open_mode = 'rt'
    else:
        open_mode = 'rb'
    form_submissions = MultipartEncoder(
        fields={
            'AUCT_option': create_AUCT_SelectField_options(df)[0],
            'usage_file': (path_to_sample_file.name, open(path_to_sample_file, open_mode)),
        },
        encoding='utf-8',
    )

    #Section: Perform Test Actions
    header_value['Content-Type'] = form_submissions.content_type
    POST_response = client.post(
        '/ingest_usage/upload-non-COUNTER',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_submissions,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    
    check_database_update = query_database(
        query=f"SELECT collection_status, usage_file_path FROM annualUsageCollectionTracking WHERE AUCT_statistics_source = {non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source} AND AUCT_fiscal_year = {non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year};",
        engine=engine,
        index=['AUCT_statistics_source', 'AUCT_fiscal_year'],
    )

    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}",
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET}", "") for file_name in bucket_contents]

    #Section: Assert Statements
    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert check_database_update.at[0,'collection_status'] == 'Collection complete'
    assert check_database_update.at[0,'usage_file_path'] == f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{path_to_sample_file.suffix}"
    #ToDo: ingest_usage.views.upload_non_COUNTER_reports() flash message after validate_on_submit  in post_response.data
    assert f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{path_to_sample_file.suffix}" in bucket_contents


def test_add_SQL_insert_statements(engine, client, header_value):
    """Tests updating the `COUNTERData` relation with insert statements in an uploaded SQL file."""
    SQL_file_path = #ToDo: pathlib.Path to a SQL file with data that can be added to the end of COUNTERData
    form_submissions = MultipartEncoder(
        fields={
            'SQL_file': (SQL_file_path.name, open(SQL_file_path, 'rt')),
        },
        encoding='utf-8',
    )
    POST_response = client.post(
        '/ingest_usage/upload-non-COUNTER',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_submissions,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    check_database_update = query_database(
        query="SELECT * FROM COUNTERData ORDER BY COUNTER_data_ID DESC LIMIT #ToDo: Number of records being inserted;",  # The entire relation can't be compared due to the SUSHI call in the previous test
        engine=engine,
    )
    insert_statement_data = #ToDo: dataframe with the same data as is in the insert statements in the SQL file

    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert_frame_equal(check_database_update, insert_statement_data)