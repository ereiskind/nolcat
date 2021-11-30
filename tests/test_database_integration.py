"""This module contains the tests for database integration and SQLAlchemy."""

import pytest

from nolcat.app import engine

@pytest.fixture
def engine():
    """Recreates the SQLAlchemy engine for the web app as a fixture."""
    yield engine


def test_engine_creation():
    """Test that a SQLAlchemy engine can be created."""
    pass


def test_loading_into_relation():
    """Tests loading a single dataframe into a relation."""
    pass


def test_loading_into_database():
    """Tests breaking apart a dataframe and loading it into the database."""
    pass 