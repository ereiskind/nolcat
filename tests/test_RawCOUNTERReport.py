"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import re
import pytest
import pandas as pd

from nolcat.raw_COUNTER_report import RawCOUNTERReport


@pytest.fixture
def sample_ImmutableMultiDict():
    """Creates a `werkzeug.datastructures.ImmutableMultiDict` object for testing how the constructor handles such an object."""
    #ToDo: Multiple days of work, shown and documented with prior commits in this repo, were unable to come up with a solution here. This was before Flask and WTForms were set up, so an actual upload is a solution now, but it also introduces a larger number of variables.
    pass


#ToDo: Create fixture of API response object


@pytest.fixture
def R4_RawCOUNTERReport_fixture():
    """A RawCOUNTERReport object based on a CSV with the data of many reformatted R4 COUNTER reports; a single CSV is used to reduce the number of potential failure points."""
    #ToDo: Hardcode data into CSV
    #ToDo: df = Convert CSV to dataframe
    #ToDo: raw_report = RawCOUNTERReport(df)
    #ToDo: yield raw_report
    pass


@pytest.fixture
def temp_fixture():
    """A temporary fixture creating a RawCOUNTERReport object from the files in `tests/bin/OpenRefine_exports` to be copied for the fixture above."""
    dfs_to_concatenate = []
    for file in os.listdir('tests/bin/OpenRefine_exports'):
        statistics_source_ID = re.findall(r'(\d*)_\w{2}\d?_\d{4}.csv', string=Path(file.filename).parts[-1])[0]
        df = pd.read_csv(
            file,
            encoding='utf-8',  # Some of the CSVs are coming in with encoding errors and strings of non-ASCII characters as question marks
            encoding_errors='backslashreplace',
            dtype={
                'Resource_Name': 'string',
                'Publisher': 'string',
                'Platform': 'string',
                'DOI': 'string',
                'Proprietary_ID': 'string',
                'ISBN': 'string',
                'Print_ISSN': 'string',
                'Online_ISSN': 'string',
                'Data_Type': 'string',
                'Section_Type': 'string',
                'Metric_Type': 'string',
                # Usage_Date is fine as default datetime64[ns]
                'Usage_Count': 'int',  # Python default used because this is a non-null field
            },
        )
        df['Statistics_Source_ID'] = statistics_source_ID
        df.date.dt.to_period('M').dt.to_timestamp()
        print(f"Dataframe:\n{df}\n")
        dfs_to_concatenate.append(df)
    temp_df = pd.concat(
        dfs_to_concatenate,
        ignore_index=True
    )
    print(f"Final dataframe:\n{temp_df}")


def test_print_temp_fixture(temp_fixture):
    """Outputs the temp fixture."""
    print(temp_fixture)
    assert True


#ToDo: Create fixture for dataframe containing reformatted R5 COUNTER reports


#ToDo: Create fixture combining the R4 and R5 dataframes into a single dataframe


#ToDo: Create fixture of `normalized_resource_data`


def test_constructor_with_ImmutableMultiDict(sample_ImmutableMultiDict):
    """Tests turning the data in one or more binary files uploaded into Flask, which is within a ImmutableMultiDict object, into a RawCOUNTERReport object."""
    #ToDo: raw_report = RawCOUNTERReport(sample_ImmutableMultiDict)
    #ToDo: RawCOUNTERReport has a method recreating pandas `equals`, but asserting data run through a broken constructor is equal to the same data run through the same broken constructor will result in a passed test; would a comparison of the data in the dataframes and a check of the data type of the result of the constructor be a more accurate pass condition?
    pass


#ToDo: Test constructor with API response object


#ToDo: Test `create_normalized_resource_data_argument` method (perform method, then compare results with fixture for it)


def test_perform_deduplication_matching(R4_RawCOUNTERReport_fixture):
    """Tests the `perform_deduplication_matching` method when a RawCOUNTERReport object instantiated from reformatted R4 reports is the sole argument."""
    #ALERT: On a workstation with 8GB RAM, this test fails with a `MemoryError` error; a workstation with 16GB RAM seems capable of running the test successfully
    #ToDo: Do versions of this test using R5 data and combined data need to be created?
    #ToDo: result = R4_RawCOUNTERReport_fixture.perform_deduplication_matching()
    #ToDo: assert result is equal to the same as literal value it should be
    pass


#ToDo: Test `perform_deduplication_matching` method with a `normalized_resource_data` value


def test_load_data_into_database():
    """Tests the `load_data_into_database` method."""
    #ToDo: Have the literal value used to check `perform_deduplication_matching` as the input
    #ToDo: Run the method
    #ToDo: Use the fixtures for loading into relations as the literal values for checking the results
    pass
