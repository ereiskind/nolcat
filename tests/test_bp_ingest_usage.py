"""Tests the routes in the `ingest_usage` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.ingest_usage import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for route to homepage/page for choosing usage ingest type, which is static


#ToDo: Create test for route for loading R4 report into database by comparing pd.from_sql of relations where the data was loaded to dataframes used to make the initial fixtures with data from uploaded report manually added


#ToDo: Create test for route for loading R5 report into database by comparing pd.from_sql of relations where the data was loaded to dataframes used to make the initial fixtures with data from uploaded report manually added


#ToDo: Create test to input the dates to use as arguments for StatisticsSources.collect_usage_statistics


#ToDo: Create test for route for adding non-COUNTER usage stats