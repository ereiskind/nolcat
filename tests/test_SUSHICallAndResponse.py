"""Tests the functionality of the `SUSHICallAndResponse` class. Because the class exists solely to encapsulate API call functionality with objects of this class never being instantiated, testing the private methods is better done by sending API calls to vendors representing a variety of edge cases, which are listed on the "Testing" page of the documentation, than by calling each method directly."""
########## Passing 2023-06-07 ##########

import calendar
from datetime import date
import re
import pytest
import pyinputplus

# `conftest.py` fixtures are imported automatically
from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

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
    """A fixture to collect and store the data for making SUSHI calls."""
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

    return (URL, SUSHI_credentials)


@pytest.mark.dependency()
def test_status_call(SUSHI_credentials_fixture):
    """Tests that an API call via ``make_SUSHI_call()`` to the ``status`` endpoint returns a value of the type ``StatisticsSources._harvest_R5_SUSHI()`` expects."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "status", SUSHI_credentials).make_SUSHI_call()  # The argument "StatisticsSources.statistics_source_name" is a placeholder
    assert isinstance(response, dict) or isinstance(response[0], dict)  # EBSCO's is a dict inside a list as of 2022-12-14


@pytest.mark.dependency(depends=['test_status_call'])  # If the status call test fails, this test is skipped
def test_status_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``status`` endpoint return a valid SUSHI status response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "status", SUSHI_credentials).make_SUSHI_call()
    # The test uses the `Service_Active` key having a true value to verify the status response, but a reference to a nonexistant key will result in a key error, and the test will fail as a result. Because the capitalization and punctuation of the key is inconsistent, a regex is used to find the key.
    service_active_value = None  # The variable is initialized here so the `assert` statement won't be referencing an unassigned variable
    for key in list(response.keys()):
        if re.fullmatch(r'[sS]ervice.?[aA]ctive', key):  # No match returns `None`, a Boolean `False`, while a match returns a match object, a Boolean `True`
            service_active_value = response[key]  # The value that goes with `key` in `response`
    assert service_active_value == True or service_active_value == "True" or service_active_value == "true"


@pytest.mark.dependency()
def test_reports_call(SUSHI_credentials_fixture):
    """Tests that an API call via ``make_SUSHI_call()`` to the ``reports`` endpoint returns a value of the type ``StatisticsSources._harvest_R5_SUSHI()`` expects."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    assert isinstance(response, dict)


@pytest.mark.dependency(depends=['test_reports_call'])  # If the reports call test fails, this test is skipped
def test_reports_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports`` endpoint return a valid SUSHI list of reports."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    list_of_reports = [report for report in list(response.values())[0]]
    number_of_reports_available = len(list_of_reports)
    number_of_valid_Report_ID_values = 0
    for report in list_of_reports:
        if "Report_ID" in list(report.keys()):
            if re.fullmatch(r'(Silverchair:CR_)?[PpDdTtIi][Rr](_\w\d)?', report["Report_ID"]):
                number_of_valid_Report_ID_values += 1
    assert number_of_reports_available == number_of_valid_Report_ID_values


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_PR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/pr`` endpoint return a valid SUSHI platform report."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_PR = False
    list_of_reports = [report for report in list(check_for_report.values())[0]]
    for report in list_of_reports:
        if report["Report_ID"] == "PR" or report["Report_ID"] == "pr":  # Know this key will be found because if it couldn't be, ``test_reports_call_validity`` wouldn't have passed
            has_PR = True
    if has_PR == False:
        pytest.skip("PR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/pr", SUSHI_credentials).make_SUSHI_call()
    assert response['Report_Header']['Report_ID'] == "PR" or response['Report_Header']['Report_ID'] == "pr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_DR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/dr`` endpoint return a valid SUSHI database report."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_DR = False
    list_of_reports = [report for report in list(check_for_report.values())[0]]
    for report in list_of_reports:
        if report["Report_ID"] == "DR" or report["Report_ID"] == "dr":  # Know this key will be found because if it couldn't be, ``test_reports_call_validity`` wouldn't have passed
            has_DR = True
    if has_DR == False:
        pytest.skip("DR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/dr", SUSHI_credentials).make_SUSHI_call()
    assert response['Report_Header']['Report_ID'] == "DR" or response['Report_Header']['Report_ID'] == "dr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_TR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/tr`` endpoint return a valid SUSHI title report."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_TR = False
    list_of_reports = [report for report in list(check_for_report.values())[0]]
    for report in list_of_reports:
        if report["Report_ID"] == "TR" or report["Report_ID"] == "tr":  # Know this key will be found because if it couldn't be, ``test_reports_call_validity`` wouldn't have passed
            has_TR = True
    if has_TR == False:
        pytest.skip("TR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/tr", SUSHI_credentials).make_SUSHI_call()
    assert response['Report_Header']['Report_ID'] == "TR" or response['Report_Header']['Report_ID'] == "tr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])  # If the reports call validity test fails, this test is skipped
def test_IR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call via ``make_SUSHI_call()`` to the ``reports/ir`` endpoint return a valid SUSHI item report."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_IR = False
    list_of_reports = [report for report in list(check_for_report.values())[0]]
    for report in list_of_reports:
        if report["Report_ID"] == "IR" or report["Report_ID"] == "ir":  # Know this key will be found because if it couldn't be, ``test_reports_call_validity`` wouldn't have passed
            has_IR = True
    if has_IR == False:
        pytest.skip("IR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/ir", SUSHI_credentials).make_SUSHI_call()
    assert response['Report_Header']['Report_ID'] == "IR" or response['Report_Header']['Report_ID'] == "ir"