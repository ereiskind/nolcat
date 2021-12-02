"""This module contains the tests for database integration and SQLAlchemy."""

import pytest
from sqlalchemy import create_engine
import pandas as pd
from pandas._testing import assert_frame_equal

from nolcat import Database_Credentials


@pytest.fixture
def engine():
    """Creates a SQLAlchemy engine as a pytest fixture."""
    engine = create_engine(f'mysql+pymysql://{Database_Credentials.Username}:{Database_Credentials.Password}@{Database_Credentials.Host}:{Database_Credentials.Post}/nolcat_db_dev')
    yield engine


@pytest.fixture
def resources_relation():
    """Creates a dataframe that can be loaded into the `resources` relation."""
    df = pd.DataFrame(
        [
            [None, None, "8755-4550", None, "Serial", None],
            [None, "978-0-585-03362-4", None, None, "Book", None],
        ],
        index=[1, 2],
        columns=["DOI", "ISBN", "Print_ISSN", "Online_ISSN", "Data_Type", "Section_Type"]
    )
    yield df


def test_engine_creation(engine):
    """Test that a SQLAlchemy engine is created."""
    assert repr(type(engine)) == "<class 'sqlalchemy.engine.base.Engine'>"


def test_loading_into_relation(engine, resources_relation):
    """Tests loading a single dataframe into a relation."""
    connection = engine.connect()
    transaction = connection.begin()
    resources_relation.to_sql(
        name='resources',
        con=engine,
        if_exists='replace',
        chunksize=1000,
        index=True,
        index_label='Resource_ID',
    )

    retrieved_data = pd.read_sql(
        sql="SELECT * FROM resources;",
        con=engine
    )

    print(resources_relation.head())
    print(retrieved_data.head())

    assert_frame_equal(resources_relation, retrieved_data)
    transaction.rollback()


def test_loading_into_database():
    """Tests breaking apart a dataframe and loading it into the database."""
    pass 