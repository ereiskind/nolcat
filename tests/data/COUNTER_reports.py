"""This module contains the dataframes representing the data from the sample COUNTER reports. This data isn't stored in a tabular file to prevent file format change problems, especially encoding problems, from adding complications to the test. Keeping this data in a separate module, however, makes the test modules easier to handle and makes it possible for this data to be output to TSVs in the same manner as the relation data used for testing."""

import pandas as pd

def sample_R4_COUNTER_reports():
    """A dataframe containing the same data as all the reformatted COUNTER R4 reports in `tests/data/reformatted_COUNTER_R4_test_data` combined."""
    #ToDo: df = pd.DataFrame(
    #     [
    #         [],
    #     ],
    #     columns=[],
    # )
    #ToDo: df.index.name = ""
    #ToDo: return df
    pass


def sample_R5_COUNTER_reports():
    """A dataframe containing the same data as all the reformatted COUNTER R5 reports in `tests/data/reformatted_COUNTER_R5_test_data` combined."""
    #ToDo: df = pd.DataFrame(
    #     [
    #         [],
    #     ],
    #     columns=[],
    # )
    #ToDo: df.index.name = ""
    #ToDo: return df
    pass


def sample_COUNTER_reports():
    """A dataframe containing the same data as all the reformatted COUNTER reports in both `tests/data/reformatted_COUNTER_R4_test_data` and `tests/data/reformatted_COUNTER_R5_test_data` combined."""
    #ToDo: df = pd.DataFrame(
    #     [
    #         [],
    #     ],
    #     columns=[],
    # )
    #ToDo: df.index.name = ""
    #ToDo: Perform methods `.encode('utf-8').decode('unicode-escape')` on all fields that might have non-ASCII escaped characters
    #ToDo: Is above the correct method for handling the encoding?
    #ToDo: return df
    pass