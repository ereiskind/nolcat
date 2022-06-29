"""This module contains the fixtures and configurations for testing."""

import pytest

from nolcat.app import create_app


@pytest.fixture
def app():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client