"""Tests the methods in FiscalYears."""

import pytest

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


def test_create_usage_tracking_records_for_fiscal_year():
    """Tests creating a record in the `annualUsageCollectionTracking` relation for the given fiscal year for each current statistics source."""
    #ToDo: Load dataframe for new record into `fiscalYears`
    #ToDo: Initialize `FiscalYears` object
    #ToDo: method_result = run method on `FiscalYears` object
    #ToDo: if "error" in method_result:
        #ToDo: test failed--know it won't pass, so stopping before any more database I/O
    #ToDo: retrieved_data = read AUCT relation out of database
    #ToDo: expected_output_data = dataframe of what AUCT relation should contain
    #ToDo: assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes
    pass


def test_collect_fiscal_year_usage_statistics():
    """Create a test calling the StatisticsSources._harvest_R5_SUSHI method with the FiscalYears.start_date and FiscalYears.end_date as the arguments."""
    #ToDo: With each year's results changing, and with each API call having the date and time of the call in it, how can matching be done?
    pass