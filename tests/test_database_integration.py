"""This module contains the tests for database integration and SQLAlchemy."""

import pytest
import pandas as pd
from pandas._testing import assert_frame_equal

from nolcat.SQLAlchemy_engine import engine

from sqlalchemy import create_engine
from nolcat.SQLAlchemy_engine import DATABASE_SCHEMA_NAME
from nolcat.SQLAlchemy_engine import DATABASE_USERNAME
from nolcat.SQLAlchemy_engine import DATABASE_PASSWORD
from nolcat.SQLAlchemy_engine import DATABASE_HOST
from nolcat.SQLAlchemy_engine import DATABASE_PORT


@pytest.fixture
def engine():
    """Recreates the SQLAlchemy engine for the web app as a fixture."""
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
    """Test that a SQLAlchemy engine can be created."""
    #ToDo: Is this needed as a separate test, and if so, how should it be done?
    e = create_engine(f'mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}')
    print(repr(type(e)))
    print(repr(type(engine)))
    yield e == engine


def test_loading_into_relation(engine, resources_relation):
    """Tests loading a single dataframe into a relation."""
    print(repr(type(engine)))
    connection = engine.connect()
    print(repr(type(connection)))
    transaction = connection.begin()
    print(repr(type(connection)))
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

    assert_frame_equal(resources_relation, retrieved_data)
    transaction.rollback()


def test_loading_into_database():
    """Tests breaking apart a dataframe and loading it into the database."""
    pass 