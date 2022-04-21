"""Tests the routes in the `annual_stats` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.annual_stats import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for route to view homepagepage, which is static


#ToDo: Create test for route to page with details of a fiscal year (display of data in a given fiscalYears record)


#ToDo: Create test for route to page displaying all `annualUsageCollectionTracking` records for a given fiscal year (which will likely be indicated through a variable route)