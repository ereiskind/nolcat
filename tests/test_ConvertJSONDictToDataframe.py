"""Test using `ConvertJSONDictToDataframe`."""

import pytest
from pathlib import Path
import os
import json

# `conftest.py` fixtures are imported automatically
from nolcat.convert_JSON_dict_to_dataframe import ConvertJSONDictToDataframe

#Section: Fixtures
@pytest.fixture(scope='session')
def sample_SUSHI_response_JSON_dict():
    """Creates a dictionary like the ones derived from the JSONs received in response to SUSHI API calls."""
    with open(Path(os.getcwd(), 'tests', 'data', 'COUNTER_JSONs_for_tests', '3_PR.json')) as JSON_file:  # CWD is where the tests are being run (root for this suite)
        dict_from_JSON = json.load(JSON_file)
        print(f"`sample_SUSHI_response_JSON_dict` result (type {type(dict_from_JSON)}):\n{dict_from_JSON}")
        yield dict_from_JSON


@pytest.fixture(scope='session')
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