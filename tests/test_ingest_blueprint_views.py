"""This module contains the tests for the route functions in the `ingest` blueprint."""

import pytest

from nolcat.app import create_app


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Does `download_file(filename)` need its own test?


#ToDo: Make test for initialize_initial_relations():
    """Returns the page with for downloading the CSV templates for the fiscal year, vendor, resource source, and statistics source relations and uploading the initial data for those relations."""
    #ToDo: Incorporate the following functionality
        #ToDo: """Tests that the three CSVs that are uploaded in the `initialize_initial_relations` route can be uploaded successfully."""
        #ToDo: Create sample CSV files to use for this test
        #ToDo: Write this test


#ToDo: Make test for save_historical_collection_tracking_info():
    """Returns the page for downloading the CSV template for `annualUsageCollectionTracking` and uploading the initial data for that relation as well as formatting the historical R4 reports for upload."""


#ToDo: Make test for upload_historical_COUNTER_usage():
    """Returns the page for uploading reformatted COUNTER R4 CSVs."""


#ToDo: Make test for determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""


#ToDo: Make test for data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
