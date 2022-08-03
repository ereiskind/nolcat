"""Tests the routes in the `view_usage` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.view_usage import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for route to homepage, which is static


#ToDo: Create test for entering SQL into SQL query text box in form on SQL page and having the query run


#ToDo: Create tests for some of the saved queries, choosing specific options and comparing the returned value to what's known as the returned value in the database


#ToDo: Create test for the query wizard, confirming that selecting specific options sends a given SQL string to the database


#ToDo: Create a test for the query wizard, making specific selections and comparing the returned value to what's known as the returned value in the database