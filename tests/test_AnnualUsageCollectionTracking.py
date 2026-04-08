"""Tests the methods in AnnualUsageCollectionTracking."""
########## Passing 2026-03-20 ##########

import pytest
from filecmp import cmp
from urllib.parse import urlsplit
from pandas.testing import assert_frame_equal
from werkzeug.datastructures import FileStorage

# `conftest.py` fixtures are imported automatically
from conftest import match_direct_SUSHI_harvest_result
from nolcat.models import *

log = logging.getLogger(__name__)


#Section: Collecting Annual COUNTER Usage Statistics
@pytest.fixture(scope='module')
def AUCT_fixture_for_SUSHI(engine):
    """Creates an `AnnualUsageCollectionTracking` object with a non-null `StatisticsSources.statistics_source_retrieval_code` value.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    
    Yields:
        nolcat.models.AnnualUsageCollectionTracking: an AnnualUsageCollectionTracking object corresponding to a record with a non-null `statistics_source_retrieval_code` attribute
    """
    # Cannot use `caplog` for `query_database()` due to scope mismatch
    record = query_database(
        query=f"SELECT * FROM annualUsageCollectionTracking JOIN statisticsSources ON statisticsSources.statistics_source_ID=annualUsageCollectionTracking.AUCT_statistics_source WHERE statisticsSources.statistics_source_retrieval_code IS NOT NULL;",
        engine=engine,
    )
    if isinstance(record, str):  #ALERT: `except DatabaseInteractionError`
        pytest.skip(database_function_skip_statements(record, False))
    record = record.sample().reset_index()
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
    log.warning(initialize_relation_class_object_statement("AnnualUsageCollectionTracking", yield_object))  # This is set at `warning` to show the retrieval code
    yield yield_object


@pytest.mark.slow
def test_collect_annual_usage_statistics(engine, client, AUCT_fixture_for_SUSHI, caplog):
    """Test calling the `StatisticsSources._harvest_R5_SUSHI()` method for the record's StatisticsSources instance with arguments taken from the record's FiscalYears instance.
    
    This test's module focuses on the `annualUsageCollectionTracking` relation, and thus this test focuses on the change to that relation made in the `nolcat.models.AnnualUsageCollectionTracking.collect_annual_usage_statistics()` method. The content of the upload(s) to S3 are not part of this test.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        client (flask.testing.FlaskClient): a Flask test client
        AUCT_fixture_for_SUSHI (nolcat.models.AnnualUsageCollectionTracking): a class instantiation via fixture used to get the necessary data to make a real SUSHI call
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    """
    caplog.set_level(logging.INFO, logger='nolcat.nolcat_glue_job')
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')

    with client:
        flash_message_dict = AUCT_fixture_for_SUSHI.collect_annual_usage_statistics(bucket_path=TEST_COUNTER_FILE_PATH)
    log.debug(f"The `collect_annual_usage_statistics()` response:\n{format_list_for_stdout(flash_message_dict)}")
    assert isinstance(flash_message_dict, dict)

    database_update_check = query_database(
        query=f"SELECT collection_status FROM annualUsageCollectionTracking WHERE annualUsageCollectionTracking.AUCT_statistics_source={AUCT_fixture_for_SUSHI.AUCT_statistics_source} AND annualUsageCollectionTracking.AUCT_fiscal_year={AUCT_fixture_for_SUSHI.AUCT_fiscal_year};",
        engine=engine,
    )
    if isinstance(database_update_check, str):  #ALERT: `except DatabaseInteractionError`
        pytest.skip(database_function_skip_statements(database_update_check))
    database_update_check = extract_value_from_single_value_df(database_update_check, False)
    assert database_update_check == "Collection complete"


#Section: Upload and Download Nonstandard Usage File
@pytest.fixture
def sample_FileStorage_object(path_to_sample_file):
    """Creates a Werkzeug FileStorage object for use in testing the `AnnualUsageCollectionTracking.upload_nonstandard_usage_file()` method.
    
    The AnnualUsageCollectionTracking.upload_nonstandard_usage_file()` method takes a Werkzeug FileStorage object; the `mock_FileStorage_object` class was devised to simulate such objects.

    Args:
        path_to_sample_file (pathlib.Path): an absolute file path to a randomly selected file

    Yields:
        werkzeug.datastructures.FileStorage: a file in a Werkzeug FileStorage object
    """
    open_file_stream = open(path_to_sample_file, 'rb')  # Opening the JSON as text raises `TypeError: a bytes-like object is required, not 'str'` on the `werkzeug.datastructures.FileStorage.save()` method 
    yield FileStorage(
        stream=open_file_stream,
        filename=path_to_sample_file.absolute(),
    )
    open_file_stream.close()


@pytest.mark.dependency()
def test_upload_nonstandard_usage_file(engine, client, tmp_path, sample_FileStorage_object, non_COUNTER_AUCT_object_before_upload, path_to_sample_file):
    """Test uploading a file with non-COUNTER usage statistics to S3 and updating the AUCT relation accordingly.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        client (flask.testing.FlaskClient): a Flask test client
        tmp_path (pathlib.Path): a temporary directory created just for running tests
        sample_FileStorage_object (werkzeug.datastructures.FileStorage): a file in a Werkzeug FileStorage object
        non_COUNTER_AUCT_object_before_upload (nolcat.models.AnnualUsageCollectionTracking): an AnnualUsageCollectionTracking object corresponding to a record which can have a non-COUNTER usage file uploaded
        path_to_sample_file (pathlib.Path): an absolute file path to a randomly selected file
    """
    file_name = f"{non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year}{Path(sample_FileStorage_object.filename).suffix}"
    with client:
        S3_file_name = non_COUNTER_AUCT_object_before_upload.upload_nonstandard_usage_file(sample_FileStorage_object, bucket_path=TEST_NON_COUNTER_FILE_PATH)

    download_location = tmp_path / file_name
    s3_client.download_file(
        Bucket=BUCKET_NAME,
        Key=S3_file_name.key,
        Filename=download_location,
    )
    assert cmp(path_to_sample_file, download_location)

    usage_file_path_in_database = query_database(
        query=f"SELECT usage_file_path FROM annualUsageCollectionTracking WHERE AUCT_statistics_source={non_COUNTER_AUCT_object_before_upload.AUCT_statistics_source} AND AUCT_fiscal_year={non_COUNTER_AUCT_object_before_upload.AUCT_fiscal_year};",
        engine=engine,
    )
    if isinstance(usage_file_path_in_database, str):  #ALERT: `except DatabaseInteractionError`
        pytest.skip(database_function_skip_statements(usage_file_path_in_database))
    usage_file_path_in_database = extract_value_from_single_value_df(usage_file_path_in_database)
    log.debug(return_value_from_query_statement(usage_file_path_in_database))
    assert file_name == usage_file_path_in_database


@pytest.mark.skip("Function needs to be updated for switch to CloudPath.")  #TEST: temp--Active on 2026-03-20
def test_download_nonstandard_usage_file(non_COUNTER_AUCT_object_after_upload, non_COUNTER_file_to_download_from_S3, download_destination):
    """Test downloading a file in S3 to a local computer.

    Args:
        non_COUNTER_AUCT_object_after_upload (nolcat.models.AnnualUsageCollectionTracking): an AnnualUsageCollectionTracking object corresponding to a record with a non-null `usage_file_path` attribute
        non_COUNTER_file_to_download_from_S3 (pathlib.Path): an absolute file path to a randomly selected file that's also been temporarily uploaded to S3
        download_destination (pathlib.Path): a path to the destination for downloaded files
    """
    log.debug(f"Before `download_nonstandard_usage_file()`," + list_folder_contents_statement(download_destination, False))
    file_path = non_COUNTER_AUCT_object_after_upload.download_nonstandard_usage_file(
        download_destination,
        bucket_path=TEST_NON_COUNTER_FILE_PATH,
        )
    log.debug(f"After `download_nonstandard_usage_file()`," + list_folder_contents_statement(download_destination, False))
    assert file_path.stem == f"{non_COUNTER_AUCT_object_after_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_after_upload.AUCT_fiscal_year}"
    assert file_path.is_file()
    assert cmp(file_path, non_COUNTER_file_to_download_from_S3)  # The file uploaded to S3 for the test and the downloaded file are the same