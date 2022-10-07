"""Tests the routes in the `view_vendors` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.view_vendors import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for route to view vendors list


#ToDo: Create test for route to add a new vendor


#ToDo: Create test for route to edit a vendor


#ToDo: Create test for route to view vendor details