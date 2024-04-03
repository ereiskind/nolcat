"""Tests the routes in the `ingest_usage` blueprint."""
########## Failing 2024-04-03 ##########

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
from nolcat.models import *
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


def test_upload_COUNTER_data_via_Excel(engine, client, header_value, COUNTERData_relation, caplog):
    """Tests adding data to the `COUNTERData` relation by uploading files with the `ingest_usage.COUNTERReportsForm` form."""
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()` and `query_database()`
    
    form_submissions = []
    for file in Path(TOP_NOLCAT_DIRECTORY, 'tests', 'bin', 'COUNTER_workbooks_for_tests').iterdir():
        tuple_to_append = (
            file.name,
            open(file, 'rb'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        form_submissions.append(tuple_to_append)
    log.debug(f"The files being uploaded to the database are:\n{form_submissions}")
    header_value['Content-Type'] = 'text/html; charset=utf-8'  # Based on header when flask app is used
    #TEST: temp
    from inspect import signature
    temp = signature(
        client.post(
            '/ingest_usage/upload-COUNTER',
            follow_redirects=True,
            headers=header_value,
            data=MultipartEncoder(
                fields={
                   'COUNTER_data': (
                       '0_PR.json',
                       open(TOP_NOLCAT_DIRECTORY / 'tests' / 'data' / 'COUNTER_JSONs_for_tests' / '0_PR.json', 'rb'),
                       'text/html; charset=utf-8',
                   )
                },
                encoding='utf-8',
            )
        )
    )
    log.info(f"`signature` (type {type(temp)}):\n{temp}")
    log.info(f"`signature.parameters` (type {type(temp.parameters)}):\n{temp.parameters}")
    #TEST: end temp
    POST_response = client.post(  #TEST: TypeError: __init__() got an unexpected keyword argument 'files'
        '/ingest_usage/upload-COUNTER',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        files=form_submissions,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    #TEST: temp commented out
    # This is the HTML file of the page the redirect goes to
    #with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
    #    file_soup = BeautifulSoup(HTML_file, 'lxml')
    #    HTML_file_title = file_soup.head.title.string.encode('utf-8')
    #    HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    #COUNTERData_relation_data = query_database(
    #    query=f"SELECT * FROM COUNTERData ORDER BY COUNTER_data_ID DESC LIMIT {COUNTERData_relation.shape[0]};",
    #    engine=engine,
    #    index='COUNTER_data_ID',
    #)
    #if isinstance(COUNTERData_relation_data, str):
    #    pytest.skip(database_function_skip_statements(COUNTERData_relation_data))

    #assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    #assert POST_response.status == "200 OK"
    #assert HTML_file_title in POST_response.data
    #assert HTML_file_page_title in POST_response.data
    #assert load_data_into_database_success_regex().search(prepare_HTML_page_for_comparison(POST_response.data))  # This confirms the flash message indicating success appears; if there's an error, the error message appears instead, meaning this statement will fail
    #assert_frame_equal(COUNTERData_relation, COUNTERData_relation_data)  # `first_new_PK_value` is part of the view function, but if it was used, this statement will fail


def test_upload_COUNTER_data_via_SQL_insert(engine, client, header_value):
    """Tests updating the `COUNTERData` relation with insert statements in an uploaded SQL file."""
    SQL_file_path = TOP_NOLCAT_DIRECTORY / 'tests' / 'data' / 'insert_statements_test_file.sql'
    form_submissions = MultipartEncoder(
        fields={
            'COUNTER_data': (SQL_file_path.name, open(SQL_file_path, 'rb'), 'application/sql'),
        },
        encoding='utf-8',
    )
    header_value['Content-Type'] = form_submissions.content_type
    POST_response = client.post(
        '/ingest_usage/upload-COUNTER',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_submissions,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    check_relation_size = query_database(
        query=f"SELECT COUNT(*) FROM COUNTERData;",
        engine=engine,
    )
    if isinstance(check_relation_size, str):
        pytest.skip(database_function_skip_statements(check_relation_size))
    check_database_update = query_database(
        query="SELECT * FROM COUNTERData ORDER BY COUNTER_data_ID DESC LIMIT 7;",  # The entire relation can't be compared due to the SUSHI call in the previous test
        engine=engine,
    )
    if isinstance(check_database_update, str):
        pytest.skip(database_function_skip_statements(check_database_update))
    check_database_update = check_database_update.astype(COUNTERData.state_data_types())
    check_database_update = check_database_update.drop(columns='COUNTER_data_ID')
    insert_statement_data = pd.DataFrame(
        [  # These records are in reverse order from the SQL file because getting the last seven records requires a SQL query that places the most recently loaded (aka last) records at the top
            [3, "IR", "Winners and Losers: Some Paradoxes in Monetary History Resolved and Some Lessons Unlearned", "Duke University Press", None, "Duke University Press", "Will E. Mason", "1977-11-01", "VoR", "10.1215/00182702-9-4-476", "Silverchair:12922", None, None, None, None, "Article", None, 1977, "Controlled", "Regular", "History of Political Economy", None, None, None, "Journal", None, "Silverchair:1000052", None, "0018-2702", "1527-1919", None, "Total_Item_Investigations", "2020-07-01", 6, None],
            [3, "PR", None, None, None, "Duke University Press", None, None, None, None, None, None, None, None, None, "Book", None, None, None, "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Title_Requests", "2020-07-01", 2, None],
            [2, "TR", "Library Journal", "Library Journals, LLC", None, "Gale", None, None, None, None, "Gale:1273", None, "0363-0277", None, None, "Journal", "Article", 1998, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Item_Requests", "2020-07-01", 3, None],
            [1, "TR", "The Yellow Wallpaper", "Open Road Media", None, "EBSCOhost", None, None, None, None, "EBSCOhost:KBID:8016659", None, None, None, None, "Book", "Book", 2016, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Item_Investigations", "2020-07-01", 4, None],
            [1, "TR", "The Yellow Wallpaper", "Open Road Media", None, "EBSCOhost", None, None, None, None, "EBSCOhost:KBID:8016659", None, None, None, None, "Book", "Book", 2016, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-07-01", 3, None],
            [0, "IR", "Where Function Meets Fabulous", "MSI Information Services", None, "ProQuest", "LJ", "2019-11-01", None, None, "ProQuest:2309469258", None, "0363-0277", None, None, "Journal", None, 2019, "Controlled", "Regular", "Library Journal", None, None, None, "Journal", None, "ProQuest:40955", None, "0363-0277", None, None, "Unique_Item_Investigations", "2020-07-01", 3, None],
            [0, "PR", None, None, None, "ProQuest", None, None, None, None, None, None, None, None, None, "Other", None, None, None, "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Item_Investigations", "2020-07-01", 77, None], 
        ],
        columns=["statistics_source_ID", "report_type", "resource_name", "publisher", "publisher_ID", "platform", "authors", "publication_date", "article_version", "DOI", "proprietary_ID", "ISBN", "print_ISSN", "online_ISSN", "URI", "data_type", "section_type", "YOP", "access_type", "access_method",  "parent_title", "parent_authors", "parent_publication_date", "parent_article_version", "parent_data_type", "parent_DOI", "parent_proprietary_ID", "parent_ISBN", "parent_print_ISSN", "parent_online_ISSN", "parent_URI", "metric_type", "usage_date", "usage_count", "report_creation_date"],
    )
    insert_statement_data = insert_statement_data.astype(COUNTERData.state_data_types())
    insert_statement_data["publication_date"] = pd.to_datetime(insert_statement_data["publication_date"])
    insert_statement_data["parent_publication_date"] = pd.to_datetime(insert_statement_data["parent_publication_date"])
    insert_statement_data["usage_date"] = pd.to_datetime(insert_statement_data["usage_date"])
    insert_statement_data["report_creation_date"] = pd.to_datetime(insert_statement_data["report_creation_date"])

    assert POST_response.status == "200 OK"
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert check_relation_size.iloc[0][0] > 7  # This confirms the table wasn't dropped and recreated, which would happen if all SQL in the test file was executed
    assert_frame_equal(check_database_update, insert_statement_data)


# Testing of `nolcat.app.check_if_data_already_in_COUNTERData()` in `tests.test_StatisticsSources.test_check_if_data_already_in_COUNTERData()`


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
        query="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL ORDER BY statistics_source_name;",
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
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert load_data_into_database_success_regex().search(prepare_HTML_page_for_comparison(POST_response.data))  # This confirms the flash message indicating success appears; if there's an error, the error message appears instead, meaning this statement will fail


def test_GET_request_for_upload_non_COUNTER_reports(engine, client, caplog):
    """Tests that the page for uploading and saving non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `change_single_field_dataframe_into_series()` and `query_database()`
    
    page = client.get('/ingest_usage/upload-non-COUNTER')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    log.debug(f"Page soup data:\n{GET_soup}")  #TEST: temp
    log.info(f"Soup find:\n{GET_soup.find(name='select', id='statistics_source')}")  #TEST: temp
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    GET_select_field_options = []
    for child in GET_soup.find(name='select', id='statistics_source').children:  #TEST: AttributeError: 'NoneType' object has no attribute 'children'
        GET_select_field_options.append((
            int(child['value']),
            str(child.string),
        ))

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'upload-non-COUNTER-usage.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    db_select_field_options = query_database(
        query="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL ORDER BY statistics_source_name;",
        engine=engine,
    )
    if isinstance(db_select_field_options, str):
        pytest.skip(database_function_skip_statements(db_select_field_options))
    db_select_field_options = list(db_select_field_options.itertuples(index=False, name=None))

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    assert GET_select_field_options == db_select_field_options


def test_upload_non_COUNTER_reports(engine, client, header_value, non_COUNTER_AUCT_object_before_upload, path_to_sample_file, caplog):
    """Tests saving files uploaded to `ingest_usage.UsageFileForm` and updating the corresponding AUCT record."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`

    #Section: Create Form Submission
    if path_to_sample_file.suffix == '.json':
        mimetype = 'application/json'
    else:
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    form_submissions = MultipartEncoder(
        fields={
            'AUCT_option': f"({non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}, {non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year})",  # The string of a tuple is what gets returned by the actual form submission in Flask; trial and error determined that for tests to pass, that was also the value that needed to be passed to the POST method
            'usage_file': (path_to_sample_file.name, open(path_to_sample_file, 'rb'), mimetype),
        },
        encoding='utf-8',
    )

    #Section: Confirm File Upload to S3
    #Subsection: Perform Test Actions
    header_value['Content-Type'] = form_submissions.content_type
    POST_response = client.post(
        '/ingest_usage/upload-non-COUNTER',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_submissions,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    #Subsection: Assert Statements
    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'ingest_usage' / 'templates' / 'ingest_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title.string.encode('utf-8')
        HTML_file_page_title = file_soup.body.h1.string.encode('utf-8')
    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert HTML_file_title in POST_response.data
    assert HTML_file_page_title in POST_response.data
    assert re.search(r"Usage file for .*--FY \d{4} uploaded successfully\.", prepare_HTML_page_for_comparison(POST_response.data))
    
    #Section: Confirm Database Update
    check_database_update = query_database(
        query=f"SELECT collection_status, usage_file_path FROM annualUsageCollectionTracking WHERE AUCT_statistics_source = {non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source} AND AUCT_fiscal_year = {non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year};",
        engine=engine,
    )
    assert check_database_update.at[0,'collection_status'] == 'Collection complete'
    assert check_database_update.at[0,'usage_file_path'] == f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{path_to_sample_file.suffix}"

    #Section: Check S3 for File
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}",
    )
    files_in_bucket = []
    log.info(f"`list_objects_response` (type {type(list_objects_response)}):\n{list_objects_response}")
    bucket_contents = list_objects_response.get('Contents')
    if bucket_contents:
        for contents_dict in bucket_contents:
            files_in_bucket.append(contents_dict['Key'])
        files_in_bucket = [file_name.replace(f"{PATH_WITHIN_BUCKET}", "") for file_name in files_in_bucket]
        assert f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{path_to_sample_file.suffix}" in files_in_bucket
    else:
        assert False  # Nothing in bucket