"""Tests the methods in ResourceSources."""
########## No tests written 2026-06-10 ##########

import pytest
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.models import *

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def ResourceSources_fixture(engine):
    """A fixture creating a `ResourceSources` object from a randomly selected record.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine

    Yields:
        nolcat.models.ResourceSources: a ResourceSources object
    """
    # Cannot use `caplog` for `query_database()` due to scope mismatch
    try:
        record = query_database(
            query="SELECT * FROM resourceSources;",
            engine=engine,
        )
    except DatabaseInteractionError as error:
        pytest.skip(f"Unable to create fixture--{error}")
    record = record.sample().reset_index()
    yield_object = ResourceSources(
        resource_source_ID=record.at[0,'resource_source_ID'],
        resource_source_name=record.at[0,'resource_source_name'],
        source_in_use=record.at[0,'source_in_use'],
        access_stop_date=record.at[0,'access_stop_date'],
        vendor_ID=record.at[0,'vendor_ID'],
    )
    log.info(initialize_relation_class_object_statement("ResourceSources", yield_object))
    yield yield_object


def test_add_access_stop_date():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_remove_access_stop_date():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_change_StatisticsSource():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_add_note(engine, client, ResourceSources_fixture, caplog):
    """Tests adding a record to the `resourceSourceNotes` relation.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        client (flask.testing.FlaskClient): a Flask test client
        ResourceSources_fixture (nolcat.models.ResourceSources): a ResourceSources object
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')

    try:
        with client:
            update_result = ResourceSources_fixture.add_note("This is a new note", "The Author")
    except DatabaseInteractionError as error:
        pytest.skip(f"Unable to run test--{error}")
    assert update_result == "Successfully loaded 1 records into the `resourceSourceNotes` relation."

    resourceSourceNotes_df = pd.DataFrame(
        [
            ["Content migrated to Ebook Central", "Jane Doe", "2022-11-30", 12],
            ["Content migrated to Ebook Central", "Jane Doe", "2022-11-30", 13],
            ["Content migrated to Ebook Central", "Jane Doe", "2022-11-30", 17],
            ["This is a new note", "The Author", date.today().strftime('%Y-%m-%d'), ResourceSources_fixture.resource_source_ID],
        ],
        columns=["note", "written_by", "date_written", "resource_source_ID"],
    )
    resourceSourceNotes_df.index.name = "resource_source_notes_ID"
    resourceSourceNotes_df = resourceSourceNotes_df.astype(ResourceSourceNotes.state_data_types())
    resourceSourceNotes_df["date_written"] = pd.to_datetime(resourceSourceNotes_df["date_written"])
    try:
        df = query_database(
            query=f"SELECT * FROM resourceSourceNotes;",
            engine=engine,
            index='resource_source_notes_ID',
        )
    except DatabaseInteractionError as error:
        pytest.skip(f"Unable to run test--{error}")
    df = df.astype(ResourceSourceNotes.state_data_types())
    assert_frame_equal(df, resourceSourceNotes_df)