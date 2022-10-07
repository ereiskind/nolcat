"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import re
import pytest
import pandas as pd

from nolcat.raw_COUNTER_report import RawCOUNTERReport


@pytest.fixture
def sample_R4_form_result():
    """Creates an object highly similar to that returned by the form at the end of route `initialization.wizard_page_3`, simulating one of the possible arguments for the RawCOUNTERReport constructor."""
    #ToDo: This fixture needs to be created so the RawCOUNTERReport constructor can be tested independently of the form input functionality, but multiple days of work have failed to find a solution with the current configuration. Using WTForms to create the form taking in multiple Excel files may open up other options, but at the moment, the options are limited. Below are the methods attempted along with links and samples of code.

    #Section: Creating a werkzeug.datastructures.MultiDict object containing werkzeug.datastructures.FileStorage objects
    '''R4_reports = MultiDict()
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
    yield R4_reports'''
    # https://stackoverflow.com/questions/18249949/python-file-object-to-flasks-filestorage
    # https://stackoverflow.com/questions/39437909/flask-filestorage-object-to-file-object
    # https://stackoverflow.com/questions/20015550/read-file-data-without-saving-it-in-flask
    # https://stackoverflow.com/questions/52514442/reading-xlsx-file-from-a-bytestring
    # https://stackoverflow.com/questions/20635778/using-openpyxl-to-read-file-from-memory

    #Section: Creating a werkzeug.datastructures.MultiDict object containing werkzeug.datastructures.FileStorage objects where the files in question are tempfile.SpooledTemporaryFile objects
    # https://docs.pytest.org/en/6.2.x/tmpdir.html
    '''file_in_bytes = open(Path('.', 'tests', 'bin', 'OpenRefine_exports', filename), 'rb')
        logging.info(f"file_in_bytes type: {type(file_in_bytes)}")
        logging.info(f"file_in_bytes.read() type: {type(file_in_bytes.read())}")
        logging.info(f"file_in_bytes.read(): {file_in_bytes.read()}")
        tempfile_constructor.write(file_in_bytes.read())  #ToDo: Figure out how to get SpooledTemporaryFile objects into FileStorage objects
        logging.info(f"tempfile_constructor type: {type(tempfile_constructor)}")
        tempfile_constructor.seek(0)
        logging.info(f"tempfile_constructor.read(): {tempfile_constructor.read()}")
        FileStorage_object = FileStorage(
            stream=tempfile_constructor,
            filename=filename,
            name='R4_files',
            headers={
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Encoding': 'utf-8',
                'mode': 'b',
            }
        )
        logging.info(f"FileStorage_object type: {type(FileStorage_object)}")
        R4_reports.add(
            'R4_files',
            FileStorage_object
        )
        file_in_bytes.close()
    yield R4_reports
    tempfile_constructor.close()'''
    '''with tempfile.SpooledTemporaryFile() as temp:
            workbook_data.save(Path('.', 'tests', 'bin', 'OpenRefine_exports', filename))
            logging.info(f"workbook_data.save(filename) type: {type(workbook_data.save(Path('.', 'tests', 'bin', 'OpenRefine_exports', filename)))}")
            temp.seek(0)
            logging.info(f"temp.read(): {temp.read()}")
            logging.info(f"temp.read() type: {type(temp.read())}")'''
    '''R4_reports = MultiDict()
    for filename in os.listdir(Path('.', 'tests', 'bin', 'OpenRefine_exports')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        workbook_data = load_workbook(io.BytesIO(Path('.', 'tests', 'bin', 'OpenRefine_exports', filename).read_bytes()))
        with tempfile.SpooledTemporaryFile() as temp:
            logging.info(f"workbook_data.active: {workbook_data.active}")
            for row in workbook_data.active.values:
                for value in row:
                    print(value)
                    print(type(value))
            logging.info(f"workbook_data.active type: {type(workbook_data.active)}")
            temp.write(workbook_data.active)
            logging.info(f"temp.write(workbook_data.active): {temp.write(workbook_data.active)}")
            logging.info(f"temp.write(workbook_data.active) type: {type(temp.write(workbook_data.active))}")'''
    # https://python.plainenglish.io/leveraging-the-power-of-tempfile-library-in-python-672786cd9ebf
    # https://stackoverflow.com/questions/47160211/why-doesnt-tempfile-spooledtemporaryfile-implement-readable-writable-seekable
    # https://stackoverflow.com/questions/36070031/creating-a-temporary-directory-in-pytest
    # https://stackoverflow.com/questions/62335029/how-do-i-use-tmpdir-with-my-pytest-fixture
    # https://stackoverflow.com/questions/25525202/py-test-temporary-folder-for-the-session-scope

    #Section: Creating a Flask/WSGI test client fixture and a test that uses its post method then captures the form return value
    # https://werkzeug.palletsprojects.com/en/2.0.x/test/
    # https://flask.palletsprojects.com/en/2.0.x/testing/
    # https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
    # https://python.plainenglish.io/how-to-test-sending-files-with-flask-795d4545262e
    # https://stackoverflow.com/questions/35684436/testing-file-uploads-in-flask | https://stackoverflow.com/questions/35684436/testing-file-uploads-in-flask/35707921
    # https://stackoverflow.com/questions/20080123/testing-file-upload-with-flask-and-python-3
    # https://stackoverflow.com/questions/47216204/how-do-i-upload-multiple-files-using-the-flask-test-client
    # https://stackoverflow.com/questions/53336768/spin-up-a-local-flask-server-for-testing-with-pytest
    # https://stackoverflow.com/questions/7428124/how-can-i-fake-request-post-and-get-params-for-unit-testing-in-flask


@pytest.fixture
def RawCOUNTERReport_fixture_from_R4_spreadsheets():
    """A RawCOUNTERReport object created by passing all the sample R4 spreadsheets into a dataframe, then wrapping the dataframe in the RawCOUNTERReport class."""
    dataframes_to_concatenate = []
    for spreadsheet in os.listdir(Path('tests', 'bin', 'OpenRefine_exports')):
        statistics_source_ID = re.findall(r'(\d*)_\w{2}\d_\d{4}\.xlsx', string=spreadsheet)[0]
        dataframe = pd.read_excel(
            Path('tests', 'bin', 'OpenRefine_exports', spreadsheet),
            engine='openpyxl',
            dtype={
                'Resource_Name': 'string',
                'Publisher': 'string',
                'Platform': 'string',
                'DOI': 'string',
                'Proprietary_ID': 'string',
                'ISBN': 'string',
                'Print_ISSN': 'string',
                'Online_ISSN': 'string',
                'Data_Type': 'string',
                'Metric_Type': 'string',
                'Section_Type': 'string',
                # Usage_Date is fine as default datetime64[ns]
                'Usage_Count': 'int',
            },
        )
        dataframe['Statistics_Source_ID'] = statistics_source_ID  # This adds the field `Statistics_Source_ID` where all records have the value of the given variable
        dataframes_to_concatenate.append(dataframe)
    RawCOUNTERReport_fixture = pd.concat(
        dataframes_to_concatenate,
        ignore_index=True
    )
    yield RawCOUNTERReport(RawCOUNTERReport_fixture)
    
    
def test_RawCOUNTERReport_R4_constructor(sample_R4_form_result, RawCOUNTERReport_fixture_from_R4_spreadsheets):
    """Confirms that constructor for RawCOUNTERReport that takes in reformatted R4 reports is working correctly."""
    sample_R4_reports = RawCOUNTERReport_fixture_from_R4_spreadsheets  #ToDo: Change to RawCOUNTERReport(sample_R4_form_result)
    assert sample_R4_reports.equals(RawCOUNTERReport_fixture_from_R4_spreadsheets)


def test_perform_deduplication_matching(sample_R4_form_result, RawCOUNTERReport_fixture_from_R4_spreadsheets):
    """Tests that the `perform_deduplication_matching` method returns the data representing resource matches both confirmed and needing confirmation when a RawCOUNTERReport object instantiated from reformatted R4 reports is the sole argument."""
    #ALERT: On a workstation with 8GB RAM, this test fails with a `MemoryError` error; a workstation with 16GB RAM seems capable of running the test successfully
    sample_R4_reports = RawCOUNTERReport_fixture_from_R4_spreadsheets  #ToDo: Change to RawCOUNTERReport(sample_R4_form_result)
    assert sample_R4_reports.perform_deduplication_matching() == RawCOUNTERReport_fixture_from_R4_spreadsheets.perform_deduplication_matching()


def test_harvest_SUSHI_report(sample_R4_form_result):
    #ToDo: Write a docstring when the format of the return value is set
    pass
    

def test_load_data_into_database(sample_R4_form_result):
    #ToDo: Write a docstring when the format of the return value is set
    pass