"""Tests the methods in FiscalYears."""
########## Passing 2023-06-07 ##########

import pytest
from datetime import date
import pandas as pd
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *


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


def test_create_usage_tracking_records_for_fiscal_year(engine, client):
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
        name='fiscalYears',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index=True,
        index_label='fiscal_year_ID',
    )
    with client:  # `client` fixture results from `test_client()` method, without which, the error `RuntimeError: No application found.` is raised; using the test client as a solution for this error comes from https://stackoverflow.com/a/67314104
        method_result = FY_instance.create_usage_tracking_records_for_fiscal_year()
    if "error" in method_result:  # If this is true,  pass
        assert False  # If the code comes here, the new AUCT records weren't successfully loaded into the relation; failing the test here means not needing add handling for this error to the database I/O later in the test
    
    #Section: Create and Compare Dataframes
    retrieved_data = pd.read_sql(
        sql="SELECT * FROM annualUsageCollectionTracking;",
        con=engine,
        index_col=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    retrieved_data = retrieved_data.astype({
        "collection_status": AnnualUsageCollectionTracking.state_data_types()["collection_status"],
        "usage_file_path": AnnualUsageCollectionTracking.state_data_types()["usage_file_path"],
        "notes": AnnualUsageCollectionTracking.state_data_types()["notes"],
    })
    retrieved_data['usage_is_being_collected'] = restore_boolean_values_to_boolean_field(retrieved_data['usage_is_being_collected'])
    retrieved_data['manual_collection_required'] = restore_boolean_values_to_boolean_field(retrieved_data['manual_collection_required'])
    retrieved_data['collection_via_email'] = restore_boolean_values_to_boolean_field(retrieved_data['collection_via_email'])
    retrieved_data['is_COUNTER_compliant'] = restore_boolean_values_to_boolean_field(retrieved_data['is_COUNTER_compliant'])
    
    multiindex = pd.MultiIndex.from_tuples(  # MySQL returns results sorted by index; the order of the dataframe elements below copies that order
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
            (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
            (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
            (7, 0), (7, 1), (7, 2),
            (8, 0), (8, 1), (8, 2),
            (9, 3), (9, 4), (9, 5), (9, 6),
            (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6),
            (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6),
        ],
        names=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    expected_output_data = pd.DataFrame(
        [
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Simulating a resource that's become COUNTER compliant"],
            [True, True, False, True, "No usage to report", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Ended subscription, only Med has content now"],
            [False, False, False, False, "N/A: Paid by Med", None, "Still have access to content through Med"],
            [None, None, None, None, None, None, None],

            [True, True, True, False, "Collection complete", None, "Simulating a resource with usage requested by sending an email"],
            [True, True, True, False, "Collection in process (see notes)", None, "When sending the email, note the date sent and who it was sent to"],
            [True, True, True, False, "Collection in process (see notes)", None, "Having the note about sending the email lets you know if you're in the response window, if you need to follow up, or if too much time has passed for a response to be expected"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [True, True, True, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, "Simulating a resource that becomes OA at the start of a calendar year"],
            [True, True, False, True, "Collection complete", None, "Resource became OA at start of calendar year 2018"],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [None, None, None, None, None, None, None],

            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],

            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],

            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [None, None, None, None, None, None, None],

            [True, True, True, False, "Usage not provided", None, "Simulating a resource that starts offering usage statistics"],
            [True, True, True, False, "Usage not provided", None, None],
            [True, True, False, False, "Collection complete", None, "This is the first FY with usage statistics"],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],
        ],
        index=multiindex,
        columns=["usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"],
    )
    expected_output_data = expected_output_data.astype(AnnualUsageCollectionTracking.state_data_types())
    
    assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes


def test_collect_fiscal_year_usage_statistics():
    """Create a test calling the StatisticsSources._harvest_R5_SUSHI method with the FiscalYears.start_date and FiscalYears.end_date as the arguments."""
    #ToDo: With each year's results changing, and with each API call having the date and time of the call in it, how can matching be done?
    pass