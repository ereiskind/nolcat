"""This module contains the tests for database integration and SQLAlchemy."""

import pytest
from sqlalchemy import create_engine
import pandas as pd
from pandas._testing import assert_frame_equal

from nolcat import Database_Credentials
from database_seeding_fixtures import resources_relation


@pytest.fixture
def engine():
    """Creates a SQLAlchemy engine as a pytest fixture."""
    engine = create_engine(f'mysql+pymysql://{Database_Credentials.Username}:{Database_Credentials.Password}@{Database_Credentials.Host}:{Database_Credentials.Post}/nolcat_db_dev')
    yield engine


def test_engine_creation(engine):
    """Test that a SQLAlchemy engine is created."""
    assert repr(type(engine)) == "<class 'sqlalchemy.engine.base.Engine'>"


@pytest.mark.usefixtures('resources_relation')
def test_loading_into_relation(engine, resources_relation):
    """Tests loading a single dataframe into a relation."""
    connection = engine.connect()
    transaction = connection.begin()
    resources_relation.to_sql(
        name='resources',
        con=engine,
        if_exists='replace',  # This removes the existing data and replaces it with the data from the fixture, ensuring that PK duplication and PK-FK matching problems don't arise; the rollback at the end of the test restores the original data
        chunksize=1000,
        index=True,
        index_label='Resource_ID',
    )

    retrieved_data = pd.read_sql(
        sql="SELECT * FROM resources;",
        con=engine,
        index_col='Resource_ID',
    )

    print(f"\nInput:\n{resources_relation.head()}")
    print(f"\nOutput:\n{retrieved_data.head()}")

    assert_frame_equal(resources_relation, retrieved_data)
    transaction.rollback()


def test_loading_into_database():
    """Tests breaking apart a dataframe and loading it into the database."""
    pass 