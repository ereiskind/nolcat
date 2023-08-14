"""Tests the methods in AnnualUsageCollectionTracking."""
########## No tests written 2023-08-11 ##########

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
@pytest.fixture(scope='module')
def choose_AUCT_PKs():
    """Chooses the `StatisticsSources.statistics_source_ID`, file name, and note value to use in the subsequent tests.
    
    Yields:
        tuple: a `StatisticsSources.statistics_source_ID`, file name, and note value
    """
    yield choice([
        (2, f"11_2.csv", "This is the first FY with usage statistics"),
        (3, f"11_3.csv", None),
        (4, f"11_4.csv", None),
    ])


@pytest.fixture(scope='module')
def AUCT_fixture_for_file_IO(choose_AUCT_PKs):
    """Creates an `AnnualUsageCollectionTracking` object with the data from `choose_AUCT_PKs()`.

    Args:
        choose_AUCT_PKs (tuple): a `StatisticsSources.statistics_source_ID`, file name, and note value
    
    Yields:
        nolcat.models.AnnualUsageCollectionTracking: an AnnualUsageCollectionTracking object corresponding to a record with a non-null `usage_file_path` attribute
    """
    yield AnnualUsageCollectionTracking(
        AUCT_statistics_source=11,
        AUCT_fiscal_year=choose_AUCT_PKs[0],
        usage_is_being_collected=True,
        manual_collection_required=True,
        collection_via_email=False,
        is_COUNTER_compliant=False,
        collection_status="Collection complete",
        usage_file_path=f"test_{choose_AUCT_PKs[1]}",  # All uses of the attribute include the prefix, so the class object is initialized with it
        notes=choose_AUCT_PKs[2],
    )


@pytest.fixture
def file_for_IO(AUCT_fixture_for_file_IO):
    """Creates a file that can be used in `test_upload_nonstandard_usage_file()` and `test_download_nonstandard_usage_file()`.
    
    The test file is saved to NoLCAT's `tests` folder instead of pytest's temporary folder because the file path for the test file needs to be passed to a function outside the testing module.

    Args:
        AUCT_fixture_for_file_IO (nolcat.models.AnnualUsageCollectionTracking): an AnnualUsageCollectionTracking object corresponding to a record with a non-null `usage_file_path` attribute

    Yields:
        #ToDo: Should it just be the `usage_file_path` attribute as pathlib.Path, the absolute file path in the container as pathlib.Path, the S3 file name as a string, or a tuple with some combination of the previous?
    """
    df=pd.DataFrame()
    df.to_csv(
        Path(__file__).parent / AUCT_fixture_for_file_IO.usage_file_path,
        encoding='utf-8',
        errors='backslashreplace',
    )
    log.info(f"Return value of `file_for_IO()` is {PATH_WITHIN_BUCKET + AUCT_fixture_for_file_IO.usage_file_path} (type {type(PATH_WITHIN_BUCKET + AUCT_fixture_for_file_IO.usage_file_path)})")
    yield PATH_WITHIN_BUCKET + AUCT_fixture_for_file_IO.usage_file_path  # The fixture returns the name of the file in S3 for use in determining its successful upload

    #ToDo: try:
    #ToDo:     s3_client.delete_object(
    #ToDo:         Bucket=BUCKET_NAME,
    #ToDo:         Key=PATH_WITHIN_BUCKET + AUCT_fixture_for_file_IO.usage_file_path
    #ToDo:     )
    #ToDo: except botocore.exceptions as error:
    #ToDo:     log.error(f"Trying to remove the test data files from the S3 bucket raised {error}.")
    #ToDo: Path(Path(__file__).parent / AUCT_fixture_for_file_IO.usage_file_path).unlink()


@pytest.fixture
def file_for_S3(tmp_path, AUCT_fixture_for_file_IO):
    """Creates a file that can be used in `test_download_nonstandard_usage_file()`.

    Args:
        tmp_path (pathlib.Path): a temporary directory created just for running tests
        AUCT_fixture_for_file_IO (nolcat.models.AnnualUsageCollectionTracking): an AnnualUsageCollectionTracking object corresponding to a record with a non-null `usage_file_path` attribute

    Yields:
        str: complete name of file in S3, including the bucket name
    """
    df=pd.DataFrame()
    df.to_csv(
        tmp_path / AUCT_fixture_for_file_IO.usage_file_path,
        encoding='utf-8',
        errors='backslashreplace',
    )
    S3_file_name = f"{BUCKET_NAME}/{PATH_WITHIN_BUCKET}test_{AUCT_fixture_for_file_IO.usage_file_path}"  # The prefix will allow filtering that prevents the test from failing
    upload_file_to_S3_bucket(
        tmp_path / AUCT_fixture_for_file_IO.usage_file_path,
        S3_file_name,
    )
    log.info(f"Yield value of `file_for_S3()` is {S3_file_name} (type {type(S3_file_name)})")
    yield S3_file_name

    #try:
    #    s3_client.delete_object(
    #        Bucket=BUCKET_NAME,
    #        Key=f"{PATH_WITHIN_BUCKET}test_{AUCT_fixture_for_file_IO.usage_file_path}"
    #    )
    #except botocore.exceptions as error:
    #    log.error(f"Trying to remove the test data files from the S3 bucket raised {error}.")


@pytest.mark.dependency()
def test_upload_nonstandard_usage_file(engine, client, AUCT_fixture_for_file_IO, file_for_IO, caplog):
    """Test uploading a file with non-COUNTER usage statistics to S3 and updating the AUCT relation accordingly.
    
    The `file_for_IO()` fixture is included as an argument because it needs to run before this test, as that fixture creates a file needed by this test.
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `upload_file_to_S3_bucket()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self.upload_nonstandard_usage_file()`
    caplog.set_level(logging.INFO, logger='botocore')

    test_file_path = Path(__file__).parent / AUCT_fixture_for_file_IO.usage_file_path
    log.info(f"`test_file_path` is {test_file_path} (type {type(test_file_path)})")
    with client:  # `client` fixture results from `test_client()` method, without which, the error `RuntimeError: No application found.` is raised; using the test client as a solution for this error comes from https://stackoverflow.com/a/67314104
        upload_result = AUCT_fixture_for_file_IO.upload_nonstandard_usage_file(test_file_path)
    upload_result = re.fullmatch(r'Successfully uploaded `(.*)` to S3 and updated `annualUsageCollectionTracking.usage_file_path` with complete S3 file name.', string=upload_result)
    log.info(f"`upload_result.group(0)` is {upload_result.group(0)} (type {type(upload_result.group(0))})")
    log.info(f"`upload_result.group(1)` is {upload_result.group(1)} (type {type(upload_result.group(1))})")

    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{PATH_WITHIN_BUCKET}test_",
    )
    log.info(f"`list_objects_response`:\n{list_objects_response}")
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    log.info(f"`bucket_contents`:\n{bucket_contents}")
    #ToDo: Confirm `file_for_IO` is name of file being looked for

    usage_file_path_in_database = pd.read_sql(
        sql=f"SELECT usage_file_path FROM annualUsageCollectionTracking WHERE AUCT_statistics_source = {AUCT_fixture_for_file_IO.AUCT_statistics_source} AND AUCT_fiscal_year = {AUCT_fixture_for_file_IO.AUCT_fiscal_year};",
        con=engine,
    )
    usage_file_path_in_database = usage_file_path_in_database.iloc[0][0]
    log.info(f"`usage_file_path_in_database` is {usage_file_path_in_database} (type {type(usage_file_path_in_database)})")

    assert upload_result is not None
    #ToDo: assert file_for_IO in bucket_contents
    #ToDo: assert usage_file_path_in_database == file_for_IO


def test_download_nonstandard_usage_file(AUCT_fixture_for_file_IO, file_for_S3, caplog):
    """Test downloading a file in S3 to a local computer."""
    caplog.set_level(logging.INFO, logger='botocore')

    log.info(f"`file_for_IO` is {file_for_IO}")
    log.info(f"`Path(__file__).parent` contents in `test_download_nonstandard_usage_file()` before method call:\n{[file_path for file_path in Path(__file__).parent.iterdir()]}")
    file_path = AUCT_fixture_for_file_IO.download_nonstandard_usage_file(Path(__file__).parent)
    log.info(f"`Path(__file__).parent` contents in `test_download_nonstandard_usage_file()` after method call:\n{[file_path for file_path in Path(__file__).parent.iterdir()]}")
    log.info(f"`file_path` in `test_download_nonstandard_usage_file()` is {file_path} (type {type(file_path)})")
    #ToDo: `file_path`, aka the absolute path to which the file will be downloaded, should be the same as the original uploaded file with the parameters above
    pass