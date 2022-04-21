"""Tests the routes in the `view_sources` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.view_sources import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for route to view statistics sources list


#ToDo: Create test for route to view resource sources list


#ToDo: Create test for route to add a new statistics source


#ToDo: Create test for route to add a new resource source


#ToDo: Create test for route to edit a statistics source


#ToDo: Create test for route to edit a resource source


#ToDo: Create test for route to add a new statistics source


#ToDo: Create test for route to add a new resource source


#ToDo: Create test for route to view statistics source details


#ToDo: Create test for route to view resource source details