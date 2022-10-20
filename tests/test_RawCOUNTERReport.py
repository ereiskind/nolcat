"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import re
import pytest
import pandas as pd

# `conftest.py` fixtures are imported automatically
from nolcat.raw_COUNTER_report import RawCOUNTERReport
from data import COUNTER_reports


#Section: Fixtures
#Subsection: Constants for Test Conditions
@pytest.fixture
def sample_R4_COUNTER_reports():
    """Creates a dataframe with the data from all the COUNTER R4 reports."""
    yield COUNTER_reports.sample_R4_COUNTER_reports()


@pytest.fixture
def sample_R5_COUNTER_reports():
    """Creates a dataframe with the data from all the COUNTER R5 reports."""
    #yield COUNTER_reports.sample_R5_COUNTER_reports()
    pass  #ToDo: Update when dataframe is created


@pytest.fixture
def sample_COUNTER_reports():
    """Creates a dataframe with the data from all the COUNTER reports."""
    #yield COUNTER_reports.sample_COUNTER_reports()
    pass  #ToDo: Update when dataframe is created


@pytest.fixture
def sample_R4_normalized_resource_data():
    """The dataframe returned by a `RawCOUNTERReport.normalized_resource_data()` method when the underlying dataframe has resource data from only R4 reports."""
    pass


@pytest.fixture
def sample_normalized_resource_data():
    """The dataframe returned by a `RawCOUNTERReport.normalized_resource_data()` method when the underlying dataframe has resource data from R4 and R5 reports."""
    pass


#Subsection: `RawCOUNTERReport` Input and Output Objects
@pytest.fixture
def sample_ImmutableMultiDict():
    """Creates a `werkzeug.datastructures.ImmutableMultiDict` object for testing how the constructor handles such an object."""
    #ToDo: Multiple days of work, shown and documented with prior commits in this repo, were unable to come up with a solution here. This was before Flask and WTForms were set up, so an actual upload is a solution now, but it also introduces a larger number of variables.
    pass


@pytest.fixture
def sample_R4_RawCOUNTERReport():
    """Creates a dataframe with all the data of the R4 COUNTER reports. 
    
    A function containing all the raw data and creating the dataframe is used so file import issues don't create problems.
    """
    df = COUNTER_reports.sample_R4_COUNTER_reports()
    #ToDo: Set dtypes based on below:
    # dtype={  # Null values represented by "NaN"/`numpy.nan` in number fields, "NaT".`pd.nat` in datetime fields, and "<NA>"/`pd.NA` in string fields
    #     'Resource_Name': 'string',
    #     'Publisher': 'string',
    #     'Platform': 'string',
    #     'DOI': 'string',
    #     'Proprietary_ID': 'string',
    #     'ISBN': 'string',
    #     'Print_ISSN': 'string',
    #     'Online_ISSN': 'string',
    #     'Data_Type': 'string',
    #     'Section_Type': 'string',
    #     'Metric_Type': 'string',
    #     'Usage_Count': 'int',  # Python default used because this is a non-null field
    #     'Statistics_Source_ID': 'int',
    # },
    raw_report = RawCOUNTERReport(df)
    yield raw_report


@pytest.fixture
def sample_R5_RawCOUNTERReport():
    """A RawCOUNTERReport object with the data of reformatted R5 COUNTER reports."""
    #ToDo: Mock data in tabular R5 reports from same statistics sources with same resources as in R4
    #ToDo: Include `Gale Business: Entrepreneurship` in resources (Gale's Small Business Resource Center -> Gale Business: Entrepreneurship in early 2020)
    #ToDo: Set up R5 data like R4 data
    #ToDo: Determine best way to get all of above data into single RawCOUNTERReport object
    pass


@pytest.fixture
def sample_RawCOUNTERReport():
    """A RawCOUNTERReport object with the data of reformatted R4 and R5 COUNTER reports."""
    #ToDo: Get both R4 and R5 data
    #ToDo: Combine above into RawCOUNTERReport
    pass


#Section: Tests
#Subsection: Test `RawCOUNTERReport.__init__()`
def test_constructor_with_ImmutableMultiDict(sample_ImmutableMultiDict):
    """Tests turning the data in one or more binary files uploaded into Flask, which is within a ImmutableMultiDict object, into a RawCOUNTERReport object."""
    #ToDo: raw_report = RawCOUNTERReport(sample_ImmutableMultiDict)
    #ToDo: RawCOUNTERReport has a method recreating pandas `equals`, but asserting data run through a broken constructor is equal to the same data run through the same broken constructor will result in a passed test; would a comparison of the data in the dataframes and a check of the data type of the result of the constructor be a more accurate pass condition?
    pass


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