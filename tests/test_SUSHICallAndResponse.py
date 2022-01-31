from datetime import date
import pytest
import pyinputplus

from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

"""
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
    user_id = input("Enter the SUSHI customer ID: ")
    requestor_id = input("Enter the SUSHI requestor ID or just press enter if none exists: ")
    api_key = input("Enter the SUSHI API key or just press enter if none exists: ")
    platform = input("Enter the SUSHI platform or just press enter if none exists: ")

    SUSHI_credentials = dict(user_id = user_id)
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
    """Tests a SUSHI API call to the `status` endpoint."""
    #ToDo: URL, SUSHI_credentials, month = SUSHI_credentials_fixture
    #ToDo: response = SUSHICallAndResponse(URL, "status", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: If constructor returns JSON-like dictionary, assert response['ServiceActive'] = True
    pass


def test_reports_call(SUSHI_credentials_fixture):
    """Tests a SUSHI API call to the `reports` endpoint."""
    #ToDo: URL, SUSHI_credentials, month = SUSHI_credentials_fixture
    #ToDo: response = SUSHICallAndResponse(URL, "reports", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: If constructor returns list of JSON-like dictionaries, checking_reports = 0
    #ToDo: for report in response:
        #ToDo: if report['Release'] == 5: should having keys "Report_Name", "Report_ID", "Release", "Report_Description", "Path" also be tested?
            #ToDo: checking_reports += 1
    #ToDo: assert len(response) == checking_reports
    pass


def test_PR_call(SUSHI_credentials_fixture):
    """Tests a SUSHI API call to the `reports/pr` endpoint."""
    #ToDo: URL, SUSHI_credentials, month = SUSHI_credentials_fixture
    #ToDo: check_for_report = SUSHICallAndResponse(URL, "reports", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: SUSHI_credentials['begin_date'] = month
    #ToDo: SUSHI_credentials['end_date'] = month
    #ToDo: If constructor returns list of JSON-like dictionaries, has_PR = False
    #ToDo: for report in check_for_report:
        #ToDo: if report['Path'] == "/reports/pr":
            #ToDo: has_PR = True
    #ToDo: if has_PR == False:
        #ToDo: assert True  # There can't be a problem with something that doesn't exist
    #ToDo: response = SUSHICallAndResponse(URL, "reports/pr", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: assert report['Report_Header']['Report_ID'] == "PR"
    pass


def test_DR_call(SUSHI_credentials_fixture):
    """Tests a SUSHI API call to the `reports/dr` endpoint."""
    #ToDo: URL, SUSHI_credentials, month = SUSHI_credentials_fixture
    #ToDo: check_for_report = SUSHICallAndResponse(URL, "reports", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: SUSHI_credentials['begin_date'] = month
    #ToDo: SUSHI_credentials['end_date'] = month
    #ToDo: If constructor returns list of JSON-like dictionaries, has_DR = False
    #ToDo: for report in check_for_report:
        #ToDo: if report['Path'] == "/reports/dr":
            #ToDo: has_DR = True
    #ToDo: if has_DR == False:
        #ToDo: assert True  # There can't be a problem with something that doesn't exist
    #ToDo: response = SUSHICallAndResponse(URL, "reports/dr", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: assert report['Report_Header']['Report_ID'] == "DR"
    pass


def test_TR_call(SUSHI_credentials_fixture):
    """Tests a SUSHI API call to the `reports/tr` endpoint."""
    #ToDo: URL, SUSHI_credentials, month = SUSHI_credentials_fixture
    #ToDo: check_for_report = SUSHICallAndResponse(URL, "reports", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: SUSHI_credentials['begin_date'] = month
    #ToDo: SUSHI_credentials['end_date'] = month
    #ToDo: If constructor returns list of JSON-like dictionaries, has_TR = False
    #ToDo: for report in check_for_report:
        #ToDo: if report['Path'] == "/reports/tr":
            #ToDo: has_TR = True
    #ToDo: if has_TR == False:
        #ToDo: assert True  # There can't be a problem with something that doesn't exist
    #ToDo: response = SUSHICallAndResponse(URL, "reports/tr", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: assert report['Report_Header']['Report_ID'] == "TR"
    pass


def test_IR_call(SUSHI_credentials_fixture):
    """Tests a SUSHI API call to the `reports/ir` endpoint."""
    #ToDo: URL, SUSHI_credentials, month = SUSHI_credentials_fixture
    #ToDo: check_for_report = SUSHICallAndResponse(URL, "reports", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: SUSHI_credentials['begin_date'] = month
    #ToDo: SUSHI_credentials['end_date'] = month
    #ToDo: If constructor returns list of JSON-like dictionaries, has_IR = False
    #ToDo: for report in check_for_report:
        #ToDo: if report['Path'] == "/reports/ir":
            #ToDo: has_IR = True
    #ToDo: if has_IR == False:
        #ToDo: assert True  # There can't be a problem with something that doesn't exist
    #ToDo: response = SUSHICallAndResponse(URL, "reports/ir", SUSHI_credentials).make_SUSHI_call()
    #ToDo: If constructor returns error messages, the test fails
    #ToDo: assert report['Report_Header']['Report_ID'] == "IR"
    pass