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


#ToDo: Create fixture to load into the statisticsSources relation based on the import but replacing the values in statisticsSources_relation['Statistics_Source_Retrieval_Code'] with random retrieval code values found in R5_SUSHI_credentials.json


def test_engine_creation(engine_fixture):
    """Test that a SQLAlchemy engine is created."""
    assert repr(type(engine_fixture)) == "<class 'sqlalchemy.engine.base.Engine'>"


#ToDo: Load the imported vendors_relation dataframe and the above modified statisticsSources_relation dataframe into the database