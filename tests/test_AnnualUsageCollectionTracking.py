"""Tests the methods in AnnualUsageCollectionTracking."""
########## Passing 2023-09-08 ##########

import pytest
import logging
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from conftest import match_direct_SUSHI_harvest_result
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
    record = pd.read_sql(
        sql=f"SELECT * FROM annualUsageCollectionTracking JOIN statisticsSources ON statisticsSources.statistics_source_ID=annualUsageCollectionTracking.AUCT_statistics_source WHERE statisticsSources.statistics_source_retrieval_code IS NOT NULL;",
        con=engine,
    ).sample().reset_index()
    yield_object = AnnualUsageCollectionTracking(
        AUCT_statistics_source=record.at[0,'AUCT_statistics_source'],
        AUCT_fiscal_year=record.at[0,'AUCT_fiscal_year'],
        usage_is_being_collected=record.at[0,'usage_is_being_collected'],
        manual_collection_required=record.at[0,'manual_collection_required'],
        collection_via_email=record.at[0,'collection_via_email'],
        is_COUNTER_compliant=record.at[0,'is_COUNTER_compliant'],
        collection_status=record.at[0,'collection_status'],
        usage_file_path=record.at[0,'usage_file_path'],
        notes=record.at[0,'notes'],
    )
    log.info(f"`AUCT_fixture_for_SUSHI()` returning {yield_object}.")
    yield yield_object


@pytest.fixture  # Since this fixture is only called once, there's no functional difference between setting it at a function scope and setting it at a module scope
def harvest_R5_SUSHI_result(engine, AUCT_fixture_for_SUSHI, caplog):
    """A fixture with the result of all the SUSHI calls that will be made in `test_collect_annual_usage_statistics()`.

    The `AnnualUsageCollectionTracking.collect_annual_usage_statistics()` method loads the data collected by the SUSHI call made to the designated statistics source for the dates indicated by the fiscal year into the database. To confirm that the data was loaded successfully, a copy of the data that was loaded is needed for comparison. This fixture yields the same dataframe that `AnnualUsageCollectionTracking.collect_annual_usage_statistics()` loads into the database by calling `StatisticsSources._harvest_R5_SUSHI()`, just like the method being tested. Because the method being tested calls the method featured in this fixture, both methods being called in the same test function outputs two nearly identical collections of logging statements in the log of a single test; placing `StatisticsSources._harvest_R5_SUSHI()` in a fixture separates its log from that of `AnnualUsageCollectionTracking.collect_annual_usage_statistics()`.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        AUCT_fixture_for_SUSHI (nolcat.models.AnnualUsageCollectionTracking): a class instantiation via fixture used to get the necessary data to make a real SUSHI call
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime

    Yields:
        dataframe: a dataframe containing all of the R5 COUNTER data
    """
    caplog.set_level(logging.ERROR, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()`
    caplog.set_level(logging.ERROR, logger='nolcat.app')  # For `upload_file_to_S3_bucket()` called in `SUSHICallAndResponse.make_SUSHI_call()` and `self._harvest_single_report()`
    caplog.set_level(logging.ERROR, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()`
    caplog.set_level(logging.ERROR, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()`

    record = pd.read_sql(
        sql=f"""
            SELECT
                fiscalYears.start_date,
                fiscalYears.end_date,
                statisticsSources.statistics_source_ID,
                statisticsSources.statistics_source_name,
                statisticsSources.statistics_source_retrieval_code,
                statisticsSources.vendor_ID
            FROM annualUsageCollectionTracking
                JOIN statisticsSources ON statisticsSources.statistics_source_ID=annualUsageCollectionTracking.AUCT_statistics_source
                JOIN fiscalYears ON fiscalYears.fiscal_year_ID=annualUsageCollectionTracking.AUCT_fiscal_year
            WHERE
                annualUsageCollectionTracking.AUCT_statistics_source={AUCT_fixture_for_SUSHI.AUCT_statistics_source}
                AND annualUsageCollectionTracking.AUCT_fiscal_year={AUCT_fixture_for_SUSHI.AUCT_fiscal_year};
        """,
        con=engine,
    )
    
    start_date = record.at[0,'start_date']
    end_date = record.at[0,'end_date']
    StatisticsSources_object = StatisticsSources(  # Even with one value, the field of a single-record dataframe is still considered a series, making type juggling necessary
        statistics_source_ID = int(record.at[0,'statistics_source_ID']),
        statistics_source_name = str(record.at[0,'statistics_source_name']),
        statistics_source_retrieval_code = str(record.at[0,'statistics_source_retrieval_code']).split(".")[0],  # String created is of a float (aka `n.0`), so the decimal and everything after it need to be removed
        vendor_ID = int(record.at[0,'vendor_ID']),
    )
    log.debug(f"`harvest_R5_SUSHI_result()` fixture using StatisticsSources object {StatisticsSources_object}, start date {start_date} (type {type(start_date)}) and end date {end_date} (type {type(end_date)}).")
    yield StatisticsSources_object._harvest_R5_SUSHI(start_date, end_date)


def test_collect_annual_usage_statistics(engine, client, AUCT_fixture_for_SUSHI, harvest_R5_SUSHI_result, caplog):
    """Test calling the `StatisticsSources._harvest_R5_SUSHI()` method for the record's StatisticsSources instance with arguments taken from the record's FiscalYears instance.
    
    The `harvest_R5_SUSHI_result` fixture contains the same data that the method being tested should've loaded into the database, so it is used to see if the test passes. There isn't a good way to review the flash messages returned by the method from a testing perspective.
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`

    with client:  # `client` fixture results from `test_client()` method, without which, the error `RuntimeError: No application found.` is raised; using the test client as a solution for this error comes from https://stackoverflow.com/a/67314104
        method_response = AUCT_fixture_for_SUSHI.collect_annual_usage_statistics()
    method_response_match_object = re.match(r'Successfully loaded (\d*) records for .* for FY \d{4} into the database.', string=method_response[0])
    assert method_response_match_object is not None  # The test fails at this point because a failing condition here raises errors below

    database_update_check = pd.read_sql(
        sql=f"SELECT collection_status FROM annualUsageCollectionTracking WHERE annualUsageCollectionTracking.AUCT_statistics_source={AUCT_fixture_for_SUSHI.AUCT_statistics_source} AND annualUsageCollectionTracking.AUCT_fiscal_year={AUCT_fixture_for_SUSHI.AUCT_fiscal_year};",
        con=engine,
    )
    database_update_check = database_update_check.iloc[0][0]

    records_loaded_by_method = match_direct_SUSHI_harvest_result(method_response_match_object.group(1))
    try:
        log.info(f"Differences:\n{records_loaded_by_method.compare(harvest_R5_SUSHI_result[records_loaded_by_method.columns.to_list()])}")
        #TEST: Test this is based on is failing because rows are out of order--above shows metric and number pairs are the same but on different rows--below shows possible fix options as output
        r1 = records_loaded_by_method.reset_index()
        r2 = harvest_R5_SUSHI_result.reset_index()
        log.info(f"Differences after the indexes are reset:\n{r1.compare(r2[r1.columns.to_list()])}")
        s2 = harvest_R5_SUSHI_result.sort_values(
            by=records_loaded_by_method.columns.to_list(),
            ignore_index=True,
        )
        s1 = records_loaded_by_method.sort_values(
            by=records_loaded_by_method.columns.to_list(),
            ignore_index=True,
        )
        log.info(f"Differences after sorting by all fields:\n{s1.compare(s2[s1.columns.to_list()])}")
    except:
        log.info(f"Dataframe from database has index {records_loaded_by_method.index} and fields\n{return_string_of_dataframe_info(records_loaded_by_method)}")
        log.info(f"Dataframe from SUSHI has index {harvest_R5_SUSHI_result.index} and fields\n{return_string_of_dataframe_info(harvest_R5_SUSHI_result[records_loaded_by_method.columns.to_list()])}")
    
    assert database_update_check == "Collection complete"
    assert_frame_equal(records_loaded_by_method, harvest_R5_SUSHI_result, check_like=True)  # `check_like` argument allows test to pass if fields aren't in the same order


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
    #ToDo: Add `assert f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{path_to_sample_file.suffix}" == usage_file_path_in_database` when database update and delete in method is completed


def test_download_nonstandard_usage_file(non_COUNTER_AUCT_object_after_upload, non_COUNTER_file_to_download_from_S3, download_destination, caplog):  # `non_COUNTER_file_to_download_from_S3()` not called but used to create and remove file from S3 for tests
    """Test downloading a file in S3 to a local computer."""
    caplog.set_level(logging.INFO, logger='botocore')

    log.info(f"`non_COUNTER_AUCT_object_after_upload` is {non_COUNTER_AUCT_object_after_upload}")
    log.debug(f"Download destination contents in `test_download_nonstandard_usage_file()` before method call:\n{[file_path for file_path in download_destination.iterdir()]}")
    file_path = non_COUNTER_AUCT_object_after_upload.download_nonstandard_usage_file(download_destination)
    log.debug(f"Download destination contents in `test_download_nonstandard_usage_file()` after method call:\n{[file_path for file_path in download_destination.iterdir()]}")
    assert file_path.stem == f"{non_COUNTER_AUCT_object_after_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_after_upload.AUCT_fiscal_year}"
    assert file_path.is_file()