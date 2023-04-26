"""Tests the methods in FiscalYears."""

import pytest
from datetime import date
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.models import FiscalYears


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
    #ToDo: retrieved_data = read AUCT relation out of database
    #ToDo: expected_output_data = dataframe of what AUCT relation should contain
    #ToDo: assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes
    pass


def test_collect_fiscal_year_usage_statistics():
    """Create a test calling the StatisticsSources._harvest_R5_SUSHI method with the FiscalYears.start_date and FiscalYears.end_date as the arguments."""
    #ToDo: With each year's results changing, and with each API call having the date and time of the call in it, how can matching be done?
    pass