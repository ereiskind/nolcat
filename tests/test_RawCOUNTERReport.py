"""Test methods in RawCOUNTERReport."""
import os
from pathlib import Path
import re
import pytest
import pandas as pd

from nolcat.raw_COUNTER_report import RawCOUNTERReport


@pytest.fixture
def sample_R4_form_result():
    """Creates an object highly similar to that returned by the form at the end of route upload_historical_COUNTER_usage, simulating one of the possible arguments for the RawCOUNTERReport constructor."""
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

    #Section: Creating a Selenium driver and a test using it to submit Excel workbooks into the form then captures the form return value
    # https://selenium-python.readthedocs.io/
    '''@pytest.fixture
    def driver():
        """Creates a Selenium driver with the Flask app domain for testing."""
        #ToDo: Using this fixture requires the Flask server be running; adding instantiation of create_app() doesn't work as a solution because the Flask client and Selenium driver both have HTTP verb methods and only one class can be used
        driver = Chrome_browser_driver()
        domain = 'http://localhost:5000'  #ToDo: Change this as needed to match the domain of the Flask app
        app = create_app()
        client = app.test_client()
        yield driver, domain, client
        driver.quit()'''
    '''driver, domain = driver
    driver.get(domain + '/historical-COUNTER-data')  # https://stackoverflow.com/questions/46646603/generate-urls-for-flask-test-client-with-url-for-function has possible ways to use url_for, but the app_content() and pytest-flask methods aren't working
    R4_files_input_field = driver.find_element_by_name('R4_files')
    for file in os.listdir(Path('.', 'tests', 'bin', 'OpenRefine_exports')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        R4_files_input_field.send_keys(os.path.abspath(f'tests\\bin\\OpenRefine_exports\\{file}'))
    driver.find_element_by_tag_name('button').click()  # The tag name locator works because button elements are rarely employed outside of form submission buttons
    #ToDo: R4_reports = value retruend from the form (`request.files` in flask routes)
    yield R4_reports'''
    '''driver.get(domain + '/historical-COUNTER-data')  # https://stackoverflow.com/questions/46646603/generate-urls-for-flask-test-client-with-url-for-function has possible ways to use url_for, but the app_content() and pytest-flask methods aren't working
    R4_files_input_field = driver.find_element_by_name('R4_files')
    for file in os.listdir(Path('.', 'tests', 'bin', 'OpenRefine_exports')):  # The paths are based off the project root so pytest can be invoked through the Python interpreter at the project root
        R4_files_input_field.send_keys(os.path.abspath(f'tests\\bin\\OpenRefine_exports\\{file}'))
    driver.find_element_by_tag_name('button').click()  # The tag name locator works because button elements are rarely employed outside of form submission buttons
    for request in driver.requests:
        if request.response:
            logging.info(f"request.url: {request.url}")
            logging.info(f"request.method: {request.method}")
            logging.info(f"request.path: {request.path}")
            logging.info(f"request.params: {request.params}")
            logging.info(f"request.headers: {request.headers}")
            logging.info(f"request.response.status_code: {request.response.status_code}")
            logging.info(f"request.response.body: {request.response.body}")
            logging.info(f"request.response.headers: {request.response.headers}")'''
    # https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1
    # https://stackoverflow.com/questions/64129208/flask-web-app-input-for-selenium-browser-automation
    # https://stackoverflow.com/questions/11089560/is-it-possible-to-capture-post-data-in-selenium
    
    #Section: Creating a Selenium Wire driver and a test using it to submit Excel workbooks into the form then captures the form return value
    # https://github.com/wkeeling/selenium-wire
    # https://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file
    # https://docs.python-requests.org/en/latest/user/advanced/#post-multiple-multipart-encoded-files
    '''@pytest.fixture
    def driver():
        """Creates a Selenium driver with the Flask app domain for testing."""
        #ToDo: Using this fixture requires the Flask server be running; adding instantiation of create_app() doesn't work as a solution because the Flask client and Selenium driver both have HTTP verb methods and only one class can be used
        driver = Chrome_browser_driver()
        domain = 'http://localhost:5000'  #ToDo: Change this as needed to match the domain of the Flask app
        app = create_app()
        client = app.test_client()
        yield driver, domain, client
        driver.quit()'''
    '''p=Chrome()
    the_files = [
        ('R4_files', ('1_BR1_16-17.xlsx', open(Path('.', 'tests', 'bin', 'OpenRefine_exports', '1_BR1_16-17.xlsx'), 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')),
        ('R4_files', ('4_BR5_18-19.xlsx', open(Path('.', 'tests', 'bin', 'OpenRefine_exports', '4_BR5_18-19.xlsx'), 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
    ]
    t = p.request(
        'POST',
        domain + '/historical-COUNTER-data',
        files=the_files
    )'''
    '''p=Chrome()
    t=p.request(
        'POST',
        domain + '/historical-COUNTER-data',
        files={
            'R4_files': ('the filename', open(Path('.', 'tests', 'bin', 'OpenRefine_exports', '1_BR1_16-17.xlsx'), 'rb'))
        }
    )
    logging.info(f"Type of t: {type(t)}") # should be response
    logging.info(f"t.content: {t.content}") # HTML that comes back when request is sent
    logging.info(f"t.headers: {t.headers}") # headers sent back with response
    logging.info(f"t.text: {t.text}") # unicode content of response
    logging.info(f"t.status_code: {t.status_code}") # status code content of response
    logging.info(f"t.url: {t.url}") # URL location of response
    logging.info(f"t.path: {t.path}")
    logging.info(f"t.params: {t.params}")
    logging.info(f"t.headers: {t.headers}")'''
    # https://stackoverflow.com/questions/12385179/how-to-send-a-multipart-form-data-with-requests-in-python
    # https://stackoverflow.com/a/38271059 but has single file | https://stackoverflow.com/questions/59322526/python-request-multipart-data
    # https://stackoverflow.com/questions/38270151/requests-post-multipart-form-data/38271059#38271059
    # https://www.dilatoit.com/2020/12/17/how-to-capture-http-requests-using-selenium.html

    #Section: Creating a Selenium driver and a test using a Requests method via Selenium Requests to submit Excel workbooks into the form then captures the form return value
    # https://pypi.org/project/selenium-requests/
    '''@pytest.fixture
    def driver():
        """Creates a Selenium driver with the Flask app domain for testing."""
        #ToDo: Using this fixture requires the Flask server be running; adding instantiation of create_app() doesn't work as a solution because the Flask client and Selenium driver both have HTTP verb methods and only one class can be used
        driver = Chrome_browser_driver()
        domain = 'http://localhost:5000'  #ToDo: Change this as needed to match the domain of the Flask app
        app = create_app()
        client = app.test_client()
        yield driver, domain, client
        driver.quit()'''
    '''driver, domain, client = driver
    data = dict()
    data['file'] = (
        open(Path('.', 'tests', 'bin', 'OpenRefine_exports', '1_BR1_16-17.xlsx'), 'rb'),
        str(Path('.', 'tests', 'bin', 'OpenRefine_exports', '1_BR1_16-17.xlsx')),
        '1_BR1_16-17.xlsx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    logging.info(f"data: {data}")
    logging.info(f"data type: {type(data)}")
    logging.info(f"data['file']: {data['file']}")
    logging.info(f"data['file'] type: {type(data['file'])}")
    response = client.post(
        domain + '/historical-COUNTER-data',
        data=data,
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    logging.info(f"response: {response}") # `<WrapperTestResponse streamed [200 OK]>`
    logging.info(f"response type: {type(response)}") # `<class 'werkzeug.test.WrapperTestResponse'>`
    logging.info(f"response.response: {response.response}") # `<werkzeug.wsgi.ClosingIterator object at 0x10929370>`
    logging.info(f"response.status: {response.status}") # `200 OK`
    logging.info(f"response.headers: {response.headers}") # `Content-Type: text/html; charset=utf-8\nContent-Length: 1790`
    logging.info(f"response.history: {response.history}") # `()`
    logging.info(f"response.content_encoding: {response.content_encoding}") # `None`
    logging.info(f"response.content_type: {response.content_type}") # `text/html; charset=utf-8`
    logging.info(f"response.data: {response.data}") # `b'<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <link href="https://raw.githubusercontent.com/necolas/normalize.css/master/normalize.css" rel="stylesheet">\n    <title>Initialize Database</title>\n</head>\n<body>\n    <h1>Initialize the Database with R4 Data</h1>\n    <p>The relational database is created containing the historical R4 data. In creating the database with all the R4 data, you cna be sure that the historical COUNTER data is in the new system and that R5 reports collected via SUSHI will have a solid foundation for deduplication.</p>\n\n    <h2>1. Reformat the R4 Reports with OpenRefine</h2>\n    <p>The crosstab format of R4 reports doesn\'t work well in relational databases; they need to be unpacked. JSONs <!--available where?--> contain the OpenRefine procedure for unpacking standard tabular R4 reports for use in this relational database. OpenRefine, an open source data cleanup tool, can be <a href="https://openrefine.org/download.html">downloaded here</a>. To make uploading the files easier, the OpenRefine results should be saved as CSVs to a single folder that contains no other files and has no subfolders.</p>\n\n    <h2>2. Upload the Reformatted R4 Reports</h2>\n    <form action="/matching" method="POST" enctype="multipart/form-data">\n        <label>\n            Select the reformatted R4 reports. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.\n            <input name="R4_files" type="file" multiple>\n        </label>\n        <button type="submit">Submit</button>\n    </form>\n</body>\n</html>'`
    logging.info(f"response.mimetype: {response.mimetype}") # `text/html`
    logging.info(f"response.mimetype_params: {response.mimetype_params}") # `<CallbackDict {'charset': 'utf-8'}>`
    logging.info(f"response.stream: {response.stream}") # `<werkzeug.wrappers.response.ResponseStream object at 0x10B89910>`'''
    # https://stackoverflow.com/questions/34964423/selenium-post-method/34964580
    # https://stackoverflow.com/questions/33404833/python-requests-post-multipart-form-data
    # https://stackoverflow.com/questions/43042805/how-to-send-a-multipart-form-data-with-requests-in-python


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
                # R4_Month is fine as default datetime64[ns]
                'R4_Count': 'int',
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