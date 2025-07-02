from datetime import date
import calendar
import io
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import boto3
import pandas as pd

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
Called in `nolcat.statements.list_folder_contents_statement()` in the return value
    test_download_nonstandard_usage_file -> list_folder_contents_statement -> format_list_for_stdout
    test_run_custom_SQL_query -> run_custom_SQL_query -> list_folder_contents_statement -> format_list_for_stdout
    test_use_predefined_SQL_query -> use_predefined_SQL_query -> list_folder_contents_statement -> format_list_for_stdout
    test_construct_PR_query_with_wizard -> construct_PR_query_with_wizard -> list_folder_contents_statement -> format_list_for_stdout
    test_construct_DR_query_with_wizard -> construct_DR_query_with_wizard -> list_folder_contents_statement -> format_list_for_stdout
    test_construct_TR_query_with_wizard -> construct_TR_query_with_wizard -> list_folder_contents_statement -> format_list_for_stdout
    test_construct_IR_query_with_wizard -> construct_IR_query_with_wizard -> list_folder_contents_statement -> format_list_for_stdout
    test_GET_request_for_download_non_COUNTER_usage -> download_non_COUNTER_usage -> list_folder_contents_statement -> format_list_for_stdout
    test_download_non_COUNTER_usage -> download_non_COUNTER_usage -> list_folder_contents_statement -> format_list_for_stdout
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
# statements.fixture_variable_value_declaration_statement


# statements.Flask_error_statement


# statements.database_function_skip_statements


#SUBSECTION: File Download Statements
# statements.file_IO_statement


# statements.list_folder_contents_statement


# statements.check_if_file_exists_statement


#SECTION: Database and Dataframe Functions
#SUBSECTION: MySQL Interaction Result Statements
# statements.database_query_fail_statement


# statements.return_value_from_query_statement


# statements.initialize_relation_class_object_statement


# statements.unable_to_get_updated_primary_key_values_statement


# statements.return_dataframe_from_query_statement


# statements.database_update_fail_statement


# statements.add_data_success_and_update_database_fail_statement


#SUBSECTION: Result Statement Regexes
# statements.load_data_into_database_success_regex


# statements.update_database_success_regex


#SUBSECTION: Common Dataframe Adjustments
# app.change_single_field_dataframe_into_series


# app.restore_boolean_values_to_boolean_field


# app.create_AUCT_SelectField_options


# app.extract_value_from_single_value_df


#SUBSECTION: MySQL Interaction
# app.load_data_into_database


# app.query_database


# app.first_new_PK_value


# app.check_if_data_already_in_COUNTERData


# app.update_database


#SECTION: S3 Interaction
#SUBSECTION: S3 Interaction Statements
# statements.failed_upload_to_S3_statement


# statements.unable_to_delete_test_file_in_S3_statement


# statements.upload_file_to_S3_bucket_success_regex


# statements.upload_nonstandard_usage_file_success_regex


#SUBSECTION: S3 Interaction Functions
# statements.file_extensions_and_mimetypes


# app.upload_file_to_S3_bucket


# app.save_unconverted_data_via_upload