"""Tests the methods in StatisticsSources."""

import pytest

from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE


@pytest.fixture(scope='session')
def StatisticsSources_fixture():
    """A fixture mocking up a StatisticsSources object based on the R5 SUSHI credentials JSON."""
    #ToDo: The fixture currently counts the number of StatisticsSources in the R5 SUSHI credentials JSON and currently chooses a number in that range for the fixture's StatisticsSources.statistics_source_retrieval_code value; all the other attributes are placeholders with static values. Should the randomly selected number be used to retrieve actual values for a StatisticsSources object instead?
    #Section: Get the Number of Statistics Sources in the JSON
    #ToDo: number_of_StatisticsSources = 0
    #ToDo: with open(path_to_credentials_file) as JSON_file:
            #ToDo: SUSHI_data_file = json.load(JSON_File)
            #ToDo: for vendor in SUSHI_data_file:
                #ToDo: for stats_source in vendor:
                    #ToDo: if stats_source['interface_id']:
                        #ToDo: number_of_StatisticsSources += 1
    
    
    #Section: Create the StatisticsSources Object
    #ToDo: random_StatisticsSources_value = str(random number between 1 and number_of_StatisticsSources)
    #ToDo: fixture_value = StatisticsSources(
        # 1,  # StatisticsSources.statistics_source_id
        # "StatisticsSources.statistics_source_name",
        # random_StatisticsSources_value,
        # 1,  # StatisticsSources.vendor_id
    # )
    #ToDo: return fixture_value


def test_fetch_SUSHI_credentials_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a StatisticsSources.statistics_source_retrieval_code value and returning a value suitable for use in a API call."""
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: credentials = stats.source.fetch_SUSHI_credentials()
    #ToDo: assert credentials == dict and credentials['URL'] matches regex /https?:\/\/.*\//
    pass


def test_fetch_SUSHI_credentials_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a StatisticsSources.statistics_source_retrieval_code value and returning the credentials for user display."""
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: credentials = stats.source.fetch_SUSHI_credentials(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


def test_harvest_R5_SUSHI(StatisticsSources_fixture):
    """Tests collecting all available R5 reports for a StatisticsSources.statistics_source_retrieval_code value and combining them into a single dataframe."""
    #ToDo: PROBLEM: Included in the method is a check to see if the provided statistics source has already been loaded for each month in the provided timeframe; this is a very good idea for the method itself, as it prevents data loading duplications, but will block testing, as the method won't make the API calls for the master reports of a vendor and month combination already in the database. How can testing be done?
    #ToDo: Set up functionality for rolling back transaction so loads for this test don't go in the database
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: Ask for dates
    #ToDo: usage = stats_source._harvest_R5_SUSHI(dates)
    #ToDo: Check `usage` in some ways to confirm the method call was a success
    pass


def test_collect_usage_statistics(StatisticsSources_fixture):
    """Tests the method making the StatisticsSources._harvest_R5_SUSHI result a RawCOUNTERReport object."""
    #ToDo: PROBLEM: Included in the method is a check to see if the provided statistics source has already been loaded for each month in the provided timeframe; this is a very good idea for the method itself, as it prevents data loading duplications, but will block testing, as the method won't make the API calls for the master reports of a vendor and month combination already in the database. How can testing be done?
    #ToDo: Set up functionality for rolling back transaction so loads for this test don't go in the database
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: Ask for dates
    #ToDo: usage = stats_source._harvest_R5_SUSHI(dates)
    #ToDo: assert usage is RawCOUNTERReport object
    pass


def test_upload_R4_report(StatisticsSources_fixture):
    """Tests the uploading and ingesting of a transformed R4 report."""
    #ToDo: Develop this test alongside the method its testing
    pass


def test_upload_R5_report(StatisticsSources_fixture):
    """Tests the uploading and ingesting of a R5 report."""
    #ToDo: Develop this test alongside the method its testing
    pass