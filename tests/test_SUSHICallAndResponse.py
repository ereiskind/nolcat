"""Tests the functionality of the `SUSHICallAndResponse` class. Because the class exists solely to encapsulate API call functionality with objects of this class never being instantiated, testing the private methods is better done by sending API calls to vendors representing a variety of edge cases, which are listed on the "Testing" page of the documentation, than by calling each method directly."""
########## Passing 2026-04-17 ##########

import pytest
from datetime import date
import re
import csv
import pyinputplus

# `conftest.py` fixtures are imported automatically
from nolcat.nolcat_glue_job import *
from nolcat.models import PATH_TO_CREDENTIALS_FILE
from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

log = logging.getLogger(__name__)

""" About this test module:
There are two ways in which the result of an API call made via the `SUSHICallAndResponse` class can be considered to be an error: there can be a Python run-time error which causes the program to crash, or there can be an invalid response to the API call resulting from either a run-time error handled in the program or a SUSHI error. This test module contains tests for both conditions: `test_status_call` and `test_reports_call` test that API calls to the `status` and `reports` endpoints can be made without run-time errors, while the `test_status_call_validity`, `test_reports_call_validity`, `test_PR_call_validity`, `test_DR_call_validity`,`test_TR_call_validity`, and `test_IR_call_validity` tests check that the API call returns a valid SUSHI response that the rest of the program can use. The customizable report calls aren't checked for run-time errors because 1) the chance of a run-time error for a customizable report call when the status and reports calls were file is low and 2) the conditional expression that would trigger a `skipif` decorator if another test was skipped couldn't be found.

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
    #TEST: temp
    from random import choice
    registry_ID = choice([
        "002f6967-f617-445c-b7cd-0c1e2bdf72c0",
        "00d5a2f9-6e24-4909-86d4-4eb867dc2e1c",
        "0657858f-f079-4200-a79e-1698cf36a95a",
        "0f213bd4-70c0-4c9d-a540-3d138af8fe9c",
        "0ffedf0a-37a5-44fb-8564-e8d0b7b6d855",
        "1860d58d-dc85-4105-8477-910a56025cc1",
        "19f529b8-f978-4484-ac0f-ad61b8ff9b06",
        "1a84e072-cf3e-4ec5-8e65-261627cc1ca6",
        "1db3607b-3046-4e78-84b7-69e1c46fdb96",
        "20db7a04-3830-4530-82bb-77261e7d708a",  # Raised error in COUNTER URL collection that's now repaired
        "216dfdc9-d477-499b-a4be-2e94401b587a",
        "27258001-c4ff-4f56-aa0b-a27c37bb921d",
        "28a08a22-5811-4a52-9596-cb9eac770e74",
        "2b76f3de-e577-4691-aab2-20abba43b3c9",
        "2b8d6f15-6824-45e0-950c-753168223d08",
        "2f0e9433-7217-4196-9ee2-9baf3cf179a1",
        "2f5ec015-04d7-4bf2-8504-81f0bff9bfa7",
        "303d7b33-8c1d-4d63-9810-15012c0200c6",
        "3293c6c6-3ced-491b-ad5d-47ce565dcdcb",
        #"335608df-e4d2-46ad-bd89-fb3683035441",  # Killed at `[2026-05-14 15:19:08] nolcat.SUSHI_call_and_response::592 -  request raised error 1011: Report Queued for Processing due to successful request. You must re-request this report to receive data. Please allow 1 hour for processing before retrying.. Try the call again later.`
        "3435e5a7-eb36-46f8-8e8e-c7368310d879",
        "34430d4c-b51d-4a7b-8f8e-ef28e48ebd53",
        "36d1e996-028c-4c72-8d45-84ba79cdf456",
        "36dbf9d6-735b-44c7-aa4c-c462b26368fa",
        "38b08a9f-4828-4ab8-82ff-38c6cffcc434",
        "3dfd4ff2-39f3-4c55-b6d6-96667632330a",
        "413dfeb0-63f4-4d6e-b47f-1fbe6546926b",
        "4549ba3a-728e-4cdb-a86f-0d84ba9cc96b",
        "463357e2-7abc-4c2b-9c51-b15c58f01281",
        "47a11f6e-4455-42de-9590-6398ab300379",
        "49bb5329-ee48-4a11-be77-8582ce73cba3",
        "4da3d0d2-2be6-49d4-a12e-b5063c9854dc",
        "54f0fec6-2b49-469d-956b-12e54e53144c",
        "5511ea8a-0c66-4ac8-ae8c-512b50ff3d17",
        "5541d245-4230-405c-b7c1-f51b27926666",
        "56b99269-420c-40f6-a6fb-78524fe57c10",
        "56bdf474-5297-45f0-841f-4083725b4595",
        "570ee10e-a903-4f06-b9b1-33759ef204d4",
        "5c6cf954-7dc4-4986-b14f-dc3b752608ce",
        "609c6759-f1a4-4f53-a142-603fa3385b9d",
        "60c7aa79-272d-4610-8ad5-c399bd938c8e",
        "618759fd-bd3e-4617-a0d1-ccbe06c22171",
        "64beeb39-6f5e-4642-96d0-fc46c4856c26",
        #"6809e99d-211e-403d-be12-bbbd871883ba",  # Killed at `[2026-05-14 15:25:23] nolcat.SUSHI_call_and_response::582 -  request raised error 3030: No Usage Available for Requested Dates due to requested data between 2025-10-01 and2026-03-31.`
        "6839b3e4-1a57-413e-9b3f-9faa4df06d54",
        "6f0e112f-34fb-40c0-a3b0-23a34dfacddd",
        "6f9530b9-6ece-446d-ac59-8c67d08927c3",
        "70846dfc-1a3a-4615-88e1-d624acd71163",
        "71f5c132-7509-4469-841f-334da840ea01",
        "741ebb85-02ad-4ad0-ae4f-8b268f528cb0",
        "76ce8454-29f6-43c4-8d1a-aaeb34bc8a1a",
        "777e6538-5ae8-443f-94e3-0110061e4f06",
        "7a59353f-c8cf-4069-891c-0c403323496a",
        #"7c7bdde7-7acf-42c3-a3b8-8f24a9dad614",  # [2026-05-14 13:32:32] nolcat.SUSHI_call_and_response::160 - The report has an `Alerts` key on the same level as `Report_Header` containing a single exception or a list of exceptions: [{'Date_Time': '2025-02-28T00:00:00Z', 'Alert': 'Report providers MUST be compliant by Feburary 2025 for delivery of reports starting with January 2025 usage'}, {'Date_Time': '2025-05-01T00:00:00Z', 'Alert': 'Report providers MUST offer R5-compliant reports until April 2025 for delivery of reports up to and including March 2025 usage'}].
        "819c19e4-7956-4990-b11d-602d08fdae81",
        "81b01046-eb27-40e6-a855-bd84a9a03c89",
        #"8370854d-5e3e-4bd7-9ea4-b06c07bf5bee",  # Killed at `[2026-05-14 15:15:53] nolcat.SUSHI_call_and_response::582 -  request raised error 3030: No Usage Available for Requested Dates due to requested data between 2025-10-01 and2026-03-31.`
        "8700fafb-1c6f-4481-975e-b93f4d8bd6ad",
        "87c1c2b6-ed9e-49f8-ab4c-ef4bf1dc058c",
        "8810096a-1a17-48f3-9614-5a81fff27e7e",
        "8c20c6d6-9205-4772-a366-5f95c79c032a",
        "91af9af9-6266-4d28-8554-966aec3311fd",
        "91e3d8ee-445c-4cb6-bd1f-17b1c12f12b6",
        "93955b59-c9ef-4a68-a57f-4e1e7182f8fa",
        "9915287a-b1b5-43eb-be89-38fd118322e6",
        "9a2d940d-dcee-4f0c-b86c-18b72df9d9d9",
        "9c7adeeb-6b27-4f36-9196-850b523473fb",
        "9cfe52d0-e9bc-49e2-9576-8aa1e875f7a0",
        "9e34f261-315a-48a3-92ca-9af70c5e099a",
        "9ffd0923-0974-4287-a124-a38a59b78198",
        "a1ac56f3-7d55-4d78-9e06-c129eddacb93",
        "a44d3e70-3166-4d1e-870f-69bb22335a77",
        "a8cead1d-6432-4fc6-8e0a-e5a8461dfccb",
        "adccc1b0-f93d-43eb-9df5-a2d8bfbb25df",
        "aeaf1e8e-094d-49cb-a243-8f1614169383",
        "aff7c360-f57b-45b7-95b7-b64e8f04a688",
        "b0d81a4b-9023-42ac-a034-703c23124cae",
        "b12a63a4-0aa0-45c9-8c92-2a60a3d97bcf",
        "b2b2736c-2cb9-48ec-91f4-870336acfb1c",
        "b930fc8f-f777-446d-be8c-7bb7acac2183",
        "bc2a4cec-e44e-4c07-bccf-3c5524bc0465",
        "c230a459-4a07-49eb-8d9f-96adeb2a762d",
        "c305c44c-e97c-491c-8c62-404a9482ad63",
        "c47393d0-95d8-4c32-8488-2dec65cd98d7",
        "c517aed2-5e9d-4f6b-9c0b-b6249e522568",
        "c5bdad2a-f434-4c9e-9ab7-ddbf44d781e9",
        "c67345a4-34f7-445e-ad49-b38b21438b59",
        "c976a8e4-ecc7-4c47-aff6-94d2fa3f996d",
        "da757bb5-4a5e-449b-9434-81eb33cfc696",
        "dedcfe80-7f4f-4d32-9c88-098b5cbc160c",
        "e193087c-543b-4c9c-939c-a70be149987e",
        "e1e34750-71c7-4baf-9a14-c5a1598dd982",
        "e7653717-21b0-4254-a49d-201654d333c9",
        "eb725161-bdba-4913-991d-203d260a6b36",
        "ed68c07f-1b69-45e4-9ee1-f675a923c448",
        "ee4dbcd0-e6ca-49c8-aca1-759eae5f624f",
        "f370697b-6baf-4c4c-bf1a-9610f6ffc284",
        "f89d2141-9ec0-4bfc-8d77-7abca78b761f",
        "f947a7dd-a67f-4037-a62a-72c614b76b09",
        "fc0690dc-a7f8-4dcc-8f7d-3f5685075a17",
        "fcffa2da-0cf6-4d6a-ab52-f2c6efc8f8d2",
    ])
    #registry_ID = input("\nEnter the COUNTER Registry ID of the statistics source to check: ")
    #TEST: end temp
    URL, code_of_practice = fetch_URL_from_COUNTER_Registry(registry_ID)
    if isinstance(URL, Exception):
        pytest.exit(URL)
    with open(PATH_TO_CREDENTIALS_FILE()) as file:
        CSV_data = csv.DictReader(file)
        for statistics_source_credentials in CSV_data:
            if statistics_source_credentials['statistics_source_retrieval_code'] == registry_ID:
                # Possible alternate credentials aren't checked
                SUSHI_credentials = {'customer_id': statistics_source_credentials['customer_ID']}
                if statistics_source_credentials.get('requestor_ID'):
                    SUSHI_credentials['requestor_id'] = statistics_source_credentials['requestor_ID']
                if statistics_source_credentials.get('API_key'):
                    SUSHI_credentials['api_key'] = statistics_source_credentials['API_key']
                if statistics_source_credentials.get('platform'):
                    SUSHI_credentials['platform']  = statistics_source_credentials['platform']
    
    #TEST: temp
    #SUSHI_credentials['begin_date'] = pyinputplus.inputDate(
    #    "Please enter the year and month for the first month of stats collection. The month must be two digits and the year must be four digits. ",
    #    formats=[
    #        '%Y%m', # yyyymm
    #        '%m-%Y', # mm-yyyy
    #        '%m/%Y', # mm/yyyy
    #        '%Y-%m', # yyyy-mm
    #        '%Y/%m', # yyyy/mm
    #    ]
    #)
    #SUSHI_credentials['end_date'] = date.min # This ensures that the while loop runs at least once
    #while SUSHI_credentials['end_date'] < SUSHI_credentials['begin_date']:
    #    SUSHI_credentials['end_date'] = pyinputplus.inputDate(
    #        f"Please enter the year and month for the last month of stats collection; this must be the same as or after {SUSHI_credentials['begin_date'].strftime('%Y-%m')}. The month must be two digits and the year must be four digits. ",
    #        formats=[
    #            '%Y%m', # yyyymm
    #            '%m-%Y', # mm-yyyy
    #            '%m/%Y', # mm/yyyy
    #            '%Y-%m', # yyyy-mm
    #            '%Y/%m', # yyyy/mm
    #        ]
    #    )
    #SUSHI_credentials['end_date'] = last_day_of_month(SUSHI_credentials['end_date'])  # This changes the date from the first to the last day of the month to avoid the SUSHI `Invalid Date Arguments` error
    SUSHI_credentials['begin_date'] = date(2025, 10, 1)
    SUSHI_credentials['end_date'] = date(2026, 3, 31)
    #TEST: end temp

    yield (URL, SUSHI_credentials)


@pytest.fixture
def StatisticsSource_instance_name(engine, caplog):
    """Selects a `statisticsSources.statistics_source_name` value from the database.

    `SUSHICallAndResponse._evaluate_individual_SUSHI_exception()` makes a StatisticsSource object for adding a note from a record based on that record's `statistics_source_name` value, so it fails if a placeholder name is used. This randomly selects a name from the database to be used in its place.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime

    Yields:
        str: a value in `statisticsSources.statistics_source_name`
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    df = query_database(
        query=f"SELECT statistics_source_name FROM statisticsSources WHERE statistics_source_name IS NOT NULL;",
        engine=engine,
    )
    if isinstance(df, str):  #ALERT: `except DatabaseInteractionError`
        pytest.skip(database_function_skip_statements(df, False))
    yield extract_value_from_single_value_df(df, False)


@pytest.mark.dependency()
def test_status_call(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, caplog):
    """Tests that an API call via `make_SUSHI_call()` to the `status` endpoint returns a value of the type `StatisticsSources._harvest_R5_SUSHI()` expects.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSource_instance_name,
                URL,
                "status",
                SUSHI_credentials
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    assert isinstance(response, tuple)
    assert isinstance(response[0], dict)
    assert isinstance(response[1], list)


@pytest.mark.dependency(depends=['test_status_call'])
def test_status_call_validity(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, caplog):
    """Tests that the API call via `make_SUSHI_call()` to the `status` endpoint return a valid SUSHI status response.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    with client:
        response = SUSHICallAndResponse(
            StatisticsSource_instance_name,
            URL,
            "status",
            SUSHI_credentials
        ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    # The test uses the `Service_Active` key having a true value to verify the status response, but a reference to a nonexistant key will result in a key error, and the test will fail as a result. Because the capitalization and punctuation of the key is inconsistent, a regex is used to find the key.
    service_active_value = None  # The variable is initialized here so the `assert` statement won't be referencing an unassigned variable
    for key in list(response[0].keys()):
        if re.fullmatch(r"[sS]ervice.?[aA]ctive", key):
            service_active_value = response[0][key]  # The value that goes with `key` in `response[0]`
    assert service_active_value == True or service_active_value == "True" or service_active_value == "true"


@pytest.mark.dependency()
def test_reports_call(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, caplog):
    """Tests that an API call via `make_SUSHI_call()` to the `reports` endpoint returns a value of the type `StatisticsSources._harvest_R5_SUSHI()` expects.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSource_instance_name,
                URL,
                "reports",
                SUSHI_credentials
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    assert isinstance(response, tuple)
    assert isinstance(response[0], dict)
    assert isinstance(response[1], list)


@pytest.mark.dependency(depends=['test_reports_call'])
def test_reports_call_validity(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, caplog):
    """Tests that the API call via `make_SUSHI_call()` to the `reports` endpoint return a valid SUSHI list of reports.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    with client:
        response = SUSHICallAndResponse(
            StatisticsSource_instance_name,
            URL,
            "reports",
            SUSHI_credentials
        ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    list_of_reports = [report for report in list(response[0].values())[0]]
    number_of_reports_available = len(list_of_reports)
    number_of_valid_Report_ID_values = 0
    for report in list_of_reports:
        if "Report_ID" in list(report.keys()):
            if (
                re.fullmatch(r"[PpDdTtIi]?[Rr](_\wJ?\d)?", report["Report_ID"])
                or report["Report_ID"].startswith("Silverchair:CR_")  # Silverchair custom report
                or report["Report_ID"].startswith("sciencedirect:")  # Elsevier custom report
                or report["Report_ID"].startswith("OUP:")  # Oxford custom report
                #or report["Report_ID"].startswith("LL_C")  # ??? custom report
            ):
                number_of_valid_Report_ID_values += 1
    assert number_of_reports_available == number_of_valid_Report_ID_values


@pytest.fixture  # Cannot use module scope due to scope mismatch
def list_of_reports(client, SUSHI_credentials_fixture, caplog):
    """A fixture generating a list of all the customizable reports offered by the given statistics source.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime

    Yields:
        list: the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    try:
        with client:
            response = SUSHICallAndResponse(
                "StatisticsSources.statistics_source_name",
                URL,
                "reports",
                SUSHI_credentials,
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    response_as_list = [report for report in list(response[0].values())[0]]
    list_of_reports = []
    for report in response_as_list:
        if "Report_ID" in list(report.keys()):
            if isinstance(report["Report_ID"], str) and re.fullmatch(r"[PpDdTtIi][Rr]", report["Report_ID"]):
                list_of_reports.append(report["Report_ID"].upper())
    log.info(f"`list_of_reports()` for {URL} yields {list_of_reports}.")
    yield list_of_reports


@pytest.mark.dependency(depends=['test_reports_call_validity'])
@pytest.mark.slow
def test_PR_call_validity(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, list_of_reports, caplog):
    """Tests that the API call via `make_SUSHI_call()` to the `reports/pr` endpoint return a valid SUSHI platform report.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        list_of_reports (list): the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "PR" not in list_of_reports:
        pytest.skip("PR not offered by this statistics source.")
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSource_instance_name,
                URL,
                "reports/pr",
                SUSHI_credentials
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    assert isinstance(response, tuple)
    assert isinstance(response[0], dict)
    assert isinstance(response[1], list)
    assert response[0].get('Report_Header').get('Report_ID') == "PR" or response[0].get('Report_Header').get('Report_ID') == "pr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])
@pytest.mark.slow
def test_DR_call_validity(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, list_of_reports, caplog):
    """Tests that the API call via `make_SUSHI_call()` to the `reports/dr` endpoint return a valid SUSHI database report.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        list_of_reports (list): the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "DR" not in list_of_reports:
        pytest.skip("DR not offered by this statistics source.")
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSource_instance_name,
                URL,
                "reports/dr",
                SUSHI_credentials
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    assert isinstance(response, tuple)
    assert isinstance(response[0], dict)
    assert isinstance(response[1], list)
    assert response[0].get('Report_Header').get('Report_ID') == "DR" or response[0].get('Report_Header').get('Report_ID') == "dr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])
@pytest.mark.slow
def test_TR_call_validity(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, list_of_reports, caplog):
    """Tests that the API call via `make_SUSHI_call()` to the `reports/tr` endpoint return a valid SUSHI title report.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        list_of_reports (list): the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "TR" not in list_of_reports:
        pytest.skip("TR not offered by this statistics source.")
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSource_instance_name,
                URL,
                "reports/tr",
                SUSHI_credentials
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    assert isinstance(response, tuple)
    assert isinstance(response[0], dict)
    assert isinstance(response[1], list)
    assert response[0].get('Report_Header').get('Report_ID') == "TR" or response[0].get('Report_Header').get('Report_ID') == "tr"


@pytest.mark.dependency(depends=['test_reports_call_validity'])
@pytest.mark.slow
def test_IR_call_validity(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, list_of_reports, caplog):
    """Tests that the API call via `make_SUSHI_call()` to the `reports/ir` endpoint return a valid SUSHI item report.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        list_of_reports (list): the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    if "IR" not in list_of_reports:
        pytest.skip("IR not offered by this statistics source.")
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSource_instance_name,
                URL,
                "reports/ir",
                SUSHI_credentials
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidAPIResponseError as error:
        pytest.skip(error.message)
    assert isinstance(response, tuple)
    assert isinstance(response[0], dict)
    assert isinstance(response[1], list)
    assert response[0].get('Report_Header').get('Report_ID') == "IR" or response[0].get('Report_Header').get('Report_ID') == "ir"


@pytest.mark.dependency(depends=['test_PR_call_validity'])
@pytest.mark.xfail(raises=InvalidAPIResponseError)
def test_call_with_invalid_credentials(client, SUSHI_credentials_fixture, StatisticsSource_instance_name, caplog):
    """Tests that a SUSHI call with invalid credentials returns an error.
    
    There's no check confirming that the PR is available; if it wasn't, the dependency would prevent this test from running. Since platforms can handle invalid credentials in multiple different ways--HTTP 400 errors, HTTP 500 errors, and SUSHI error 2000 are the most common--the xfail can confirm that an error statement was returned, but the test cannot confirm that the error statements was for incorrect credentials; since triggering any other error, however, requires having data, this is a minor concern.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        SUSHI_credentials_fixture (tuple): the URL and parameters dictionary needed to make a SUSHI call
        StatisticsSource_instance_name (str): a value in `statisticsSources.statistics_source_name`
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    URL, SUSHI_credentials = SUSHI_credentials_fixture
    SUSHI_credentials['customer_id'] = "deliberatelyIncorrect"
    with client:
        response = SUSHICallAndResponse(
            StatisticsSource_instance_name,
            URL,
            "reports/pr",
            SUSHI_credentials
        ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    assert isinstance(response[0], dict)