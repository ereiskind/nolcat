"""Test using `UploadCOUNTERReports`."""
########## Passing 2023-10-10 ##########

import pytest
import logging
from pathlib import Path
import os
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from conftest import mock_FileStorage_object  # Direct import is required because it isn't a fixture
from nolcat.upload_COUNTER_reports import UploadCOUNTERReports

log = logging.getLogger(__name__)


#Section: Fixture
@pytest.fixture
def sample_COUNTER_report_workbooks():
    """Creates a list of mock_FileStorage_object object(s) for use in testing the `UploadCOUNTERReports` class.
    
    The `UploadCOUNTERReports` constructor takes a list of Werkzeug FileStorage object(s), but when this fixture uses those objects, a `File is not a zip file` error is raised. The `mock_FileStorage_object` class was devised as a way around that issue.

    Yields:
        list: a list of mock_FileStorage_object object(s) simulating multiple files selected in a MultipleFileField field
    """
    folder_path = Path(*Path(__file__).parts[0:Path(__file__).parts.index('tests')+1]) / 'bin' / 'COUNTER_workbooks_for_tests'
    fixture = []
    for workbook in folder_path.iterdir():
        fixture.append(mock_FileStorage_object(folder_path / workbook))
    fixture.sort(key=lambda mock_FileStorage: mock_FileStorage.filename)  # Modifying list in place returns `None`, so making modification in `return` statement makes fixture value `None`
    yield fixture


#Section: Test
def test_create_dataframe(sample_COUNTER_report_workbooks, COUNTERData_relation):
    """Tests transforming multiple Excel workbooks with tabular COUNTER data into a single dataframe."""
    df = UploadCOUNTERReports(sample_COUNTER_report_workbooks).create_dataframe()  #ToDo:: Returns tuple, second part is list of error messages for workbooks and worksheets rejected
    COUNTERData_relation = COUNTERData_relation.drop(columns='report_creation_date')  # Reports ingested using the `UploadCOUNTERReports.create_dataframe()` method have no `report_creation_date` values, so a field for this value containing entirely null values is added to the dataframe returned by the method; thus, the dataframe returned by this method shouldn't have the `report_creation_date` field
    assert_frame_equal(df, COUNTERData_relation, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order