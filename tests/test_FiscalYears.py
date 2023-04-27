"""Tests the methods in FiscalYears."""

import pytest
from datetime import date
import pandas as pd
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import return_string_of_dataframe_info
from nolcat.models import FiscalYears


@pytest.fixture(scope='module')
def load_relation_data(engine, fiscalYears_relation, vendors_relation,  vendorNotes_relation, statisticsSources_relation, statisticsSourceNotes_relation, resourceSources_relation, resourceSourceNotes_relation, statisticsResourceSources_relation, AUCT_relation, COUNTERData_relation):
    """This fixture loads data into all the relations because all of the methods being tested in this module require there to be data in the database."""
    fiscalYears_relation.to_sql(
        'fiscalYears',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='fiscal_year_ID',
    )
    vendors_relation.to_sql(
        'vendors',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='vendor_ID',
    )
    vendorNotes_relation.to_sql(
        'vendorNotes',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='vendor_notes_ID',
    )
    statisticsSources_relation.to_sql(
        'statisticsSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='statistics_source_ID',
    )
    statisticsSourceNotes_relation.to_sql(
        'statisticsSourceNotes',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='statistics_source_notes_ID',
    )
    resourceSources_relation.to_sql(
        'resourceSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='resource_source_ID',
    )
    resourceSourceNotes_relation.to_sql(
        'resourceSourceNotes',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='resource_source_notes_ID',
    )
    statisticsResourceSources_relation.to_sql(
        'statisticsResourceSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label=['SRS_statistics_source', 'SRS_resource_source'],
    )
    AUCT_relation.to_sql(
        'annualUsageCollectionTracking',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label=['AUCT_statistics_source', 'AUCT_fiscal_year'],
    )
    COUNTERData_relation.to_sql(
        'COUNTERData',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='COUNTER_data_ID',
    )
    # Nothing is being returned, so no `yield` statement


def test_calculate_ACRL_60b():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ACRL_63():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ARL_18():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ARL_19():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ARL_20():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_create_usage_tracking_records_for_fiscal_year(engine):
    """Tests creating a record in the `annualUsageCollectionTracking` relation for the given fiscal year for each current statistics source.
    
    The test data AUCT relation includes all of the years in the fiscal years relation, so to avoid primary key duplication, a new record needs to be added to the `fiscalYears` relation and used for the method.
    """
    #Section: Create `FiscalYears` Object and `fiscalYears` Record
    primary_key_value = 6
    fiscal_year_value = "2023"
    start_date_value = date.fromisoformat('2022-07-01')
    end_date_value = date.fromisoformat('2023-06-30')

    FY_instance = FiscalYears(
        fiscal_year_ID = primary_key_value,
        fiscal_year = fiscal_year_value,
        start_date = start_date_value,
        end_date = end_date_value,
        ACRL_60b = None,
        ACRL_63 = None,
        ARL_18 = None,
        ARL_19 = None,
        ARL_20 = None,
        notes_on_statisticsSources_used = None,
        notes_on_corrections_after_submission = None,
    )
    FY_df = pd.DataFrame(
        [[fiscal_year_value, start_date_value, end_date_value, None, None, None, None, None, None, None]],
        index=[primary_key_value],
        columns=["fiscal_year", "start_date", "end_date", "ACRL_60b", "ACRL_63", "ARL_18", "ARL_19", "ARL_20", "notes_on_statisticsSources_used", "notes_on_corrections_after_submission"],
    )
    FY_df.index.name = "fiscal_year_ID"

    #Section: Update Relation and Run Method
    FY_df.to_sql(
        name='annualUsageCollectionTracking',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index=True,
        index_label='fiscal_year_ID',
    )
    method_result = FY_instance.create_usage_tracking_records_for_fiscal_year()
    if "error" in method_result:  # If this is true,  pass
        assert False  # If the code comes here, the new AUCT records weren't successfully loaded into the relation; failing the test here means not needing add handling for this error to the database I/O later in the test
    
    #Section: Create and Compare Dataframes
    retrieved_data = pd.read_sql(
        sql="SELECT * FROM annualUsageStatisticsTracking;",
        con=engine,
        index_col=['SRS_statistics_source', 'SRS_resource_source'],
    )
    print(f"Info on `retrieved_data` dataframe;\n{return_string_of_dataframe_info(retrieved_data)}")
    multiindex = pd.MultiIndex.from_tuples(
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 3), (8, 4), (8, 5), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5),  # Multiindex before method
            (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (9, 6), (10, 6), (11, 6),  # New values in multiindex
        ],
        names=["SRS_statistics_source", "SRS_resource_source"],
    )
    expected_output_data = pd.DataFrame(
        [
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],

            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Simulating a resource that's become COUNTER compliant"],
            [True, True, False, True, "No usage to report", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Ended subscription, only Med has content now"],
            [False, False, False, False, "N/A: Paid by Med", None, "Still have access to content through Med"],

            [True, True, True, False, "Collection complete", None, "Simulating a resource with usage requested by sending an email"],
            [True, True, True, False, "Collection in process (see notes)", None, "When sending the email, note the date sent and who it was sent to"],
            [True, True, True, False, "Collection in process (see notes)", None, "Having the note about sending the email lets you know if you're in the response window, if you need to follow up, or if too much time has passed for a response to be expected"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [True, True, True, False, "Collection not started", None, None],

            [True, True, False, True, "Collection complete", None, "Simulating a resource that becomes OA at the start of a calendar year"],
            [True, True, False, True, "Collection complete", None, "Resource became OA at start of calendar year 2018"],
            [False, False, False, False, "N/A: Open access", None, None],

            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],

            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],

            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection not started", None, None],

            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],

            [True, True, True, False, "Usage not provided", None, "Simulating a resource that starts offering usage statistics"],
            [True, True, True, False, "Usage not provided", None, None],
            [True, True, False, False, "Collection complete", None, "This is the first FY with usage statistics"],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection not started", None, None],

            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
        ],
        index=multiindex,
        columns=["usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"],
    )
    assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes


def test_collect_fiscal_year_usage_statistics():
    """Create a test calling the StatisticsSources._harvest_R5_SUSHI method with the FiscalYears.start_date and FiscalYears.end_date as the arguments."""
    #ToDo: With each year's results changing, and with each API call having the date and time of the call in it, how can matching be done?
    pass