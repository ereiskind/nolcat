"""Tests the methods in Vendors."""
########## No tests written 2026-06-10 ##########

import pytest
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.models import *

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def Vendors_fixture(engine):
    """A fixture creating a `Vendors` object from a randomly selected record.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine

    Yields:
        nolcat.models.Vendors: a Vendors object
    """
    # Cannot use `caplog` for `query_database()` due to scope mismatch
    try:
        record = query_database(
            query="SELECT * FROM vendors;",
            engine=engine,
        )
    except DatabaseInteractionError as error:
        pytest.skip(f"Unable to create fixture--{error}")
    record = record.sample().reset_index()
    yield_object = Vendors(
        vendor_ID=record.at[0,'vendor_ID'],
        vendor_name=record.at[0,'vendor_name'],
    )
    log.info(initialize_relation_class_object_statement("Vendors", yield_object))
    yield yield_object


def test_get_statisticsSources_records():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_get_resourceSources_records():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_add_note(engine, Vendors_fixture, caplog):
    """Tests adding a record to the `vendorNotes` relation.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        Vendors_fixture (nolcat.models.Vendors): a Vendors object
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')

    try:
        update_result = Vendors_fixture.add_note("This is a new note", "The Author")
    except DatabaseInteractionError as error:
        pytest.skip(f"Unable to run test--{error}")
    assert update_result == "Successfully loaded 1 records into the `vendorNotes` relation."

    vendorNotes_df = pd.DataFrame(
        [
            ["No longer exists", "Jane Doe", "2022-11-30", 4],
            ["No longer exists", "Jane Doe", "2022-11-30", 5],
            ["No longer exists", "Jane Doe", "2022-11-30", 6],
            ["This is a new note", "The Author", date.today().strftime('%Y-%m-%d'), Vendors_fixture.vendor_ID],
        ],
        columns=["note", "written_by", "date_written", "vendor_ID"],
    )
    vendorNotes_df.index.name = "vendor_notes_ID"
    vendorNotes_df = vendorNotes_df.astype(VendorNotes.state_data_types())
    vendorNotes_df["date_written"] = pd.to_datetime(vendorNotes_df["date_written"])
    try:
        df = query_database(
            query=f"SELECT * FROM vendorNotes;",
            engine=engine,
            index='vendor_notes_ID',
        )
    except DatabaseInteractionError as error:
        pytest.skip(f"Unable to run test--{error}")
    df = df.astype(VendorNotes.state_data_types())
    assert_frame_equal(df, vendorNotes_df)