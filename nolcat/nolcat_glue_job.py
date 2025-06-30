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


# statements.remove_IDE_spacing_from_statement


# app.truncate_longer_lines


#SUBSECTION: SUSHI Statements and Regexes
# statements.unable_to_convert_SUSHI_data_to_dataframe_statement


# statements.successful_SUSHI_call_statement


# statements.harvest_R5_SUSHI_success_statement


# statements.failed_SUSHI_call_statement


# statements.no_data_returned_by_SUSHI_statement


# statements.attempted_SUSHI_call_with_invalid_dates_statement


# statements.reports_with_no_usage_regex


# statements.skip_test_due_to_SUSHI_error_regex


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