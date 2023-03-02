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
    """Create a test for adding records to the annualUsageCollectionTracking relation for the instance's FY for every current statistics source."""
    #ToDo: Write test and docstring
    pass


def test_collect_fiscal_year_usage_statistics():
    """Create a test calling the StatisticsSources._harvest_R5_SUSHI method with the FiscalYears.start_date and FiscalYears.end_date as the arguments."""
    #ToDo: With each year's results changing, and with each API call having the date and time of the call in it, how can matching be done?
    pass