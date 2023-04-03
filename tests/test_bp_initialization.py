"""Tests the routes in the `initialization` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.app import date_parser
from nolcat.initialization import *


#Section: Fixtures
@pytest.fixture
def create_fiscalYears_CSV_file(tmp_path, fiscalYears_relation):
    """Create a CSV file with the test data for the `fiscalYears` relation, then removes the file at the end of the test."""
    yield fiscalYears_relation.to_csv(
        tmp_path / 'fiscalYears_relation.csv',
        index_label="fiscal_year_ID",
        encoding='utf-8',
        errors='backslashreplace',  
    )
    os.remove(tmp_path / 'fiscalYears_relation.csv')


@pytest.fixture
def create_vendors_CSV_file(tmp_path, vendors_relation):
    """Create a CSV file with the test data for the `vendors` relation, then removes the file at the end of the test."""
    yield vendors_relation.to_csv(
        tmp_path / 'vendors_relation.csv',
        index_label="vendor_ID",
        encoding='utf-8',
        errors='backslashreplace',  
    )
    os.remove(tmp_path / 'vendors_relation.csv')


@pytest.fixture
def create_vendorNotes_CSV_file(tmp_path, vendorNotes_relation):
    """Create a CSV file with the test data for the `vendorNotes_relation` relation, then removes the file at the end of the test."""
    yield vendorNotes_relation.to_csv(
        tmp_path / 'vendorNotes_relation.csv',
        index_label="vendor_notes_ID",
        encoding='utf-8',
        errors='backslashreplace',  
    )
    os.remove(tmp_path / 'vendorNotes_relation.csv')


#Section: Tests
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
def test_collect_initial_relation_data(tmp_path, create_fiscalYears_CSV_file, create_vendors_CSV_file):
    """Tests uploading CSVs with data related to usage collection and loading that data into the database."""
    fiscalYears_CSV = pd.read_csv(
        tmp_path / 'fiscalYears_relation.csv',
        index_col="fiscal_year_ID",
        parse_dates=['start_date', 'end_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    vendors_CSV = pd.read_csv(
        tmp_path / 'vendors_relation.csv',
        index_col='vendor_ID',
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    print(f"The `vendors` CSV data:\n{vendors_CSV}")
    print(f"The `fiscalYears` CSV data:\n{fiscalYears_CSV}")
    #ToDo: Get the fixtures representing the relations in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Submit the files to the form on the page
    #ToDo: At or after function return statement/redirect, query database for `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations and ensure results match files used for submitting data and/or `conftest.py`
    assert True


@pytest.mark.dependency(depends=['test_collect_initial_relation_data'])
def test_GET_request_for_collect_AUCT_and_historical_COUNTER_data():
    """Test creating the AUCT relation template CSV."""
    #ToDo: Enter route function with `if request.method == 'GET':`
    #ToDo: Create pathlib.Path variable for location of CSV created below
    #ToDo: tests.data.relations.annualUsageCollectionTracking_relation.to_CSV(
    #     pathlib.Path variable
    #     index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
    #     encoding='utf-8',
    #     errors='backslashreplace',  
    # )
    #ToDo: Create pathlib.Path variable for location of CSV file created by route function at location it's saved to
    #ToDo: When download functionality is set up, capture downloaded CSV instead
    #ToDo: Compare the contents of the files at the locations of the two pathlib.Path variables
    pass


@pytest.mark.dependency(depends=['test_GET_request_for_collect_AUCT_and_historical_COUNTER_data'])
def test_collect_AUCT_and_historical_COUNTER_data():
    """Tests uploading the AUCT relation CSV and historical tabular COUNTER reports and loading that data into the database."""
    #ToDo: Get the fixture representing the AUCT relation in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Get other files to serve as temp tabular COUNTER report files
    #ToDo: Submit the files to the appropriate forms on the page
    #ToDo: At or after function return statement/redirect, query database for `annualUsageCollectionTracking` and `COUNTERData` relations and ensure results match files used for submitting data and/or `conftest.py`
    pass


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


def test_file_removal():
    """Removes all the files created in previous test functions.
    
    Fixtures in the conftest module cannot be used to create files, but for some functions, the desired output is a file based on a conftest fixture. To ensure the exact output is being compared, files are created in the test functions. To ensure those files don't remain in the repo, this test function removes the created files at the end of this test module.
    """
    #ToDo: os.remove(pathlib.Path variable for location of CSV created in `test_GET_request_for_collect_AUCT_and_historical_COUNTER_data`)
    assert True