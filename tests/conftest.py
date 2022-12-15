"""This module contains the fixtures and configurations for testing.

The fixtures for connecting to the database are primarily based upon the fixtures at https://github.com/alysivji/flask-family-tree-api/blob/master/tests/conftest.py. The test data is a small subset of the institution's own data, with usage numbers changes for confidentiality, with items selected to contain as many edge cases as possible. All test data is stored in dataframes in other files to remove encoding issues that might arise when reading data in from a tabular file but still allow the data to be exported to a tabular file.
"""

import pytest

from nolcat.app import db as _db
from nolcat.app import create_app
from data import relations


#Section: Fixtures for Connecting to the Database
@pytest.fixture(scope='session')
def app():
    """Creates an instance of the Flask object for the test session.
    
    This instance of the Flask object includes the application context (https://flask.palletsprojects.com/en/2.0.x/appcontext/) and thus access to application-level data, such as configurations, logging, and the database connection.
    """
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    context = app.app_context()  # Creates an application context
    context.push()  # Binds the application context to the current context/Flask application
    yield app
    context.pop()  # Removes and deletes the application context; placement after the yield statement means the action occurs at the end of the session


@pytest.fixture(scope='session')
def client(app):
    """Creates an instance of the Flask test client.
    
    The Flask test client lets tests make HTTP requests without running the server.
    """
    yield app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """Creates a temporary copy of the database for testing.
    
    The variable of the first statement, `_db.app`, is the Flask-SQLAlchemy integration's attribute for the Flask application (context). As a result, the fixture's first statement connects the Flask-SQLAlchemy integration to the Flask application (context) being used for testing.
    """
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()  # Drops all the tables created at the beginning of the session; placement after the yield statement means the action occurs at the end of the session


@pytest.fixture(scope='module')
def session():
    """A fixture creating a session for a module, enabling CRUD transactions, then rolling all of them back once the module's tests are complete.
    
    The scope of the fixture is set to module because setting the scope to `function` would prevent tests from building upon one another--for example, to test loading data with foreign keys in an environment whereCRUD operations were rolled back after every test function, the function would need to load the data from which the foreign keys derive and then the data containing the foreign keys; when the session covers the entire module, the data in the database from a previous test for loading data can be used as the reference for the foreign keys.
    """
    #ToDo: Even with `-s` flag, neither `print` nor `sys.stdout.write` output f-strings to the console, so the exact nature and types of the variables invoked below are unknown
    engine = db.engine  #ALERT: `RuntimeError: No application found. Either work inside a view function or push an application context. See http://flask-sqlalchemy.pocoo.org/contexts/.` upon running test_flask_factory_pattern.test_loading_data_into_relation and test_flask_factory_pattern.test_loading_connected_data_into_other_relation
    connection = engine.connect()  # Creates a connection to the database
    transaction = connection.begin()  # Begins a transaction
    options = dict(bind=connection, binds={})  #ToDo: What does this do?
    session = db.create_scoped_session(options=options)  # Creates the scoped session; `session = sessionmaker(bind=connection)` in SQLAlchemy alone
    # db.session = session  #ToDo: What does this do?
    yield session
    transaction.rollback()
    connection.close()
    session.remove()  # `session.close()` in SQLAlchemy alone


#Section: Data for Sources of Resources and Statistics
@pytest.fixture
def fiscalYears_relation():
    """Creates a dataframe that can be loaded into the `fiscalYears` relation."""
    yield relations.fiscalYears_relation()


@pytest.fixture
def vendors_relation():
    """Creates a dataframe that can be loaded into the `vendors` relation."""
    yield relations.vendors_relation()


@pytest.fixture
def vendorNotes_relation():
    """Creates a dataframe that can be loaded into the `vendorNotes` relation."""
    yield relations.vendorNotes_relation()


@pytest.fixture
def statisticsSources_relation():
    """Creates a dataframe that can be loaded into the `statisticsSources` relation."""
    yield relations.statisticsSources_relation()


@pytest.fixture
def statisticsSourceNotes_relation():
    """Creates a dataframe that can be loaded into the `statisticsSourceNotes` relation."""
    yield relations.statisticsSourceNotes_relation()


@pytest.fixture
def resourceSources_relation():
    """Creates a dataframe that can be loaded into the `resourceSources` relation."""
    yield relations.resourceSources_relation()


@pytest.fixture
def resourceSourceNotes_relation():
    """Creates a dataframe that can be loaded into the `resourceSourceNotes` relation."""
    yield relations.resourceSourceNotes_relation()


@pytest.fixture
def statisticsResourceSources_relation():
    """Creates a series that can be loaded into the `statisticsResourceSources` relation."""
    yield relations.statisticsResourceSources_relation()


@pytest.fixture
def annualUsageCollectionTracking_relation():
    """Creates a dataframe that can be loaded into the `annualUsageCollectionTracking` relation."""
    yield relations.annualUsageCollectionTracking_relation()


#Section: Data for Resources (from samples based on ProQuest, EBSCOhost, Gale Cengage Learning reports)
@pytest.fixture
def resources_relation():
    """Creates a series that can be loaded into the `resources` relation."""
    yield relations.resources_relation()


@pytest.fixture
def resourceMetadata_relation():
    """Creates a dataframe that can be loaded into the `resourceMetadata` relation."""
    yield relations.resourceMetadata_relation()


@pytest.fixture
def resourcePlatforms_relation():
    """Creates a dataframe that can be loaded into the `resourcePlatforms` relation."""
    yield relations.resourcePlatforms_relation()


@pytest.fixture
def usageData_relation():
    """Creates a dataframe that can be loaded into the `usageData` relation."""
    yield relations.usageData_relation()