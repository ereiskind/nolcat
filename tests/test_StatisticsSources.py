"""Tests the methods in StatisticsSources."""

import pytest
import json
import datetime
import calendar
from random import choice
import re
import pandas as pd
from dateutil.relativedelta import relativedelta  # dateutil is a pandas dependency, so it doesn't need to be in requirements.txt

# `conftest.py` fixtures are imported automatically
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE


#Section: Fixtures
@pytest.fixture(scope='session')
def first_day_of_most_recent_month_with_usage():
    """Creates the value that will be used for the `begin_date` SUSHI parameter.

    Some StatisticsSources methods call other parts of the code that make SUSHI calls, but since that testing isn't the focus of this module, values unlikely to raise errors are supplied to be passed to the SUSHI API calls. In the case of the dates, the most recent month for which usage is likely to be available is used as both the start and end of the available date range, as more recent data is less likely to be in the database and thus cause a problem with the check for previously loaded data.

    Yields:
        datetime.date: the first day of a month
    """
    
    current_date = datetime.date.today()
    if current_date.day < 10:
        begin_month = current_date + relativedelta(months=-2)
        yield begin_month.replace(day=1)
    else:
        begin_month = current_date + relativedelta(months=-1)
        yield begin_month.replace(day=1)


@pytest.fixture(scope='session')
def last_day_of_month(first_day_of_most_recent_month_with_usage):
    """The last day of the month identified in the `first_day_of_month_with_usage` fixture.

    When including the day in the `end_date` value for a SUSHI API call, that date must be the last day of the month. This fixture creates the last day of the month that corresponds to the first day of the month from the `first_day_of_month_with_usage` fixture.

    Args:
        first_day_of_most_recent_month_with_usage (datetime.date): the first day of the most recent month for which COUNTER data is available

    Yields:
        datetime.date: the last day of a month
    """
    yield datetime.date(
        first_day_of_most_recent_month_with_usage.year,
        first_day_of_most_recent_month_with_usage.month,
        calendar.monthrange(first_day_of_most_recent_month_with_usage.year, first_day_of_most_recent_month_with_usage.month)[1],
    )


@pytest.fixture(scope='session')
def StatisticsSources_fixture(engine, first_day_of_most_recent_month_with_usage):
    """A fixture simulating a `StatisticsSources` object containing the necessary data to make a real SUSHI call.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. This fixture creates a `StatisticsSources` object with mocked values in all fields except `statisticsSources_relation['Statistics_Source_Retrieval_Code']`, which uses a random value taken from the R5 SUSHI credentials file. Because the `_harvest_R5_SUSHI()` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics are filtered out to prevent their use.

    Args:
        PATH_TO_CREDENTIALS_FILE (str): the file path for "R5_SUSHI_credentials.json"
        first_day_of_most_recent_month_with_usage (datetime.date): the first day of the most recent month for which COUNTER data is available

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
    print(f"Possible retrieval code choices:\n{retrieval_codes_as_interface_IDs}")
    
    retrieval_codes = []
    for interface in retrieval_codes_as_interface_IDs:
        query_result = pd.read_sql(
            sql=f"SELECT COUNT(*) FROM statisticsSources JOIN COUNTERData ON statisticsSources.statistics_source_ID=COUNTERData.statistics_source_ID WHERE statisticsSources.statistics_source_retrieval_code={interface} AND COUNTERData.usage_date={first_day_of_most_recent_month_with_usage.strftime('%Y-%m-%d')}",
            con=engine,
        )
        if not query_result.empty or not query_result.isnull().all().all():  # `empty` returns Boolean based on if the dataframe contains data elements; `isnull().all().all()` returns a Boolean based on a dataframe of Booleans based on if the value of the data element is null or not
            retrieval_codes.append(interface)
    print(f"Retrieval code choices:\n{retrieval_codes}")
    
    fixture = StatisticsSources(
        statistics_source_ID = 1,
        statistics_source_name = "Stats source fixture name",
        statistics_source_retrieval_code = choice(retrieval_codes),
        vendor_ID = 1,
    )
    yield fixture


#Section: Tests
@pytest.mark.dependency()
def test_fetch_SUSHI_information_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning a value suitable for use in a API call."""
    credentials = StatisticsSources_fixture.fetch_SUSHI_information()
    assert repr(type(credentials)) == "<class 'dict'>" and re.match(r"https?:\/\/.*\/", string=credentials['URL'])


def test_fetch_SUSHI_information_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning the credentials for user display."""
    #ToDo: credentials = StatisticsSources_fixture.fetch_SUSHI_information(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


@pytest.mark.dependency(depends=['test_fetch_SUSHI_information_for_API'])
def test_harvest_R5_SUSHI(StatisticsSources_fixture, first_day_of_most_recent_month_with_usage, last_day_of_month):
    """Tests collecting all available R5 reports for a `StatisticsSources.statistics_source_retrieval_code` value and combining them into a single dataframe."""
    begin_test = datetime.datetime.now()
    before_data_collection = datetime.datetime.now()
    SUSHI_data = StatisticsSources_fixture._harvest_R5_SUSHI(first_day_of_most_recent_month_with_usage, last_day_of_month)
    data_collected = datetime.datetime.now()
    print(SUSHI_data)
    print(f"The test function start is at {begin_test}, the data collection start is at {before_data_collection}, and the data collection end is at {data_collected}; can any of these be compared to the timestamp in the report to further confirm accuracy?")
    print(type(SUSHI_data))
    assert repr(type(SUSHI_data)) == "<class 'pandas.core.frame.DataFrame'>" and SUSHI_data['statistics_source_ID'].eq(1).all()  #ToDo: and time collected value is equal to one of the above if possible


@pytest.mark.dependency(depends=['test_harvest_R5_SUSHI'])
def test_collect_usage_statistics(StatisticsSources_fixture, first_day_of_most_recent_month_with_usage, last_day_of_month):
    """Tests that the `StatisticsSources.collect_usage_statistics()` successfully loads COUNTER data into the `COUNTERData` relation."""
    #ToDo: to_check_against = StatisticsSources_fixture._harvest_R5_SUSHI(first_day_of_most_recent_month_with_usage, last_day_of_month)
    #ToDo: number_of_records = to_check_against.shape[0]
    #ToDo: StatisticsSources_fixture.collect_usage_statistics(first_day_of_most_recent_month_with_usage, last_day_of_month)
    #ToDo: SQL_query = f"""
    #ToDo:     SELECT *
    #ToDo:     FROM (
    #ToDo:         SELECT * FROM COUNTERData
    #ToDo:         ORDER BY COUNTER_data_ID DESC
    #ToDo:         LIMIT {number_of_records}
    #ToDo:     ) subquery
    #ToDo:     ORDER BY COUNTER_data_ID ASC;
    #ToDo: """
    #ToDo: most_recently_loaded_records = pd.read_sql(
    #ToDo:     sql=SQL_query,
    #ToDo:     con=engine,
    #ToDo: )
    #ToDo: most_recently_loaded_records = most_recently_loaded_records.drop(columns='COUNTER_data_ID')
    #ToDo: assert_frame_equal(most_recently_loaded_records, to_check_against, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order; `check_index_type=False` argument allows test to pass if indexes are different dtypes (might be needed)
    pass


def test_add_note():
    """Test adding notes about statistics sources."""
    #ToDo: Develop this test alongside the method it's testing
    pass