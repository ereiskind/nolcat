"""Tests the routes in the `view_lists` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.view_lists import *


def test_view_lists_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #ToDo: Either randomly choose from or iterate through the route options = ["resources", "statistics", "vendors"]
    #Section: Get Data from `GET` Requested Page
    #homepage = client.get('/view_lists/')  #ToDo: Add variable route element
    #GET_soup = BeautifulSoup(homepage.data, 'lxml')
    #GET_response_title = GET_soup.head.title
    #GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    #with open(Path(os.getcwd(), 'nolcat', 'view_lists', 'templates', 'view_lists', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
    #    file_soup = BeautifulSoup(HTML_file, 'lxml')
    #    HTML_file_title = file_soup.head.title  #ToDo: Replace `{{ title }}` with value from route function corresponding to the string in the homepage route
    #    HTML_file_page_title = file_soup.body.h1  #ToDo: Replace `{{ title }}` with value from route function corresponding to the string in the homepage route

    #assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title
    pass


def test_GET_request_for_view_list_record():
    """Tests that the page with a record's details and affiliated notes can be successfully GET requested."""
    #ToDo: Write test
    pass


def test_view_list_record():
    """Tests adding a record to the notes relation appropriate for the record the note is being added to.
    
    The function name derives from the fact that adding a note is the behavior after `validate_on_submit()` in the `view_list_record()` route.
    """
    #ToDo: Write test
    pass


def test_GET_request_for_edit_list_record_for_existing_record():
    """Tests rendering the page with the edit record form prefilled with values from an existing record."""
    #ToDo: Write test
    pass


def test_GET_request_for_edit_list_record_for_new_record():
    """Tests rendering a blank edit record form page."""
    #ToDo: Write test
    pass


def test_edit_list_record():
    """Tests changing values in a given record."""
    #ToDo: Write test
    pass