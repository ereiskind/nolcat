"""Tests the methods in StatisticsSources."""

import json
from random import sample
import datetime
import pytest
import pandas as pd
from dateutil import relativedelta  # dateutil is a pandas dependency, so it doesn't need to be in requirements.txt

# `conftest.py` fixtures are imported automatically
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE


@pytest.fixture(autouse=True, scope='function')
def CREDENTIALS_FILE_PATH():
    """This will skip the rest of the tests in this module if the `nolcat.models.PATH_TO_CREDENTAILS_FILE()` function doesn't return a string."""
    #ALERT: This is untested
    if str(type(PATH_TO_CREDENTIALS_FILE())) == "<class 'str'>":
        yield PATH_TO_CREDENTIALS_FILE()
    pytest.skip("Credentials file path not available.")


@pytest.fixture
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
def StatisticsSources_fixture(CREDENTIALS_FILE_PATH, most_recent_month_with_usage):
    """A fixture modifying the `StatisticsSources` sample dataframe by adding values from the R5 SUSHI JSON to the `StatisticsSources.statistics_source_retrieval_code` field.
    
    This fixture modifies the `statisticsSources_relation` sample data fixture by replacing the values in `statisticsSources_relation['Statistics_Source_Retrieval_Code']` with retrieval code values found in "R5_SUSHI_credentials.json" so any SUSHI API calls will work. Because the `_harvest_R5_SUSHI` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics cannot be used.
    """
    #Section: Get List of StatisticsSources.statistics_source_retrieval_code Values
    retrieval_codes_as_interface_IDs = []  # The list of `StatisticsSources.statistics_source_retrieval_code` values from the JSON, which are labeled as `interface_id` in the JSON
    with open(CREDENTIALS_FILE_PATH) as JSON_file:  #Alert: Use of fixture instead of function directly untested
        SUSHI_data_file = json.load(JSON_file)
        for vendor in SUSHI_data_file:
            for stats_source in vendor['interface']:
                if "interface_id" in list(stats_source.keys()):
                        retrieval_codes_as_interface_IDs.append(stats_source['interface_id'])
    
    #Section: Remove Values for Ineligible Statistics Sources
    # The `StatisticsSources._harvest_R5_SUSHI()` method prohibits the loading of statistics if the stats source/date combo is already in the database. When using just the test data, this won't be an issue, but once data is loaded in, conflicts may emerge. To handle this, each statistics source is checked to see if it has usage for the date specified in the `most_recent_month_with_usage` fixture loaded; any stats source that does isn't provided as an option for use in the sample data.
    retrieval_codes = []
    for interface in retrieval_codes_as_interface_IDs:
        retrieval_codes.append(interface)  #ALERT: placeholder for below
        #ToDo: Run query to check if usage for the source and date combination exists
        #ToDo: if the query returns an empty set:
            #ToDo: retrieval_codes.append(interface)
    
    #Section: Create Dataframe
    df = statisticsSources_relation
    retrieval_code_series = sample(retrieval_codes, len(df.index))  # Creates a list of valid `statistics_source_retrieval_code` values the same length of the number of records
    df['Statistics_Source_Retrieval_Code'] = retrieval_code_series
    yield df


#ToDo: Is a test that confirms database I/O by loading the sample data into the database needed here?


def test_fetch_SUSHI_credentials_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning a value suitable for use in a API call."""
    #ToDo: Select a record from `StatisticsSources_fixture` dataframe
    #ToDo: credentials = record_from_fixture.fetch_SUSHI_credentials()
    #ToDo: assert credentials == dict and credentials['URL'] matches regex /https?:\/\/.*\//
    pass


def test_fetch_SUSHI_credentials_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a `StatisticsSources.statistics_source_retrieval_code` value and returning the credentials for user display."""
    #ToDo: Select a record from `StatisticsSources_fixture` dataframe
    #ToDo: credentials = record_from_fixture.fetch_SUSHI_credentials(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


def test_harvest_R5_SUSHI(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests collecting all available R5 reports for a `StatisticsSources.statistics_source_retrieval_code` value and combining them into a single dataframe."""
    #ToDo: Set up functionality for rolling back transaction so loads for this test don't go in the database
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: last_day = the last day of the month represented by most_recent_month_with_usage
    #ToDo: SUSHI_data = stats_source._harvest_R5_SUSHI(most_recent_month_with_usage, last_day)
    #ToDo: assert `SUSHI_data` is a dataframe; what else can be checked to confirm the right data was returned?
    pass


def test_collect_usage_statistics(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests that the `StatisticsSources.collect_usage_statistics()` returns a RawCOUNTERReport object."""
    #ToDo: Set up functionality for rolling back transaction so loads for this test don't go in the database
    #ToDo: stats_source = Select a record from `StatisticsSources_fixture` dataframe
    #ToDo: wrapped_data = stats_source.collect_usage_statistics(most_recent_month_with_usage, last_day)
    #ToDo: assert wrapped_data is a RawCOUNTERReport
    pass


def test_upload_R4_report(StatisticsSources_fixture):
    """Tests the uploading and ingesting of a transformed R4 report."""
    #ToDo: Develop this test alongside the method it's testing
    pass


def test_upload_R5_report(StatisticsSources_fixture):
    """Tests the uploading and ingesting of a R5 report."""
    #ToDo: Develop this test alongside the method it's testing
    pass