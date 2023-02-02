"""Tests the methods in StatisticsSources."""

import json
from random import sample
import datetime
import pytest
import pandas as pd
from dateutil.relativedelta import relativedelta  # dateutil is a pandas dependency, so it doesn't need to be in requirements.txt
from random import choice
import calendar

# `conftest.py` fixtures are imported automatically
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE


#Section: Fixtures
@pytest.fixture(scope='session')
def most_recent_month_with_usage():
    """Creates the value that will be used for the `begin_date` SUSHI parameter and for database queries in other locations in the testing module."""
    current_date = datetime.date.today()
    if current_date.day < 10:
        begin_month = current_date + relativedelta(months=-2)
        yield begin_month.replace(day=1)
    else:
        begin_month = current_date + relativedelta(months=-1)
        yield begin_month.replace(day=1)


@pytest.fixture(scope='session')
def StatisticsSources_fixture(engine, most_recent_month_with_usage):
    """A fixture simulating a `StatisticsSources` object containing the necessary data to make a real SUSHI call.
    
    The SUSHI API has no test values, so testing SUSHI calls requires using actual SUSHI credentials. This fixture creates a `StatisticsSources` object with mocked values in all fields except `statisticsSources_relation['Statistics_Source_Retrieval_Code']`, which uses a random value taken from the R5 SUSHI credentials file. Because the `_harvest_R5_SUSHI()` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics are filtered out to prevent their use.

    Args:
        PATH_TO_CREDENTIALS_FILE (str): the file path for "R5_SUSHI_credentials.json"
        most_recent_month_with_usage (datetime.date): the most recent month for which COUNTER data is available

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
            sql=f"SELECT COUNT(*) FROM statisticsSources JOIN COUNTERData ON statisticsSources.statistics_source_ID=COUNTERData.statistics_source_ID WHERE statisticsSources.statistics_source_retrieval_code={interface} AND COUNTERData.usage_date={most_recent_month_with_usage.strftime('%Y-%m-%d')}",
            con=engine,
        )
        if not query_result.empty or not query_result.isnull().all().all():  # `empty` returns Boolean based on if the dataframe contains data elements; `isnull().all().all()` returns a Boolean based on a dataframe of Booleans based on if the value of the data element is null or not
            retrieval_codes.append(interface)
    
    fixture = StatisticsSources(
        statistics_source_ID = 1,
        statistics_source_name = "Stats source fixture name",
        statistics_source_retrieval_code = choice(retrieval_codes),
        vendor_ID = 1,
    )
    yield fixture


#Section: Tests
def test_fetch_SUSHI_credentials_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning a value suitable for use in a API call."""
    #ToDo: credentials = StatisticsSources_fixture.fetch_SUSHI_credentials()
    #ToDo: assert credentials == dict and credentials['URL'] matches regex /https?:\/\/.*\//
    pass


def test_fetch_SUSHI_credentials_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning the credentials for user display."""
    #ToDo: credentials = StatisticsSources_fixture.fetch_SUSHI_credentials(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


def test_harvest_R5_SUSHI(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests collecting all available R5 reports for a `StatisticsSources.statistics_source_retrieval_code` value and combining them into a single dataframe."""
    end_date = datetime.date(
        most_recent_month_with_usage.year,
        most_recent_month_with_usage.month,
        calendar.monthrange(most_recent_month_with_usage.year, most_recent_month_with_usage.month)[1],
    )
    #ToDo: SUSHI_data = StatisticsSources_fixture._harvest_R5_SUSHI(most_recent_month_with_usage, end_date)
    #ToDo: assert `SUSHI_data` is a dataframe; what else can be checked to confirm the right data was returned?
    pass


def test_collect_usage_statistics(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests that the `StatisticsSources.collect_usage_statistics()` successfully loads COUNTER data into the `COUNTERData` relation."""
    end_date = datetime.date(
        most_recent_month_with_usage.year,
        most_recent_month_with_usage.month,
        calendar.monthrange(most_recent_month_with_usage.year, most_recent_month_with_usage.month)[1],
    )
    #ToDo: to_check_against = StatisticsSources_fixture._harvest_R5_SUSHI(most_recent_month_with_usage, end_date)
    #ToDo: number_of_records = to_check_against.shape[0]
    #ToDo: StatisticsSources_fixture.collect_usage_statistics(most_recent_month_with_usage, end_date)
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
    #ToDo: assert_frame_equal(most_recently_loaded_records, to_check_against, check_like=True)  # Keyword argument allows test to pass if fields aren't in the same order
    pass


def test_add_note():
    """Test adding notes about statistics sources."""
    #ToDo: Develop this test alongside the method it's testing
    pass