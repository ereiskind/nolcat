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


@pytest.fixture
def create_statisticsSources_CSV_file(tmp_path, statisticsSources_relation):
    """Create a CSV file with the test data for the `statisticsSources_relation` relation, then removes the file at the end of the test."""
    yield statisticsSources_relation.to_csv(
        tmp_path / 'statisticsSources_relation.csv',
        index_label="statistics_source_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'statisticsSources_relation.csv')


@pytest.fixture
def create_statisticsSourceNotes_CSV_file(tmp_path, statisticsSourceNotes_relation):
    """Create a CSV file with the test data for the `statisticsSourceNotes_relation` relation, then removes the file at the end of the test."""
    yield statisticsSourceNotes_relation.to_csv(
        tmp_path / 'statisticsSourceNotes_relation.csv',
        index_label="statistics_source_notes_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'statisticsSourceNotes_relation.csv')


@pytest.fixture
def create_resourceSources_CSV_file(tmp_path, resourceSources_relation):
    """Create a CSV file with the test data for the `resourceSources_relation` relation, then removes the file at the end of the test."""
    yield resourceSources_relation.to_csv(
        tmp_path / 'resourceSources_relation.csv',
        index_label="resource_source_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'resourceSources_relation.csv')


@pytest.fixture
def create_resourceSourceNotes_CSV_file(tmp_path, resourceSourceNotes_relation):
    """Create a CSV file with the test data for the `resourceSourceNotes_relation` relation, then removes the file at the end of the test."""
    yield resourceSourceNotes_relation.to_csv(
        tmp_path / 'resourceSourceNotes_relation.csv',
        index_label="resource_source_notes_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'resourceSourceNotes_relation.csv')


@pytest.fixture
def create_statisticsResourceSources_CSV_file(tmp_path, statisticsResourceSources_relation):
    """Create a CSV file with the test data for the `statisticsResourceSources_relation` relation, then removes the file at the end of the test."""
    yield statisticsResourceSources_relation.to_csv(
        tmp_path / 'statisticsResourceSources_relation.csv',
        index_label=["SRS_statistics_source", "SRS_resource_source"],
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'statisticsResourceSources_relation.csv')


@pytest.fixture
def create_annualUsageCollectionTracking_CSV_file(tmp_path, annualUsageCollectionTracking_relation):
    """Create a CSV file with the test data for the `annualUsageCollectionTracking_relation` relation, then removes the file at the end of the test."""
    yield annualUsageCollectionTracking_relation.to_csv(
        tmp_path / 'annualUsageCollectionTracking_relation.csv',
        index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'annualUsageCollectionTracking_relation.csv')


@pytest.fixture
def create_COUNTERData_CSV_file(tmp_path, COUNTERData_relation):
    """Create a CSV file with the test data for the `COUNTERData_relation` relation, then removes the file at the end of the test."""
    yield COUNTERData_relation.to_csv(
        tmp_path / 'COUNTERData_relation.csv',
        index_label="COUNTER_data_ID",
        encoding='utf-8',
        errors='backslashreplace',  
    )
    os.remove(tmp_path / 'COUNTERData_relation.csv')


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
def test_collect_initial_relation_data(tmp_path, header_value, client):
    """Tests uploading CSVs with data related to usage collection and loading that data into the database."""
    POST_request = client.post('/initialization/', data={
        'fiscalYears_CSV': tmp_path / 'fiscalYears_relation.csv',
        'vendors_CSV': tmp_path / 'vendors_relation.csv',
        'vendorNotes_CSV': tmp_path / 'vendorNotes_relation.csv',
        'statisticsSources_CSV': tmp_path / 'statisticsSources_relation.csv',
        'statisticsSourceNotes_CSV': tmp_path / 'statisticsSourceNotes_relation.csv',
        'resourceSources_CSV': tmp_path / 'resourceSources_relation.csv',
        'resourceSourceNotes_CSV': tmp_path / 'resourceSourceNotes_relation.csv',
        'statisticsResourceSources_CSV': tmp_path / 'statisticsResourceSources_relation.csv',
    }, timeout=90, headers=header_value)  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    print(f"`POST_request.content`: {POST_request.content}")
    print(f"`POST_request.encoding`: {POST_request.encoding}")
    print(f"`POST_request.raise_for_status()`: {POST_request.raise_for_status()}")
    print(f"`POST_request.status_code`: {POST_request.status_code}")
    print(f"`POST_request.text`: {POST_request.text}")
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