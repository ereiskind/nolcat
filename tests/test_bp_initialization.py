"""Tests the routes in the `initialization` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.initialization import *


def test_GET_request_for_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'initialization', 'templates', 'initialization', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


def test_download_file():
    """Tests the route enabling file downloads."""
    #ToDo: How can this route be tested?
    pass


@pytest.mark.dependency()
def test_submitting_collect_initial_relation_data():
    """Tests uploading CSVs with data related to usage collection and loading that data into the database."""
    #ToDo: Get the fixtures representing the relations in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Submit the files to the form on the page
    #ToDo: At or after function return statement/redirect, query database for `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations and ensure results match files used for submitting data and/or `conftest.py`
    pass


@pytest.mark.dependency(depends=['test_submitting_collect_initial_relation_data'])
def test_requesting_collect_AUCT_and_historical_COUNTER_data():
    """Test creating the AUCT relation template CSV."""
    #ToDo: Enter route function with `if request.method == 'GET':`
    #ToDo: Create CSV file (function through `CSV_file.close()`)
    #ToDo: Compare CSV file to contents of existing CSV file which aligns with what result should be saved in `tests` folder
    pass
    

@pytest.mark.dependency(depends=['test_requesting_collect_AUCT_and_historical_COUNTER_data'])
def test_submitting_collect_AUCT_and_historical_COUNTER_data():
    """Tests uploading the AUCT relation CSV and historical tabular COUNTER reports and loading that data into the database."""
    #ToDo: Get the fixture representing the AUCT relation in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Get other files to serve as temp tabular COUNTER report files
    #ToDo: Submit the files to the appropriate forms on the page
    #ToDo: At or after function return statement/redirect, query database for `annualUsageCollectionTracking` and `COUNTERData` relations and ensure results match files used for submitting data and/or `conftest.py`
    pass


@pytest.mark.dependency(depends=['test_requesting_collect_AUCT_and_historical_COUNTER_data'])
def test_requesting_upload_historical_non_COUNTER_usage():
    """Tests creating a form with the option to upload a file for each statistics source and fiscal year combination that's not COUNTER-compliant."""
    #ToDo: Render the page
    #ToDo: Compare the fields in the form on the page to a static list of the test data values that meet the requirements
    pass


@pytest.mark.dependency(depends=['test_requesting_upload_historical_non_COUNTER_usage'])
def test_submitting_upload_historical_non_COUNTER_usage():
    """Tests uploading the files with non-COUNTER usage statistics."""
    #ToDo: Get the file paths out of the AUCT relation
    #ToDo: For each file path, get the file at that path and compare its contents to the test data file used to create it
    pass


def test_requesting_data_load_complete():
    """Tests calling the route and subsequently rendering the page."""
    #ToDo: A direct call to `data_load_complete()` just renders a page in the browser--does this need a test?
    pass