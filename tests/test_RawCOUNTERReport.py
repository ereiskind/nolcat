"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import pytest
import pandas as pd
from nolcat.raw_COUNTER_report import RawCOUNTERReport


@pytest.fixture
def sample_R4_dataframe():
    """Reads the sample CSVs of reformatted R4 data into a single dataframe using the same expression as in the `determine_if_resources_match` function."""
    R4_reports = []
    for file in os.listdir(Path('.', 'tests', 'data')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        R4_reports.append(Path('.', 'tests', 'data', file))
    
    R4_dataframe = pd.concat(
        [
            pd.read_csv(
                CSV,
                dtype={
                    # 'Interface' is fine as default float64
                    'Resource_Name': 'string',
                    'Publisher': 'string',
                    'Platform': 'string',
                    'DOI': 'string',
                    'Proprietary_ID': 'string',
                    'ISBN': 'string',
                    'Print_ISSN': 'string',
                    'Online_ISSN': 'string',
                    'Data_Type': 'string',
                    'Metric_Type': 'string',
                    # R4_Month uses parse_dates
                    # R4_Count is fine as default int64
                },
                parse_dates=['R4_Month'],  # For this to work, the dates need to be ISO-formatted strings (with CSVs, all the values are strings)
                encoding='unicode_escape',  # This allows for CSVs with non-ASCII characters
                infer_datetime_format=True  # Speeds up the parsing process if the format can be inferred; since all dates will be in the same format, this should be easy to do
            ) for CSV in R4_reports
        ],
        ignore_index=True
    )
    yield R4_dataframe


def test_perform_deduplication_matching(sample_R4_dataframe):
    #ToDo: Write a docstring when the format of the return value is set
    pass


def test_harvest_SUSHI_report(sample_R4_dataframe):
    #ToDo: Write a docstring when the format of the return value is set
    pass
    

def test_load_data_into_database(sample_R4_dataframe):
    #ToDo: Write a docstring when the format of the return value is set
    pass