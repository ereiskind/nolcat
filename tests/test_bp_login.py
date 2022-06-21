"""Tests the routes in the `login` blueprint."""

import pytest

from nolcat.app import create_app
from nolcat.login import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test for logging in as regular user


#ToDo: Create test for logging in as admin user


#ToDo: Create test using Selenium to log in as a regular user


#ToDo: Create test using Selenium to log in as an admin user


#ToDo: If individual accounts are to be created, create test for making an account both with and without Selenium
