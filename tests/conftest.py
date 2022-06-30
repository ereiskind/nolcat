"""This module contains the fixtures and configurations for testing."""

import sys
import pytest

from nolcat.app import db
from nolcat.app import create_app


@pytest.fixture(scope='session')
def app():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='module')
def session(db, request):
    """A fixture creating a session for a module, enabling CRUD transactions, then rolling all of them back once the module's tests are complete.
    
    The scope of the fixture is set to module because setting the scope to `function` would prevent tests from building upon one another--for example, to test loading data with foreign keys in an environment whereCRUD operations were rolled back after every test function, the function would need to load the data from which the foreign keys derive and then the data containing the foreign keys; when the session covers the entire module, the data in the database from a previous test for loading data can be used as the reference for the foreign keys.

    Args:
        db (_type_): the name of the database??? the connection to the database???
        request (pytest.FixtureRequest): a built-in fixture providing access to the requesting test's context (https://docs.pytest.org/en/7.1.x/reference/reference.html#request)
    """
    sys.stdout.write(f"`db` is {db} of type {repr(type(db))}")
    engine = db.engine
    sys.stdout.write(f"`engine` is {engine} of type {repr(type(engine))}")
    connection = engine.connect()  # Creates a connection to the database
    sys.stdout.write(f"`connection` is {connection} of type {repr(type(connection))}")
    transaction = connection.begin()  # Begins a transaction
    sys.stdout.write(f"`transaction` is {transaction} of type {repr(type(transaction))}")
    options = dict(bind=connection, binds={})  #ToDo: What does this do?
    session = db.create_scoped_session(options=options)  # Creates the scoped session; `session = sessionmaker(bind=connection)` in SQLAlchemy alone
    sys.stdout.write(f"`session` is {session} of type {repr(type(session))}")
    # db.session = session  #ToDo: What does this do?
    sys.stdout.write(f"`db.session` is {db.session} of type {repr(type(db.session))}")
    def teardown():
        """Rolls back, closes, and removes (garbage collects?) the session created for testing."""
        transaction.rollback()
        connection.close()
        session.remove()  # `session.close()` in SQLAlchemy alone
    request.addfinalizer(teardown)  # Runs the `teardown` subfunction after any test that uses this fixture
    yield session