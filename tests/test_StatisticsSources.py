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