"""Tests the methods in AnnualUsageCollectionTracking."""
########## Failing 2023-08-24 ##########

import pytest
import logging
from random import choice

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *

log = logging.getLogger(__name__)


#Section: Collecting Annual COUNTER Usage Statistics
@pytest.fixture(scope='module')
def AUCT_fixture_for_SUSHI(engine):
    """Creates an `AnnualUsageCollectionTracking` object with a non-null `StatisticsSources.statistics_source_retrieval_code` value.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
    
    Yields:
        nolcat.models.AnnualUsageCollectionTracking: an AnnualUsageCollectionTracking object corresponding to a record with a non-null `statistics_source_retrieval_code` attribute
    """
    #ToDo: sql=f"SELECT * FROM annualUsageCollectionTracking JOIN statisticsSources ON statisticsSources.statistics_source_ID = annualUsageCollectionTracking.AUCT_statistics_source WHERE StatisticsSources.statistics_source_retrieval_code IS NOT NULL;"
    #ToDo: Randomly select a record and use its data to create a `AnnualUsageCollectionTracking` object
    pass


def test_collect_annual_usage_statistics(caplog):
    """Test calling the `StatisticsSources._harvest_R5_SUSHI()` method for the record's StatisticsSources instance with arguments taken from the record's FiscalYears instance."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`

    #ToDo: AUCT_fixture -> PK used to get SUSHI start date, SUSHI end date, StatisticsSources object
    #ToDo: `StatisticsSources._harvest_R5_SUSHI()` called with stats source and dates above
    #ToDo: Index adjusted for upload to `COUNTERData` relation, then loaded into the relation
    #ToDo: Success returns f"Successfully loaded {df.shape[0]} records for {statistics_source.statistics_source_name} for FY {fiscal_year} into the database."
    pass


#Section: Upload and Download Nonstandard Usage File
@pytest.mark.dependency()
def test_upload_nonstandard_usage_file(engine, client, path_to_sample_file, non_COUNTER_AUCT_object_before_upload, remove_file_from_S3, caplog):  # `remove_file_from_S3()` not called but used to remove file loaded during test
    """Test uploading a file with non-COUNTER usage statistics to S3 and updating the AUCT relation accordingly."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self.upload_nonstandard_usage_file()`
    caplog.set_level(logging.INFO, logger='botocore')

    with client:  # `client` fixture results from `test_client()` method, without which, the error `RuntimeError: No application found.` is raised; using the test client as a solution for this error comes from https://stackoverflow.com/a/67314104
        upload_result = non_COUNTER_AUCT_object_before_upload.upload_nonstandard_usage_file(path_to_sample_file)
    upload_result = re.fullmatch(r'Successfully uploaded `(.*)` to S3 and updated `annualUsageCollectionTracking.usage_file_path` with complete S3 file name.', string=upload_result)
    log.info(f"`upload_result.group(0)` is {upload_result.group(0)} (type {type(upload_result.group(0))})")
    log.info(f"`upload_result.group(1)` is {upload_result.group(1)} (type {type(upload_result.group(1))})")

    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}",
    )
    log.info(f"`list_objects_response`:\n{list_objects_response}")
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET}", "") for file_name in bucket_contents]
    log.info(f"`bucket_contents`:\n{bucket_contents}")

    usage_file_path_in_database = pd.read_sql(
        sql=f"SELECT usage_file_path FROM annualUsageCollectionTracking WHERE AUCT_statistics_source = {non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source} AND AUCT_fiscal_year = {non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year};",
        con=engine,
    )
    usage_file_path_in_database = usage_file_path_in_database.iloc[0][0]
    log.info(f"`usage_file_path_in_database` is {usage_file_path_in_database} (type {type(usage_file_path_in_database)})")

    assert upload_result is not None
    assert f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{path_to_sample_file.suffix}" in bucket_contents
    #ToDo: assert usage_file_path_in_database == file_for_IO


def test_download_nonstandard_usage_file(non_COUNTER_AUCT_object_after_upload, non_COUNTER_file_to_download_from_S3, caplog):  # `non_COUNTER_file_to_download_from_S3()` not called but used to create and remove file from S3 for tests
    """Test downloading a file in S3 to a local computer."""
    #caplog.set_level(logging.INFO, logger='botocore')

    log.info(f"`non_COUNTER_AUCT_object_after_upload` is {non_COUNTER_AUCT_object_after_upload}")
    #TEST: `non_COUNTER_AUCT_object_after_upload` is <'AUCT_statistics_source': '11', 'AUCT_fiscal_year': '3', 'usage_is_being_collected': '1', 'manual_collection_required': '1', 'collection_via_email': '0', 'is_COUNTER_compliant': '0', 'collection_status': 'Collection complete', 'usage_file_path': 'raw-vendor-reports/11_3.csv', 'notes': 'None'>
    #TEST: `non_COUNTER_AUCT_object_after_upload` is <'AUCT_statistics_source': '11', 'AUCT_fiscal_year': '2', 'usage_is_being_collected': '1', 'manual_collection_required': '1', 'collection_via_email': '0', 'is_COUNTER_compliant': '0', 'collection_status': 'Collection complete', 'usage_file_path': 'raw-vendor-reports/11_2.csv', 'notes': 'This is the first FY with usage statistics'>
    log.info(f"`Path(__file__).parent` contents in `test_download_nonstandard_usage_file()` before method call:\n{[file_path for file_path in Path(__file__).parent.iterdir()]}")
    file_path = non_COUNTER_AUCT_object_after_upload.download_nonstandard_usage_file(Path(__file__).parent)
    #TEST: FileNotFoundError: [Errno 2] No such file or directory: 'raw-vendor-reports/11_2.csv.F1578cF1'
    #TEST: FileNotFoundError: [Errno 2] No such file or directory: 'raw-vendor-reports/11_3.csv.a945F004'
    log.info(f"`Path(__file__).parent` contents in `test_download_nonstandard_usage_file()` after method call:\n{[file_path for file_path in Path(__file__).parent.iterdir()]}")
    log.info(f"`file_path` in `test_download_nonstandard_usage_file()` is {file_path} (type {type(file_path)})")
    #ToDo: `file_path`, aka the absolute path to which the file will be downloaded, should be the same as the original uploaded file with the parameters above
    pass