"""Tests the methods in StatisticsSources."""

import pytest
import pandas as pd
from sqlalchemy.orm import sessionmaker

from nolcat.SQLAlchemy_engine import engine as _engine
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE
from database_seeding_fixtures import vendors_relation
from database_seeding_fixtures import statisticsSources_relation


@pytest.fixture(scope="module")
def engine():
    """Creates a SQLAlchemy engine object by calling the `create_engine` function with the appropriate variables."""
    yield _engine()


@pytest.fixture(scope='module')
def session(engine):
    """Creates a SQLAlchemy session object so all tests in this module run within a transaction that will be rolled back once the tests are complete."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)
    yield session
    connection.close()
    session.close()
    transaction.rollback()


@pytest.fixture
def statisticsSources_fixture():
    """Creates a dataframe for loading into the statisticsSources relation with data for creating StatisticsSources objects.
    
    This fixture modifies the `statisticsSources_relation` fixture from the  `database_seeding_fixtures` helper module by replacing the values in `statisticsSources_relation['Statistics_Source_Retrieval_Code']` with random retrieval code values found in R5_SUSHI_credentials.json. As a result, methods including SUSHI API calls will have the data necessary to make the calls.
    """
    pass


def test_engine_creation(engine_fixture):
    """Test that a SQLAlchemy engine is created."""
    assert repr(type(engine_fixture)) == "<class 'sqlalchemy.engine.base.Engine'>"


def test_loading_into_relation(engine, vendors_relation, statisticsSources_fixture):
    """Test using the engine to load and query data.
    
    This is a basic integration test, determining if dataframes cna be loaded into the database and if data can be queried out of the database, not a StatisticsSources method test. All of those method tests, however, require the database I/O to be working and the existence of data in the `statisticsSources` and `vendors` relations; this test checks the former and ensures the latter.
    """
    #ToDo: Confirm that the imported fixture can be used as an argument directly
    pass