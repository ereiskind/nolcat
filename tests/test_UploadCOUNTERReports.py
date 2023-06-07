"""Test using `UploadCOUNTERReports`."""
########## Failing 2023-06-07 ##########

import pytest
from pathlib import Path
import os
import io
from wtforms import MultipleFileField
from wtforms.validators import DataRequired
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.upload_COUNTER_reports import UploadCOUNTERReports


@pytest.fixture
def sample_COUNTER_report_workbooks():
    """Creates a Flask-WTF File object for use in testing the `UploadCOUNTERReports` class.
    
    While this fixture would ideally create a MultipleFileField object containing all of the Excel workbooks in `\\nolcat\\tests\\bin\\COUNTER_workbooks_for_tests`, it actually creates an UnboundField object because it uses a constructor for an object that inherits from the WTForms Form base class but lacks the `_form` and `_name` parameters, which are automatically supplied during standard Form object construction. At this point, appropriate values for the above parameters are unknown, so the fixture is used as-is, and the `UploadCOUNTERReports.create_dataframe()` method repeats the loop for gathering the workbook names seen below.
    """
    folder_path = Path('tests', 'bin', 'COUNTER_workbooks_for_tests')
    data_attribute = []

    for workbook in os.listdir(folder_path):
        file_path = folder_path / workbook
        with open(file_path, mode='rb') as file:
            data_attribute.append(io.BytesIO(file.read()))

    fixture = MultipleFileField({
        'data': data_attribute,
        'id': 'COUNTER_reports',
        'label': "Select the COUNTER report workbooks. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.",
        'name': 'COUNTER_reports',
        'type': 'MultipleFileField',
        'validators': DataRequired(),
    })
    return fixture


def test_create_dataframe(sample_COUNTER_report_workbooks, COUNTERData_relation):
    """Tests transforming multiple Excel workbooks with tabular COUNTER data into a single dataframe."""
    df = UploadCOUNTERReports(sample_COUNTER_report_workbooks).create_dataframe()
    COUNTERData_relation = COUNTERData_relation.drop(columns='report_creation_date')  # Reports ingested using the `UploadCOUNTERReports.create_dataframe()` method have no `report_creation_date` values, so a field for this value containing entirely null values is added to the dataframe returned by the method; thus, the dataframe returned by this method shouldn't have the `report_creation_date` field
    assert_frame_equal(df, COUNTERData_relation, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order