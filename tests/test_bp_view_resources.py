"""Tests the routes in the `view_resources` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.view_resources import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for route to list of resources


#ToDo: Create test for route to add a new resource


#ToDo: Create test for route to edit a resource


#ToDo: Create test for route to view resource details