"""Tests the routes in the `annual_stats` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.annual_stats import *


def test_GET_request_for_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    #ToDo: Should the dynamic values in the `annual_stats.ChooseFiscalYearForm.fiscal_year` also be captured and compared to the contents of `fiscalYears`?

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'annual_stats', 'templates', 'annual_stats', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_GET_request_for_FY_details_page():
    """Tests that the data for the given year from the `fiscalYears` and `annualUsageCollectionTracking` relations as well as the `annual_stats.RunAnnualStatsMethodsForm`, `annual_stats.EditFiscalYearForm`, and `annual_stats.EditAUCTForm` forms."""
    pass


def test_running_annual_statistics():
    """Tests requesting an annual report."""
    pass


def test_editing_fiscalYears_relation():
    """Tests changing the values in the fields of the displayed fiscal year."""
    pass


def test_editing_AUCT_relation():
    """Tests changing the values in the fields of one of the AUCT records being displayed."""
    pass