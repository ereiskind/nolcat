"""Test using `UploadCOUNTERReports`."""
########## Failing 2023-06-07 ##########

import pytest
from pathlib import Path
from tempfile import SpooledTemporaryFile
import os
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import Headers
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.upload_COUNTER_reports import UploadCOUNTERReports


@pytest.fixture
def sample_COUNTER_report_workbooks():
    """Creates a list of Werkzeug FileStorage object(s) for use in testing the `UploadCOUNTERReports` class.
    
    The `UploadCOUNTERReports` constructor takes an attribute of the MultipleFileField object that lists each file uploaded to the MultipleFileField object as an individual Werkzeug FileStorage object.
    """
    folder_path = Path('tests', 'bin', 'COUNTER_workbooks_for_tests')
    fixture = []
    for workbook in os.listdir(folder_path):
        #Test: Start testing section
        with open(Path(folder_path / workbook), 'rb+') as f:
            print(f"`with open(p, 'rb+')` is {f} (type {repr(type(f))})")
            temp_file_object = SpooledTemporaryFile()
            print(f"`SpooledTemporaryFile()` in block is {temp_file_object} (type {repr(type(temp_file_object))})\n{temp_file_object.__dict__}")
        print(f"`SpooledTemporaryFile()` out of block is {temp_file_object} (type {repr(type(temp_file_object))})\n{temp_file_object.__dict__}")
        #Test: End testing section
        FileStorage_object = FileStorage(
            stream = temp_file_object,
            filename=str(workbook),
            name='COUNTER_reports',  # Name of form field, which is the same in both forms
            headers=Headers([  # Copied from `FileStorage.__dict__` logging from the `COUNTER_reports` fields
                ('Content-Disposition', f'form-data; name="COUNTER_reports"; filename="{str(workbook)}"'),
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ]),
        )
        fixture.append(FileStorage_object)
    return fixture


def test_create_dataframe(sample_COUNTER_report_workbooks, COUNTERData_relation):
    """Tests transforming multiple Excel workbooks with tabular COUNTER data into a single dataframe."""
    df = UploadCOUNTERReports(sample_COUNTER_report_workbooks).create_dataframe()  #TEST: Test fails due to raising `TypeError: object cannot be converted to an IntegerDtype`
    COUNTERData_relation = COUNTERData_relation.drop(columns='report_creation_date')  # Reports ingested using the `UploadCOUNTERReports.create_dataframe()` method have no `report_creation_date` values, so a field for this value containing entirely null values is added to the dataframe returned by the method; thus, the dataframe returned by this method shouldn't have the `report_creation_date` field
    assert_frame_equal(df, COUNTERData_relation, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order