"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import pytest
import pandas as pd
from selenium.webdriver.common.keys import Keys

from nolcat.raw_COUNTER_report import RawCOUNTERReport
from nolcat.app import Chrome_browser_driver


@pytest.fixture
def driver():
    driver = Chrome_browser_driver()
    domain = 'http://localhost:5000'  #ToDo: Change this as needed to match the domain of the Flask app
    yield driver, domain
    driver.quit()


@pytest.fixture
def sample_R4_form_result():
    """Uses Selenium to pass reformatted R4 COUNTER reports into the form at the end of route upload_historical_COUNTER_usage, simulating one of the possible arguments for the RawCOUNTERReport constructor."""
    driver = Chrome_browser_driver()
    #ToDo: Go to url_for('upload_historical_COUNTER_usage')
    #ToDo: Find form element with name 'R4_files'
    #ToDo: for file in os.listdir(Path('.', 'tests', 'bin', 'OpenRefine_exports')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        #ToDo: Add Path('.', 'tests', 'bin', 'OpenRefine_exports', file) to the list of files selected in field 'R4_files'
    #ToDo: Select type="submit" button
    #ToDo: R4_reports = value retruend from the form (`request.files` in flask routes)
    yield R4_reports


def test_RawCOUNTERReport_R4_constructor(sample_R4_form_result):
    """Confirms that constructor for RawCOUNTERReport that takes in reformatted R4 reports is working correctly."""
    pass


def test_perform_deduplication_matching(sample_R4_form_result):
    """Tests that the `perform_deduplication_matching` method returns the data representing resource matches both confirmed and needing confirmation with the object instantiated from `sample_R4_form_result` as the sole argument."""
    assert sample_R4_form_result.perform_deduplication_matching() == None  #ToDo: Determine what new value is


def test_harvest_SUSHI_report(sample_R4_form_result):
    #ToDo: Write a docstring when the format of the return value is set
    pass
    

def test_load_data_into_database(sample_R4_form_result):
    #ToDo: Write a docstring when the format of the return value is set
    pass