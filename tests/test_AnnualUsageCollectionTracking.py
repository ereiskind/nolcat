"""Tests the methods in AnnualUsageCollectionTracking."""
########## No tests written 2023-07-11 ##########

import pytest
import logging
from random import choice
import os

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *

log = logging.getLogger(__name__)


#Section: collect_annual_usage_statistics()
def test_collect_annual_usage_statistics():
    """Test calling the StatisticsSources._harvest_R5_SUSHI method for the record's StatisticsSources instance with arguments taken from the record's FiscalYears instance."""
    #ToDo: caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    #ToDo: Get the data from the other relations, then call the method
    pass


#Section: upload_nonstandard_usage_file()
def test_upload_nonstandard_usage_file():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


#Section: download_nonstandard_usage_file()
@pytest.fixture(scope='module')
def choose_AUCT_PKs():
    """Chooses the `StatisticsSources.statistics_source_ID`, file name, and note value to use in the subsequent tests."""
    yield choice([
        (2, f"11_2.csv", "This is the first FY with usage statistics"),
        (3, f"11_3.csv", None),
        (4, f"11_4.csv", None),
    ])


@pytest.fixture(scope='module')
def AUCT_fixture_3(choose_AUCT_PKs):
    """Creates an `AnnualUsageCollectionTracking` object with the data from `choose_AUCT_PKs()`."""
    yield AnnualUsageCollectionTracking(
        AUCT_statistics_source=11,
        AUCT_fiscal_year=choose_AUCT_PKs[0],
        usage_is_being_collected=True,
        manual_collection_required=True,
        collection_via_email=False,
        is_COUNTER_compliant=False,
        collection_status="Collection complete",
        usage_file_path=f"{choose_AUCT_PKs[1]}",
        notes=choose_AUCT_PKs[2],
    )


@pytest.fixture
def file_for_download(tmp_path, AUCT_fixture_3):
    """Creates a file in S3 that can be used in `test_download_nonstandard_usage_file()`."""
    df=pd.DataFrame()
    df.to_csv(
        tmp_path / 'df.csv',
        encoding='utf-8',
        errors='backslashreplace',
    )
    upload_file_to_S3_bucket(
        Path(tmp_path / 'df.csv'),
        f"test_{AUCT_fixture_3.usage_file_path}",
    )
    yield f"{PATH_WITHIN_BUCKET}test_{AUCT_fixture_3.usage_file_path}"  # The fixture returns the name of the file for use in determining its successful upload

    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=f"{PATH_WITHIN_BUCKET}test_{AUCT_fixture_3.usage_file_path}"
        )
    except botocore.exceptions as error:
        log.error(f"Trying to remove the test data files from the S3 bucket raised {error}.")
    os.remove(tmp_path / 'df.csv')


def test_download_nonstandard_usage_file(AUCT_fixture_3, file_for_download):
    """Test downloading a file in S3 to a local computer."""
    #Subsection: Confirm File to Download is in S3
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}test_",
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    if file_for_download not in bucket_contents:
        pytest.skip(f"The file {file_for_download} wasn't successfully loaded into the S3 bucket.")
    
    #Subsection: Download File Via Method
    file_path = AUCT_fixture_3.download_nonstandard_usage_file()
    log.info(f"`file_path` is {file_path} (type {type(file_path)})")
    assert False