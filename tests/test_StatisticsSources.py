"""Tests the methods in StatisticsSources."""
########## Data in all relations ##########

import pytest
import json
import datetime
from random import choice
import re
import pandas as pd
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE


#Section: Fixtures
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
    print(f"Possible retrieval code choices:\n{retrieval_codes_as_interface_IDs}")
    
    retrieval_codes = []
    for interface in retrieval_codes_as_interface_IDs:
        query_result = pd.read_sql(
            sql=f"SELECT COUNT(*) FROM statisticsSources JOIN COUNTERData ON statisticsSources.statistics_source_ID=COUNTERData.statistics_source_ID WHERE statisticsSources.statistics_source_retrieval_code={interface} AND COUNTERData.usage_date={most_recent_month_with_usage[0].strftime('%Y-%m-%d')}",
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
    assert repr(type(credentials)) == "<class 'dict'>"
    assert re.match(r"https?:\/\/.*\/", string=credentials['URL'])


def test_fetch_SUSHI_information_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning the credentials for user display."""
    #ToDo: credentials = StatisticsSources_fixture.fetch_SUSHI_information(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


@pytest.mark.dependency(depends=['test_fetch_SUSHI_information_for_API'])
def test_harvest_R5_SUSHI(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests collecting all available R5 reports for a `StatisticsSources.statistics_source_retrieval_code` value and combining them into a single dataframe."""
    SUSHI_data = StatisticsSources_fixture._harvest_R5_SUSHI(most_recent_month_with_usage[0], most_recent_month_with_usage[1])
    assert repr(type(SUSHI_data)) == "<class 'pandas.core.frame.DataFrame'>"
    assert SUSHI_data['statistics_source_ID'].eq(1).all()
    assert SUSHI_data['report_creation_date'].map(lambda datetime: datetime.strftime('%Y-%m-%d')).eq(datetime.datetime.utcnow().strftime('%Y-%m-%d')).all()  # Inconsistencies in timezones and UTC application among vendors mean time cannot be used to confirm the recency of an API call response


@pytest.mark.dependency(depends=['test_harvest_R5_SUSHI'])
def test_collect_usage_statistics(StatisticsSources_fixture, most_recent_month_with_usage, engine):
    """Tests that the `StatisticsSources.collect_usage_statistics()` successfully loads COUNTER data into the `COUNTERData` relation."""
    to_check_against = StatisticsSources_fixture._harvest_R5_SUSHI(most_recent_month_with_usage[0], most_recent_month_with_usage[1])
    number_of_records = to_check_against.shape[0]
    StatisticsSources_fixture.collect_usage_statistics(most_recent_month_with_usage[0], most_recent_month_with_usage[1])
    SQL_query = f"""
        SELECT *
        FROM (
            SELECT * FROM COUNTERData
            ORDER BY COUNTER_data_ID DESC
            LIMIT {number_of_records}
        ) subquery
        ORDER BY COUNTER_data_ID ASC;
    """
    most_recently_loaded_records = pd.read_sql(
        sql=SQL_query,
        con=engine,
    )
    most_recently_loaded_records = most_recently_loaded_records.drop(columns='COUNTER_data_ID')
    most_recently_loaded_records = most_recently_loaded_records.astype({
        "statistics_source_ID": 'int',
        "report_type": 'string',
        "resource_name": 'string',
        "publisher": 'string',
        "publisher_ID": 'string',
        "platform": 'string',
        "authors": 'string',
        "article_version": 'string',
        "DOI": 'string',
        "proprietary_ID": 'string',
        "ISBN": 'string',
        "print_ISSN": 'string',
        "online_ISSN": 'string',
        "URI": 'string',
        "data_type": 'string',
        "section_type": 'string',
        "YOP": 'Int64',  # Using the pandas data type here because it allows null values
        "access_type": 'string',
        "access_method": 'string',
        "parent_title": 'string',
        "parent_authors": 'string',
        "parent_article_version": 'string',
        "parent_data_type": 'string',
        "parent_DOI": 'string',
        "parent_proprietary_ID": 'string',
        "parent_ISBN": 'string',
        "parent_print_ISSN": 'string',
        "parent_online_ISSN": 'string',
        "parent_URI": 'string',
        "metric_type": 'string',
        # `usage_count` is a numpy int type, let the program determine the number of bits used for storage
    })
    most_recently_loaded_records["parent_publication_date"] = pd.to_datetime(most_recently_loaded_records["parent_publication_date"])
    most_recently_loaded_records["publication_date"] = pd.to_datetime(most_recently_loaded_records["publication_date"])
    most_recently_loaded_records["report_creation_date"] = pd.to_datetime(most_recently_loaded_records["report_creation_date"])
    most_recently_loaded_records["usage_date"] = pd.to_datetime(most_recently_loaded_records["usage_date"])
    assert_frame_equal(most_recently_loaded_records, to_check_against, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order; `check_index_type=False` argument allows test to pass if indexes are different dtypes (might be needed)
    pass


def test_add_note():
    """Test adding notes about statistics sources."""
    #ToDo: Develop this test alongside the method it's testing
    pass
