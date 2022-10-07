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


#ToDo: Create test for InitialRelationDataForm (which also serves as test for `homepage` route)
    #ToDo: Submit TSV copies of data in conftest to form
    #ToDo: assert data from each form variable == corresponding fixture value


#ToDo: Create test for AUCTForm
    #ToDo: Submit TSV copies of data in conftest to form
    #ToDo: assert data from each form variable == corresponding fixture value


#ToDo: Create test for `wizard_page_2` route
    #ToDo: Confirm data can be read into pandas, then into the database
    #ToDo: Check by having cartesian product output from database query be compared to constant of what the value should be


#ToDo: Create test for creating and downloading "initialize_annualUsageCollectionTracking.tsv"


#ToDo: Create test for `wizard_page_3` route
    #ToDo: Confirm data can be read into pandas, then into the database


#ToDo: Create test to upload formatter R4 reports into single RawCOUNTERReport object, then RawCOUNTERReport.perform_deduplication_matching


#ToDo: Create test for route showing data in database at end of initialization wizard