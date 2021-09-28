"""This module contains the tests for the Flask web app."""
# https://flask.palletsprojects.com/en/2.0.x/testing/
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/

import pytest

from nolcat.app import create_app


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


def test_flask_client_creation(flask_client):
    """Tests that the flask_client fixture works by invoking it in a test wth an assert statement set to `True`."""
    assert True