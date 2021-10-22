"""This module contains the tests for those classes representing relations used only in the `ingest` blueprint."""
import pytest

from nolcat.ingest import models


def test_harvest_R5_SUSHI():
    #ToDo: Write test for StatisticsSources._harvest_R5_SUSHI()
    #ToDo: For the compare value, what should be used? The timestamp field in the dataframe means the live API retrieval results can't be compared to a static file in full.
    pass


def test_collect_usage_statistics():
    #ToDo: Write test for StatisticsSources.collect_usage_statistics()
    pass


def test_collect_annual_usage_statistics():
    #ToDo: Write test for AnnualUsageCollectionTracking.collect_annual_usage_statistics()
    pass


def collect_fiscal_year_usage_statistics():
    #ToDo: Write test for FiscalYears.collect_fiscal_year_usage_statistics()
    pass