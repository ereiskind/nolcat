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
            # 3_PR data
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


@pytest.fixture(scope='session')
def sample_SUSHI_DR_response_dataframe():
    """Creates a dataframe with the same data as is in the `sample_SUSHI_DR_response_JSON_dict` fixture."""
    df = pd.DataFrame(
        [
            # 0_DR data
        ],
        columns=['resource_name', 'publisher', 'platform', 'proprietary_ID', 'data_type', 'access_method', 'metric_type', 'usage_date', 'usage_count', 'report_creation_date'],  # All of the values in the `publisher_ID` field were null values, so the field isn't created
    )
    df = df.astype({
        'resource_name': 'string',
        'publisher': 'string',
        'platform': 'string',
        'proprietary_ID': 'string',
        'data_type': 'string',
        'access_method': 'string',
        'metric_type': 'string',
        'usage_count': 'int',
    })
    df['usage_date'] = pd.to_datetime(df['usage_date'])
    df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])
    yield df


@pytest.fixture(scope='session')
def sample_SUSHI_TR_response_dataframe():
    """Creates a dataframe with the same data as is in the `sample_SUSHI_TR_response_JSON_dict` fixture."""
    df = pd.DataFrame(
        [
            # 3_TR data
        ],
        columns=['resource_name', 'publisher', 'platform', 'DOI', 'proprietary_ID', 'ISBN', 'data_type', 'section_type', 'YOP', 'access_type', 'access_method', 'metric_type', 'usage_date', 'usage_count', 'report_creation_date'],  # Fields where all values are null removed from dataframe
    )
    df = df.astype({
        'resource_name': 'string',
        'publisher': 'string',
        'platform': 'string',
        'DOI': 'string',
        'proprietary_ID': 'string',
        'ISBN': 'string',
        'data_type': 'string',
        'section_type': 'string',
        'YOP': 'Int64',
        'access_type': 'string',
        'access_method': 'string',
        'metric_type': 'string',
        'usage_count': 'int',
    })
    df['usage_date'] = pd.to_datetime(df['usage_date'])
    df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])
    yield df


@pytest.fixture(scope='session')
def sample_SUSHI_IR_response_dataframe():
    """Creates a dataframe with the same data as is in the `sample_SUSHI_IR_response_JSON_dict` fixture."""
    df = pd.DataFrame(
        [
            # 3_IR data
        ],
        columns=['resource_name', 'publisher', 'publisher_ID', 'platform', 'authors', 'publication_date', 'article_version', 'DOI', 'proprietary_ID', 'ISBN', 'print_ISSN', 'online_ISSN', 'URI', 'data_type', 'YOP', 'access_type', 'access_method', 'parent_title', 'parent_authors', 'parent_publication_date', 'parent_article_version', 'parent_data_type', 'parent_DOI', 'parent_proprietary_ID', 'parent_ISBN', 'parent_print_ISSN', 'parent_online_ISSN', 'parent_URI', 'metric_type', 'usage_date', 'usage_count', 'report_creation_date'],
    )
    df = df.astype({
        'resource_name': 'string',
        'publisher': 'string',
        'publisher_ID': 'string',
        'platform': 'string',
        'authors': 'string',
        'article_version': 'string',
        'DOI': 'string',
        'proprietary_ID': 'string',
        'ISBN': 'string',
        'print_ISSN': 'string',
        'online_ISSN': 'string',
        'URI': 'string',
        'data_type': 'string',
        'YOP': 'Int64',
        'access_type': 'string',
        'access_method': 'string',
        'parent_title': 'string',
        'parent_authors': 'string',
        'parent_article_version': 'string',
        'parent_data_type': 'string',
        'parent_DOI': 'string',
        'parent_proprietary_ID': 'string',
        'parent_ISBN': 'string',
        'parent_print_ISSN': 'string',
        'parent_online_ISSN': 'string',
        'parent_URI': 'string',
        'metric_type': 'string',
        'usage_count': 'int',
    })
    df['publication_date'] = pd.to_datetime(df['publication_date'])
    df['parent_publication_date'] = pd.to_datetime(df['parent_publication_date'])
    df['usage_date'] = pd.to_datetime(df['usage_date'])
    df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])
    yield df


#Section: Tests
def test_create_dataframe_from_PR(sample_SUSHI_PR_response_JSON_dict, sample_SUSHI_PR_response_dataframe):
    """Tests transforming dictionaries derived from SUSHI PR JSONs into dataframes."""
    df = ConvertJSONDictToDataframe(sample_SUSHI_PR_response_JSON_dict).create_dataframe()
    assert_frame_equal(df, sample_SUSHI_PR_response_dataframe, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order


def test_create_dataframe_from_DR(sample_SUSHI_DR_response_JSON_dict, sample_SUSHI_DR_response_dataframe):
    """Tests transforming dictionaries derived from SUSHI PR JSONs into dataframes."""
    df = ConvertJSONDictToDataframe(sample_SUSHI_DR_response_JSON_dict).create_dataframe()
    assert_frame_equal(df, sample_SUSHI_DR_response_dataframe, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order


def test_create_dataframe_from_TR(sample_SUSHI_TR_response_JSON_dict, sample_SUSHI_TR_response_dataframe):
    """Tests transforming dictionaries derived from SUSHI PR JSONs into dataframes."""
    df = ConvertJSONDictToDataframe(sample_SUSHI_TR_response_JSON_dict).create_dataframe()
    assert_frame_equal(df, sample_SUSHI_TR_response_dataframe, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order


def test_create_dataframe_from_IR(sample_SUSHI_IR_response_JSON_dict, sample_SUSHI_IR_response_dataframe):
    """Tests transforming dictionaries derived from SUSHI PR JSONs into dataframes."""
    df = ConvertJSONDictToDataframe(sample_SUSHI_IR_response_JSON_dict).create_dataframe()
    assert_frame_equal(df, sample_SUSHI_IR_response_dataframe, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order