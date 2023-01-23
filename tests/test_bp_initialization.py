"""Tests the routes in the `initialization` blueprint."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.initialization import *


@pytest.fixture(scope='module')
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create fixtures for other files that are uploaded that will need to remove themselves from the system at the end of the test


def test_download_file():
    """Tests the route enabling file downloads."""
    #ToDo: How can this route be tested?
    pass


def test_requesting_collect_initial_relation_data():
    """Tests calling the route and subsequently rendering the page."""
    #ToDo: The call to `collect_initial_relation_data()` without data to validate just renders a page in the browser--does this need a test?
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