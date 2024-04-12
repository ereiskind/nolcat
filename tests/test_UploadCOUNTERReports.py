"""Test using `UploadCOUNTERReports`."""
########## Passing 2024-02-21 ##########

import pytest
import logging
from pathlib import Path
from random import choice
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
    file_path = TOP_NOLCAT_DIRECTORY / 'tests' / 'bin' / 'COUNTER_workbooks_for_tests'
    file_name = choice([file.name for file in file_path.iterdir()])
    file_path_and_name = file_path / file_name
    log.warning(f"`path_to_sample_file()` yields {file_path_and_name} (type {type(file_path_and_name)}).")  #TEST: Level `info`
    yield file_path_and_name


def test_create_dataframe_from_single_workbook(sample_COUNTER_report_workbook):
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
    import numpy as np
    x = [df.iloc[i,j] for i,j in zip(*np.where(pd.isnull(df)))]
    log.warning(f"`df` has {len(x)} null values")
    y_df = COUNTERData_relation[df.columns.tolist()]
    y = [y_df.iloc[i,j] for i,j in zip(*np.where(pd.isnull(y_df)))]
    log.warning(f"`COUNTERData_relation` has {len(y)} null values")
    for z in list(enumerate(zip(z,y))):
        if z[1][0] != z[1][1]:
            log.warning(f"Null values {int(z[0]) + 1} are {z[1]}")
    #TEST: end temp
    assert_frame_equal(df, COUNTERData_relation[df.columns.tolist()])