"""Test using `ConvertJSONDictToDataframe`."""

import pytest
from pathlib import Path
import os
import json
import pandas as pd
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.convert_JSON_dict_to_dataframe import ConvertJSONDictToDataframe

#Section: Fixtures
@pytest.fixture(scope='session')
def sample_SUSHI_PR_response_JSON_dict():
    """Creates a dictionary like the ones derived from the JSONs received in response to SUSHI PR API calls."""
    with open(Path(os.getcwd(), 'tests', 'data', 'COUNTER_JSONs_for_tests', '3_PR.json')) as JSON_file:  # CWD is where the tests are being run (root for this suite)
        dict_from_JSON = json.load(JSON_file)
        yield dict_from_JSON


@pytest.fixture(scope='session')
def sample_SUSHI_DR_response_JSON_dict():
    """Creates a dictionary like the ones derived from the JSONs received in response to SUSHI DR API calls."""
    with open(Path(os.getcwd(), 'tests', 'data', 'COUNTER_JSONs_for_tests', '0_DR.json')) as JSON_file:  # CWD is where the tests are being run (root for this suite)
        dict_from_JSON = json.load(JSON_file)
        yield dict_from_JSON


@pytest.fixture(scope='session')
def sample_SUSHI_TR_response_JSON_dict():
    """Creates a dictionary like the ones derived from the JSONs received in response to SUSHI TR API calls."""
    with open(Path(os.getcwd(), 'tests', 'data', 'COUNTER_JSONs_for_tests', '3_TR.json')) as JSON_file:  # CWD is where the tests are being run (root for this suite)
        dict_from_JSON = json.load(JSON_file)
        yield dict_from_JSON


@pytest.fixture(scope='session')
def sample_SUSHI_IR_response_JSON_dict():
    """Creates a dictionary like the ones derived from the JSONs received in response to SUSHI IR API calls."""
    with open(Path(os.getcwd(), 'tests', 'data', 'COUNTER_JSONs_for_tests', '3_IR.json')) as JSON_file:  # CWD is where the tests are being run (root for this suite)
        dict_from_JSON = json.load(JSON_file)
        yield dict_from_JSON


@pytest.fixture(scope='session')
def sample_SUSHI_PR_response_dataframe():
    """Creates a dataframe with the same data as is in the `sample_SUSHI_PR_response_JSON_dict` fixture."""
    df = pd.DataFrame(
        [
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2019-07-01", 10, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2019-07-01", 10, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2019-08-01", 10, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2019-08-01", 10, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2019-08-01", 10, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2019-09-01", 36, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2019-09-01", 24, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2019-09-01", 20, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2019-10-01", 46, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2019-10-01", 24, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2019-10-01", 24, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2019-11-01", 62, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2019-11-01", 38, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2019-11-01", 32, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2019-12-01", 62, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2019-12-01", 32, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2019-12-01", 22, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2020-01-01", 50, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Requests", "2020-01-01", 4, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2020-01-01", 26, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Requests", "2020-01-01", 4, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2020-01-01", 24, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Requests", "2020-01-01", 4, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2020-02-01", 38, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2020-02-01", 30, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2020-02-01", 24, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2020-03-01", 52, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Requests", "2020-03-01", 32, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2020-03-01", 50, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Requests", "2020-03-01", 32, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2020-03-01", 18, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Requests", "2020-03-01", 2, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2020-04-01", 24, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Requests", "2020-04-01", 18, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2020-04-01", 20, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Requests", "2020-04-01", 20, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2020-04-01", 6, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Requests", "2020-04-01", 2, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Total_Item_Investigations", "2020-06-01", 4, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Item_Investigations", "2020-06-01", 4, "2019-07-01"],
            ["Duke University Press", "Book", "Regular", "Unique_Title_Investigations", "2020-06-01", 4, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2019-07-01", 216, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2019-07-01", 118, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2019-07-01", 128, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2019-07-01", 90, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2019-08-01", 178, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2019-08-01", 94, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2019-08-01", 108, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2019-08-01", 76, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2019-09-01", 684, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2019-09-01", 406, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2019-09-01", 364, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2019-09-01", 290, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2019-10-01", 3252, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2019-10-01", 1744, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2019-10-01", 1576, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2019-10-01", 1414, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2019-11-01", 522, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2019-11-01", 254, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2019-11-01", 320, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2019-11-01", 216, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2019-12-01", 388, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2019-12-01", 224, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2019-12-01", 242, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2019-12-01", 194, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2020-01-01", 308, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2020-01-01", 176, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2020-01-01", 204, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2020-01-01", 154, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2020-02-01", 472, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2020-02-01", 266, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2020-02-01", 282, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2020-02-01", 204, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2020-03-01", 284, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2020-03-01", 148, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2020-03-01", 168, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2020-03-01", 130, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2020-04-01", 188, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2020-04-01", 116, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2020-04-01", 130, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2020-04-01", 104, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2020-05-01", 74, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2020-05-01", 44, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2020-05-01", 50, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2020-05-01", 38, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Investigations", "2020-06-01", 172, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Total_Item_Requests", "2020-06-01", 94, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Investigations", "2020-06-01", 104, "2019-07-01"],
            ["Duke University Press", "Journal", "Regular", "Unique_Item_Requests", "2020-06-01", 84, "2019-07-01"],
        ],
        columns=['platform', 'data_type', 'access_method', 'metric_type', 'usage_date', 'usage_count', 'report_creation_date'],
    )
    df = df.astype({
        'platform': 'string',
        'data_type': 'string',
        'access_method': 'string',
        'metric_type': 'string',
        'usage_count': 'int',
    })
    df['usage_date'] = pd.to_datetime(df['usage_date'])
    df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])
    yield df


#Section: Tests
def test_create_dataframe_from_PR(sample_SUSHI_PR_response_JSON_dict, sample_SUSHI_PR_response_dataframe):
    """Tests transforming dictionaries derived from SUSHI PR JSONs into dataframes."""
    df = ConvertJSONDictToDataframe(sample_SUSHI_PR_response_JSON_dict).create_dataframe()
    assert_frame_equal(df, sample_SUSHI_PR_response_dataframe, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order