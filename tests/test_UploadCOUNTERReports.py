"""Test using `UploadCOUNTERReports`."""
########## Passing 2023-06-16 ##########

import pytest
import logging
from pathlib import Path
import os
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.upload_COUNTER_reports import UploadCOUNTERReports

log = logging.getLogger(__name__)


#Section: Classes to Use in Fixture
class _fileAttribute:
    """Enables the `_file` attribute of the `mock_FileStorage_object.stream` attribute.

    Attributes:
        self._file (str): The absolute file path for the COUNTER report being uploaded
    """
    def __init__(self, file_path):
        """The constructor method for `_fileAttribute`, which instantiates the string of the absolute file path for the COUNTER report being uploaded."""
        self._file = str(file_path)


class mock_FileStorage_object:
    """A replacement for a Werkzeug FileStorage object.

    The `UploadCOUNTERReports` constructor takes the list of Werkzeug FileStorage object(s) in the `data` attribute of a WTForms MultipleFileField object. When a list of Werkzeug FileStorage object(s) created with the FileStorage constructor in a fixture is used, however, the _io.BytesIO object returned by the `.stream._file` attribute raises a `File is not a zip file` error in OpenPyXL's `load_workbook()` function. With the same files encapsulated in the same classes raising an error depending on their source, it could not be determined how to prevent the FileStorage object(s) created in the fixture from raising the error. As an alternative, this class was created; it has the attributes of the Werkzeug FileStorage object used in the `UploadCOUNTERReports.create_dataframe()` method, so it works the same way in the method, but it features the absolute file path as a string instead of a _io.BytesIO object to avoid the `File is not a zip file` error.

    Attributes:
        self.stream (_fileAttribute._file): The intermediary attribute for the absolute file path for the COUNTER report being uploaded
        self.filename (str): The name of the file of the COUNTER report being uploaded
    """
    def __init__(self, file_path):
        """The constructor method for `mock_FileStorage_object`, which instantiates the attributes `stream` and `filename` based on the absolute file path for the COUNTER report being uploaded.

        Args:
            file_path (pathlib.Path): The absolute file path for the COUNTER report being uploaded
        """
        self.stream = _fileAttribute(file_path.absolute())
        self.filename = file_path.name


    def __repr__(self):
        """The printable representation of a `mock_FileStorage_object` instance."""
        return f"<__main__.mock_FileStorage_object {{'stream._file': '{self.stream._file}', 'filename': '{self.filename}'}}>"


#Section: Fixture
@pytest.fixture
def sample_COUNTER_report_workbooks():
    """Creates a list of mock_FileStorage_object object(s) for use in testing the `UploadCOUNTERReports` class.
    
    The `UploadCOUNTERReports` constructor takes a list of Werkzeug FileStorage object(s), but when this fixture uses those objects, a `File is not a zip file` error is raised. The `mock_FileStorage_object` class was devised as a way around that issue.
    """
    folder_path = Path('tests', 'bin', 'COUNTER_workbooks_for_tests')
    fixture = []
    for workbook in os.listdir(folder_path):
        fixture.append(mock_FileStorage_object(folder_path / workbook))
    fixture.sort(key=lambda mock_FileStorage: mock_FileStorage.filename)  # Modifying list in place returns `None`, so making modification in `return` statement makes fixture value `None`
    return fixture


#Section: Test
def test_create_dataframe(sample_COUNTER_report_workbooks, COUNTERData_relation):
    """Tests transforming multiple Excel workbooks with tabular COUNTER data into a single dataframe."""
    df = UploadCOUNTERReports(sample_COUNTER_report_workbooks).create_dataframe()
    COUNTERData_relation = COUNTERData_relation.drop(columns='report_creation_date')  # Reports ingested using the `UploadCOUNTERReports.create_dataframe()` method have no `report_creation_date` values, so a field for this value containing entirely null values is added to the dataframe returned by the method; thus, the dataframe returned by this method shouldn't have the `report_creation_date` field
    assert_frame_equal(df, COUNTERData_relation, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order