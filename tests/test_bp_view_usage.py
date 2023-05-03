"""Tests the routes in the `view_usage` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.view_usage import *


def test_view_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    page = client.get('/view_usage/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'view_usage', 'templates', 'view_usage', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert page.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_run_custom_SQL_query():
    """Tests running a user-written SQL query against the database and returning a CSV download."""
    #ToDo: Write test
    pass


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
    #Section: Get Data from `GET` Requested Page
    page = client.get('/view_usage/non-COUNTER-downloads')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Get the values from the SQL query in the best way for the purpose of comparison

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'view_usage', 'templates', 'view_usage', 'download-non-COUNTER-usage.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
        #ToDo: Get the list of file path options presented for populating the drop-down

    #assert page.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title  #ToDo: Compare the possible file download options; `page.status` may be 404 until route is completed
    assert HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title # `page.status` may be 404 until route is completed


def test_download_non_COUNTER_usage():
    """Tests downloading the file at the path selected in the `view_usage.ChooseNonCOUNTERDownloadForm` form."""
    #ToDo: Write test
    pass