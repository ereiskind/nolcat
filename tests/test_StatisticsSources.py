"""Tests the methods in StatisticsSources."""
########## Passing 2026-04-20 ##########

import pytest
import json
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from random import choice
import re
import pandas as pd
from pandas.testing import assert_frame_equal
from dateutil.relativedelta import relativedelta  # dateutil is a pandas dependency, so it doesn't need to be in requirements.txt

# `conftest.py` fixtures are imported automatically
from conftest import match_direct_SUSHI_harvest_result
from nolcat.models import *

log = logging.getLogger(__name__)


#Section: Introductory Fixtures
@pytest.fixture(scope='module')
def current_month_like_most_recent_month_with_usage():
    """Creates `begin_date` and `end_date` SUSHI parameter values representing the current month.

    Testing `StatisticsSources._check_if_data_in_database()` requires a month for which the `StatisticsSources_fixture` statistics source won't have SUSHI data loaded. The current month is guaranteed to meet this criteria, as that data isn't available.

    Yields:
        tuple: two datetime.date values, representing the first and last day of a month respectively
    """
    current_date = date.today()
    begin_date = current_date.replace(day=1)
    end_date = last_day_of_month(begin_date)
    log.info(f"`current_month_like_most_recent_month_with_usage()` yields `begin_date` {begin_date} (type {type(begin_date)}) and `end_date` {end_date} (type {type(end_date)}).")
    yield (begin_date, end_date)


@pytest.fixture(scope='module')
def StatisticsSources_fixture(valid_COUNTER_retrieval_code):
    """A fixture simulating a `StatisticsSources` object containing the necessary data to make a real SUSHI call.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. This fixture creates a `StatisticsSources` object with mocked values in all fields except `statisticsSources_relation['Statistics_Source_Retrieval_Code']`, which uses a random value taken from the R5 SUSHI credentials file.

    Args:
        valid_COUNTER_retrieval_code (str): a COUNTER Registry ID

    Yields:
        StatisticsSources: a StatisticsSources object connected to valid SUSHI data
    """
    # Cannot use `caplog` for `query_database()` due to scope mismatch
    yield_object = StatisticsSources(
        statistics_source_ID = 0,
        statistics_source_name = choice([  # If the name isn't in the database, `SUSHICallAndResponse._evaluate_individual_SUSHI_exception()`, which makes a StatisticsSource object from a record based on that record's `statistics_source_name` value, fails; using the names of the statistics sources associated with COUNTER in the test data is a further hedge against problems
            "ProQuest",
            "EBSCOhost",
            "Duke UP",
        ]),
        statistics_source_retrieval_code = valid_COUNTER_retrieval_code,
        vendor_ID = 0,
    )
    log.warning(f"The statistics source retrieval code being used is {yield_object.statistics_source_retrieval_code}.")  # The level is `warning` so it always displays, ensuring the SUSHI credentials source can be determined in the event that the tests don't pass because of problems on the vendor side
    yield yield_object


#Section: Tests and Fixture for SUSHI Credentials
@pytest.mark.slow
def test_fetch_SUSHI_information_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning a value suitable for use in a API call.
    
    Regex taken from https://stackoverflow.com/a/3809435.

    Args:
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
    """
    credentials = StatisticsSources_fixture.fetch_SUSHI_information()
    assert isinstance(credentials, dict)
    assert re.fullmatch(r"https?://(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*/", credentials['URL'])


def test_fetch_SUSHI_information_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning the credentials for user display.

    Args:
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
    """
    # credentials = StatisticsSources_fixture.fetch_SUSHI_information(code_of_practice=False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


@pytest.fixture(scope='module')
def SUSHI_credentials_fixture(StatisticsSources_fixture):
    """A fixture returning the SUSHI credentials dictionary to avoid repeated callings of the `StatisticsSources.fetch_SUSHI_information()` method in later test functions.

    Args:
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
    
    Yields:
        dict: SUSHI credentials
    """
    yield StatisticsSources_fixture.fetch_SUSHI_information()


#Section: Fixture Listing Available Reports
@pytest.fixture
def reports_offered_by_StatisticsSource_fixture(client, StatisticsSources_fixture, SUSHI_credentials_fixture, caplog):
    """A fixture generating a list of all the customizable reports offered by the given StatisticsSources object.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        StatisticsSources_fixture (StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        SUSHI_credentials_fixture (dict): a SUSHI credentials dictionary
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    
    Yields:
        list: the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    try:
        with client:
            response = SUSHICallAndResponse(
                StatisticsSources_fixture.statistics_source_name,
                SUSHI_credentials_fixture['URL'],
                "reports",
                {k: v for (k, v) in SUSHI_credentials_fixture.items() if k != "URL"},
            ).make_SUSHI_call(bucket_path=TEST_COUNTER_FILE_PATH)
    except InvalidSUSHIResponseError as error:
        pytest.skip(f"Skipping test because of problem with SUSHI: {error.message}")
    log.info(f"The call to reports for {StatisticsSources_fixture.statistics_source_name} was successful.")
    response_as_list = [report for report in list(response[0].values())[0]]
    list_of_reports = []
    for report in response_as_list:
        if "Report_ID" in list(report.keys()):
            if isinstance(report["Report_ID"], str) and re.fullmatch(r"[PpDdTtIi][Rr]", report["Report_ID"]):
                list_of_reports.append(report["Report_ID"].upper())
    log.info(f"{StatisticsSources_fixture.statistics_source_name} offers the following reports: {list_of_reports}.")
    yield list_of_reports


#Section: Test SUSHI Harvesting Methods in Reverse Call Order
#Subsection: Test `StatisticsSources._check_if_data_in_database()`
def test_check_if_data_in_database_no(client, StatisticsSources_fixture, reports_offered_by_StatisticsSource_fixture, current_month_like_most_recent_month_with_usage, caplog):
    """Tests if a given date and statistics source combination has any usage in the database when there aren't any matches.
    
    This test uses the current month as the date; since the current month's data isn't available, it won't be in the database.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        reports_offered_by_StatisticsSource_fixture (list): the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
        current_month_like_most_recent_month_with_usage (tuple): `begin_date` and `end_date` SUSHI parameter values representing the current month
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    with client:
        data_check = StatisticsSources_fixture._check_if_data_in_database(
            choice(reports_offered_by_StatisticsSource_fixture),
            current_month_like_most_recent_month_with_usage[0],
            current_month_like_most_recent_month_with_usage[1],
        )
    assert data_check is None


@pytest.mark.skip  #TEST: temp
def test_check_if_data_in_database_yes(client, StatisticsSources_fixture, reports_offered_by_StatisticsSource_fixture, current_month_like_most_recent_month_with_usage, caplog):
    """Tests if a given date and statistics source combination has any usage in the database when there are matches.
    
    To be certain the date range includes dates for which the given `StatisticsSources.statistics_source_ID` value both does and doesn't have usage, the date range must span from the dates covered by the test data to the current month, for which no data is available. Additionally, the `StatisticsSources.statistics_source_ID` value in `StatisticsSources_fixture` must correspond to a source that has all four possible reports in the test data.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        reports_offered_by_StatisticsSource_fixture (list): the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
        current_month_like_most_recent_month_with_usage (tuple):  `begin_date` and `end_date` SUSHI parameter values representing the current month
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    report = choice(reports_offered_by_StatisticsSource_fixture)
    last_month_with_usage_in_test_data = date(2020, 6, 1)
    with client:
        data_check = StatisticsSources_fixture._check_if_data_in_database(
            report,
            last_month_with_usage_in_test_data,
            current_month_like_most_recent_month_with_usage[1],
        )
    assert isinstance(data_check, list)
    assert date(2020, 6, 1) not in data_check
    assert current_month_like_most_recent_month_with_usage[0] in data_check


#Subsection: Test `StatisticsSources._harvest_single_report()`
@pytest.fixture
def data_for_testing_harvest_single_report(most_recent_month_with_usage, reports_offered_by_StatisticsSource_fixture):
    """A fixture with data to match for the next two tests.

    The `test_harvest_single_report_with_partial_date_range()` needs to include a date range where some but not all of the data for the specified statistics source is loaded. The easiest way to ensure such a range is used is to have the range be the month used in `test_harvest_single_report()` and the preceding two months and for the report pulled to be the same. The month before the month in `test_harvest_R5_SUSHI_with_report_to_harvest()` is used as the starting month to avoid being stopped by duplication check.

    Args:
        most_recent_month_with_usage (tuple): `begin_date` and `end_date` SUSHI parameter values representing the most recent month with available data
        reports_offered_by_StatisticsSource_fixture (list): the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source

    Yields:
        tuple: the uppercase abbreviation of one of the COUNTER R5 reports offered by the given statistics source (str); the month before the month in `test_harvest_R5_SUSHI_with_report_to_harvest()` (datetime.date)
    """
    yield (
        choice(reports_offered_by_StatisticsSource_fixture),
        most_recent_month_with_usage[0] + relativedelta(months=-2),
    )


@pytest.mark.dependency
@pytest.mark.slow
@pytest.mark.skip  #TEST: temp
def test_harvest_single_report(client, tmp_path, StatisticsSources_fixture, data_for_testing_harvest_single_report, SUSHI_credentials_fixture, caplog):
    """Tests the method making the API call and turing the result into a dataframe.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        tmp_path (pathlib.Path): a temporary directory created just for running tests
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        data_for_testing_harvest_single_report (tuple): a COUNTER R5 report type offered by the given statistics source (str); the month before the month in `test_harvest_R5_SUSHI_with_report_to_harvest()` (datetime.date)
        SUSHI_credentials_fixture (dict): a SUSHI credentials dictionary
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    report_to_check, begin_date = data_for_testing_harvest_single_report
    end_date = last_day_of_month(begin_date)
    try:
        with client:
            S3_file_name, messages_to_flash = StatisticsSources_fixture._harvest_single_report(
                report_to_check,
                SUSHI_credentials_fixture['URL'],
                {k: v for (k, v) in SUSHI_credentials_fixture.items() if k != "URL"},
                begin_date,
                end_date,
                bucket_path=TEST_COUNTER_FILE_PATH,
            )
    except InvalidSUSHIResponseError as error:
        pytest.skip(f"Skipping test because of problem with SUSHI: {error.message}")
    assert isinstance(S3_file_name, CloudPath)
    assert S3_file_name.name.startswith(f"{StatisticsSources_fixture.statistics_source_ID}_{report_to_check}")
    assert isinstance(messages_to_flash, list)
    download_location = tmp_path / S3_file_name.name
    s3_client.download_file(
        Bucket=BUCKET_NAME,
        Key=S3_file_name.key,
        Filename=download_location,
    )
    assert download_location.is_file()
    #remove_file_from_S3(S3_file_name)


@pytest.mark.dependency(depends=['test_harvest_single_report'])
@pytest.mark.slow
@pytest.mark.skip  #TEST: temp
def test_harvest_single_report_with_partial_date_range(client, tmp_path, StatisticsSources_fixture, data_for_testing_harvest_single_report, SUSHI_credentials_fixture, caplog):
    """Tests the method making the API call and turing the result into a dataframe when the given date range includes dates for which the date and statistics source combination already has usage in the database.
    
    To be certain the date range includes dates for which the given `StatisticsSources.statistics_source_ID` value both does and doesn't have usage, the date range ends with the month pulled in the test above; for efficiency, the date range only looks at three months total.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        tmp_path (pathlib.Path): a temporary directory created just for running tests
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        data_for_testing_harvest_single_report (tuple): a COUNTER R5 report type offered by the given statistics source (str); the month before the month in `test_harvest_R5_SUSHI_with_report_to_harvest()` (datetime.date)
        SUSHI_credentials_fixture (dict): a SUSHI credentials dictionary
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    report_to_check, end_month = data_for_testing_harvest_single_report
    begin_date = end_month + relativedelta(months=-2)
    end_date = last_day_of_month(end_month)
    try:
        with client:
            S3_file_name, messages_to_flash = StatisticsSources_fixture._harvest_single_report(
                report_to_check,
                SUSHI_credentials_fixture['URL'],
                {k: v for (k, v) in SUSHI_credentials_fixture.items() if k != "URL"},
                begin_date,
                end_date,
                bucket_path=TEST_COUNTER_FILE_PATH,
            )
    except InvalidSUSHIResponseError as error:
        pytest.skip(f"Skipping test because of problem with SUSHI: {error.message}")
    assert isinstance(S3_file_name, CloudPath)
    assert S3_file_name.name.startswith(f"{StatisticsSources_fixture.statistics_source_ID}_{report_to_check}")
    assert isinstance(messages_to_flash, list)
    download_location = tmp_path / S3_file_name.name
    s3_client.download_file(
        Bucket=BUCKET_NAME,
        Key=S3_file_name.key,
        Filename=download_location,
    )
    assert download_location.is_file()


#Subsection: Test `StatisticsSources._harvest_R5_SUSHI()`
@pytest.mark.dependency(depends=['test_harvest_single_report'])
@pytest.mark.slow
@pytest.mark.skip  #TEST: temp
def test_harvest_R5_SUSHI(client, StatisticsSources_fixture, most_recent_month_with_usage, reports_offered_by_StatisticsSource_fixture, caplog):
    """Tests collecting all available R5 reports for a `StatisticsSources.statistics_source_retrieval_code` value and combining them into a single dataframe.

    Args:
        client (flask.testing.FlaskClient): a Flask test client
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        most_recent_month_with_usage (tuple): `begin_date` and `end_date` SUSHI parameter values representing the most recent month with available data
        reports_offered_by_StatisticsSource_fixture (list): the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    try:
        with client:
            flash_message_dict = StatisticsSources_fixture._harvest_R5_SUSHI(
            most_recent_month_with_usage[0],
            most_recent_month_with_usage[1],
            bucket_path=TEST_COUNTER_FILE_PATH,
        )
    except InvalidSUSHIResponseError as error:
        pytest.skip(f"Skipping test because of problem with SUSHI: {error.message}")
    assert isinstance(flash_message_dict, dict)
    assert 'status' in list(flash_message_dict.keys())
    assert 'reports' in list(flash_message_dict.keys())
    for report in reports_offered_by_StatisticsSource_fixture:
        assert report in list(flash_message_dict.keys())


@pytest.mark.dependency(depends=['test_harvest_single_report'])
@pytest.mark.slow
@pytest.mark.skip  #TEST: temp
def test_harvest_R5_SUSHI_with_report_to_harvest(StatisticsSources_fixture, most_recent_month_with_usage, reports_offered_by_StatisticsSource_fixture, caplog):
    """Tests collecting a single R5 report for a `StatisticsSources.statistics_source_retrieval_code` value.

    Args:
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        most_recent_month_with_usage (tuple): `begin_date` and `end_date` SUSHI parameter values representing the most recent month with available data
        reports_offered_by_StatisticsSource_fixture (list): the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    begin_date = most_recent_month_with_usage[0] + relativedelta(months=-2)  # Using two months before `most_recent_month_with_usage` to avoid being stopped by duplication check
    end_date = last_day_of_month(begin_date)
    report_being_called = choice(reports_offered_by_StatisticsSource_fixture)
    try:
        flash_message_dict = StatisticsSources_fixture._harvest_R5_SUSHI(
            begin_date,
            end_date,
            report_being_called,
            bucket_path=TEST_COUNTER_FILE_PATH,
        )
    except InvalidSUSHIResponseError as error:
        pytest.skip(f"Skipping test because of problem with SUSHI: {error.message}")
    assert isinstance(flash_message_dict, dict)
    assert 'status' in list(flash_message_dict.keys())
    assert report_being_called in list(flash_message_dict.keys())


@pytest.mark.dependency(depends=['test_harvest_single_report'])
@pytest.mark.skip  #TEST: temp
def test_harvest_R5_SUSHI_with_invalid_dates(StatisticsSources_fixture, most_recent_month_with_usage, reports_offered_by_StatisticsSource_fixture, caplog):
    """Tests the code for rejecting a SUSHI end date before the begin date.

    Args:
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a StatisticsSources object connected to valid SUSHI data
        most_recent_month_with_usage (tuple): `begin_date` and `end_date` SUSHI parameter values representing the most recent month with available data
        reports_offered_by_StatisticsSource_fixture (list): the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')
    begin_date = most_recent_month_with_usage[0] + relativedelta(months=-3)  # Using three months before `most_recent_month_with_usage` so `end_date` is still in the past
    end_date = begin_date - timedelta(days=32)  # Sets `end_date` far enough before `begin_date` that it will be at least the last day of the month before `begin_date`
    end_date = last_day_of_month(end_date)
    flash_message_dict = StatisticsSources_fixture._harvest_R5_SUSHI(
        begin_date,
        end_date,
        choice(reports_offered_by_StatisticsSource_fixture),
        bucket_path=TEST_COUNTER_FILE_PATH,
    )
    assert isinstance(flash_message_dict, dict)
    assert len(flash_message_dict) == 1
    assert flash_message_dict['dates']


#ToDo: Is a test for `_harvest_R5_SUSHI()` with a specified code of practice needed?


# `nolcat.models.StatisticsSources.collect_usage_statistics()` returns a call to `nolcat.models.StatisticsSources._harvest_R5_SUSHI()`, so no `tests.test_StatisticsSources.test_collect_usage_statistics()` is required


#Section: Test `StatisticsSources.add_note()`
def test_add_note():
    """Test adding notes about statistics sources."""
    #ToDo: Develop this test alongside the method it's testing
    pass


#Section: Run `test_check_if_data_already_in_COUNTERData()`
# The function being tested is in `nolcat.app`, but it needs to have data in the `COUNTERData` relation, while the other tests in that module require the database to be empty; the function is being tested here for more accurate results.
@pytest.fixture
def partially_duplicate_COUNTER_data():
    """COUNTER data, some of which is in the `COUNTERData_relation` dataframe.

    Yields:
        dataframe: data formatted for loading into the `COUNTERData` relation
    """
    df = pd.DataFrame(
        [
            [3, "TR", "Empires of Vision<subtitle>A Reader</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822378976", "Silverchair:417", "978-0-8223-7897-6", None, None, None, "Book", "Chapter", 2013, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-01-01", 4, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-01-01", 4, None],
            [3, "TR", "Pikachu's Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822385813", "Silverchair:891", "978-0-8223-8581-3", None, None, None, "Book", "Book", 2004, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-03-01", 2, None],
            [3, "TR", "Pikachu's Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822385813", "Silverchair:891", "978-0-8223-8581-3", None, None, None, "Book", "Book", 2004, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Item_Investigations", "2020-03-01", 2, None],
            [3, "TR", "Pikachu's Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822385813", "Silverchair:891", "978-0-8223-8581-3", None, None, None, "Book", None, 2004, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Unique_Title_Investigations", "2020-03-01", 2, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 16, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 4, None],
        ],
        columns=["statistics_source_ID", "report_type", "resource_name", "publisher", "publisher_ID", "platform", "authors", "publication_date", "article_version", "DOI", "proprietary_ID", "ISBN", "print_ISSN", "online_ISSN", "URI", "data_type", "section_type", "YOP", "access_type", "access_method",  "parent_title", "parent_authors", "parent_publication_date", "parent_article_version", "parent_data_type", "parent_DOI", "parent_proprietary_ID", "parent_ISBN", "parent_print_ISSN", "parent_online_ISSN", "parent_URI", "metric_type", "usage_date", "usage_count", "report_creation_date"],
    )
    df.index.name = "COUNTER_data_ID"
    df = df.astype(COUNTERData.state_data_types())
    df["publication_date"] = pd.to_datetime(df["publication_date"])
    df["parent_publication_date"] = pd.to_datetime(df["parent_publication_date"])
    df["usage_date"] = pd.to_datetime(df["usage_date"])
    df["report_creation_date"] = pd.to_datetime(df["report_creation_date"])
    yield df


@pytest.fixture
def non_duplicate_COUNTER_data():
    """The COUNTER data from `partially_duplicate_COUNTER_data` not in the `COUNTERData_relation` dataframe.

    Yields:
        dataframe: data formatted for loading into the `COUNTERData` relation
    """
    df = pd.DataFrame(
        [
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 16, None],
            [3, "TR", "Within the Circle<subtitle>An Anthology of African American Literary Criticism from the Harlem Renaissance to the Present</subtitle>", "Duke University Press", None, "Duke University Press", None, None, None, "10.1215/9780822399889", "Silverchair:1923", "978-0-8223-1536-0", None, None, None, "Book", "Chapter", 1994, "Controlled", "Regular", None, None, None, None, None, None, None, None, None, None, None, "Total_Item_Investigations", "2020-02-01", 4, None],
        ],
        columns=["statistics_source_ID", "report_type", "resource_name", "publisher", "publisher_ID", "platform", "authors", "publication_date", "article_version", "DOI", "proprietary_ID", "ISBN", "print_ISSN", "online_ISSN", "URI", "data_type", "section_type", "YOP", "access_type", "access_method",  "parent_title", "parent_authors", "parent_publication_date", "parent_article_version", "parent_data_type", "parent_DOI", "parent_proprietary_ID", "parent_ISBN", "parent_print_ISSN", "parent_online_ISSN", "parent_URI", "metric_type", "usage_date", "usage_count", "report_creation_date"],
    )
    df.index.name = "COUNTER_data_ID"
    df = df.astype(COUNTERData.state_data_types())
    df["publication_date"] = pd.to_datetime(df["publication_date"])
    df["parent_publication_date"] = pd.to_datetime(df["parent_publication_date"])
    df["usage_date"] = pd.to_datetime(df["usage_date"])
    df["report_creation_date"] = pd.to_datetime(df["report_creation_date"])
    yield df


def test_check_if_data_already_in_COUNTERData(engine, client, partially_duplicate_COUNTER_data, non_duplicate_COUNTER_data, caplog):
    """Tests the check for statistics source/report type/usage date combinations already in the database.
    
    While the function being tested here is in `nolcat.app`, the test is in this module because it requires the `COUNTERData` relation to contain data, while the `nolcat.app` test module starts with an empty database and never loads data into that relation.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        client (flask.testing.FlaskClient): a Flask test client
        partially_duplicate_COUNTER_data (dataframe): data for loading into the `COUNTERData` relation, some of which is already in the test data for that relation
        non_duplicate_COUNTER_data (dataframe): data in `partially_duplicate_COUNTER_data()` not in the `COUNTERData` relation
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    number_of_records = query_database(
        query=f"SELECT COUNT(*) FROM COUNTERData;",
        engine=engine,
    )
    if isinstance(number_of_records, str):  #ALERT: `except DatabaseInteractionError`
        pytest.skip(database_function_skip_statements(number_of_records))
    if extract_value_from_single_value_df(number_of_records) == 0:
        pytest.skip(f"The prerequisite test data isn't in the database, so this test will fail if run.")
    with client:
        df, message = check_if_data_already_in_COUNTERData(partially_duplicate_COUNTER_data)
    assert_frame_equal(df.reset_index(drop=True), non_duplicate_COUNTER_data.reset_index(drop=True))  # The `drop` argument handles the fact that `check_if_data_already_in_COUNTERData()` returns the matched records with the index values from the dataframe used as the function argument
    # The order of the statistics source ID, report type, and date combinations that were matched is inconsistent, so the return statement containing them is tested in multiple parts
    assert message.startswith(f"Usage statistics for the report type, usage date, and statistics source combination(s) below, which were included in the upload, are already in the database; as a result, it wasn't uploaded to the database. If the data needs to be re-uploaded, please remove the existing data from the database first.\n")
    assert f"TR  | 2020-03-01 | Duke UP (ID 3)" in message
    assert f"TR  | 2020-01-01 | Duke UP (ID 3)" in message