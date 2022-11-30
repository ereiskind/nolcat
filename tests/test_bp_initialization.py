"""Tests the routes in the `initialization` blueprint."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.initialization import *


@pytest.fixture
def flask_client():
    """Creates an instance of the Flask web app for testing."""
    app = create_app()
    app.testing = True  # Lets exceptions come through to test client
    with app.test_client() as client:
        yield client


#ToDo: Create test rendering page at `collect_initial_relation_data()` without submitting data
    #ToDo: This is just showing a page--is this test needed?


#ToDo: @pytest.mark.dependency()
#ToDo: Create test for collecting data by uploading TSVs in `collect_initial_relation_data()` 
    #ToDo: Create files with same data that's in `tests\bin\fixture_data.xlsx` aka the data in `conftest.py`
    #ToDo: Submit the files to the forms on the page (via Selenium?)
    #ToDo: Confirm that the form submission and conversion to dataframes were successful by comparing variables containing data from forms as dataframes to files used for submitting data and/or `conftest.py`


#ToDo: @pytest.mark.dependency(depends=['name_of_test_function_for_multiple_TSV_upload'])
#ToDo: Create test for loading data collected via TSV into database in `collect_initial_relation_data()`
    #ToDo: Create files with same data that's in `tests\bin\fixture_data.xlsx` aka the data in `conftest.py`
    #ToDo: Submit the files to the forms on the page (via Selenium?)
    #ToDo: At return statement for function/redirect to new page, query database for `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations and ensure results match files used for submitting data and/or `conftest.py`


#ToDo: @pytest.mark.dependency(depends=['name_of_test_function_for_multiple_TSV_upload'])--if moved to a different module, could this test be preceded by populating the database with known values?
#ToDo: @pytest.mark.dependency()
#ToDo: Create test for creation of the `annualUsageCollectionTracking` relation template in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Enter route function with `if request.method == 'GET':`
    #ToDo: Create TSV file (function through `TSV_file.close()`)
    #ToDo: Compare TSV file to contents of existing TSV file which aligns with what result should be saved in `tests` folder
    

#ToDo: @pytest.mark.dependency(depends=['name_of_test_function_for_creating_AUCT_template'])
#ToDo: Create test confirming the `annualUsageCollectionTracking` relation template can be uploaded in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Enter route function `collect_AUCT_and_historical_COUNTER_data()` with `if request.method == 'GET':`
    #ToDo: Let the page at `initial-data-upload-2.html` render
    #ToDo: Download the AUCT template via the link on the page (via Selenium?)
    #ToDo: Compare downloaded file to file which matches what result should be saved in `tests` folder


#ToDo: @pytest.mark.dependency()
#ToDo: Create test for collecting data by uploading TSVs in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Create TSV for AUCT with same data that's in `tests\bin\fixture_data.xlsx`
    #ToDo: Let the page at `initial-data-upload-2.html` render
    #ToDo: Submit the file to the appropriate form on the page (via Selenium?)
    #ToDo: Confirm that the form submission and conversion to a dataframe was successful by comparing variable containing data from form as a dataframe to file used for submitting data


#ToDo: @pytest.mark.dependency(depends=['name_of_test_function_for_AUCT_TSV_upload'])
#ToDo: Create test for loading data collected via TSV into database in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Create TSV for AUCT with same data that's in `tests\bin\fixture_data.xlsx`
    #ToDo: Let the page at `initial-data-upload-2.html` render
    #ToDo: Submit the file to the appropriate form on the page (via Selenium?)
    #ToDo: Upload AUCT data to database
    #ToDo: Check success by querying database for AUCT relation to ensure results match file used for submitting data


#ToDo: @pytest.mark.dependency()
#ToDo: Create test confirming the multi-file upload in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Upload all files in `tests\data\sample_COUNTER_data` into the appropriate form field
    #ToDo: Confirm an object of the correct type ("<class 'werkzeug.datastructures.ImmutableMultiDict'>"?) is created


#ALERT: `UploadCOUNTERReports.create_dataframe()` turns Excel workbooks into dataframes; revise tests in light of this and changes to module being tested
#ToDo: @pytest.mark.dependency(depends=['name_of_test_function_for_multiple_file_upload'])
#ToDo: @pytest.mark.dependency()
#ToDo: Create test confirming the creation of the `RawCOUNTERReport` object from the uploaded COUNTER reports in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Upload all files in `tests\data\sample_COUNTER_data` into the appropriate form field
    #ToDo: Use `RawCOUNTERReport` constructor
    #ToDo: Compare constructor result to file containing data matching what the result should be


#ToDo: @pytest.mark.dependency(depends=['name_of_test_function_for_creating_RawCOUNTERReport_object'])
#ToDo: Create test confirming the `RawCOUNTERReport` object is saved to a temp file in `collect_AUCT_and_historical_COUNTER_data()`
    #ToDo: Upload all files in `tests\data\sample_COUNTER_data` into the appropriate form field
    #ToDo: Run the route function through the redirect
    #ToDo: Compare the contents of the file that was saved by the route function to the file containing data matching what the result should be