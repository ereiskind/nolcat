"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import re
import pytest
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.raw_COUNTER_report import RawCOUNTERReport
from data import COUNTER_reports
from data import deduplication_data


#Section: Fixtures
@pytest.fixture
def sample_COUNTER_reports():
    """Creates a dataframe with the data from all the COUNTER reports."""
    yield COUNTER_reports.sample_COUNTER_reports()


@pytest.fixture
def sample_normalized_resource_data():
    """The dataframe returned by a `RawCOUNTERReport.normalized_resource_data()` method, which returns a dataframe of resource data from the `COUNTER_workbooks_for_tests` test data COUNTER reports."""
    yield deduplication_data.sample_normalized_resource_data()


@pytest.fixture
def matched_records():
    """Creates the set of record index matches not needing manual confirmation created by ``RawCOUNTERReport.perform_deduplication_matching()`` with the test data."""
    yield deduplication_data.matched_records()


@pytest.fixture
def matches_to_manually_confirm():
    """Creates the dictionary of metadata pairs and record index pair sets for manually confirming matches created by ``RawCOUNTERReport.perform_deduplication_matching()`` with the test data."""
    yield deduplication_data.matches_to_manually_confirm()


@pytest.fixture
def matched_records_including_sample_normalized_resource_data():
    """Creates the set of record index matches not needing manual confirmation created by ``RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data)`` with the test data."""
    yield deduplication_data.matched_records_including_sample_normalized_resource_data()


@pytest.fixture
def matches_to_manually_confirm_including_sample_normalized_resource_data():
    """Creates the dictionary of metadata pairs and record index pair sets for manually confirming matches created by ``RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data)`` with the test data."""
    yield deduplication_data.matches_to_manually_confirm_including_sample_normalized_resource_data()


@pytest.fixture
def sample_RawCOUNTERReport(sample_COUNTER_reports):
    """A RawCOUNTERReport object with the data from the `COUNTER_workbooks_for_tests` test data COUNTER reports."""
    yield RawCOUNTERReport(sample_COUNTER_reports)


@pytest.fixture
def another_sample_RawCOUNTERReport():
    """A RawCOUNTERReport object with different data than is in the `COUNTER_workbooks_for_tests` test data for loading into the database when the latter data set is already loaded."""
    #ToDo: Create small second set of COUNTER R5 data with some overlapping resources
    pass


#Section: Tests
# Some tests have preconditions that can be filled by other tests; the tests are ordered to utilize that fact instead of the order in which they appear in the class
#Subsection: Test `RawCOUNTERReport.perform_deduplication_matching()` Without Preexisting Data
#ToDo: Confirm constants exist for confirming all test results, then save those constants as dataframes in "tests/data/deduplication_data.py"
def test_perform_deduplication_matching(sample_RawCOUNTERReport, matched_records, matches_to_manually_confirm):
    """Tests the `perform_deduplication_matching()` method when a RawCOUNTERReport object instantiated from ingested COUNTER reports is loaded into an empty database."""
    #ToDo: As of 2022-12-19 with a t3.2xlarge instance, the test ended for no clear programmatic reason just after starting the "High Platform Name String Matching Threshold" section
    # Resources where an ISSN appears in both the Print_ISSN and Online_ISSN fields and/or is paired with different ISSNs still need to be paired
    assert sample_RawCOUNTERReport.perform_deduplication_matching() == (matched_records, matches_to_manually_confirm)


#Subsection: Test `RawCOUNTERReport.load_data_into_database()`
#ToDo: Determine what the input constant(s) should be for each function
def test_load_data_into_database():
    """Tests the `load_data_into_database()` method..."""
    #ToDo: Flesh out along with the method itself
    #ToDo: To test, pull the data from `COUNTER_reports.py` loaded into the database out of the database and compare it to the `data.relations` dataframes for the same relations
    pass


#Subsection: Test `RawCOUNTERReport.create_normalized_resource_data_argument()`
def test_create_normalized_resource_data_argument(sample_RawCOUNTERReport, sample_normalized_resource_data):
    """Tests the `create_normalized_resource_data_argument()` method when pulling from a database with resource data from R4 and R5 reports already loaded."""
    #ToDo: Ensure the data from `sample_COUNTER_reports` is in the database
    #ToDo: method_result = sample_RawCOUNTERReport.create_normalized_resource_data_argument()
    #ToDo: assert method_result.equals(sample_normalized_resource_data)
    pass


#Subsection: Test `RawCOUNTERReport.perform_deduplication_matching()` With Preexisting Data
def test_perform_deduplication_matching_with_data_from_TBD(another_sample_RawCOUNTERReport, sample_normalized_resource_data, matched_records_including_sample_normalized_resource_data, matches_to_manually_confirm_including_sample_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method when a RawCOUNTERReport object instantiated from ??? is loaded into a database with content."""
    # Resources where an ISSN appears in both the Print_ISSN and Online_ISSN fields and/or is paired with different ISSNs still need to be paired
    #assert another_sample_RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data) == (matched_records_including_sample_normalized_resource_data, matches_to_manually_confirm_including_sample_normalized_resource_data)
    pass