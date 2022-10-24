"""This module contains the dataframe with all the test data COUNTER reports formatted for normalization. A dataframe constructor is used instead of any tabular file to prevent file format change problems, especially encoding problems, from adding complications to the tests. From these separate modules, this partially transformed test data can become fixtures for use in assert statements or be output to tabular data formats."""

import pandas as pd


def sample_COUNTER_reports():
    """A dataframe containing the same data as all the test data COUNTER reports in `COUNTER_workbooks_for_tests` reformatted to enable normalization."""
    #ToDo: df = pd.DataFrame(
    #     [
    #         [],
    #     ],
    #     columns=[],
    # )
    #ToDo: df.index.name = ""
    #ToDo: return df
    pass