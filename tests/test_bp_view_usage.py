"""Tests the routes in the `view_usage` blueprint."""
########## Passing 2023-08-11 ##########

import pytest
import logging
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
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


def test_use_predefined_SQL_query_with_COUNTER_standard_views():
    """Tests running one of the provided SQL queries which match the definitions of the COUNTER R5 standard views against the database and returning a CSV download."""
    #ToDo: Write test
    pass


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