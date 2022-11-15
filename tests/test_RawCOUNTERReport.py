"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import re
import pytest
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.raw_COUNTER_report import RawCOUNTERReport
from data import COUNTER_reports_LFS
from data import deduplication_data


#Section: Fixtures
@pytest.fixture
def sample_COUNTER_reports():
    """Creates a dataframe with the data from all the COUNTER reports."""
    yield COUNTER_reports_LFS.sample_COUNTER_reports()


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
    yield deduplication_data.matches_to_manually_confirm_including_sample_normalized_resource_data


@pytest.fixture
def sample_RawCOUNTERReport(sample_COUNTER_reports):
    """A RawCOUNTERReport object with the data from the `COUNTER_workbooks_for_tests` test data COUNTER reports."""
    #ToDo: yield RawCOUNTERReport(sample_COUNTER_reports)
    pass


#Section: Tests
#Subsection: Test `RawCOUNTERReport.create_normalized_resource_data_argument()`
def test_create_normalized_resource_data_argument_with_R4():
    """Tests the `create_normalized_resource_data_argument()` method when pulling from a database with resource data from only R4 reports."""
    #ToDo: Establish database fixture with data from only R4 resources
    #ToDo: assert RawCOUNTERReport.create_normalized_resource_data_argument = sample_R4_normalized_resource_data
    pass


def test_create_normalized_resource_data_argument_with_R4_and_R5():
    """Tests the `create_normalized_resource_data_argument()` method when pulling from a database with resource data from R4 and R5 reports."""
    #ToDo: Establish database fixture with data from R4 and R5 resources
    #ToDo: assert RawCOUNTERReport.create_normalized_resource_data_argument = sample_normalized_resource_data
    pass


#Subsection: Test `RawCOUNTERReport.perform_deduplication_matching()`
#ALERT: On a workstation with 8GB RAM, these tests fail with a `MemoryError` error; a workstation with 16GB RAM seems capable of running the tests successfully
#ToDo: Review the amount of variance between the method outputs depending on their inputs and ensure constants exist for confirming all test results
def test_perform_deduplication_matching_with_R4(sample_R4_RawCOUNTERReport):
    """Tests the `perform_deduplication_matching()` method when a RawCOUNTERReport object instantiated from reformatted R4 reports is the sole argument."""
    # Resources where an ISSN appears in both the Print_ISSN and Online_ISSN fields and/or is paired with different ISSNs still need to be paired
    assert sample_R4_RawCOUNTERReport.perform_deduplication_matching() == (matched_records, matches_to_manually_confirm)  # ToDo: Confirm that these imports don't need to be parameters


def test_perform_deduplication_matching_with_R4_and_R5(sample_RawCOUNTERReport):
    """Tests the `perform_deduplication_matching()` method when a RawCOUNTERReport object instantiated from reformatted R4 and R5 reports is the sole argument."""
    #ToDo: assert sample_RawCOUNTERReport.perform_deduplication_matching() == 
    pass


def test_perform_deduplication_matching_with_R4_and_normalized_resource_data_from_R4(sample_R4_RawCOUNTERReport, sample_R4_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method with a RawCOUNTERReport object instantiated from reformatted R4 reports and a `sample_R4_normalized_resource_data` fixture."""
    #ToDo: assert sample_R4_RawCOUNTERReport.perform_deduplication_matching(sample_R4_normalized_resource_data) == 
    pass


def test_perform_deduplication_matching_with_R4_and_normalized_resource_data_from_R4_and_R5(sample_R4_RawCOUNTERReport, sample_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method with a RawCOUNTERReport object instantiated from reformatted R4 reports and a `sample_normalized_resource_data` fixture."""
    #ToDo: assert sample_R4_RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data) == 
    pass


def test_perform_deduplication_matching_with_R4_and_R5_and_normalized_resource_data_from_R4(sample_RawCOUNTERReport, sample_R4_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method with a RawCOUNTERReport object instantiated from reformatted R4 and R5 reports and a `sample_R4_normalized_resource_data` fixture."""
    #ToDo: assert sample_RawCOUNTERReport.perform_deduplication_matching(sample_R4_normalized_resource_data) == 
    pass


def test_perform_deduplication_matching_with_R4_and_R5_and_normalized_resource_data_from_R4_and_R5(sample_RawCOUNTERReport, sample_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method with a RawCOUNTERReport object instantiated from reformatted R4 and R5 reports and a `sample_normalized_resource_data` fixture."""
    #ToDo: assert sample_RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data) == 
    pass


def test_perform_deduplication_matching_with_R5_and_normalized_resource_data_from_R4(sample_R5_RawCOUNTERReport, sample_R4_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method with a RawCOUNTERReport object instantiated from reformatted R5 reports and a `sample_R4_normalized_resource_data` fixture."""
    #ToDo: assert sample_R5_RawCOUNTERReport.perform_deduplication_matching(sample_R4_normalized_resource_data) == 
    pass


def test_perform_deduplication_matching_with_R5_and_normalized_resource_data_from_R4_and_R5(sample_R5_RawCOUNTERReport, sample_normalized_resource_data):
    """Tests the `perform_deduplication_matching()` method with a RawCOUNTERReport object instantiated from reformatted R5 reports and a `sample_normalized_resource_data` fixture."""
    #ToDo: assert sample_R5_RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data) == 
    pass


#Subsection: Test `RawCOUNTERReport.load_data_into_database()`
#ToDo: Determine what the input constant(s) should be for each function
def test_load_data_into_database_from_R4():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R4` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R4_and_R5():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R4_and_R5` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R4_and_normalized_resource_data_from_R4():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R4_and_normalized_resource_data_from_R4` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R4_and_normalized_resource_data_from_R4_and_R5():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R4_and_normalized_resource_data_from_R4_and_R5` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R4_and_R5_and_normalized_resource_data_from_R4():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R4_and_R5_and_normalized_resource_data_from_R4` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R4_and_R5_and_normalized_resource_data_from_R4_and_R5():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R4_and_R5_and_normalized_resource_data_from_R4_and_R5` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R5_and_normalized_resource_data_from_R4():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R5_and_normalized_resource_data_from_R4` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass


def test_load_data_into_database_from_R5_and_normalized_resource_data_from_R4_and_R5():
    #ToDo: Test method based on results from `test_perform_deduplication_matching_with_R5_and_normalized_resource_data_from_R4_and_R5` after manual matching
    #ToDo: The database fixture from conftest should be able to serve as the constant for checking the results
    pass