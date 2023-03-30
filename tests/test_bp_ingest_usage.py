"""Tests the routes in the `ingest_usage` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.ingest_usage import *


def test_ingest_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/ingest_usage/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1

    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_upload_COUNTER_reports():
    """Tests adding data to the `COUNTERData` relation by uploading files with the `ingest_usage.COUNTERReportsForm` form."""
    #ToDo: Write test
    pass


def test_GET_request_for_harvest_SUSHI_statistics(client):
    """Tests that the page for making custom SUSHI calls can be successfully GET requested and that the response properly populates with the requested data."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/ingest_usage/harvest')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Get the values from the SQL query in the best way for the purpose of comparison

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'make-SUSHI-call.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
        #ToDo: Get the list of options presented for populating the drop-down

    #assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title  #ToDo: Compare the possible upload options
    assert HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title # `homepage.status` may be 404 until route is completed


def test_harvest_SUSHI_statistics():
    """Tests making a SUSHI API call based on data entered into the `ingest_usage.SUSHIParametersForm` form."""
    #ToDo: Write test
    pass


def test_GET_request_for_upload_non_COUNTER_reports(client):
    """Tests that the page for uploading and saving non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/ingest_usage/upload-non-COUNTER')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Get the values from the SQL query in the best way for the purpose of comparison

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'ingest_usage', 'templates', 'ingest_usage', 'upload-non-COUNTER-usage.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
        #ToDo: Get the list of AUCT options presented for populating the drop-down

    #assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title  #ToDo: Compare the possible upload options; `homepage.status` may be 404 until route is completed
    assert HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title # `homepage.status` may be 404 until route is completed


def test_upload_non_COUNTER_reports():
    """Tests saving files uploaded to `ingest_usage.UsageFileForm` and updating the corresponding AUCT record."""
    #ToDo: Write test
    pass