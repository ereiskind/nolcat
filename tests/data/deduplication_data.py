"""This module contains the data needed to test the deduplication functionality of the `RawCOUNTERReport` class. A dataframe constructor is used instead of any tabular file to prevent file format change problems, especially encoding problems, from adding complications to the tests. From these separate modules, this partially transformed test data can become fixtures for use in assert statements or be output to tabular data formats."""

import pandas as pd


def sample_normalized_resource_data():
    """A dataframe..."""
    #ToDo: The data used here will be the same sample data as is loaded when there's no data already in the database; the data that gets loaded into the database prior to tests that call this will be different
    pass


def matched_records():
    """The set of record index matches not needing manual confirmation created by ``RawCOUNTERReport.perform_deduplication_matching()`` with the test data."""
    #ToDo: return <set>
    pass


def matches_to_manually_confirm():
    """The dictionary of metadata pairs and record index pair sets for manually confirming matches created by ``RawCOUNTERReport.perform_deduplication_matching()`` with the test data."""
    #ToDo: return <dict>
    pass


def matched_records_including_sample_normalized_resource_data():
    """The set of record index matches not needing manual confirmation created by ``RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data)`` with the test data."""
    #ToDo: return <set>
    pass


def matches_to_manually_confirm_including_sample_normalized_resource_data():
    """The dictionary of metadata pairs and record index pair sets for manually confirming matches created by ``RawCOUNTERReport.perform_deduplication_matching(sample_normalized_resource_data)`` with the test data."""
    #ToDo: return <dict>
    pass