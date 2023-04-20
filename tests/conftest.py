"""This module contains the fixtures and configurations for testing.

The fixtures for connecting to the database are primarily based upon the fixtures at https://github.com/alysivji/flask-family-tree-api/blob/master/tests/conftest.py with some further modifications based on the code at https://spotofdata.com/flask-testing/. The test data is a small subset of the institution's own data, with usage numbers changes for confidentiality, with items selected to contain as many edge cases as possible. All test data is stored in dataframes in other files to remove encoding issues that might arise when reading data in from a tabular file but still allow the data to be exported to a tabular file.
"""

import pytest
from sqlalchemy import create_engine

from nolcat.app import db as _db
from nolcat.app import create_app
from nolcat.app import DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_SCHEMA_NAME
from nolcat.app import MAX_CONTENT_LENGTH_KB
from data import relations


#Section: Fixtures for Connecting to the Database
@pytest.fixture(scope='session')
def app():
    """Creates an instance of the Flask object for the test session.
    
    This instance of the Flask object includes the application context (https://flask.palletsprojects.com/en/2.0.x/appcontext/) and thus access to application-level data, such as configurations, logging, and the database connection.
    """
    app = create_app()
    app.debug = True
    app.testing = True  # Lets exceptions come through to test client
    app.env = 'test'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Explicitly set to disable warning in tests
    app.config['WTF_CSRF_ENABLED'] = False  # Without this, tests involving forms return a HTTP 400 error with the message `The CSRF token is missing.`
    app.config['MAX_CONTENT_LENGTH'] = 1024 * MAX_CONTENT_LENGTH_KB  # Number of bytes to read from incoming data; without setting this variable, the connection seems to be unexpectedly closed by the server when executing the `redirect` method
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
    print(f"\nAbout to run `_db.drop_all()` on {_db}.")  # The statement appears in stdout after all the tests in the module, but the database isn't being rolled back
    _db.drop_all()  # Drops all the tables created at the beginning of the session; placement after the yield statement means the action occurs at the end of the session


@pytest.fixture(scope="session")
def engine():
    """Creates a SQLAlchemy engine for testing.
    
    The engine object is the starting point for an SQLAlchemy application. Engines are a crucial intermediary object in how SQLAlchemy connects the user and the database.
    """
    yield create_engine(
        f'mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}',
        echo=True,
    )


@pytest.fixture(scope='module')
def session(engine, db):
    """Creates a database session for each test module, enabling CRUD transactions, then rolling all of them back once the module's tests are complete.
    
    First, the scope of the fixture is set to `module` because a scope of `function` would prohibit tests involving primary and foreign key relationships from using data loaded into the database during previous transactions, a more accurate reflection of actual database use. On the other hand, setting the scope to `session` would disallow the reuse of the test data, as loading test data sets multiple times would cause primary key duplication. Second, this fixture instantiates both database connection objects provided by SQLAlchemy. The connection object, used in SQLAlchemy Core and the SQL language, and the session object, used by the SQLAlchemy ORM, are both offered so the fixture can work with tests using the core or the ORM paradigm. The two objects are connected--session objects use connection objects as part of the database connection, and the fixture's session object explicitly uses its connection object.
    """
    #Section: Create Connections
    #Subsection: Create Connection Object (SQLAlchemy Core Connection)
    connection = db.engine.connect()  # Tutorials vary between `engine.connect()` or `db.engine.connect()`

    #Subsection: Create Session Object (SQLAlchemy ORM Connection)
    options = {
        'bind': connection,  # Tutorials vary between `'bind': connection,` and `'bind': engine,`
        'binds': {},  # This explicitly empty value seems to exist to force everything in the session object to use the connection object specified in `bind`
    }
    session = db.create_scoped_session(options=options)

    #Subsection: Yield Fixture
    transaction = connection.begin()
    db.session = session  # Sets the scoped session object created above equal to the Flask-SQLAlchemy integration's attribute for creating scoped sessions
    yield session

    #Section: Close and Remove Connections
    print(f"\nAbout to close/rollback/remove session {session}, transaction {transaction}, and connection {connection}.")  # The statement appears in stdout after all the tests in the module, but the database isn't being rolled back
    print("\nFocus on `transaction.rollback()`, `connection.close()`, and ``session.remove()")
    session.close()
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def header_value():
    """A dictionary containing a HTTP request header that makes the URL request appear to come from a Chrome browser and not the requests module; some platforms return 403 errors with the standard requests header."""
    return {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


#Section: Test Data for Relations
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


@pytest.fixture
def COUNTERData_relation():
    """Creates a dataframe that can be loaded into the `COUNTERData` relation."""
    yield relations.COUNTERData_relation()