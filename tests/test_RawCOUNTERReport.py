"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import pytest


@pytest.fixture
def sample_R4_dataframe():
    """Reads the sample CSVs of reformatted R4 data into a single dataframe using the same expression as in the `determine_if_resources_match` function."""
    R4_reports = []
    for file in os.listdir(Path('.', 'tests', 'data')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        R4_reports.append(Path('.', 'tests', 'data', file))


def test_perform_deduplication_matching(sample_R4_dataframe):
    #ToDo: Write a docstring when the format of the return value is set
    pass


def test_harvest_SUSHI_report(sample_R4_dataframe):
    #ToDo: Write a docstring when the format of the return value is set
    pass
    

def test_load_data_into_database(sample_R4_dataframe):
    #ToDo: Write a docstring when the format of the return value is set
    pass