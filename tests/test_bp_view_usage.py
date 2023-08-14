"""Tests the routes in the `view_usage` blueprint."""
########## Passing 2023-08-11 ##########

import pytest
import logging
from pathlib import Path
import os
from random import choice
from bs4 import BeautifulSoup
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *
from nolcat.view_usage import *

log = logging.getLogger(__name__)


def test_view_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    page = client.get('/view_usage/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'view_usage', 'templates', 'view_usage', 'index.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_run_custom_SQL_query(client, header_value):
    """Tests running a user-written SQL query against the database and returning a CSV download."""
    POST_response = client.post(
        '/view_usage/custom-SQL',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data="SELECT COUNT(*) FROM COUNTERData;",
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    log.info(f"`POST_response.history` (type {type(POST_response.history)}) is\n{POST_response.history}")
    log.info(f"`POST_response.data` (type {type(POST_response.data)}) is\n{POST_response.data}")
    df = pd.read_csv(
        Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'view_usage', 'NoLCAT_download.csv'),
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    log.info(f"`df` is\n{df}")
    log.info(f"`df.iloc[0][0]` (type {type(df.iloc[0][0])}) is {df.iloc[0][0]}")

    assert POST_response.status == "200 OK"
    assert Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'view_usage', 'NoLCAT_download.csv').is_file()
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


def test_use_predefined_SQL_query_with_COUNTER_standard_views(engine, client, header_value):
    """Tests running one of the provided SQL queries which match the definitions of the COUNTER R5 standard views against the database and returning a CSV download."""
    query_options = choice(
        ("PR_P1", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='PR' AND access_method='Regular' AND (metric_type='Searches_Platform' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("DR_D1", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='DR' AND access_method='Regular'AND (metric_type='Searches_Automated' OR metric_type='Searches_Federated' OR metric_type='Searches_Regular' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests');"),
        ("DR_D2", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='DR' AND access_method='Regular'AND (metric_type='Limit_Exceeded' OR metric_type='No_License');"),
        ("TR_B1", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular'AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("TR_B2", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Book' AND access_method='Regular'AND (metric_type='Limit_Exceeded' OR metric_type='No_License');"),
        ("TR_B3", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Book' AND access_method='Regular'AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests');"),
        ("TR_J1", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("TR_J2", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Journal' AND access_method='Regular'AND (metric_type='Limit_Exceeded' OR metric_type='No_License');"),
        ("TR_J3", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Journal' AND access_method='Regular'AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' Or metric_type='Unique_Item_Investigations' Or metric_type='Unique_Item_Requests');"),
        ("TR_J4", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("IR_A1", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='IR' AND data_type='Article' AND access_method='Regular' AND parent_data_type='Journal'AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("IR_M1", "SELECT * FROM COUNTERDataWHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01'AND report_type='IR' AND data_type='Multimedia' AND access_method='Regular'AND metric_type='Total_Item_Requests';"),
    )
    form_input = {
        'begin_date': '2016-07-01',
        'end_date': '2020-06-01',
        'query_options': query_options[0],
    }
    POST_response = client.post(
        '/view_usage/query-wizard',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    log.info(f"`POST_response.history` (type {type(POST_response.history)}) is\n{POST_response.history}")
    log.info(f"`POST_response.data` (type {type(POST_response.data)}) is\n{POST_response.data}")

    CSV_df = pd.read_csv(
        Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'view_usage', 'NoLCAT_download.csv'),
        index_col='COUNTER_data_ID',
        parse_dates=['publication_date', 'parent_publication_date', 'usage_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    CSV_df = CSV_df.astype(COUNTERData.state_data_types())
    database_df = pd.read_sql(
        sql=query_options[1],
        con=engine,
        index_col='COUNTER_data_ID',
    )
    database_df = database_df.astype(COUNTERData.state_data_types())

    assert POST_response.status == "200 OK"
    assert Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'view_usage', 'NoLCAT_download.csv').is_file()
    assert_frame_equal(CSV_df, database_df)
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


def test_use_predefined_SQL_query_with_wizard():
    """Tests running a SQL query constructed using the SQL query construction wizard and returning a CSV download."""
    #ToDo: Write test
    pass


def test_GET_request_for_download_non_COUNTER_usage(client):
    """Tests that the page for downloading non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    page = client.get('/view_usage/non-COUNTER-downloads')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Get the values from the SQL query in the best way for the purpose of comparison

    with open(Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1], 'nolcat', 'view_usage', 'templates', 'view_usage', 'download-non-COUNTER-usage.html'), 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
        #ToDo: Get the list of file path options presented for populating the drop-down

    #ToDo: `assert page.status == "200 OK"` when route is completed
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    #ToDo: Compare the possible file download options


def test_download_non_COUNTER_usage():
    """Tests downloading the file at the path selected in the `view_usage.ChooseNonCOUNTERDownloadForm` form."""
    #ToDo: Write test
    pass