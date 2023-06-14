"""Test using `UploadCOUNTERReports`."""
########## Failing 2023-06-07 ##########

import pytest
from pathlib import Path
from io import BytesIO
from tempfile import SpooledTemporaryFile
import os
from werkzeug.datastructures import FileStorage
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
        p=Path(folder_path / workbook)
        x=open(p, 'rb+')
        print(f"`open(p, 'rb+')` while open is {x} (type {repr(type(x))})\n{x.__dict__}")
        x.close()
        print(f"`open(p, 'rb+')` after closing is {x} (type {repr(type(x))})\n{x.__dict__}")
        with open(p, 'rb+') as f:
            y=BytesIO(f.read())
            print(f"`BytesIO(f.read())` in block is {y} (type {repr(type(y))})\n{y.__dict__}")
        try:
            print(f"`BytesIO(f.read())` out of block is {y} (type {repr(type(y))})\n{y.__dict__}")
        except:
            pass

        try:
            z=SpooledTemporaryFile(_file=x)
            print(f"`SpooledTemporaryFile(_file=x)` is {z} (type {repr(type(z))})\n{z.__dict__}")
        except Exception as e:
            print(f"`SpooledTemporaryFile(_file=x)` raised {e}")
        
        try:
            z=SpooledTemporaryFile()
            z._file=x
            print(f"`SpooledTemporaryFile()` followed by `._file=` is {z} (type {repr(type(z))})\n{z.__dict__}")
        except Exception as e:
            print(f"`SpooledTemporaryFile()` followed by `._file=` raised {e}")
        
        try:
            with SpooledTemporaryFile() as t:
                print(f"`with SpooledTemporaryFile() as t` is {t} (type {repr(type(t))})\n{t.__dict__}")
                with open(p, 'rb+') as f:
                    print(f"`with open(p, 'rb+') as f` in block `with SpooledTemporaryFile() as t` is {f} (type {repr(type(f))})\n{f.__dict__}")
                    try:
                        z = BytesIO(f)
                        print(f"`BytesIO(f)` is {z} (type {repr(type(z))})\n{z.__dict__}")
                    except Exception as e:
                        print(f"`BytesIO(f)` raised {e}")
                    
                    try:
                        print(f"`f.read()` is {f.read()} (type {repr(type(f.read()))})")
                        z = BytesIO(f.read())
                        print(f"`BytesIO(f.read())` is {z} (type {repr(type(z))})\n{z.__dict__}")
                    except Exception as e:
                        print(f"`BytesIO(f.read())` raised {e}")
        except Exception as e:
            print(f"`with SpooledTemporaryFile() as t` raised {e}")
        #Test: End testing section
        FileStorage_object = FileStorage(
            stream = z,  # tempfile.SpooledTemporaryFile object from `workbook`
            filename=str(workbook),
            name='COUNTER_reports',  # Name of form field, which is the same in both forms
        )
        fixture.append(FileStorage_object)
    return fixture


def test_create_dataframe(sample_COUNTER_report_workbooks, COUNTERData_relation):
    """Tests transforming multiple Excel workbooks with tabular COUNTER data into a single dataframe."""
    df = UploadCOUNTERReports(sample_COUNTER_report_workbooks).create_dataframe()  #TEST: Test fails due to raising `TypeError: object cannot be converted to an IntegerDtype`
    COUNTERData_relation = COUNTERData_relation.drop(columns='report_creation_date')  # Reports ingested using the `UploadCOUNTERReports.create_dataframe()` method have no `report_creation_date` values, so a field for this value containing entirely null values is added to the dataframe returned by the method; thus, the dataframe returned by this method shouldn't have the `report_creation_date` field
    assert_frame_equal(df, COUNTERData_relation, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order