"""Test using `UploadCOUNTERReports`."""
########## Passing 2024-02-21 ##########

import pytest
import logging
from pathlib import Path
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from conftest import mock_FileStorage_object  # Direct import is required because it isn't a fixture
from nolcat.upload_COUNTER_reports import UploadCOUNTERReports
from nolcat.app import *

log = logging.getLogger(__name__)


#Section: Test Uploading Single Workbook
@pytest.fixture
def sample_COUNTER_report_workbook():
    """Creates a mock_FileStorage_object object enclosed in a list for use in testing the `UploadCOUNTERReports` class.
    
    The `UploadCOUNTERReports` constructor takes a list of Werkzeug FileStorage object(s), but when this fixture uses those objects, a `File is not a zip file` error is raised. The `mock_FileStorage_object` class was devised as a way around that issue.

    Yields:
        list: a mock_FileStorage_object object enclosed in a list simulating a single file selected in a MultipleFileField field
    """
    pass


def test_create_dataframe_from_single_workbook():
    """Tests transforming an Excel workbook with tabular COUNTER data into a dataframe."""
    pass


#Section: Test Uploading All Workbooks
@pytest.fixture
def sample_COUNTER_report_workbooks():
    """Creates a list of mock_FileStorage_object object(s) for use in testing the `UploadCOUNTERReports` class.
    
    The `UploadCOUNTERReports` constructor takes a list of Werkzeug FileStorage object(s), but when this fixture uses those objects, a `File is not a zip file` error is raised. The `mock_FileStorage_object` class was devised as a way around that issue.

    Yields:
        list: a list of mock_FileStorage_object object(s) simulating multiple files selected in a MultipleFileField field
    """
    folder_path = TOP_NOLCAT_DIRECTORY / 'tests' / 'bin' / 'COUNTER_workbooks_for_tests'
    fixture = []
    for workbook in folder_path.iterdir():
        fixture.append(mock_FileStorage_object(folder_path / workbook))
    fixture.sort(key=lambda mock_FileStorage: mock_FileStorage.filename)  # Modifying list in place returns `None`, so making modification in `return` statement makes fixture value `None`
    yield fixture


def test_create_dataframe(sample_COUNTER_report_workbooks, COUNTERData_relation):
    """Tests transforming multiple Excel workbooks with tabular COUNTER data into a single dataframe.
    
    The order of the possible delimiters means the existence of the delimiter characters in a string field is tested, but the possibility of a delimiter character as the first character in a string field isn't covered by this test.
    """
    df, data_not_in_df = UploadCOUNTERReports(sample_COUNTER_report_workbooks).create_dataframe()
    assert isinstance(data_not_in_df, list)
    #TEST: temp
    log.info(f"Dataframe compare:\n{df.compare(COUNTERData_relation[df.columns.tolist()])}")
    dtypes = {k:'object' for k in df.columns.tolist()}
    temp_df = df.astype(dtypes)
    temp_COUNTERData_relation = COUNTERData_relation.astype(dtypes)
    temp_df = temp_df.applymap(lambda cell_value: None if cell_value.isnull() else cell_value)
    temp_COUNTERData_relation = temp_COUNTERData_relation.applymap(lambda cell_value: None if cell_value.isnull() else cell_value)
    assert_frame_equal(temp_df, temp_COUNTERData_relation[df.columns.tolist()])
    #TEST: end temp
    assert_frame_equal(df, COUNTERData_relation[df.columns.tolist()])