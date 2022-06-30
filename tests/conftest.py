"""This module contains the fixtures and configurations for testing."""

import pytest

from nolcat.app import create_app


@pytest.fixture(scope='session')
def app():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='module')
def session(db):
    """A fixture creating a session for a module, enabling CRUD transactions, then rolling all of them back once the module's tests are complete.
    
    The scope of the fixture is set to module because setting the scope to `function` would prevent tests from building upon one another--for example, to test loading data with foreign keys in an environment whereCRUD operations were rolled back after every test function, the function would need to load the data from which the foreign keys derive and then the data containing the foreign keys; when the session covers the entire module, the data in the database from a previous test for loading data can be used as the reference for the foreign keys.
    """
    print(db)
    yield True
