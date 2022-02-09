from datetime import date
import pytest
import pyinputplus

from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

""" About this test module:
There are two ways in which the result of an API call made via the `SUSHICallAndResponse` class can be considered to be an error: there can be a Python run-time error which causes the program to crash, or there can be an invalid response to the API call resulting from either a run-time error handled in the program or a SUSHI error. This test module contains tests for both conditions: `test_status_call` and `test_reports_call` test that API calls to the `status` and `reports` endpoints can be made without run-time errors, while the `test_status_call_validity`, `test_reports_call_validity`, `test_PR_call_validity`, `test_DR_call_validity`, and `test_IR_call_validity` tests check that the API call returns a valid SUSHI response that the rest of the program can use. The master report calls aren't checked for run-time errors because 1) the chance of a run-time error for a master report call when the status and reports calls were file is low and 2) the conditional expression that would trigger a `skipif` decorator if another test was skipped couldn't be found.

For testing the SUSHI API, a fixture that prompts the user for the SUSHI API information in stdout is applied to all the tests requiring data to make API calls. This semi-automated method, which collects a valid SUSHI URL and set of credentials from the user and applies them to all tests, is used because:
    1. There is no set of testing credentials; even using the SwaggerHub testing service requires SUSHI credentials from a vendor.
    2. SUSHI credentials are unique to each institution and should be secret, so using the API would require another secure file or a mechanism to randomly select a set of SUSHI credentials from whereever they're being stored.
    3. The JSON formatting used for the API responses contains some inconsistencies among vendors, so the ability to control which vendor is being used for testing is valuable.
"""
#ToDo: Test for longer periods of time and more granular reports will be done by testing the StatisticsSources._harvest_R5_SUSHI method


@pytest.fixture(scope='session')  # Without the scope, the data prompts appear in stdout for each test
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

    return (URL, SUSHI_credentials)


def test_status_call(SUSHI_credentials_fixture):
    """Tests that a valid value is returned from using ``make_SUSHI_call`` to make the API call to the ``status`` endpoint."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "status", SUSHI_credentials).make_SUSHI_call()  # The argument "StatisticsSources.statistics_source_name" is a placeholder
    assert str(type(response)) == "<class 'dict'>"


@pytest.mark.skipif('not test_status_call')  # If the status call test fails, this test is skipped
def test_status_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call to the ``status`` endpoint return a valid SUSHI response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "status", SUSHI_credentials).make_SUSHI_call()
    if list(response.keys()) == ["ERROR"]:
        assert False
    # When the assert statement is a series of expressions featuring named index references to `response` seperated by `or`, the test fails if the first expression features a dictionary key/field name not in `response`, even if one of the later expressions is true. Tests don't finish with a passing result at assert statements that evaluate to true, so if blocks and try/except statements aren't viable; an intermediary variable is the only viable solution.
    if "Service_Active" in list(response.keys()):
        service_active_value = response['Service_Active']
    elif "ServiceActive" in list(response.keys()):
        service_active_value = response['ServiceActive']
    assert service_active_value == True or service_active_value == "True" or service_active_value == "true"


def test_reports_call(SUSHI_credentials_fixture):
    """Tests that a valid value is returned from using ``make_SUSHI_call`` to make the API call to the ``reports`` endpoint."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    assert str(type(response)) == "<class 'dict'>"


@pytest.mark.skipif('not test_status_call')  # If the status call test fails, this test is skipped
def test_reports_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call to the ``reports`` endpoint return a valid SUSHI response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    for reports_list in response.values():
        reports_list_length = len(reports_list)  # Because this loop only executes once, this assignment is viable
        counting_Report_ID = 0
        for report_description in reports_list:
            if "Report_ID" in list(report_description.keys()):
                counting_Report_ID += 1
    assert reports_list_length == counting_Report_ID


@pytest.mark.skipif('not test_reports_call')
def test_PR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call to the ``reports/pr`` endpoint return a valid SUSHI response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_PR = False
    for reports_list in check_for_report.values():
        for report_description in reports_list:
            if report_description['Report_ID'] == "PR":
                has_PR = True
    if has_PR == False:
        pytest.skip("PR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/pr", SUSHI_credentials).make_SUSHI_call()
    print(f"The PR validity response is {response}")
    #ToDo: assert report['Report_Header']['Report_ID'] == "PR"


@pytest.mark.skipif('not test_reports_call')
def test_DR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call to the ``reports/dr`` endpoint return a valid SUSHI response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_DR = False
    for reports_list in check_for_report.values():
        for report_description in reports_list:
            if report_description['Report_ID'] == "DR":
                has_DR = True
    if has_DR == False:
        pytest.skip("DR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/dr", SUSHI_credentials).make_SUSHI_call()
    print(f"The DR validity response is {response}")
    #ToDo: assert report['Report_Header']['Report_ID'] == "DR"


@pytest.mark.skipif('not test_reports_call')
def test_TR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call to the ``reports/tr`` endpoint return a valid SUSHI response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_TR = False
    for reports_list in check_for_report.values():
        for report_description in reports_list:
            if report_description['Report_ID'] == "TR":
                has_TR = True
    if has_TR == False:
        pytest.skip("TR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/tr", SUSHI_credentials).make_SUSHI_call()
    print(f"The TR validity response is {response}")
    #ToDo: assert report['Report_Header']['Report_ID'] == "TR"


@pytest.mark.skipif('not test_reports_call')
def test_IR_call_validity(SUSHI_credentials_fixture):
    """Tests that the API call to the ``reports/ir`` endpoint return a valid SUSHI response."""
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    check_for_report = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports", SUSHI_credentials).make_SUSHI_call()
    has_IR = False
    for reports_list in check_for_report.values():
        for report_description in reports_list:
            if report_description['Report_ID'] == "IR":
                has_IR = True
    if has_IR == False:
        pytest.skip("IR not offered by this vendor.")
    response = SUSHICallAndResponse("StatisticsSources.statistics_source_name", URL, "reports/ir", SUSHI_credentials).make_SUSHI_call()
    print(f"The IR validity response is {response}")
    #ToDo: assert report['Report_Header']['Report_ID'] == "IR"