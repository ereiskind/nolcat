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


@pytest.fixture
def create_file_for_download(tmp_path):
    """Creates an `annualUsageCollectionTracking` object and a related file in S3 that can be used in `test_download_nonstandard_usage_file()`."""
    PK_for_AUCT_object = choice([
        (2, f"11_2.csv", "This is the first FY with usage statistics"),
        (3, f"11_3.csv", None),
        (4, f"11_4.csv", None),
    ])
    AUCT_object = AnnualUsageCollectionTracking(
        AUCT_statistics_source=11,
        AUCT_fiscal_year=PK_for_AUCT_object[0],
        usage_is_being_collected=True,
        manual_collection_required=True,
        collection_via_email=False,
        is_COUNTER_compliant=False,
        collection_status="Collection complete",
        usage_file_path=f"{PATH_WITHIN_BUCKET}{PK_for_AUCT_object[1]}",
        notes=PK_for_AUCT_object[2],
    )
    log.info(f"`AUCT_object`: {AUCT_object}")

    df=pd.DataFrame()
    file_for_S3 = df.to_csv(
        tmp_path / 'df.csv',
        encoding='utf-8',
        errors='backslashreplace',
    )
    upload_file_to_S3_bucket(
        file_for_S3,
        f"{PATH_WITHIN_BUCKET}test_{PK_for_AUCT_object[1]}",
    )
    yield AUCT_object

    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=f"{PATH_WITHIN_BUCKET}test_{PK_for_AUCT_object[1]}"
        )
    except botocore.exceptions as error:
        log.error(f"Trying to remove the test data files from the S3 bucket raised {error}.")
    os.remove(tmp_path / 'df.csv')


def test_collect_annual_usage_statistics():
    """Test calling the StatisticsSources._harvest_R5_SUSHI method for the record's StatisticsSources instance with arguments taken from the record's FiscalYears instance."""
    #ToDo: caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    #ToDo: Get the data from the other relations, then call the method
    pass


def test_upload_nonstandard_usage_file():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_download_nonstandard_usage_file(create_file_for_download):
    """Test downloading a file in S3 to a local computer."""
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}test_",
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET}test_", "") for file_name in bucket_contents]
    if create_file_for_download['usage_file_path'].split("/")[-1] not in bucket_contents:
        pytest.skip(f"The file {create_file_for_download['usage_file_path']} wasn't successfully loaded into the S3 bucket.")
    #ToDo: Get file
    #ToDo: File should be empty
    assert False