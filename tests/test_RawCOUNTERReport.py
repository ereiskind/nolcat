"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import pytest
import pandas as pd
from selenium.webdriver.common.keys import Keys
from werkzeug.datastructures import *
from nolcat.raw_COUNTER_report import RawCOUNTERReport


@pytest.fixture
def sample_R4_RawCOUNTERReport():
    """Uses the RawCOUNTERReport constructor to create a RawCOUNTERReport object from reformatted R4 COUNTER reports."""
    R4_reports = MultiDict()
    for file in os.listdir(Path('.', 'tests', 'bin', 'OpenRefine_exports')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        R4_reports.add(
            'R4_files',
            FileStorage(
                stream=open(
                    Path('.', 'tests', 'bin', 'OpenRefine_exports', file),
                    encoding='unicode_escape',
                ),
                name='R4_files',
                headers={
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'Content-Encoding': 'utf-8',
                    'mode': 'b',
                }
            )
        )
    yield R4_reports


def test_RawCOUNTERReport_fixture_creation(sample_R4_RawCOUNTERReport):
    """Confirms that the RawCOUNTERReport object `sample_R4_RawCOUNTERReport`, which is used as a fixture, was instantiated correctly."""
    pass


def test_perform_deduplication_matching(sample_R4_RawCOUNTERReport):
    """Tests that the `perform_deduplication_matching` method returns the data representing resource matches both confirmed and needing confirmation with the `sample_R4_RawCOUNTERReport` instance as the sole argument."""
    assert sample_R4_RawCOUNTERReport.perform_deduplication_matching() == None  #ToDo: Determine what new value is


def test_harvest_SUSHI_report(sample_R4_RawCOUNTERReport):
    #ToDo: Write a docstring when the format of the return value is set
    pass
    

def test_load_data_into_database(sample_R4_RawCOUNTERReport):
    #ToDo: Write a docstring when the format of the return value is set
    pass