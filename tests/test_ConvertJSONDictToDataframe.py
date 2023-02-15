"""Test using `ConvertJSONDictToDataframe`."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.convert_JSON_dict_to_dataframe import ConvertJSONDictToDataframe

#Section: Fixtures
@pytest.fixture
def sample_SUSHI_response_JSON_dict():
    """Creates a dictionary like the ones derived from the JSONs received in response to SUSHI API calls."""
    #ToDo: Create dictionary
    pass


@pytest.fixture
def sample_SUSHI_response_dataframe():
    """Creates a dataframe with the same data as is in the `sample_SUSHI_response_JSON_dict` fixture."""
    #ToDo: Create dataframe
    pass


#Section: Tests
def test_create_dataframe(sample_SUSHI_response_JSON_dict, sample_SUSHI_response_dataframe):
    """Tests transforming dictionaries derived from SUSHI JSONs into dataframes."""
    #ToDo: df = ConvertJSONDictToDataframe(sample_SUSHI_response_JSON_dict).create_dataframe()
    #ToDo: assert_frame_equal(df, sample_SUSHI_response_dataframe, check_like=True)  # Keyword argument allows test to pass if fields aren't in the same order
    pass