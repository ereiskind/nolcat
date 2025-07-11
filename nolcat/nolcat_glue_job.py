from datetime import date
import calendar
import io
from itertools import product
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import boto3
import pandas as pd
from numpy import squeeze
from sqlalchemy import text

from .logging_config import *

"""Since GitHub is used to manage the code, and the repo is public, secret information is stored in a file named `nolcat_secrets.py` exclusive to the Docker container and imported into this file.

The overall structure of this app doesn't facilitate a separate module for a SQLAlchemy `create_engine` function: when `nolcat/__init__.py` is present, keeping these functions in a separate module and importing them causes a ``ModuleNotFoundError: No module named 'database_connectors'`` error when starting up the Flask server, but with no `__init__` file, the blueprint folder imports don't work. With Flask-SQLAlchemy, a string for the config variable `SQLALCHEMY_DATABASE_URI` is all that's needed, so the data the string needs are imported from a `nolcat_secrets.py` file saved to Docker and added to this directory during the build process. This import has been problematic; moving the file from the top-level directory to this directory and providing multiple possible import statements in try-except blocks are used to handle the problem.
"""
try:
    import nolcat_secrets as secrets
except:
    try:
        from . import nolcat_secrets as secrets
    except:
        try:
            from nolcat import nolcat_secrets as secrets
        except:
            print("None of the provided import statements for `nolcat\\nolcat_secrets.py` worked.")

DATABASE_USERNAME = secrets.Username
DATABASE_PASSWORD = secrets.Password
DATABASE_HOST = secrets.Host
DATABASE_PORT = secrets.Port
DATABASE_SCHEMA_NAME = secrets.Database
SECRET_KEY = secrets.Secret
BUCKET_NAME = secrets.Bucket
TOP_NOLCAT_DIRECTORY = Path(*Path(__file__).parts[0:Path(__file__).parts.index('nolcat')+1])

PRODUCTION_COUNTER_FILE_PATH = "nolcat/usage/"
PRODUCTION_NON_COUNTER_FILE_PATH = "nolcat/usage/raw_vendor_reports/"
TEST_COUNTER_FILE_PATH = "nolcat/usage/test/"
TEST_NON_COUNTER_FILE_PATH = "nolcat/usage/test/raw_vendor_reports/"
PATH_WITHIN_BUCKET = "raw-vendor-reports/"  #ToDo: The location of files within a S3 bucket isn't sensitive information; should it be included in the "nolcat_secrets.py" file?
PATH_WITHIN_BUCKET_FOR_TESTS = PATH_WITHIN_BUCKET + "tests/"

csrf = CSRFProtect()
db = SQLAlchemy()
s3_client = boto3.client('s3')  # Authentication is done through a CloudFormation init file

log = logging.getLogger(__name__)


#SECTION: Basic Helper Functions
def last_day_of_month(original_date):
    """The function for returning the last day of a given month.

    When COUNTER date ranges include the day, the "End_Date" value needs to be the last day of the month. This function facilitates finding that last day while combining two previously existing functions, both named `last_day_of_month`: one accepting and returning datetime.date objects, the other getting pd.Timestamp objects and returning strings for use in pandas `map` functions.

    Args:
        original_date (datetime.date or pd.Timestamp): the original date; if from a dataframe, the dataframe of origin will have the date in a datetime64[ns] data type, but within this function, the data type is Timestamp
    
    Returns:
        datetime.date: the last day of the month
        str: the last day of the given month in ISO format
    """
    if isinstance(original_date, date):
        return date(
            original_date.year,
            original_date.month,
            calendar.monthrange(original_date.year, original_date.month)[1],
        )
    elif isinstance(original_date, pd.Timestamp):
        year_and_month_string = original_date.date().isoformat()[0:-2]  # Returns an ISO date string, then takes off the last two digits
        return year_and_month_string + str(original_date.days_in_month)
'''
Called in `nolcat.models.StatisticsSources._harvest_R5_SUSHI()` via `nolcat.models.StatisticsSources._harvest_single_report()` after calls to `SUSHICallAndResponse`
    Called in test `tests.test_StatisticsSources.test_harvest_R5_SUSHI()`
    Called in test `tests.test_StatisticsSources.test_harvest_R5_SUSHI_with_report_to_harvest()`
    Called in test `tests.test_StatisticsSources.test_harvest_R5_SUSHI_with_invalid_dates()`  
    Called in `nolcat.models.AnnualUsageCollectionTracking.collect_annual_usage_statistics()`
        Called in test `tests.test_AnnualUsageCollectionTracking.test_collect_annual_usage_statistics()`
            Called in fixture `tests.test_AnnualUsageCollectionTracking.harvest_R5_SUSHI_result()` for `tests.test_AnnualUsageCollectionTracking.test_collect_annual_usage_statistics()`
    Called in `nolcat.models.StatisticsSources.collect_usage_statistics()`
        Called in test `tests.test_StatisticsSources.test_collect_usage_statistics()`
            Called in fixture `tests.test_StatisticsSources.harvest_R5_SUSHI_result()` for `tests.test_StatisticsSources.test_collect_usage_statistics()`
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> last_day_of_month
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> last_day_of_month
        test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> last_day_of_month
Called in `SUSHICallAndResponse` in non-fixture `tests.conftest.COUNTER_reports_offered_by_statistics_source()` via `tests.test_StatisticsSources.reports_offered_by_StatisticsSource_fixture()` via both `tests.test_StatisticsSources.StatisticsSources_fixture()` and `tests.test_StatisticsSources.SUSHI_credentials_fixture_in_test_StatisticsSources()` via `tests.test_StatisticsSources.most_recent_month_with_usage()`
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> most_recent_month_with_usage -> last_day_of_month
Called in `nolcat.models.StatisticsSources._harvest_single_report()` in loop designed to combine the output of multiple calls to `SUSHICallAndResponse`
    test_harvest_single_report -> _harvest_single_report -> last_day_of_month
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> last_day_of_month
Called in `SUSHICallAndResponse` in non-fixture `tests.conftest.COUNTER_reports_offered_by_statistics_source()` via `tests.test_SUSHICallAndResponse.list_of_reports()` via `tests.test_SUSHICallAndResponse.SUSHI_credentials_fixture()`
    test_PR_call_validity -> list_of_reports -> SUSHI_credentials_fixture_in_test_SUSHICallAndResponse -> last_day_of_month
    test_DR_call_validity -> list_of_reports -> SUSHI_credentials_fixture_in_test_SUSHICallAndResponse -> last_day_of_month
    test_TR_call_validity -> list_of_reports -> SUSHI_credentials_fixture_in_test_SUSHICallAndResponse -> last_day_of_month
    test_IR_call_validity -> list_of_reports -> SUSHI_credentials_fixture_in_test_SUSHICallAndResponse -> last_day_of_month
Called in `tests.test_bp_view_usage.start_query_wizard_form_data()` after a SQL query on relation `COUNTERData`
    test_start_query_wizard -> start_query_wizard_form_data -> last_day_of_month
    test_GET_query_wizard_sort_redirect -> start_query_wizard_form_data -> last_day_of_month

Make call function with call to database including or after `last_day_of_month`; check if `COUNTERData` relation is referenced
    test_harvest_R5_SUSHI -> most_recent_month_with_usage -> last_day_of_month
    test_check_if_data_in_database_no -> current_month_like_most_recent_month_with_usage -> last_day_of_month
    test_check_if_data_in_database_yes -> current_month_like_most_recent_month_with_usage -> last_day_of_month
'''


def ISSN_regex():
    """A regex object matching an ISSN.

    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"\d{4}\-\d{3}[\dxX]\s*")


def ISBN_regex():
    """A regex object matching an ISBN.

    Regex copied from https://stackoverflow.com/a/53482655.
    
    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"(978-?|979-?)?\d{1,5}-?\d{1,7}-?\d{1,6}-?\d{1,3}\s*")


def AWS_timestamp_format():
    """The `strftime()` format code to use with AWS names.

    ISO format cannot be used where AWS calls for datetimes--S3 file names can't contain colons, while Step Function execution names only accept alphanumeric characters, hyphens, and underscores.
    
    Returns:
        str: Python datetime format code
    """
    return '%Y-%m-%dT%H-%M-%S'
'''
Called in `nolcat.models.StatisticsSources._harvest_single_report()` after calls to both `SUSHICallAndResponse` and `ConvertJSONDictToDataframe`
    test_harvest_single_report -> _harvest_single_report -> AWS_timestamp_format | test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> AWS_timestamp_format | test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> AWS_timestamp_format | test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format | test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
    test_status_call -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_status_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_reports_call -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_reports_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_PR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_DR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_TR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_IR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
        test_call_with_invalid_credentials -> make_SUSHI_call -> _save_raw_Response_text -> AWS_timestamp_format
Called in fixture `tests.test_app.file_name_stem_and_data()` which is for `tests.test_app.test_save_unconverted_data_via_upload()`
'''


def non_COUNTER_file_name_regex():
    """A regex for the format of non-COUNTER usage files saved in S3.
    
    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"(\d+)_(\d{4})\.\w{3,4}")


def empty_string_regex():
    """A regex for matching empty strings and whitespace-only strings.

    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"^\s*$")


#SUBSECTION: Formatting Changes
def return_string_of_dataframe_info(df):
    """Returns the data output by `pandas.DataFrame.info()` as a string so the method can be used in logging statements.

    The `pandas.DataFrame.info()` method forgoes returning a value in favor of printing directly to stdout; as a result, it doesn't output anything when used in a logging statement. This function captures the data traditionally output directly to stdout in a string for use in a logging statement. This function is based off the one at https://stackoverflow.com/a/39440325.

    Args:
        df (dataframe): the dataframe in the logging statement
    
    Returns:
        str: the output of the `pandas.DataFrame.info()` method
    """
    in_memory_stream = io.StringIO()
    df.info(buf=in_memory_stream)
    return in_memory_stream.getvalue()


def format_list_for_stdout(stdout_list):
    """Changes a sequence into a string which places each item of the list on its own line.

    Using the list comprehension allows the function to accept generators, which are transformed into lists by the comprehension, and to handle both lists and generators with individual items that aren't strings by type juggling.

    Args:
        stdout_list (list or generator): a sequence for pretty printing to stdout
    
    Returns:
        str: the sequence contents with a line break between each item
    """
    if isinstance(stdout_list, dict):
        return '\n'.join([f"{k}: {v}" for k, v in stdout_list.items()])
    else:
        return '\n'.join([str(file_path) for file_path in stdout_list])
'''
Called in `nolcat.SUSHICallAndResponse._handle_SUSHI_exceptions()` in the return value
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_status_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_status_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_reports_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_reports_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_PR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_DR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_TR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_IR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
    test_call_with_invalid_credentials -> make_SUSHI_call -> _handle_SUSHI_exceptions -> format_list_for_stdout
'''


def remove_IDE_spacing_from_statement(statement):
    """Removes from a SQL statement the newlines and spaces used to for readability in the IDE.

    The `view_usage.views` module has route functions that add AND and GROUP BY clauses to SQL statements on new lines but without spaces in front; the non-regex lines are designed to remove those newlines.

    Args:
        statement (str): a SQL statement

    Returns:
        str: the same SQL statement on a single line without multi-space gaps
    """
    statement = " ".join(re.split(r"\n\s+", statement)).strip()
    statement = " AND ".join(statement.split("\nAND ")).strip()
    return " GROUP BY ".join(statement.split("\nGROUP BY ")).strip()
'''
Called in `nolcat.app.query_database()` and in return value if query fails
    add_access_stop_date -> update_database -> query_database -> remove_IDE_spacing_from_statement
        add_access_stop_date -> update_database -> remove_IDE_spacing_from_statement
    remove_access_stop_date -> update_database -> query_database -> remove_IDE_spacing_from_statement
        remove_access_stop_date -> update_database -> remove_IDE_spacing_from_statement
    change_StatisticsSource -> query_database -> remove_IDE_spacing_from_statement
        change_StatisticsSource -> update_database -> query_database -> remove_IDE_spacing_from_statement
        change_StatisticsSource -> update_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> match_direct_SUSHI_harvest_result -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> AUCT_fixture_for_SUSHI -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> AUCT_fixture_for_SUSHI -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> query_database -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> non_COUNTER_AUCT_object_before_upload -> query_database -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_download_nonstandard_usage_file -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
    test_download_nonstandard_usage_file -> non_COUNTER_file_to_download_from_S3 -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
    test_query_database -> query_database -> remove_IDE_spacing_from_statement
    test_loading_connected_data_into_other_relation -> query_database -> remove_IDE_spacing_from_statement
    test_first_new_PK_value -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_update_database -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_update_database -> query_database -> remove_IDE_spacing_from_statement
        test_update_database -> update_database -> remove_IDE_spacing_from_statement
        test_update_database_with_insert_statement -> query_database -> remove_IDE_spacing_from_statement
            test_update_database_with_insert_statement -> update_database -> query_database -> remove_IDE_spacing_from_statement
                test_update_database_with_insert_statement -> update_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_annual_stats_homepage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_annual_stats_homepage -> annual_stats_homepage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_annual_stats_homepage -> annual_stats_homepage -> show_fiscal_year_details -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_match_direct_SUSHI_harvest_result -> match_direct_SUSHI_harvest_result -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> non_COUNTER_AUCT_object_before_upload -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement
    test_run_custom_SQL_query -> run_custom_SQL_query -> query_database -> remove_IDE_spacing_from_statement
    test_use_predefined_SQL_query -> query_database -> remove_IDE_spacing_from_statement
    test_use_predefined_SQL_query -> use_predefined_SQL_query -> query_database -> remove_IDE_spacing_from_statement
    test_start_query_wizard -> start_query_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_GET_query_wizard_sort_redirect -> start_query_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_PR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_PR_query_with_wizard -> construct_PR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_DR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_DR_query_with_wizard -> construct_DR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_TR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_TR_query_with_wizard -> construct_TR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_IR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_IR_query_with_wizard -> construct_IR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_download_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_download_non_COUNTER_usage -> download_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_download_non_COUNTER_usage -> download_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_download_non_COUNTER_usage -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
    test_download_non_COUNTER_usage -> non_COUNTER_file_to_download_from_S3 -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_60b -> calculate_depreciated_ACRL_60b -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_60b -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_63 -> calculate_depreciated_ACRL_63 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_63 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61a -> calculate_ACRL_61a -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61a -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61b -> calculate_ACRL_61b -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61b -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_18 -> calculate_ARL_18 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_18 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_19 -> calculate_ARL_19 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_19 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_20 -> calculate_ARL_20 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_20 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_create_usage_tracking_records_for_fiscal_year -> query_database -> remove_IDE_spacing_from_statement
    test_create_usage_tracking_records_for_fiscal_year -> create_usage_tracking_records_for_fiscal_year -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_fiscal_year_usage_statistics -> update_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> FY2022_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_fetch_SUSHI_information_for_API -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> match_direct_SUSHI_harvest_result -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_already_in_COUNTERData -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_status_call -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_status_call -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_status_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_status_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_status_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_status_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_call_with_invalid_credentials -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.statements.database_update_fail_statement()` in return value
    add_access_stop_date -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    remove_access_stop_date -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    change_StatisticsSource -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
'''


def truncate_longer_lines(line):
    """Truncates any string longer than 150 characters at 150 characters.

    Args:
        line (str or bin): a string to possibly truncate
    
    Returns:
        str: a string of 150 characters at most
    """
    line = str(line)  # Type juggling in case the parameter value is a binary string
    if len(line) > 150:
        return line[:147] + "..."
    else:
        return line
'''
Called in `nolcat.app.update_database()` in return value if there was a problem with the update
    add_access_stop_date -> update_database -> truncate_longer_lines
    remove_access_stop_date -> update_database -> truncate_longer_lines
    change_StatisticsSource -> update_database -> truncate_longer_lines
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> truncate_longer_lines
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> truncate_longer_lines
    test_update_database -> update_database -> truncate_longer_lines
        test_update_database_with_insert_statement -> update_database -> truncate_longer_lines
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> truncate_longer_lines
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> truncate_longer_lines
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> truncate_longer_lines
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> truncate_longer_lines
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> truncate_longer_lines
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> truncate_longer_lines
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> truncate_longer_lines
    test_collect_fiscal_year_usage_statistics -> update_database -> truncate_longer_lines
        test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> truncate_longer_lines
'''


#SUBSECTION: SUSHI Statements and Regexes
def unable_to_convert_SUSHI_data_to_dataframe_statement(error_message, report_type=None, statistics_source_name=None):
    """This statement indicates that the provided COUNTER data couldn't be converted into a dataframe.

    Args:
        error_message (str): the error message returned by the attempt to convert the COUNTER data to a dataframe
        report_type (str, optional): the type of report for a SUSHI call; default is `None`
        statistics_source_name (str, optional): the name of the statistics source for a SUSHI call; default is `None`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if report_type and statistics_source_name:
        return f"Changing the JSON-like dictionary of {report_type} for {statistics_source_name} into a dataframe raised the error {error_message}."
    else:
        return f"Changing the uploaded COUNTER data workbooks into a dataframe raised the error {error_message}."
'''
Called in `nolcat.models.StatisticsSources._harvest_single_report()` in return value
    test_harvest_single_report -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> unable_to_convert_SUSHI_data_to_dataframe_statement
'''


def successful_SUSHI_call_statement(call_path, statistics_source_name):
    """This statement indicates a successful call to `SUSHICallAndResponse.make_SUSHI_call()`.

    Args:
        call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        statistics_source_name (str): the name of the statistics source
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"The call to the `{call_path}` endpoint for {statistics_source_name} was successful."


def harvest_R5_SUSHI_success_statement(statistics_source_name, number_of_records, fiscal_year=None):
    """This statement indicates a successful call to `StatisticsSources._harvest_R5_SUSHI()`.

    Args:
        statistics_source_name (str): the name of the statistics source
        number_of_records (int): the number of records found by `StatisticsSources._harvest_R5_SUSHI()`
        fiscal_year (str, optional): the fiscal year for the `StatisticsSources._harvest_R5_SUSHI()` call; default is `None`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if fiscal_year:
        return f"The SUSHI harvest for statistics source {statistics_source_name} for FY {fiscal_year} successfully found {number_of_records} records."
    else:
        return f"The SUSHI harvest for statistics source {statistics_source_name} successfully found {number_of_records} records."


def failed_SUSHI_call_statement(call_path, statistics_source_name, error_messages, SUSHI_error=True, no_usage_data=False, stop_API_calls=False):
    """This statement indicates a failed call to `SUSHICallAndResponse.make_SUSHI_call()`.

    Args:
        call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        statistics_source_name (str): the name of the statistics source
        error_messages (str): the message detailing the error(s) returned by `SUSHICallAndResponse.make_SUSHI_call()`
        SUSHI_error (bool, optional): indicates if the error is a SUSHI error handled by the program; default is `True`
        no_usage_data (bool, optional): indicates if the error indicates that there shouldn't be any usage data; default is `False`
        stop_API_calls (bool, optional): indicates if the error is stopping all SUSHI calls to the given statistics source; default is `False`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if '\n' in error_messages:
        error_messages = f"s\n{error_messages}\n"
    else:
        error_messages = f" {error_messages} "
    
    if SUSHI_error:
        main_value = f"The call to the `{call_path}` endpoint for {statistics_source_name} raised the SUSHI error{error_messages}"
    else:
        main_value = f"The call to the `{call_path}` endpoint for {statistics_source_name} raised the error{error_messages}"
    
    if no_usage_data:
        return f"{main_value[:-1]}, so the call returned no usage data."
    elif stop_API_calls:
        return main_value + f"API calls to {statistics_source_name} have stopped and no other calls will be made."
    else:
        return main_value[:-1]  # Removing the whitespace character at the end
'''
Called in `nolcat.models.StatisticsSources._harvest_R5_SUSHI()` in return value
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
            test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
            test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> failed_SUSHI_call_statement
Called in `nolcat.SUSHICallAndResponse.make_SUSHI_call()` in return value via `nolcat.models.StatisticsSources._harvest_R5_SUSHI()`
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> failed_SUSHI_call_statement
Called in `nolcat.SUSHICallAndResponse._convert_Response_to_JSON()` in return value in `nolcat.SUSHICallAndResponse.make_SUSHI_call()`
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_status_call -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_status_call_validity -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_reports_call -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_reports_call_validity -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_PR_call_validity -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_DR_call_validity -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_TR_call_validity -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_IR_call_validity -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
        test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _convert_Response_to_JSON -> failed_SUSHI_call_statement
Called in `nolcat.SUSHICallAndResponse.make_SUSHI_call()` in return value
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_status_call -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_status_call_validity -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_reports_call -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_reports_call_validity -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_PR_call_validity -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_DR_call_validity -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_TR_call_validity -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_IR_call_validity -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> failed_SUSHI_call_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> failed_SUSHI_call_statement
'''


def no_data_returned_by_SUSHI_statement(call_path, statistics_source_name, is_empty_string=False, has_Report_Items=True):
    """This statement indicates a SUSHI call that returned no usage data but didn't contain a SUSHI error explaining the lack of data

    Args:
        call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        statistics_source_name (str): the name of the statistics source
        is_empty_string (bool, optional): indicates if the SUSHI call returned an empty string; default is `False`
        has_Report_Items (bool, optional): indicates if the data returned by the SUSHI call had a `Report_Items` section; default is `True`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if is_empty_string:
        main_value = f"The call to the `{call_path}` endpoint for {statistics_source_name} returned no data"
    else:
        main_value = f"The call to the `{call_path}` endpoint for {statistics_source_name} returned no usage data"
    
    if has_Report_Items:
        return main_value + "."
    else:
        return main_value + " because the SUSHI data didn't have a `Report_Items` section."


def attempted_SUSHI_call_with_invalid_dates_statement(end_date, start_date):
    """This statement indicates an attempter SUSHI call with an invalid date range.

    Args:
        end_date (datetime.date): the given end date of the range
        start_date (datetime.date): the given start date of the range
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"The given end date of {end_date.strftime('%Y-%m-%d')} is before the given start date of {start_date.strftime('%Y-%m-%d')}, which will cause any SUSHI API calls to return errors; as a result, no SUSHI calls were made. Please correct the dates and try again."
'''
Called in `nolcat.models.StatisticsSources._harvest_R5_SUSHI()` in return value
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> attempted_SUSHI_call_with_invalid_dates_statement
Called in `assert` statement in test
    test_harvest_R5_SUSHI_with_invalid_dates -> attempted_SUSHI_call_with_invalid_dates_statement
'''


def reports_with_no_usage_regex():
    """This regex object matches the return statements in `no_data_returned_by_SUSHI_statement()` and `failed_SUSHI_call_statement()` that indicate no usage data was returned.

    In the pytest modules, the statements using this function are looking just for those SUSHI responses with neither data nor a SUSHI error, but this regex matches all return values that indicate no usage data was returned; having the `skip_test_due_to_SUSHI_error_regex()` comparison first in test functions means `failed_SUSHI_call_statement()` return values indicating no usage data are never compared to this regex.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.load_data_into_database()`
    """
    return re.compile(r"The call to the `.+` endpoint for .+ returned no (usage )?data( because the SUSHI data didn't have a `Report_Items` section)?\.")
'''
Called in `nolcat.models.StatisticsSources._harvest_single_report()`
    test_harvest_single_report -> _harvest_single_report -> reports_with_no_usage_regex
        test_harvest_single_report -> reports_with_no_usage_regex
        test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> reports_with_no_usage_regex
            test_harvest_single_report_with_partial_date_range -> reports_with_no_usage_regex
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> reports_with_no_usage_regex
Called in `nolcat.models.StatisticsSources._harvest_R5_SUSHI()`
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> reports_with_no_usage_regex
Called in `tests/test_SUSHICallAndResponse`
    test_status_call -> reports_with_no_usage_regex
    test_reports_call -> reports_with_no_usage_regex
    test_PR_call_validity -> reports_with_no_usage_regex
    test_DR_call_validity -> reports_with_no_usage_regex
    test_TR_call_validity -> reports_with_no_usage_regex
    test_IR_call_validity -> reports_with_no_usage_regex
'''


def skip_test_due_to_SUSHI_error_regex():
    """This regex object matches the return statements in `failed_SUSHI_call_statement()`.

    The `failed_SUSHI_call_statement()` return value can end so many different ways, so this regex is designed to capture the shared beginning of all those return statements and be used with the `re.match()` method.

    Returns:
        re.Pattern: the regex object for the success return statement for `failed_SUSHI_call_statement()`
    """
    return re.compile(r"The call to the `.+` endpoint for .+ raised the (SUSHI )?errors?")
'''
Called in `tests/test_SUSHICallAndResponse` to compare to `SUSHICallAndResponse.make_SUSHI_call()` return value
    test_harvest_single_report -> skip_test_due_to_SUSHI_error_regex
    test_harvest_single_report_with_partial_date_range -> skip_test_due_to_SUSHI_error_regex
    test_status_call -> skip_test_due_to_SUSHI_error_regex
    test_reports_call -> skip_test_due_to_SUSHI_error_regex
    test_PR_call_validity -> skip_test_due_to_SUSHI_error_regex
    test_DR_call_validity -> skip_test_due_to_SUSHI_error_regex
    test_TR_call_validity -> skip_test_due_to_SUSHI_error_regex
    test_IR_call_validity -> skip_test_due_to_SUSHI_error_regex
'''


#SUBSECTION: Testing and Error Statements
def fixture_variable_value_declaration_statement(variable_name, variable_value):
    """This statement adds the value of any arguments used in fixture functions to the logging output for troubleshooting purposes.

    Args:
        variable_name (str): the name of the argument/variable
        variable_value (object): the argument/variable value
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    if isinstance(variable_value, Path):
        return f"The `{variable_name}` is {variable_value.resolve()}."
    else:
        return f"The `{variable_name}` is {variable_value}."


def Flask_error_statement(error_statement):
    """This statement provides details on why the form couldn't be successfully submitted.

    Args:
        error_statement (dict): the error(s) returned by the form submission

    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"The form submission failed because of the following error(s):\n{'\n'.join([f"{k}: {v}" for k, v in error_statement.items()])}"


def database_function_skip_statements(return_value, is_test_function=True, SUSHI_error=False, no_data=False):
    """This statement provides the logging output when a pytest skip is initiated after a `nolcat.app.query_database()`, `nolcat.app.load_data_into_database()`, or `nolcat.app.update_database()` function fails.
    
    Args:
        return_value (str): the error message returned by the database helper function
        is_test_function (bool, optional): indicates if this function is being called within a test function; default is `True`
        SUSHI_error (bool, optional): indicates if the skip is because a SUSHI call returned a SUSHI error; default is `False`
        no_data (bool, optional): indicates if the skip is because a SUSHI call returned no data; default is `False`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    if is_test_function:
        if SUSHI_error:
            return f"Unable to run test because the API call raised a server-based SUSHI error, specifically {return_value[0].lower()}{return_value[1:]}"
        elif no_data:
            return f"Unable to run test because no SUSHI data was in the API call response, specifically raising {return_value[0].lower()}{return_value[1:]}"
        else:
            return f"Unable to run test because it relied on {return_value[0].lower()}{return_value[1:].replace(' raised', ', which raised')}"
    else:
        return f"Unable to create fixture because it relied on {return_value[0].lower()}{return_value[1:].replace(' raised', ', which raised')}"


#SUBSECTION: File Download Statements
def file_IO_statement(name_of_file, origin_location, destination_location, upload=True):
    """This statement prepares the name of a file to be subject to an I/O process, plus its origin and destination, for the logging output.

    Args:
        name_of_file (str): the name the file will have after the I/O process
        origin_location (str or Path): the original file location with description
        destination_location (str or Path): the new file location with description
        upload (bool, optional): if the I/O operation is an upload (versus a download); default is `True`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    if upload:
        return f"About to upload file '{name_of_file}' from {origin_location} to {destination_location}."
    else:
        return f"About to download file '{name_of_file}' from {origin_location} to {destination_location}."


def list_folder_contents_statement(file_path, alone=True):
    """This statement lists the contents of a folder for the logging output.

    Information about the logging statement's relative location in a function can be added at the very beginning of the statement.

    Args:
        file_path (pathlib.Path): the folder whose contents are being listed
        alone (bool, optional): indicates if any of the aforementioned information about the statement's location is included; default is `True`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    main_value = f"he files in the folder {file_path.resolve()}\n{format_list_for_stdout(file_path.iterdir())}"
    if alone:
        return "T" + main_value
    else:
        return " t" + main_value


def check_if_file_exists_statement(file_path, alone=True):
    """This statement indicates if there's a file at the given file path for the logging output.

   Information about the logging statement's relative location in a function can be added at the very beginning of the statement.

    Args:
        file_path (pathlib.Path): the path to the file being checked
        alone (bool, optional): indicates if any of the aforementioned information about the statement's location is included; default is `True`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    main_value = f"here's a file at {file_path.resolve()}: {file_path.is_file()}"
    if alone:
        return "T" + main_value
    else:
        return " t" + main_value


#SECTION: Database and Dataframe Functions
#SUBSECTION: MySQL Interaction Result Statements
def database_query_fail_statement(error_message, value_type="load requested page"):
    """This statement indicates the failure of a call to `nolcat.app.query_database()`.

    Args:
        error_message (str): the return statement indicating the failure of `nolcat.app.query_database()`
        value_type (str, optional): the type of value that the query should have returned; default is ``

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if value_type == "load requested page":
        return f"Unable to {value_type} because {error_message[0].lower()}{error_message[1:].replace(' raised', ', which raised')}"
    else:
        return f"Unable to {value_type} because {error_message[0].lower()}{error_message[1:]}"
'''
Called in `nolcat.SUSHICallAndResponse._save_raw_Response_text()` via `nolcat.SUSHICallAndResponse.make_SUSHI_call()` in return statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_status_call -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_status_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_reports_call -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_reports_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_PR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_DR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_TR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_IR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _save_raw_Response_text -> database_query_fail_statement
Called in `nolcat.SUSHICallAndResponse._evaluate_individual_SUSHI_exception()` via `nolcat.SUSHICallAndResponse._handle_SUSHI_exceptions()`via `nolcat.SUSHICallAndResponse.make_SUSHI_call()` in return statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_status_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_status_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_reports_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_reports_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_PR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_DR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_TR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_IR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> database_query_fail_statement
Called in `nolcat.models.StatisticsSources._check_if_data_in_database()` in return statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_check_if_data_in_database_no -> _check_if_data_in_database -> database_query_fail_statement
    test_check_if_data_in_database_yes -> _check_if_data_in_database -> database_query_fail_statement
    test_harvest_single_report -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> database_query_fail_statement
Called in `nolcat.app.check_if_data_already_in_COUNTERData()` in return value
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
    test_check_if_data_already_in_COUNTERData -> check_if_data_already_in_COUNTERData -> database_query_fail_statement
Called in return statements with minimal cascading changes
    change_StatisticsSource -> database_query_fail_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> database_query_fail_statement
    test_calculate_depreciated_ACRL_60b -> calculate_depreciated_ACRL_60b -> database_query_fail_statement
    test_calculate_depreciated_ACRL_63 -> calculate_depreciated_ACRL_63 -> database_query_fail_statement
    test_calculate_ACRL_61a -> calculate_ACRL_61a -> database_query_fail_statement
    test_calculate_ACRL_61b -> calculate_ACRL_61b -> database_query_fail_statement
    test_calculate_ARL_18 -> calculate_ARL_18 -> database_query_fail_statement
    test_calculate_ARL_19 -> calculate_ARL_19 -> database_query_fail_statement
    test_calculate_ARL_20 -> calculate_ARL_20 -> database_query_fail_statement
    test_create_usage_tracking_records_for_fiscal_year -> create_usage_tracking_records_for_fiscal_year -> database_query_fail_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> database_query_fail_statement
'''


def return_value_from_query_statement(return_value, type_of_query=None):
    """This statement shows an individual value or sequence of values returned by a call to `nolcat.app.query_database()`.

    Args:
        return_value (str, int, or tuple): the value(s) returned by `nolcat.app.query_database()`
        type_of_query (str, optional): some descriptive information about the query; default is `None`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if type_of_query:
        main_value = f"The {type_of_query} query returned a dataframe from which "
    else:
        main_value = f"The query returned a dataframe from which "
    
    if isinstance(return_value, tuple):
        i = 0
        for value in return_value:
            if i==len(return_value)-1:
                main_value = main_value + "and "
            main_value = f"{main_value}{value} (type {type(value)}), "
            i += 1
        return f"{main_value[:-2]} were extracted."
    else:
        return f"{main_value}{return_value} (type {type(return_value)}) was extracted."


def initialize_relation_class_object_statement(relation_class_name, object_value):
    """This statement shows the value of a relation class object initialized using the values returned from a query.

    Args:
        relation_class_name (str): the name of the relation class
        object_value (nolcat.models): a relation class object

    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"The following {relation_class_name} object was initialized based on the query results:\n{object_value}"


def unable_to_get_updated_primary_key_values_statement(relation, error):
    """This statement prepares the error raised by `nolcat.app.first_new_PK_value()` for the logging output.

    Args:
        relation (str): the relation name
        error (Exception): the Python Exception raised by `nolcat.app.first_new_PK_value()`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Running the function `first_new_PK_value()` for the relation `{relation}` raised the error {error}."
'''
Called in return statements for SUSHI collection
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> unable_to_get_updated_primary_key_values_statement
    test_collect_usage_statistics -> collect_usage_statistics -> unable_to_get_updated_primary_key_values_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> unable_to_get_updated_primary_key_values_statement
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> unable_to_get_updated_primary_key_values_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> unable_to_get_updated_primary_key_values_statement
'''


def return_dataframe_from_query_statement(query_subject, df):
    """This statement shows the dataframe returned by a call to `nolcat.app.query_database()`.

    Args:
        query_subject (str): a short summary of what the query was for
        df (dataframe): the dataframe returned by `nolcat.app.query_database()`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    if df.shape[0] > 20:
        return f"The beginning and the end of the query for {query_subject}:\n{df.head(10)}\n...\n{df.tail(10)}"
    else:
        return f"The result of the query for {query_subject}:\n{df}"


def database_update_fail_statement(update_statement):
    """This statement indicates the failure of a call to `nolcat.app.update_database()`.

    The repetition of the statement in both a print statement and as the return value ensures the SQL UPDATE statement isn't truncated, which would happen if the statement only went to stdout via log statements. 

    Args:
        update_statement (str): the SQL update statement

    Returns:
        str: the statement for outputting the arguments to logging
    """
    message = f"Updating the {update_statement.split()[1]} relation automatically failed, so the SQL update statement needs to be submitted via the SQL command line:\n{remove_IDE_spacing_from_statement(update_statement)}"
    print(message)
    return message
'''
Called in `nolcat.statements.add_data_success_and_update_database_fail_statement()` in return statement
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
        test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
Called in return statements with minimal cascading changes
    add_access_stop_date -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    remove_access_stop_date -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    change_StatisticsSource -> database_update_fail_statement -> remove_IDE_spacing_from_statement
'''


def add_data_success_and_update_database_fail_statement(load_data_response, update_statement):
    """This statement indicates that data was successfully loaded into the database or the S3 bucket, but the corresponding update to the database failed.

    Args:
        load_data_response (str): the return value indicating success from `nolcat.app.load_data_into_database()` or `nolcat.app.upload_file_to_S3_bucket()`
        update_statement (str): the SQL update statement

    Returns:
        str: the statement for outputting the arguments to logging
    """
    update_statement = database_update_fail_statement(update_statement)
    return f"{load_data_response[:-1]}, but {update_statement[0].lower()}{update_statement[1:]}"
'''
Called in `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()` in return statement
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
        test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
                        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
            test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
Called in mass SUSHI harvest functions in return statements
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> add_data_success_and_update_database_fail_statement -> database_update_fail_statement -> remove_IDE_spacing_from_statement
'''


#SUBSECTION: Result Statement Regexes
def load_data_into_database_success_regex():
    """This regex object matches the success return statement for `nolcat.app.load_data_into_database()`.

    The optional period at the end allows the regex to match when it's being used as the beginning of a statement.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.load_data_into_database()`
    """
    return re.compile(r"[Ss]uccessfully loaded (\d+) records into the (.+) relation\.?")
'''
Called in SUSHI calling functions in `nolcat.models`
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> load_data_into_database_success_regex
        test_collect_annual_usage_statistics -> load_data_into_database_success_regex
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> load_data_into_database_success_regex
        test_collect_fiscal_year_usage_statistics -> load_data_into_database_success_regex
    test_collect_usage_statistics -> load_data_into_database_success_regex
Called in `nolcat.initialization.collect_FY_and_vendor_data()` and return value changed if matched
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> load_data_into_database_success_regex
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> load_data_into_database_success_regex
Called in `nolcat.initialization.collect_sources_data()` and return value changed if matched
    test_collect_sources_data -> collect_sources_data -> load_data_into_database_success_regex
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> load_data_into_database_success_regex
            test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> load_data_into_database_success_regex
Called in `nolcat.initialization.collect_AUCT_and_historical_COUNTER_data()` and return value changed if matched
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database_success_regex
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database_success_regex
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database_success_regex
            test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database_success_regex
            test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database_success_regex
Called in tests
    test_load_data_into_database -> load_data_into_database_success_regex
    test_loading_connected_data_into_other_relation -> load_data_into_database_success_regex
    test_upload_COUNTER_data_via_Excel -> load_data_into_database_success_regex
    test_create_usage_tracking_records_for_fiscal_year -> load_data_into_database_success_regex
        load_new_record_into_fiscalYears -> load_data_into_database_success_regex
'''


def update_database_success_regex():
    """This regex object matches the success return statement for `nolcat.app.update_database()`.

    The variable capitalization of the first letter allows the regex to match when it's being used as the latter half of a statement. The `re.DOTALL` flag is included because update statements include line breaks. The period at the end can be the period at the end of a sentence or the final period in the ellipsis from `nolcat.app.truncate_longer_lines()`.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.update_database()`
    """
    return re.compile(r"[Ss]uccessfully performed the update .+\.", flags=re.DOTALL)
'''
Called in `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()` and return value changed if matched
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database_success_regex
        test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database_success_regex
            test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database_success_regex
        test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
            test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
            test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
            test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
            test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
            test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
                test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database_success_regex
Called in `nolcat.initialization.collect_AUCT_and_historical_COUNTER_data()` and return value changed if matched
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database_success_regex
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database_success_regex
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database_success_regex
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database_success_regex
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database_success_regex
Called in `nolcat.models.ResourceSources` methods and return value changed if matched
    add_access_stop_date -> update_database_success_regex
    remove_access_stop_date -> update_database_success_regex
    change_StatisticsSource -> update_database_success_regex
Called in looping SUSHI calling functions in `nolcat.models` and return value changed if matched
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database_success_regex
        test_collect_annual_usage_statistics -> update_database_success_regex
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database_success_regex
        test_collect_fiscal_year_usage_statistics -> update_database_success_regex
Called in test assert statements
    test_update_database -> update_database_success_regex
    test_update_database_with_insert_statement -> update_database_success_regex
'''


#SUBSECTION: Common Dataframe Adjustments
def change_single_field_dataframe_into_series(df):
    """The function for changing a dataframe with a single field into a series.

    This function transforms any dataframe with a single non-index field into a series with the same index. Dataframes with multiindexes are accepted and those indexes are preserved.

    Args:
        df (dataframe): the dataframe to be transformed
    
    Returns:
        pd.Series: a series object with the same exact data as the initial dataframe
    """
    return pd.Series(
        data=squeeze(df.values),  # `squeeze` converts the numpy array from one column with n elements to an array with n elements
        index=df.index,
        dtype=df[df.columns[0]].dtype,
        name=df.columns[0],
    )
'''
Called in `nolcat.app.create_AUCT_SelectField_options()` in return value
    test_create_AUCT_SelectField_options -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
            test_GET_request_for_upload_non_COUNTER_reports -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
            test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
            test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
            test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
                test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
                    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
                    test_collect_FY_and_vendor_data -> change_single_field_dataframe_into_series
    test_download_non_COUNTER_usage -> download_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_download_non_COUNTER_usage -> download_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_download_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
Called in tests
    test_harvest_SUSHI_statistics -> change_single_field_dataframe_into_series
    test_collect_sources_data -> change_single_field_dataframe_into_series
'''


def restore_boolean_values_to_boolean_field(series):
    """The function for converting the integer field used for Booleans in MySQL into a pandas `boolean` field.

    MySQL stores Boolean values in a `TINYINT(1)` field, so any Boolean fields read from the database into a pandas dataframe appear as integer or float fields with the values `1`, `0`, and, if nulls are allowed, `pd.NA`. For simplicity, clarity, and consistency, turning these fields back into pandas `boolean` fields is often a good idea.

    Args:
        series (pd.Series): a Boolean field with numeric values and a numeric dtype from MySQL
    
    Returns:
        pd.Series: a series object with the same information as the initial series but with Boolean values and a `boolean` dtype
    """
    return series.astype('boolean')
'''
Called in tests
    test_create_usage_tracking_records_for_fiscal_year -> restore_boolean_values_to_boolean_field
Called to create `nolcat.models.AnnualUsageCollectionTracking` object
    test_download_non_COUNTER_usage -> download_non_COUNTER_usage -> restore_boolean_values_to_boolean_field
        test_GET_request_for_download_non_COUNTER_usage -> download_non_COUNTER_usage -> restore_boolean_values_to_boolean_field
'''


def create_AUCT_SelectField_options(df):
    """Transforms a dataframe into a list of options for use as SelectField options.

    A dataframe with the fields `annualUsageCollectionTracking.AUCT_statistics_source`, `annualUsageCollectionTracking.AUCT_fiscal_year`, `statisticsSources.statistics_source_name`, and `fiscalYears.fiscal_year` is changed into a list of tuples, one for each record; the first value is another tuple with the primary key values from `annualUsageCollectionTracking`, and the second value is a string showing the statistics source name and fiscal year.

    Args:
        df (dataframe): a dataframe with the fields `annualUsageCollectionTracking.AUCT_statistics_source`, `annualUsageCollectionTracking.AUCT_fiscal_year`, `statisticsSources.statistics_source_name`, and `fiscalYears.fiscal_year`
    
    Returns:
        list: a list of tuples; see the docstring's detailed description for the contents of the list
    """
    log.info(f"Starting `create_AUCT_SelectField_options()` for the\n{df}\ndataframe.")
    df = df.set_index(['AUCT_statistics_source', 'AUCT_fiscal_year'])
    df['field_display'] = df[['statistics_source_name', 'fiscal_year']].apply("--FY ".join, axis='columns')  # Standard string concatenation with `astype` methods to ensure both values are strings raises `IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or Boolean arrays are valid indices
    df = df.drop(columns=['statistics_source_name', 'fiscal_year'])
    s = change_single_field_dataframe_into_series(df)
    log.info(f"AUCT multiindex values and their corresponding form choices:\n{s}")
    return list(s.items())
'''
Called in `nolcat.initialization.upload_historical_non_COUNTER_usage()` for form creation
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
Called in `nolcat.ingest_usage.upload_non_COUNTER_reports()` for form creation
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_upload_non_COUNTER_reports -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
Called in `nolcat.view_usage.download_non_COUNTER_usage()` for form creation
    test_download_non_COUNTER_usage -> download_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_download_non_COUNTER_usage -> download_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
        test_GET_request_for_download_non_COUNTER_usage -> create_AUCT_SelectField_options -> change_single_field_dataframe_into_series
'''


def extract_value_from_single_value_df(df, expect_int=True):
    """The value in a dataframe containing a single value.

    Since the single-value dataframes are often numerical query results, this function includes the type juggling to convert floats to ints and nulls to zeros. To ensure null values are preserved when strings are requested, the `expect_int` parameter is used.

    Args:
        df (dataframe): a dataframe with a single value
        expect_int (bool, optional): if the return value is expected to have a numerical data type; default is True
    
    Returns:
        int or str: the value in the dataframe
    """
    return_value = df.iloc[0].iloc[0]
    if expect_int:
        if return_value is None:
            return_value = int(0)
        elif isinstance(return_value, float):
            return_value = int(return_value)
    return return_value
'''
Called in `nolcat.app.update_database()` impacting return value
    add_access_stop_date -> update_database -> extract_value_from_single_value_df
    remove_access_stop_date -> update_database -> extract_value_from_single_value_df
    change_StatisticsSource -> update_database -> extract_value_from_single_value_df
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> extract_value_from_single_value_df
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_update_database_with_insert_statement -> update_database -> extract_value_from_single_value_df
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> extract_value_from_single_value_df
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> extract_value_from_single_value_df
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> extract_value_from_single_value_df
        test_collect_fiscal_year_usage_statistics -> update_database -> extract_value_from_single_value_df
Called in `nolcat.app.first_new_PK_value()` in return value
    test_first_new_PK_value -> first_new_PK_value -> extract_value_from_single_value_df
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> extract_value_from_single_value_df
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> first_new_PK_value -> extract_value_from_single_value_df
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> extract_value_from_single_value_df
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> first_new_PK_value -> extract_value_from_single_value_df
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
    test_collect_sources_data -> collect_sources_data -> first_new_PK_value -> extract_value_from_single_value_df
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df
    test_collect_usage_statistics -> collect_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df
Called in `nolcat.SUSHICallAndResponse.make_SUSHI_call()` via `nolcat.SUSHICallAndResponse._save_raw_Response_text()` to get value passed to `nolcat.app.save_unconverted_data_via_upload()`
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
            test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
            test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_status_call -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_status_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_reports_call -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_reports_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_PR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_DR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_TR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_TR_call_validity -> StatisticsSource_instance_name -> extract_value_from_single_value_df
        test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_IR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
        test_IR_call_validity -> StatisticsSource_instance_name -> extract_value_from_single_value_df
        test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
    test_call_with_invalid_credentials -> make_SUSHI_call -> _save_raw_Response_text -> extract_value_from_single_value_df
Called in `nolcat.models.StatisticsSources._check_if_data_in_database()` impacting return value
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_check_if_data_in_database_no -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_check_if_data_in_database_yes -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_harvest_single_report -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> extract_value_from_single_value_df
Called in `nolcat.app.check_if_data_already_in_COUNTERData()` impacting return value
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
    test_check_if_data_already_in_COUNTERData -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
        test_check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df
Called in `tests.test_StatisticsSources.StatisticsSources_fixture()` yield object
    test_fetch_SUSHI_information_for_API -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_check_if_data_in_database_no -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
            test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_check_if_data_in_database_yes -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
            test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_harvest_single_report -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_harvest_single_report -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
            test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_harvest_single_report_with_partial_date_range -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_harvest_single_report_with_partial_date_range -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
            test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_harvest_R5_SUSHI -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_report_to_harvest -> StatisticsSources_fixture -> extract_value_from_single_value_df
            test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
                test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_harvest_R5_SUSHI_with_invalid_dates -> StatisticsSources_fixture -> extract_value_from_single_value_df
            test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> extract_value_from_single_value_df
                test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
    test_collect_usage_statistics -> StatisticsSources_fixture -> extract_value_from_single_value_df
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> StatisticsSources_fixture -> extract_value_from_single_value_df
Other calls
    test_collect_annual_usage_statistics -> extract_value_from_single_value_df
    test_upload_nonstandard_usage_file -> extract_value_from_single_value_df
    test_extract_value_from_single_value_df -> extract_value_from_single_value_df
    test_upload_COUNTER_data_via_SQL_insert -> extract_value_from_single_value_df
    test_calculate_depreciated_ACRL_60b -> calculate_depreciated_ACRL_60b -> extract_value_from_single_value_df
    test_calculate_depreciated_ACRL_63 -> calculate_depreciated_ACRL_63 -> extract_value_from_single_value_df
    test_calculate_ACRL_61a -> calculate_ACRL_61a -> extract_value_from_single_value_df
    test_calculate_ACRL_61b -> calculate_ACRL_61b -> extract_value_from_single_value_df
    test_calculate_ARL_18 -> calculate_ARL_18 -> extract_value_from_single_value_df
    test_calculate_ARL_19 -> calculate_ARL_19 -> extract_value_from_single_value_df
    test_calculate_ARL_20 -> calculate_ARL_20 -> extract_value_from_single_value_df
    test_collect_fiscal_year_usage_statistics -> extract_value_from_single_value_df
    test_status_call -> StatisticsSource_instance_name -> extract_value_from_single_value_df
    test_status_call_validity -> StatisticsSource_instance_name -> extract_value_from_single_value_df
    test_reports_call -> StatisticsSource_instance_name -> extract_value_from_single_value_df
    test_reports_call_validity -> StatisticsSource_instance_name -> extract_value_from_single_value_df
    test_PR_call_validity -> StatisticsSource_instance_name -> extract_value_from_single_value_df
    test_DR_call_validity -> StatisticsSource_instance_name -> extract_value_from_single_value_df
    test_call_with_invalid_credentials -> StatisticsSource_instance_name -> extract_value_from_single_value_df
'''


#SUBSECTION: MySQL Interaction
def load_data_into_database(df, relation, engine, index_field_name=None):
    """A wrapper for the pandas `to_sql()` method that includes the error handling.

    In the cases where `df` doesn't have a field corresponding to the primary key field in `relation`, auto-increment issues can cause a duplicate primary key error to be raised on `0` for the very first record loaded (see https://stackoverflow.com/questions/54808848/pandas-to-sql-increase-tables-index-when-appending-dataframe, https://stackoverflow.com/questions/31315806/insert-dataframe-into-sql-table-with-auto-increment-column, https://stackoverflow.com/questions/26770489/how-to-get-autoincrement-values-for-a-column-after-uploading-a-pandas-dataframe, https://stackoverflow.com/questions/30867390/python-pandas-to-sql-how-to-create-a-table-with-a-primary-key, https://stackoverflow.com/questions/65426278/to-sql-method-of-pandas-sends-primary-key-column-as-null-even-if-the-column-is). Using the return value of `to_sql()` to determine the number of records loaded is due to an enhancement request from pandas 1.4.

    Args:
        df (dataframe): the data to load into the database
        relation (str): the relation the data is being loaded into
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        index_field_name (str or list of str): the name of the field(s) in the relation that the dataframe index values should be loaded into; default is `None`, same as in the wrapped method, which means the index field name(s) are matched to field(s) in the relation

    Returns:
        str: a message indicating success or including the error raised by the attempt to load the data
    """
    log.info(f"Starting `load_data_into_database()` for relation {relation}.")
    try:
        number_of_records = df.to_sql(
            name=relation,
            con=engine,
            if_exists='append',
            chunksize=1000,
            index_label=index_field_name,
        )
        message = f"Successfully loaded {number_of_records} records into the {relation} relation."
        log.info(message)
        return message
    except Exception as error:
        message = f"Loading data into the {relation} relation raised the error {error}."
        log.error(message)
        return message
'''
Called in methods calling `nolcat.models.StatisticsSources._harvest_R5_SUSHI()` to add data to database
    test_collect_usage_statistics -> collect_usage_statistics -> load_data_into_database
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> load_data_into_database
            test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> load_data_into_database
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> load_data_into_database
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> load_data_into_database
Called in initialization blueprint route functions
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> load_data_into_database
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> load_data_into_database
    test_collect_sources_data -> collect_sources_data -> load_data_into_database
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> load_data_into_database
Called in `nolcat.ingest_usage.upload_COUNTER_data()` to add data to database
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> load_data_into_database
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> load_data_into_database
Called in other functions to add data to database
    change_StatisticsSource -> load_data_into_database
    test_load_data_into_database -> load_data_into_database
    test_loading_connected_data_into_other_relation -> load_data_into_database
    load_new_record_into_fiscalYears -> load_data_into_database
    test_create_usage_tracking_records_for_fiscal_year -> create_usage_tracking_records_for_fiscal_year -> load_data_into_database
'''


def query_database(query, engine, index=None):
    """A wrapper for the `pd.read_sql()` method that includes the error handling.

    Args:
        query (str): the SQL query
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        index (str or list of str): the field(s) in the resulting dataframe to use as the index; default is `None`, same as in the wrapped method
    
    Returns:
        dataframe: the result of the query
        str: a message including the error raised by the attempt to run the query
    """
    log.info(f"Starting `query_database()` for query {remove_IDE_spacing_from_statement(query)}.")
    try:
        df = pd.read_sql(
            sql=query,
            con=engine,
            index_col=index,
        )
        if df.shape[0] > 20:
            log.info(f"The beginning and the end of the response to `{remove_IDE_spacing_from_statement(query)}`:\n{df.head(10)}\n...\n{df.tail(10)}")
            log.debug(f"The complete response to `{remove_IDE_spacing_from_statement(query)}`:\n{df}")
        else:
            log.info(f"The complete response to `{remove_IDE_spacing_from_statement(query)}`:\n{df}")
        return df
    except Exception as error:
        message = f"Running the query `{remove_IDE_spacing_from_statement(query)}` raised the error {error}."
        log.error(message)
        return message
'''
Called in `nolcat.app.update_database()`
    add_access_stop_date -> update_database -> query_database -> remove_IDE_spacing_from_statement
    remove_access_stop_date -> update_database -> query_database -> remove_IDE_spacing_from_statement
    change_StatisticsSource -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_update_database -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_update_database -> query_database -> remove_IDE_spacing_from_statement
    test_update_database_with_insert_statement -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_fiscal_year_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.app.first_new_PK_value()`
    test_first_new_PK_value -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.SUSHICallAndResponse.make_SUSHI_call()` via `nolcat.SUSHICallAndResponse._save_raw_Response_text()`
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_status_call -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_status_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _save_raw_Response_text -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.models.StatisticsSources._check_if_data_in_database()` to determine return value
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> _check_if_data_in_database -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.SUSHICallAndResponse.make_SUSHI_call()` via `nolcat.SUSHICallAndResponse._handle_SUSHI_exceptions()` via `nolcat.SUSHICallAndResponse._handle_individual_SUSHI_exception()` impacting return value and used to create `nolcat.models.StatisticsSources` object for the `nolcat.models.StatisticsSources.add_note()` method
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report_with_partial_date_range -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> collect_usage_statistics -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> _harvest_R5_SUSHI -> _harvest_single_report -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_status_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_status_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_PR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_DR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_TR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
        test_IR_call_validity -> list_of_reports -> COUNTER_reports_offered_by_statistics_source -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
    test_call_with_invalid_credentials -> make_SUSHI_call -> _handle_SUSHI_exceptions -> _evaluate_individual_SUSHI_exception -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.app.check_if_data_already_in_COUNTERData()` to determine return value
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_already_in_COUNTERData -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
Called in `tests.test_FiscalYears.FY2020_FiscalYears_object()` to create object yielded by fixture
    test_calculate_depreciated_ACRL_60b -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_63 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61a -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61b -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_18 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_19 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_20 -> FY2020_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
Called in `tests.stest_StatisticsSources.StatisticsSources_fixture()` impacting returned yield value
    test_fetch_SUSHI_information_for_API -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_COUNTER_reports_offered_by_statistics_source -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_no -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_check_if_data_in_database_no -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_in_database_yes -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_check_if_data_in_database_yes -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_single_report_with_partial_date_range -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report_with_partial_date_range -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_single_report_with_partial_date_range -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_report_to_harvest -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_report_to_harvest -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_R5_SUSHI_with_invalid_dates -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_R5_SUSHI_with_invalid_dates -> reports_offered_by_StatisticsSource_fixture -> SUSHI_credentials_fixture_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> harvest_R5_SUSHI_result_in_test_StatisticsSources -> StatisticsSources_fixture -> query_database -> remove_IDE_spacing_from_statement
Called in `tests.test_SUSHICallAndResponse.StatisticsSource_instance_name()` to get yielded value
    test_status_call -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_status_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_reports_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_PR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_DR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_TR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_IR_call_validity -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
    test_call_with_invalid_credentials -> StatisticsSource_instance_name -> query_database -> remove_IDE_spacing_from_statement
Other Calls
    change_StatisticsSource -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_match_direct_SUSHI_harvest_result -> match_direct_SUSHI_harvest_result -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> match_direct_SUSHI_harvest_result -> query_database -> remove_IDE_spacing_from_statement
        test_collect_usage_statistics -> match_direct_SUSHI_harvest_result -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> AUCT_fixture_for_SUSHI -> query_database -> remove_IDE_spacing_from_statement
        test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> AUCT_fixture_for_SUSHI -> query_database -> remove_IDE_spacing_from_statement
    test_collect_annual_usage_statistics -> harvest_R5_SUSHI_result_in_test_AnnualUsageCollectionTracking -> query_database -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> query_database -> remove_IDE_spacing_from_statement
    test_upload_nonstandard_usage_file -> non_COUNTER_AUCT_object_before_upload -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> non_COUNTER_AUCT_object_before_upload -> query_database -> remove_IDE_spacing_from_statement
    test_download_nonstandard_usage_file -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
        test_download_nonstandard_usage_file -> non_COUNTER_file_to_download_from_S3 -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
    test_download_non_COUNTER_usage -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
        test_download_non_COUNTER_usage -> non_COUNTER_file_to_download_from_S3 -> non_COUNTER_AUCT_object_after_upload -> query_database -> remove_IDE_spacing_from_statement
    test_loading_connected_data_into_other_relation -> query_database -> remove_IDE_spacing_from_statement
    test_update_database_with_insert_statement -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_annual_stats_homepage -> annual_stats_homepage -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_annual_stats_homepage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_annual_stats_homepage -> annual_stats_homepage -> show_fiscal_year_details -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_Excel -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
        test_harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
        test_upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
        test_collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> query_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_collect_sources_data -> collect_sources_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_collect_FY_and_vendor_data -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> query_database -> remove_IDE_spacing_from_statement
    test_run_custom_SQL_query -> run_custom_SQL_query -> query_database -> remove_IDE_spacing_from_statement
    test_use_predefined_SQL_query -> query_database -> remove_IDE_spacing_from_statement
    test_use_predefined_SQL_query -> use_predefined_SQL_query -> query_database -> remove_IDE_spacing_from_statement
    test_start_query_wizard -> start_query_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_GET_query_wizard_sort_redirect -> start_query_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_PR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_PR_query_with_wizard -> construct_PR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_DR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_DR_query_with_wizard -> construct_DR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_TR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_TR_query_with_wizard -> construct_TR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_IR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_construct_IR_query_with_wizard -> construct_IR_query_with_wizard -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_download_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_GET_request_for_download_non_COUNTER_usage -> download_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_download_non_COUNTER_usage -> download_non_COUNTER_usage -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_60b -> calculate_depreciated_ACRL_60b -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_depreciated_ACRL_63 -> calculate_depreciated_ACRL_63 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61a -> calculate_ACRL_61a -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ACRL_61b -> calculate_ACRL_61b -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_18 -> calculate_ARL_18 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_19 -> calculate_ARL_19 -> query_database -> remove_IDE_spacing_from_statement
    test_calculate_ARL_20 -> calculate_ARL_20 -> query_database -> remove_IDE_spacing_from_statement
    test_create_usage_tracking_records_for_fiscal_year -> query_database -> remove_IDE_spacing_from_statement
    test_create_usage_tracking_records_for_fiscal_year -> create_usage_tracking_records_for_fiscal_year -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> FY2022_FiscalYears_object -> query_database -> remove_IDE_spacing_from_statement
    test_check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
'''


def first_new_PK_value(relation):
    """The function for getting the next value in the primary key sequence.

    The default value of the SQLAlchemy `autoincrement` argument in the field constructor method adds `AUTO_INCREMENT` to the primary key field in the data definition language. Loading values, even ones following the sequential numbering that auto-incrementation would use, alters the relation's `AUTO_INCREMENT` attribute, causing a primary key duplication error. Stopping this error requires removing auto-incrementation from the primary key fields (by setting the `autoincrement` argument in the field constructor method to `False`); without the auto-incrementation, however, the primary key values must be included as the dataframe's record index field. This function finds the highest value in the primary key field of the given relation and returns the next integer.

    Args:
        relation (str): the name of the relation being checked
    
    Returns:
        int: the first primary key value in the data to be uploaded to the relation
        str: a message including the error raised by the attempt to run the query
    """
    log.info(f"Starting `first_new_PK_value()` for the {relation} relation.")
    if relation == 'fiscalYears':
        PK_field = 'fiscal_year_ID'
    elif relation == 'vendors':
        PK_field = 'vendor_ID'
    elif relation == 'vendorNotes':
        PK_field = 'vendor_notes_ID'
    elif relation == 'statisticsSources':
        PK_field = 'statistics_source_ID'
    elif relation == 'statisticsSourceNotes':
        PK_field = 'statistics_source_notes_ID'
    elif relation == 'resourceSources':
        PK_field = 'resource_source_ID'
    elif relation == 'resourceSourceNotes':
        PK_field = 'resource_source_notes_ID'
    elif relation == 'COUNTERData':
        PK_field = 'COUNTER_data_ID'
    
    largest_PK_value = query_database(
        query=f"""
            SELECT {PK_field} FROM {relation}
            ORDER BY {PK_field} DESC
            LIMIT 1;
        """,
        engine=db.engine,
    )
    if isinstance(largest_PK_value, str):
        log.debug(database_query_fail_statement(largest_PK_value, "return requested value"))
        return largest_PK_value  # Only passing the initial returned error statement to `nolcat.statements.unable_to_get_updated_primary_key_values_statement()`
    elif largest_PK_value.empty:  # If there's no data in the relation, the dataframe is empty, and the primary key numbering should start at zero
        log.debug(f"The {relation} relation is empty.")
        return 0
    else:
        largest_PK_value = extract_value_from_single_value_df(largest_PK_value)
        log.debug(return_value_from_query_statement(largest_PK_value))
        return int(largest_PK_value) + 1
'''
Called in `nolcat.models.StatisticsSources.collect_usage_statistics()` impacting loaded data and return statement
    test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df | test_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df | test_GET_request_for_harvest_SUSHI_statistics -> harvest_SUSHI_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_usage_statistics -> collect_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df | test_collect_usage_statistics -> collect_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
Called in other methods for calling `nolcat.models.StatisticsSources._harvest_R5_SUSHI()`
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df | test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> first_new_PK_value -> extract_value_from_single_value_df | test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.ingest_usage.upload_COUNTER_data()` impacting loaded data
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df | test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df | test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
Called in initialization blueprint
    test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> extract_value_from_single_value_df | test_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> extract_value_from_single_value_df | test_GET_request_for_collect_FY_and_vendor_data -> collect_FY_and_vendor_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_sources_data -> collect_sources_data -> first_new_PK_value -> extract_value_from_single_value_df | test_collect_sources_data -> collect_sources_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df | test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> extract_value_from_single_value_df | test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> first_new_PK_value -> query_database -> remove_IDE_spacing_from_statement
'''


def check_if_data_already_in_COUNTERData(df):
    """Checks if records for a given combination of statistics source, report type, and date are already in the `COUNTERData` relation.

    Individual attribute lists are deduplicated with `list(set())` construction because `pandas.Series.unique()` method returns numpy arrays or experimental pandas arrays depending on the origin series' dtype.

    Args:
        df (dataframe): the data to be loaded into the `COUNTERData` relation
    
    Returns:
        tuple: the dataframe to be loaded into `COUNTERData` or `None` if if no records are being loaded; the message to be flashed about the records not loaded or `None` if all records are being loaded (str or None)
    """
    log.info(f"Starting `check_if_data_already_in_COUNTERData()`.")

    #Section: Get the Statistics Sources, Report Types, and Dates
    #Subsection: Get the Statistics Sources
    statistics_sources_in_dataframe = df['statistics_source_ID'].tolist()
    log.debug(f"All statistics sources as a list:\n{format_list_for_stdout(statistics_sources_in_dataframe)}")
    statistics_sources_in_dataframe = list(set(statistics_sources_in_dataframe))
    log.debug(f"All statistics sources as a deduped list:\n{format_list_for_stdout(statistics_sources_in_dataframe)}")

    #Subsection: Get the Report Types
    report_types_in_dataframe = df['report_type'].tolist()
    log.debug(f"All report types as a list:\n{format_list_for_stdout(report_types_in_dataframe)}")
    report_types_in_dataframe = list(set(report_types_in_dataframe))
    log.debug(f"All report types as a deduped list:\n{format_list_for_stdout(report_types_in_dataframe)}")

    #Subsection: Get the Dates
    dates_in_dataframe = df['usage_date'].tolist()
    log.debug(f"All usage dates as a list:\n{format_list_for_stdout(dates_in_dataframe)}")
    dates_in_dataframe = list(set(dates_in_dataframe))
    log.debug(f"All usage dates as a deduped list:\n{format_list_for_stdout(dates_in_dataframe)}")

    #Section: Check Database for Combinations of Above
    combinations_to_check = tuple(product(statistics_sources_in_dataframe, report_types_in_dataframe, dates_in_dataframe))
    log.info(f"Checking the database for the existence of records with the following statistics source ID, report type, and usage date combinations: {combinations_to_check}")
    total_number_of_matching_records = 0
    matching_record_instances = []
    for combo in combinations_to_check:
        number_of_matching_records = query_database(
            query=f"SELECT COUNT(*) FROM COUNTERData WHERE statistics_source_ID={combo[0]} AND report_type='{combo[1]}' AND usage_date='{combo[2].strftime('%Y-%m-%d')}';",
            engine=db.engine,
        )
        if isinstance(number_of_matching_records, str):
            return (None, database_query_fail_statement(number_of_matching_records, "return requested value"))
        number_of_matching_records = extract_value_from_single_value_df(number_of_matching_records)
        log.debug(return_value_from_query_statement(number_of_matching_records, f"existing usage for statistics_source_ID {combo[0]}, report {combo[1]}, and date {combo[2].strftime('%Y-%m-%d')}"))
        if number_of_matching_records > 0:
            matching_record_instances.append({
                'statistics_source_ID': combo[0],
                'report_type': combo[1],
                'usage_date': combo[2],
            })
            log.debug(f"The list of combinations with matches in the database now includes {matching_record_instances[-1]}.")
            total_number_of_matching_records = total_number_of_matching_records + number_of_matching_records
        
    #Section: Return Result
    if total_number_of_matching_records > 0:
        #Subsection: Get Records and Statistics Source Names for Matches
        records_to_remove = []
        for instance in matching_record_instances:
            to_remove = df[
                (df['statistics_source_ID']==instance['statistics_source_ID']) &
                (df['report_type']==instance['report_type']) &
                (df['usage_date']==instance['usage_date'])
            ]
            if not to_remove.empty:
                records_to_remove.append(to_remove)

            statistics_source_name = query_database(
                query=f"SELECT statistics_source_name FROM statisticsSources WHERE statistics_source_ID={instance['statistics_source_ID']};",
                engine=db.engine,
            )
            if isinstance(statistics_source_name, str):
                return (None, database_query_fail_statement(statistics_source_name, "return requested value"))
            instance['statistics_source_name'] = extract_value_from_single_value_df(statistics_source_name, False)
        
        #Subsection: Return Results
        records_to_remove = pd.concat(records_to_remove)
        records_to_keep = df[
            pd.merge(
                df,
                records_to_remove,
                how='left',  # Because all records come from the left (first) dataframe, there's no difference between a left and outer join
                indicator=True,
            )['_merge']=='left_only'
        ]
        matching_record_instances_list = []
        for instance in matching_record_instances:
            matching_record_instances_list.append(f"{instance['report_type']:3} | {instance['usage_date'].strftime('%Y-%m-%d')} | {instance['statistics_source_name']} (ID {instance['statistics_source_ID']})")
        message = f"Usage statistics for the report type, usage date, and statistics source combination(s) below, which were included in the upload, are already in the database; as a result, it wasn't uploaded to the database. If the data needs to be re-uploaded, please remove the existing data from the database first.\n{format_list_for_stdout(matching_record_instances_list)}"
        log.info(message)
        return (records_to_keep, message)
    else:
        return (df, None)
'''
**Calls impact second value of returned tuple**
Called in `nolcat.ingest_usage.upload_COUNTER_data()` impacting return value and uploaded data
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> format_list_for_stdout | test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement | test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df | test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> format_list_for_stdout |     test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement | test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df | test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.initialization.collect_AUCT_and_historical_COUNTER_data()` impacting return value and uploaded data
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> format_list_for_stdout | test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement | test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df | test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> format_list_for_stdout | test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> database_query_fail_statement | test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> extract_value_from_single_value_df | test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> check_if_data_already_in_COUNTERData -> query_database -> remove_IDE_spacing_from_statement
'''


def update_database(update_statement, engine):
    """A wrapper for the `Engine.execute()` method that includes the error handling.

    The `execute()` method of the `sqlalchemy.engine.Engine` class automatically commits the changes made by the statement.

    Args:
        update_statement (str): the SQL update statement
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
    
    Returns:
        str: a message indicating success or including the error raised by the attempt to update the data
    """
    update_statement = remove_IDE_spacing_from_statement(update_statement)
    display_update_statement = truncate_longer_lines(update_statement)
    log.info(f"Starting `update_database()` for the update statement {display_update_statement}.")

    # These returns a tuple wrapped in a list, but since at least two return `None`, the list can't be removed by index operator here
    UPDATE_regex = re.findall(r"UPDATE (\w+) SET .+( WHERE .+);", update_statement)
    INSERT_regex = re.findall(r"INSERT INTO `?(\w+)`? .+;", update_statement)
    TRUNCATE_regex = re.findall(r"TRUNCATE (\w+);", update_statement)
    if UPDATE_regex:
        query = f"SELECT * FROM {UPDATE_regex[0][0]}{UPDATE_regex[0][1]};"
        before_df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(before_df, str):
            log.warning(database_query_fail_statement(before_df, "confirm success of change to database"))
        else:
            log.debug(f"The records to be updated:\n{before_df}")
    elif INSERT_regex:
        query = f"SELECT COUNT(*) FROM {INSERT_regex[0]};"
        before_df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(before_df, str):
            log.warning(database_query_fail_statement(before_df, "confirm success of change to database"))
        else:
            before_number = extract_value_from_single_value_df(before_df)
            log.debug(f"There are {before_number} records in the relation to be updated.")
    elif TRUNCATE_regex:
        log.debug(f"Since the change caused by TRUNCATE is absolute, not relative, the before condition of the relation doesn't need to be captured for comparison.")
    else:
        log.warning(f"The database has no way to confirm success of change to database after executing {display_update_statement}.")

    try:
        with engine.connect() as connection:
            try:
                connection.execute(text(update_statement))
                connection.commit()
            except Exception as error:
                message = f"Running the update statement {display_update_statement} raised the error {error}."
                log.error(message)
                return message
    except Exception as error:
        message = f"Opening a connection with engine {engine} raised the error {error}."
        log.error(message)
        return message
    
    if UPDATE_regex and isinstance(before_df, pd.core.frame.DataFrame):
        after_df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(after_df, str):
            log.warning(database_query_fail_statement(after_df, "confirm success of change to database"))
        else:
            log.debug(f"The records after being updated:\n{after_df}")
            if before_df.equals(after_df):
                message = f"The update statement {display_update_statement} executed but there was no change in the database."
                log.warning(message)
                return message
    elif INSERT_regex and isinstance(before_df, pd.core.frame.DataFrame):
        after_df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(after_df, str):
            log.warning(database_query_fail_statement(after_df, "confirm success of change to database"))
        else:
            after_number = extract_value_from_single_value_df(after_df)
            log.debug(f"There are {after_number} records in the relation that was updated.")
            if before_number >= after_number:
                message = f"The update statement {display_update_statement} executed but there was no change in the database."
                log.warning(message)
                return message
    elif TRUNCATE_regex:
        df = query_database(
            query=f"SELECT COUNT(*) FROM {TRUNCATE_regex[0][0]};",
            engine=db.engine,
        )
        if isinstance(df, str):
            log.warning(database_query_fail_statement(df, "confirm success of change to database"))
        else:
            if extract_value_from_single_value_df(df) > 0:
                message = f"The update statement {display_update_statement} executed but there was no change in the database."
                log.warning(message)
                return message
    else:
        log.warning(f"The database has no way to confirm success of change to database after executing {display_update_statement}.")
    message = f"Successfully performed the update {display_update_statement}."
    log.info(message)
    return message
'''
Called in `nolcat.models.ResourceSources` methods
    add_access_stop_date -> update_database -> extract_value_from_single_value_df | add_access_stop_date -> update_database -> remove_IDE_spacing_from_statement | add_access_stop_date -> update_database -> query_database -> remove_IDE_spacing_from_statement
    remove_access_stop_date -> update_database -> extract_value_from_single_value_df | remove_access_stop_date -> update_database -> remove_IDE_spacing_from_statement | remove_access_stop_date -> update_database -> query_database -> remove_IDE_spacing_from_statement
    change_StatisticsSource -> update_database -> extract_value_from_single_value_df | change_StatisticsSource -> update_database -> remove_IDE_spacing_from_statement | change_StatisticsSource -> update_database -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.ingest_usage.upload_COUNTER_data()`
    test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> extract_value_from_single_value_df | test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement | test_upload_COUNTER_data_via_Excel -> upload_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> extract_value_from_single_value_df | test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement | test_upload_COUNTER_data_via_SQL_insert -> upload_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()`
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df | test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement | test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df | test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement | test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df | test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement | test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df | test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement | test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df | test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement | test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> extract_value_from_single_value_df | test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> remove_IDE_spacing_from_statement | test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> update_database -> query_database -> remove_IDE_spacing_from_statement
Called in `nolcat.initialization.collect_AUCT_and_historical_COUNTER_data()`
    test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df | test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement | test_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> extract_value_from_single_value_df | test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> remove_IDE_spacing_from_statement | test_GET_request_for_collect_AUCT_and_historical_COUNTER_data -> collect_AUCT_and_historical_COUNTER_data -> update_database -> query_database -> remove_IDE_spacing_from_statement
Called in other methods for calling `nolcat.models.StatisticsSources._harvest_R5_SUSHI()`
    test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> extract_value_from_single_value_df | test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> remove_IDE_spacing_from_statement | test_collect_annual_usage_statistics -> collect_annual_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
    test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> extract_value_from_single_value_df | test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> remove_IDE_spacing_from_statement | test_collect_fiscal_year_usage_statistics -> collect_fiscal_year_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
        test_collect_fiscal_year_usage_statistics -> update_database -> extract_value_from_single_value_df | test_collect_fiscal_year_usage_statistics -> update_database -> remove_IDE_spacing_from_statement | test_collect_fiscal_year_usage_statistics -> update_database -> query_database -> remove_IDE_spacing_from_statement
'''


#SECTION: S3 Interaction
#SUBSECTION: S3 Interaction Statements
def failed_upload_to_S3_statement(file_name, error_message):
    """This statement indicates that a call to `nolcat.app.upload_file_to_S3_bucket()` returned an error, meaning the file that should've been uploaded isn't being saved.

    Args:
        file_name (str): the name of the file that wasn't uploaded to S3
        error_message (str): the return statement indicating the failure of `nolcat.app.upload_file_to_S3_bucket()`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Uploading the file {file_name} to S3 failed because {error_message[0].lower()}{error_message[1:]} NoLCAT HAS NOT SAVED THIS DATA IN ANY WAY!"
'''
Called in `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()` as possible return value
    test_upload_nonstandard_usage_file -> upload_nonstandard_usage_file -> failed_upload_to_S3_statement
    test_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> failed_upload_to_S3_statement
        test_GET_request_for_upload_non_COUNTER_reports -> upload_non_COUNTER_reports -> upload_nonstandard_usage_file -> failed_upload_to_S3_statement
    test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> failed_upload_to_S3_statement
        test_GET_request_for_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> failed_upload_to_S3_statement
        test_upload_historical_non_COUNTER_usage -> files_for_test_upload_historical_non_COUNTER_usage -> upload_historical_non_COUNTER_usage -> upload_nonstandard_usage_file -> failed_upload_to_S3_statement
'''


def unable_to_delete_test_file_in_S3_statement(file_name, error_message):
    """This statement indicates that a file uploaded to a S3 bucket as part of a test function couldn't be removed from the bucket.

    Args:
        file_name (str): the final part of the name of the file in S3
        error_message (str): the AWS error message returned by the attempt to delete the file

    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Trying to remove file {file_name} from the S3 bucket raised the error {error_message}."


def upload_file_to_S3_bucket_success_regex():
    """This regex object matches the success return statement for `nolcat.app.upload_file_to_S3_bucket()`.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.upload_file_to_S3_bucket()`
    """
    return re.compile(r"[Ss]uccessfully loaded the file (.+) into S3 location `.+/.+`\.?")


# statements.upload_nonstandard_usage_file_success_regex


#SUBSECTION: S3 Interaction Functions
# statements.file_extensions_and_mimetypes


# app.upload_file_to_S3_bucket


# app.save_unconverted_data_via_upload