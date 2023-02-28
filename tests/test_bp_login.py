"""Tests the routes in the `login` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.login import *


def test_GET_request_for_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'login', 'templates', 'login', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


#ToDo: Create test for logging in as regular user


#ToDo: Create test for logging in as admin user


#ToDo: Create test to log in as a regular user


#ToDo: Create test to log in as an admin user


#ToDo: If individual accounts are to be created, create test for making an account