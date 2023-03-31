"""Tests the routes in the `initialization` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.initialization import *


def test_download_file():
    """Tests the route enabling file downloads."""
    #ToDo: How can this route be tested?
    pass


def test_GET_request_for_collect_initial_relation_data(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/initialization/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'initialization', 'templates', 'initialization', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1

    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


@pytest.mark.dependency()
def test_collect_initial_relation_data():
    """Tests uploading CSVs with data related to usage collection and loading that data into the database."""
    #ToDo: Get the fixtures representing the relations in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Submit the files to the form on the page
    #ToDo: At or after function return statement/redirect, query database for `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations and ensure results match files used for submitting data and/or `conftest.py`
    pass


@pytest.mark.dependency(depends=['test_collect_initial_relation_data'])
def test_GET_request_for_collect_AUCT_and_historical_COUNTER_data():
    """Test creating the AUCT relation template CSV."""
    df = pd.DataFrame(
        [
            ['a', 1, '2022-02-02'],
            ['b', pd.NA, '2023-02-02'],
            ['c', 3, '2022-02-02'],
        ],
        columns=['one', 'two', 'three'],
    )
    df.to_csv(
        'test.csv',
        index_label='index',
        date_format='%Y-%m-%d',
        encoding='utf-8',
        errors='backslashreplace',  # For encoding errors
    )
    #ToDo: Enter route function with `if request.method == 'GET':`
    #ToDo: Point to CSV file at location it's saved to
    #ToDo: When download functionality is set up, capture downloaded CSV
    #ToDo: Compare CSV file to contents of existing CSV file which aligns with what result should be saved in `tests` folder
    assert True


@pytest.mark.dependency(depends=['test_GET_request_for_collect_AUCT_and_historical_COUNTER_data'])
def test_collect_AUCT_and_historical_COUNTER_data():
    """Tests uploading the AUCT relation CSV and historical tabular COUNTER reports and loading that data into the database."""
    #ToDo: Get the fixture representing the AUCT relation in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Get other files to serve as temp tabular COUNTER report files
    #ToDo: Submit the files to the appropriate forms on the page
    #ToDo: At or after function return statement/redirect, query database for `annualUsageCollectionTracking` and `COUNTERData` relations and ensure results match files used for submitting data and/or `conftest.py`
    os.remove('test.csv')
    assert True


@pytest.mark.dependency(depends=['test_GET_request_for_collect_AUCT_and_historical_COUNTER_data'])
def test_GET_request_for_upload_historical_non_COUNTER_usage():
    """Tests creating a form with the option to upload a file for each statistics source and fiscal year combination that's not COUNTER-compliant."""
    #ToDo: Render the page
    #ToDo: Compare the fields in the form on the page to a static list of the test data values that meet the requirements
    pass


@pytest.mark.dependency(depends=['test_GET_request_for_upload_historical_non_COUNTER_usage'])
def test_upload_historical_non_COUNTER_usage():
    """Tests uploading the files with non-COUNTER usage statistics."""
    #ToDo: Get the file paths out of the AUCT relation
    #ToDo: For each file path, get the file at that path and compare its contents to the test data file used to create it
    pass


def test_data_load_complete():
    """Tests calling the route and subsequently rendering the page."""
    #ToDo: Write test once this route contains content for displaying the newly uploaded data in the browser
    pass