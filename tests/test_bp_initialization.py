"""Tests the routes in the `initialization` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.initialization import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test to confirm that form can successfully upload all CSV files
    #ToDo: Save CSV files with mock data in `tests/bin`
    #ToDo: Submit those CSVs with the form on the page
    #ToDo: Compare data from form submissions to dataframes with same data as in CSVs


#ToDo:Create test confirming the uploading of the data of the requested CSVs, the creation of the `annualUsageCollectionTracking` records, and the outputting of the CSV for that relation


#ToDo: Create test confirming route uploading CSV with data for `annualUsageCollectionTracking` records


#ToDo: Create test to upload formatter R4 reports into single RawCOUNTERReport object, then RawCOUNTERReport.perform_deduplication_matching


#ToDo: Create test for route showing data in database at end of initialization wizard