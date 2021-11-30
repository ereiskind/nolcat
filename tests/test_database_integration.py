"""This module contains the tests for database integration and SQLAlchemy."""

import pytest
import pandas as pd

from nolcat.app import engine

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


def test_engine_creation():
    """Test that a SQLAlchemy engine can be created."""
    pass


def test_loading_into_relation():
    """Tests loading a single dataframe into a relation."""
    pass


def test_loading_into_database():
    """Tests breaking apart a dataframe and loading it into the database."""
    pass 