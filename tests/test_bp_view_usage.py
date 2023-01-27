"""Tests the routes in the `view_usage` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.view_usage import *


def test_GET_request_for_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'view_usage', 'templates', 'view_usage', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


#ToDo: Create test for `run_custom_SQL_query()` route method, which returns a CSV download


#ToDo: Create test for `use_predefined_SQL_query()` route method, which returns a CSV download, that starts with selecting one of the predefined queries


#ToDo: Create test for `use_predefined_SQL_query()` route method, which returns a CSV download, that starts with choosing to make a custom query with the query wizard


#ToDo: Create test for `download_non_COUNTER_usage()` route method, which is all about downloading files