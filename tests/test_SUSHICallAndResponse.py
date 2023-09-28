"""Tests the functionality of the `SUSHICallAndResponse` class. Because the class exists solely to encapsulate API call functionality with objects of this class never being instantiated, testing the private methods is better done by sending API calls to vendors representing a variety of edge cases, which are listed on the "Testing" page of the documentation, than by calling each method directly."""
########## Passing 2023-09-13 ##########

import pytest
import logging
import calendar
from datetime import date
import re
import pyinputplus

# `conftest.py` fixtures are imported automatically
from conftest import COUNTER_reports_offered_by_statistics_source
from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

log = logging.getLogger(__name__)

""" About this test module:
There are two ways in which the result of an API call made via the `SUSHICallAndResponse` class can be considered to be an error: there can be a Python run-time error which causes the program to crash, or there can be an invalid response to the API call resulting from either a run-time error handled in the program or a SUSHI error. This test module contains tests for both conditions: `test_status_call` and `test_reports_call` test that API calls to the `status` and `reports` endpoints can be made without run-time errors, while the `test_status_call_validity`, `test_reports_call_validity`, `test_PR_call_validity`, `test_DR_call_validity`, and `test_IR_call_validity` tests check that the API call returns a valid SUSHI response that the rest of the program can use. The customizable report calls aren't checked for run-time errors because 1) the chance of a run-time error for a customizable report call when the status and reports calls were file is low and 2) the conditional expression that would trigger a `skipif` decorator if another test was skipped couldn't be found.

For testing the SUSHI API, a fixture that prompts the user for the SUSHI API information in stdout which is then applied to all the tests requiring data to make API calls. This semi-automated method, which collects a valid SUSHI URL and set of credentials from the user and applies them to all tests, is used because:
    1. There is no set of testing credentials; even using the SwaggerHub testing service requires SUSHI credentials from a vendor.
    2. SUSHI credentials are unique to each institution and should be secret, so using the API would require another secure file or a mechanism to randomly select a set of SUSHI credentials from wherever they're being stored.
    3. The JSON formatting used for the API responses contains some inconsistencies among vendors, so the ability to control which vendor is being used for testing is valuable.

The private helper methods don't have their own tests because they operate only as part of the `SUSHICallAndResponse.make_SUSHI_call()` method and are thus only being tested in that context.
"""


@pytest.fixture(scope='module')  # Without the scope, the data prompts appear in stdout for each test
def SUSHI_credentials_fixture():
    """A fixture to collect and store the data for making SUSHI calls.
    
    Yields:
        tuple: the URL and parameters dictionary needed to make a SUSHI call
    """
    URL = input("Enter the SUSHI base URL, including the final backslash: ")
    customer_id = input("Enter the SUSHI customer ID: ")
    requestor_id = input("Enter the SUSHI requestor ID or just press enter if none exists: ")
    api_key = input("Enter the SUSHI API key or just press enter if none exists: ")
    platform = input("Enter the SUSHI platform or just press enter if none exists: ")

    SUSHI_credentials = dict(customer_id = customer_id)
    if requestor_id != "":
        SUSHI_credentials['requestor_id'] = requestor_id
    if api_key != "":
        SUSHI_credentials['api_key'] = api_key
    if platform != "":
        SUSHI_credentials['platform'] = platform
    
    SUSHI_credentials['begin_date'] = pyinputplus.inputDate(
        "Please enter the year and month for the first month of stats collection. The month must be two digits and the year must be four digits. ",
        formats=[
            '%Y%m', # yyyymm
            '%m-%Y', # mm-yyyy
            '%m/%Y', # mm/yyyy
            '%Y-%m', # yyyy-mm
            '%Y/%m', # yyyy/mm
        ]
    )
    SUSHI_credentials['end_date'] = date.min # This ensures that the while loop runs at least once
    while SUSHI_credentials['end_date'] < SUSHI_credentials['begin_date']:
        SUSHI_credentials['end_date'] = pyinputplus.inputDate(
            f"Please enter the year and month for the last month of stats collection; this must be the same as or after {SUSHI_credentials['begin_date'].strftime('%Y-%m')}. The month must be two digits and the year must be four digits. ",
            formats=[
                '%Y%m', # yyyymm
                '%m-%Y', # mm-yyyy
                '%m/%Y', # mm/yyyy
                '%Y-%m', # yyyy-mm
                '%Y/%m', # yyyy/mm
            ]
        )
    SUSHI_credentials['end_date'] = date(  # This changes the date from the first to the last day of the month to avoid the SUSHI `Invalid Date Arguments` error
        SUSHI_credentials['end_date'].year,
        SUSHI_credentials['end_date'].month,
        calendar.monthrange(SUSHI_credentials['end_date'].year, SUSHI_credentials['end_date'].month)[1]
    )

    yield (URL, SUSHI_credentials)


@pytest.mark.dependency()
def test_status_call(SUSHI_credentials_fixture, SUSHI_server_error_regex_object, no_SUSHI_data_regex_object, caplog):
    """Tests that an API call via ``make_SUSHI_call()`` to the ``status`` endpoint returns a value of the type ``StatisticsSources._harvest_R5_SUSHI()`` expects."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "status", SUSHI_credentials).make_SUSHI_call()  # The argument "StatisticsSources.statistics_source_name" is a placeholder
    assert isinstance(response, tuple)
    if isinstance(response[0], str):
        if SUSHI_server_error_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned a server-based SUSHI error.")
        elif no_SUSHI_data_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned no data.")
    assert isinstance(response[0], dict) or (isinstance(response[0][0], dict) and len(response[0]) == 1)  # EBSCO's is a dict inside a list as of 2022-12-14


@pytest.mark.dependency(depends=['test_status_call'])  # If the status call test fails, this test is skipped
def test_status_call_validity(SUSHI_credentials_fixture, caplog):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``status`` endpoint return a valid SUSHI status response."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "status", SUSHI_credentials).make_SUSHI_call()
    # The test uses the `Service_Active` key having a true value to verify the status response, but a reference to a nonexistant key will result in a key error, and the test will fail as a result. Because the capitalization and punctuation of the key is inconsistent, a regex is used to find the key.
    service_active_value = None  # The variable is initialized here so the `assert` statement won't be referencing an unassigned variable
    for key in list(response[0].keys()):
        if re.fullmatch(r'[sS]ervice.?[aA]ctive', key):  # No match returns `None`, a Boolean `False`, while a match returns a match object, a Boolean `True`
            service_active_value = response[0][key]  # The value that goes with `key` in `response[0]`
    assert service_active_value == True or service_active_value == "True" or service_active_value == "true"


@pytest.mark.dependency()
def test_reports_call(SUSHI_credentials_fixture, SUSHI_server_error_regex_object, no_SUSHI_data_regex_object, caplog):
    """Tests that an API call via ``make_SUSHI_call()`` to the ``reports`` endpoint returns a value of the type ``StatisticsSources._harvest_R5_SUSHI()`` expects."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, tuple)
    if isinstance(response[0], str):
        if SUSHI_server_error_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned a server-based SUSHI error.")
        elif no_SUSHI_data_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned no data.")
    assert isinstance(response[0], dict)


@pytest.mark.dependency(depends=['test_reports_call'])  # If the reports call test fails, this test is skipped
def test_reports_call_validity(SUSHI_credentials_fixture, caplog):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports`` endpoint return a valid SUSHI list of reports."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    list_of_reports = [report for report in list(response[0].values())[0]]
    number_of_reports_available = len(list_of_reports)
    number_of_valid_Report_ID_values = 0
    for report in list_of_reports:
        if "Report_ID" in list(report.keys()):
            if re.fullmatch(r'(Silverchair:CR_)?(LL_C)?[PpDdTtIi]?[Rr](_\w\d)?', report["Report_ID"]):
                number_of_valid_Report_ID_values += 1
    assert number_of_reports_available == number_of_valid_Report_ID_values


@pytest.fixture
def list_of_reports(SUSHI_credentials_fixture):
    """A fixture feeding the entered SUSHI data into the `COUNTER_reports_offered_by_statistics_source` function.

    Args:
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call

    Yields:
        list: the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
    """
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    yield COUNTER_reports_offered_by_statistics_source(
        "StatisticsSources.statistics_source_name",
        URL,
        SUSHI_credentials
    )


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_PR_call_validity(SUSHI_credentials_fixture, list_of_reports, SUSHI_server_error_regex_object, no_SUSHI_data_regex_object, caplog):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/pr`` endpoint return a valid SUSHI platform report."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "PR" not in list_of_reports:
        pytest.skip("PR not offered by this statistics source.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/pr", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, tuple)
    if isinstance(response[0], str):
        if SUSHI_server_error_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned a server-based SUSHI error.")
        elif no_SUSHI_data_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned no data.")
    else:
        assert response[0].get('Report_Header').get('Report_ID') == "PR" or response[0].get('Report_Header').get('Report_ID') == "pr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_DR_call_validity(SUSHI_credentials_fixture, list_of_reports, SUSHI_server_error_regex_object, no_SUSHI_data_regex_object, caplog):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/dr`` endpoint return a valid SUSHI database report."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "DR" not in list_of_reports:
        pytest.skip("DR not offered by this statistics source.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/dr", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, tuple)
    if isinstance(response[0], str):
        if SUSHI_server_error_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned a server-based SUSHI error.")
        elif no_SUSHI_data_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned no data.")
    else:
        assert response[0].get('Report_Header').get('Report_ID') == "DR" or response[0].get('Report_Header').get('Report_ID') == "dr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_TR_call_validity(SUSHI_credentials_fixture, list_of_reports, SUSHI_server_error_regex_object, no_SUSHI_data_regex_object, caplog):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/tr`` endpoint return a valid SUSHI title report."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "TR" not in list_of_reports:
        pytest.skip("TR not offered by this statistics source.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/tr", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, tuple)
    if isinstance(response[0], str):
        if SUSHI_server_error_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned a server-based SUSHI error.")
        elif no_SUSHI_data_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned no data.")
    else:
        assert response[0].get('Report_Header').get('Report_ID') == "TR" or response[0].get('Report_Header').get('Report_ID') == "tr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_IR_call_validity(SUSHI_credentials_fixture, list_of_reports, SUSHI_server_error_regex_object, no_SUSHI_data_regex_object, caplog):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/ir`` endpoint return a valid SUSHI item report."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "IR" not in list_of_reports:
        pytest.skip("IR not offered by this statistics source.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/ir", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, tuple)
    if isinstance(response[0], str):
        if SUSHI_server_error_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned a server-based SUSHI error.")
        elif no_SUSHI_data_regex_object.match(string=response[0]):
            pytest.skip("The test is being skipped because the API call returned no data.")
    else:
        assert response[0].get('Report_Header').get('Report_ID') == "IR" or response[0].get('Report_Header').get('Report_ID') == "ir"


@pytest.mark.dependency(depends=['test_PR_call_validity'])  # If the PR call validity test fails, this test is skipped
def test_call_with_invalid_credentials(SUSHI_credentials_fixture, caplog):
    """Tests that a SUSHI call with invalid credentials returns an error.
    
    There's no check confirming that the PR is available; if it wasn't, the dependency would prevent this test from running.
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    SUSHI_credentials['customer_id'] = "deliberatelyIncorrect"
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/pr", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, tuple)
    assert response[0].startswith(f"Call to StatisticsSources.statistics_source_name raised")  # Each platform seems to handle invalid credentials slightly differently--some use HTTP 400, some use HTTP 500, some use SUSHI error--so a more specific match can't be made
    assert isinstance(response[1], list)