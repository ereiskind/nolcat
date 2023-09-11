"""Tests the methods in StatisticsSources."""
########## Failing 2023-09-08 ##########

import pytest
import logging
import json
from datetime import date
from datetime import datetime
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
    end_date = date(
        begin_date.year,
        begin_date.month,
        calendar.monthrange(begin_date.year, begin_date.month)[1],
    )
    yield (begin_date, end_date)


@pytest.fixture(scope='module')
def StatisticsSources_fixture(engine, most_recent_month_with_usage):
    """A fixture simulating a `StatisticsSources` object containing the necessary data to make a real SUSHI call.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. This fixture creates a `StatisticsSources` object with mocked values in all fields except `statisticsSources_relation['Statistics_Source_Retrieval_Code']`, which uses a random value taken from the R5 SUSHI credentials file. Because the `_harvest_R5_SUSHI()` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics are filtered out to prevent their use.

    Args:
        PATH_TO_CREDENTIALS_FILE (str): the file path for "R5_SUSHI_credentials.json"
        most_recent_month_with_usage (tuple): the first and last days of the most recent month for which COUNTER data is available

    Yields:
        StatisticsSources: a StatisticsSources object connected to valid SUSHI data
    """
    retrieval_codes_as_interface_IDs = []  # The list of `StatisticsSources.statistics_source_retrieval_code` values from the JSON, which are labeled as `interface_id` in the JSON
    with open(PATH_TO_CREDENTIALS_FILE()) as JSON_file:
        SUSHI_data_file = json.load(JSON_file)
        for vendor in SUSHI_data_file:
            for stats_source in vendor['interface']:
                if "interface_id" in list(stats_source.keys()):
                        retrieval_codes_as_interface_IDs.append(stats_source['interface_id'])
    
    retrieval_codes = []
    for interface in retrieval_codes_as_interface_IDs:
        query_result = pd.read_sql(
            sql=f"SELECT COUNT(*) FROM statisticsSources JOIN COUNTERData ON statisticsSources.statistics_source_ID=COUNTERData.statistics_source_ID WHERE statisticsSources.statistics_source_retrieval_code={interface} AND COUNTERData.usage_date={most_recent_month_with_usage[0].strftime('%Y-%m-%d')};",
            con=engine,
        )
        if not query_result.empty or not query_result.isnull().all().all():  # `empty` returns Boolean based on if the dataframe contains data elements; `isnull().all().all()` returns a Boolean based on a dataframe of Booleans based on if the value of the data element is null or not
            retrieval_codes.append(interface)
    
    fixture_retrieval_code = choice(retrieval_codes)
    yield StatisticsSources(
        statistics_source_ID = 0,
        statistics_source_name = f"SUSHI code {fixture_retrieval_code}",
        statistics_source_retrieval_code = fixture_retrieval_code,
        vendor_ID = 0,
    )


#Section: Tests and Fixture for SUSHI Credentials
def test_fetch_SUSHI_information_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning a value suitable for use in a API call."""
    credentials = StatisticsSources_fixture.fetch_SUSHI_information()
    assert isinstance(credentials, dict)
    assert re.match(r"https?:\/\/.*\/", string=credentials['URL'])


def test_fetch_SUSHI_information_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning the credentials for user display."""
    #ToDo: credentials = StatisticsSources_fixture.fetch_SUSHI_information(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


@pytest.fixture(scope='module')
def SUSHI_credentials_fixture(StatisticsSources_fixture):
    """A fixture returning the SUSHI credentials dictionary to avoid repeated callings of the `StatisticsSources.fetch_SUSHI_information()` method in later test functions.

    Args:
        StatisticsSources_fixture (StatisticsSources): a StatisticsSources object connected to valid SUSHI data
    
    Yields:
        dict: SUSHI credentials
    """
    yield StatisticsSources_fixture.fetch_SUSHI_information()


#Section: Fixture Listing Available Reports
@pytest.fixture(scope='module')
def reports_offered_by_StatisticsSource_fixture(StatisticsSources_fixture):
    """A fixture feeding a StatisticsSources object into the `COUNTER_reports_offered_by_statistics_source` fixture.

    Args:
        StatisticsSources_fixture (StatisticsSources): a StatisticsSources object connected to valid SUSHI data
    
    Yields:
        list: the uppercase abbreviation of all the customizable COUNTER R5 reports offered by the given statistics source
    """
    SUSHI_data = StatisticsSources_fixture.fetch_SUSHI_information()
    yield COUNTER_reports_offered_by_statistics_source(
        StatisticsSources_fixture.statistics_source_name,
        SUSHI_data['URL'],
        {k:v for (k, v) in SUSHI_data.items() if k != "URL"},
    )


#Section: Test SUSHI Harvesting Methods in Reverse Call Order
#Subsection: Test `StatisticsSources._check_if_data_in_database()`
def test_check_if_data_in_database_no(client, StatisticsSources_fixture, reports_offered_by_StatisticsSource_fixture, current_month_like_most_recent_month_with_usage):
    """Tests if a given date and statistics source combination has any usage in the database when there aren't any matches.
    
    This test uses the current month as the date; since the current month's data isn't available, it won't be in the database. 
    """
    with client:
        data_check = StatisticsSources_fixture._check_if_data_in_database(
            choice(reports_offered_by_StatisticsSource_fixture),
            current_month_like_most_recent_month_with_usage[0],
            current_month_like_most_recent_month_with_usage[1],
        )
    #TEST: AttributeError: 'NoneType' object has no attribute 'get'
    assert data_check is None


def test_check_if_data_in_database_yes(client, StatisticsSources_fixture, reports_offered_by_StatisticsSource_fixture, current_month_like_most_recent_month_with_usage):
    """Tests if a given date and statistics source combination has any usage in the database when there are matches.
    
    To be certain the date range includes dates for which the given `StatisticsSources.statistics_source_ID` value both does and doesn't have usage, the date range must span from the dates covered by the test data to the current month, for which no data is available. Additionally, the `StatisticsSources.statistics_source_ID` value in `StatisticsSources_fixture` must correspond to a source that has all four possible reports in the test data.
    """
    with client:
        data_check = StatisticsSources_fixture._check_if_data_in_database(
            choice(reports_offered_by_StatisticsSource_fixture),
            date(2020, 6, 1),  # The last month with usage in the test data
            current_month_like_most_recent_month_with_usage[1],
        )
    #TEST: AttributeError: 'NoneType' object has no attribute 'get'
    assert isinstance(data_check, list)
    assert date(2020, 6, 1) not in data_check
    assert current_month_like_most_recent_month_with_usage[0] in data_check


#Subsection: Test `StatisticsSources._harvest_single_report()`
@pytest.mark.dependency()
def test_harvest_single_report(client, StatisticsSources_fixture, most_recent_month_with_usage, reports_offered_by_StatisticsSource_fixture, SUSHI_credentials_fixture, caplog):
    """Tests the method making the API call and turing the result into a dataframe."""
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()`
    begin_date = most_recent_month_with_usage[0] + relativedelta(months=-2)  # Using month before month in `test_harvest_R5_SUSHI_with_report_to_harvest()` to avoid being stopped by duplication check
    end_date = date(
        begin_date.year,
        begin_date.month,
        calendar.monthrange(begin_date.year, begin_date.month)[1],
    )
    with client:
        SUSHI_response = StatisticsSources_fixture._harvest_single_report(
            choice(reports_offered_by_StatisticsSource_fixture),
            SUSHI_credentials_fixture['URL'],
            {k:v for (k, v) in SUSHI_credentials_fixture.items() if k != "URL"},
            begin_date,
            end_date,
        )
    #TEST: AttributeError: 'NoneType' object has no attribute 'get'
    assert isinstance(SUSHI_response, pd.core.frame.DataFrame)
    assert SUSHI_response['statistics_source_ID'].eq(StatisticsSources_fixture.statistics_source_ID).all()
    assert SUSHI_response['report_creation_date'].map(lambda dt: dt.strftime('%Y-%m-%d')).eq(datetime.utcnow().strftime('%Y-%m-%d')).all()  # Inconsistencies in timezones and UTC application among vendors mean time cannot be used to confirm the recency of an API call response


@pytest.mark.dependency()
def test_harvest_single_report_with_partial_date_range(client, StatisticsSources_fixture, reports_offered_by_StatisticsSource_fixture, SUSHI_credentials_fixture, caplog):
    """Tests the method making the API call and turing the result into a dataframe when the given date range includes dates for which the date and statistics source combination already has usage in the database.
    
    To be certain the date range includes dates for which the given `StatisticsSources.statistics_source_ID` value both does and doesn't have usage, the date range starts with the last month covered by the test data; for efficiency, the date range only goes another two months past that point.
    """
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()`
    with client:
        SUSHI_response = StatisticsSources_fixture._harvest_single_report(
            choice(reports_offered_by_StatisticsSource_fixture),
            SUSHI_credentials_fixture['URL'],
            {k:v for (k, v) in SUSHI_credentials_fixture.items() if k != "URL"},
            date(2020, 6, 1),  # The last month with usage in the test data
            date(2020, 8, 1),
        )
    #ToDo: if SUSHI_response contains "Call to SUSHI code \d* for reports/\w{2} returned no usage data, which may or may not be appropriate.", skip test
    #Test: Many statistics source providers don't have usage going back this far
    #TEST: AttributeError: 'NoneType' object has no attribute 'get'
    assert isinstance(SUSHI_response, pd.core.frame.DataFrame)
    assert pd.concat([
        SUSHI_response['usage_date'].eq(pd.Timestamp(2020, 7, 1)),
        SUSHI_response['usage_date'].eq(pd.Timestamp(2020, 8, 1)),
    ], axis='columns').any(axis='columns').all()


#Subsection: Test `StatisticsSources._harvest_R5_SUSHI()`
@pytest.mark.dependency(depends=['test_harvest_single_report'])
def test_harvest_R5_SUSHI(client, StatisticsSources_fixture, most_recent_month_with_usage, caplog):
    """Tests collecting all available R5 reports for a `StatisticsSources.statistics_source_retrieval_code` value and combining them into a single dataframe."""
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()` called in `SUSHICallAndResponse.make_SUSHI_call()` and `self._harvest_single_report()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()`
    with client:
        SUSHI_response = StatisticsSources_fixture._harvest_R5_SUSHI(most_recent_month_with_usage[0], most_recent_month_with_usage[1])
    assert isinstance(SUSHI_response, pd.core.frame.DataFrame)
    assert SUSHI_response['statistics_source_ID'].eq(StatisticsSources_fixture.statistics_source_ID).all()
    assert SUSHI_response['report_creation_date'].map(lambda dt: dt.strftime('%Y-%m-%d')).eq(datetime.utcnow().strftime('%Y-%m-%d')).all()  # Inconsistencies in timezones and UTC application among vendors mean time cannot be used to confirm the recency of an API call response


@pytest.mark.dependency(depends=['test_harvest_single_report'])
def test_harvest_R5_SUSHI_with_report_to_harvest(StatisticsSources_fixture, most_recent_month_with_usage, reports_offered_by_StatisticsSource_fixture, caplog):
    """Tests collecting a single R5 report for a `StatisticsSources.statistics_source_retrieval_code` value."""
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()` called in `SUSHICallAndResponse.make_SUSHI_call()` and `self._harvest_single_report()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()`
    begin_date = most_recent_month_with_usage[0] + relativedelta(months=-2)  # Using two months before `most_recent_month_with_usage` to avoid being stopped by duplication check
    end_date = date(
        begin_date.year,
        begin_date.month,
        calendar.monthrange(begin_date.year, begin_date.month)[1],
    )
    SUSHI_response = StatisticsSources_fixture._harvest_R5_SUSHI(begin_date, end_date, choice(reports_offered_by_StatisticsSource_fixture))
    assert isinstance(SUSHI_response, pd.core.frame.DataFrame)
    assert SUSHI_response['statistics_source_ID'].eq(StatisticsSources_fixture.statistics_source_ID).all()
    assert SUSHI_response['report_creation_date'].map(lambda dt: dt.strftime('%Y-%m-%d')).eq(datetime.utcnow().strftime('%Y-%m-%d')).all()  # Inconsistencies in timezones and UTC application among vendors mean time cannot be used to confirm the recency of an API call response


#Subsection: Test `StatisticsSources.collect_usage_statistics()`
@pytest.fixture(scope='module')
def month_before_month_like_most_recent_month_with_usage(most_recent_month_with_usage):
    """Creates `begin_date` and `end_date` SUSHI parameter values representing the month before the month in `most_recent_month_with_usage`.

    Testing `StatisticsSources.check_usage_statistics()` requires a month for which the `StatisticsSources_fixture` statistics source won't have SUSHI data loaded. The month before the month in `most_recent_month_with_usage` is likely to meet this criteria even after `test_StatisticsSources.test_harvest_R5_SUSHI()` loads data for the month in `most_recent_month_with_usage`. The dates are in a fixture so they can be used by both the test function and the `test_StatisticsSources.SUSHI_result()` fixture.

    Args:
        most_recent_month_with_usage (tuple): the first and last days of the most recent month for which COUNTER data is available

    Yields:
        tuple: two datetime.date values, representing the first and last day of a month respectively
    """
    begin_date = most_recent_month_with_usage[0] + relativedelta(months=-1)
    end_date = date(
        begin_date.year,
        begin_date.month,
        calendar.monthrange(begin_date.year, begin_date.month)[1],
    )
    yield (begin_date, end_date)


@pytest.fixture  # Since this fixture is only called once, there's no functional difference between setting it at a function scope and setting it at a module scope
def harvest_R5_SUSHI_result(StatisticsSources_fixture, month_before_month_like_most_recent_month_with_usage, caplog):
    """A fixture with the result of all the SUSHI calls that will be made in `test_collect_usage_statistics()`.

    The `StatisticsSources.collect_usage_statistics()` method loads the data collected by the SUSHI call(s) made in `StatisticsSources._harvest_R5_SUSHI()` into the database. To confirm that the data was loaded successfully, a copy of the data that was loaded is needed for comparison. This fixture yields the same dataframe that `StatisticsSources.collect_usage_statistics()` loads into the database by calling `StatisticsSources._harvest_R5_SUSHI()`, just like the method being tested. Because the method being tested calls the method featured in this fixture, both methods being called in the same test function outputs two nearly identical collections of logging statements in the log of a single test; placing `StatisticsSources._harvest_R5_SUSHI()` in a fixture separates its log from that of `StatisticsSources.collect_usage_statistics()`.

    Args:
        StatisticsSources_fixture (nolcat.models.StatisticsSources): a class instantiation via fixture containing the necessary data to make a real SUSHI call
        month_before_month_like_most_recent_month_with_usage (tuple): the first and last days of the month before the most recent month for which COUNTER data is available
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime

    Yields:
        dataframe: a dataframe containing all of the R5 COUNTER data
    """
    # The log for `test_StatisticsSources.test_harvest_R5_SUSHI()` contains log data from the modules below, it doesn't need to be repeated
    caplog.set_level(logging.ERROR, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()`
    caplog.set_level(logging.ERROR, logger='nolcat.app')  # For `upload_file_to_S3_bucket()` called in `SUSHICallAndResponse.make_SUSHI_call()` and `self._harvest_single_report()`
    caplog.set_level(logging.ERROR, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()`
    caplog.set_level(logging.ERROR, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()`
    yield StatisticsSources_fixture._harvest_R5_SUSHI(month_before_month_like_most_recent_month_with_usage[0], month_before_month_like_most_recent_month_with_usage[1])


@pytest.mark.dependency(depends=['test_harvest_R5_SUSHI'])
def test_collect_usage_statistics(StatisticsSources_fixture, month_before_month_like_most_recent_month_with_usage, harvest_R5_SUSHI_result, caplog):
    """Tests that the `StatisticsSources.collect_usage_statistics()` successfully loads COUNTER data into the `COUNTERData` relation.
    
    The `harvest_R5_SUSHI_result` fixture contains the same data that the method being tested should've loaded into the database, so it is used to see if the test passes. There isn't a good way to review the flash messages returned by the method from a testing perspective.
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`
    method_response = StatisticsSources_fixture.collect_usage_statistics(month_before_month_like_most_recent_month_with_usage[0], month_before_month_like_most_recent_month_with_usage[1])
    method_response_match_object = re.match(r'Successfully loaded (\d*) records into the database.', string=method_response[0])
    assert method_response_match_object is not None  # The test fails at this point because a failing condition here raises errors below

    records_loaded_by_method = match_direct_SUSHI_harvest_result(method_response_match_object.group(1))
    try:
        log.info(f"Differences:\n{records_loaded_by_method.compare(harvest_R5_SUSHI_result[records_loaded_by_method.columns.to_list()])}")
        #TEST: Test is failing because rows are out of order--above shows metric and number pairs are the same but on different rows--below shows possible fix options as output
        r1 = records_loaded_by_method.reset_index()
        r2 = harvest_R5_SUSHI_result.reset_index()
        log.info(f"Differences after the indexes are reset:\n{r1.compare(r2[r1.columns.to_list()])}")
        s2 = harvest_R5_SUSHI_result.sort_values(
            by=records_loaded_by_method.columns.to_list(),
            ignore_index=True,
        )
        s1 = records_loaded_by_method.sort_values(
            by=records_loaded_by_method.columns.to_list(),
            ignore_index=True,
        )
        log.info(f"Differences after sorting by all fields:\n{s1.compare(s2[s1.columns.to_list()])}")
    except:
        log.info(f"Dataframe from database has index {records_loaded_by_method.index} and fields\n{return_string_of_dataframe_info(records_loaded_by_method)}")
        log.info(f"Dataframe from SUSHI has index {harvest_R5_SUSHI_result.index} and fields\n{return_string_of_dataframe_info(harvest_R5_SUSHI_result[records_loaded_by_method.columns.to_list()])}")
    assert_frame_equal(records_loaded_by_method, harvest_R5_SUSHI_result, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order

#Section: Test `StatisticsSources.add_note()`
def test_add_note():
    """Test adding notes about statistics sources."""
    #ToDo: Develop this test alongside the method it's testing
    pass