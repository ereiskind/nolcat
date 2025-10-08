"""The classes and function in this file will be used in both Glue and the Flask server."""

import logging
import re
from pathlib import Path
from datetime import date
import calendar
import io
from itertools import product
import json
from dateutil import parser
from copy import deepcopy
from datetime import datetime
from math import ceil
from sqlalchemy import log as SQLAlchemy_log
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import s3fs
import boto3
import pandas as pd
from numpy import squeeze
from sqlalchemy import text
import botocore.exceptions  # `botocore` is a dependency of `boto3`

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

RESOURCE_NAME_LENGTH = 3600
PUBLISHER_LENGTH = 425
PUBLISHER_ID_LENGTH = 150
PLATFORM_LENGTH = 135
AUTHORS_LENGTH = 4400
DOI_LENGTH = 110
PROPRIETARY_ID_LENGTH = 100
URI_LENGTH = 450

PRODUCTION_COUNTER_FILE_PATH = "nolcat/usage/"
PRODUCTION_NON_COUNTER_FILE_PATH = "nolcat/usage/raw_vendor_reports/"
TEST_COUNTER_FILE_PATH = "nolcat/usage/test/"
TEST_NON_COUNTER_FILE_PATH = "nolcat/usage/test/raw_vendor_reports/"


def filter_empty_parentheses(log_statement):
    """A filter removing log statements containing only empty parentheses.

    SQLAlchemy logging has lines for outputting query parameters, but since pandas doesn't use parameters, these lines always appear in stdout as empty parentheses. This function and its use in `nolcat.app.create_logging()` is based upon information at https://stackoverflow.com/a/58583082.

    Args:
        log_statement (logging.LogRecord): a Python logging statement

    Returns:
        bool: if `log_statement` should go to stdout
    """
    if log_statement.name == "sqlalchemy.engine.base.Engine" and log_statement.msg == "%r":
        return False
    elif log_statement.name == "sqlalchemy.engine.base.Engine" and re.search(r"\n\s+", log_statement.msg):
        log_statement.msg = remove_IDE_spacing_from_statement(log_statement.msg)
        return True
    else:
        return True


def configure_logging(app):
    """Create single logging configuration for entire program.

    This function was largely based upon the information at https://shzhangji.com/blog/2022/08/10/configure-logging-for-flask-sqlalchemy-project/ (site no longer available) with some additional information from https://engineeringfordatascience.com/posts/python_logging/. The logging level and format set in `logging.basicConfig` are used when directly running NoLCAT in the container; the `nolcat/pytest.ini` supplies that information when using pytest. The module `sqlalchemy.engine.base.Engine` is used for the SQLAlchemy logger instead of the more common `sqlalchemy.engine` because the latter includes log statements from modules `sqlalchemy.engine.base.Engine` and `sqlalchemy.engine.base.OptionEngine`, which are repeats of one another.

    Args:
        app (flask.Flask): the Flask object

    Returns:
        None: no return value is needed, so the default `None` is used
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(name)s::%(lineno)d - %(message)s",  # "[timestamp] module name::line number - error message"
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
        force=True,  # With this argument and a call to the function before `logging.getLogger()`, Glue jobs can use this logging config
    )
    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.INFO)  # Statements appear when when no live log output is requested
    logging.getLogger('sqlalchemy.engine.base.Engine').addFilter(filter_empty_parentheses)  # From Python docs: "Multiple calls to `getLogger()` with the same name will always return a reference to the same Logger object."
    SQLAlchemy_log._add_default_handler = lambda handler: None  # Patch to avoid duplicate logging (from https://stackoverflow.com/a/76498428)
    logging.getLogger('botocore').setLevel(logging.INFO)  # This prompts `s3transfer` module logging to appear
    logging.getLogger('s3transfer.utils').setLevel(logging.INFO)  # Expected log statements seem to be set at debug level, so this hides all log statements
    if app.debug:
        logging.getLogger('werkzeug').handlers = []  # Prevents Werkzeug from outputting messages twice in debug mode


csrf = CSRFProtect()
db = SQLAlchemy()
# AWS authentication managed through IAM roles and a CloudFormation init file
s3_client = boto3.client('s3')
#ToDo: `s3fs.S3FileSystem(profile='PROFILE')` goes here

log = logging.getLogger(__name__)
#TEST: temp
log.error(f"`s3fs.S3FileSystem(profile='PROFILE')` (type {type(s3fs.S3FileSystem(profile='PROFILE'))}): {s3fs.S3FileSystem(profile='PROFILE')}")
s3fs.S3FileSystem(profile='PROFILE')
#TEST: end temp


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


def non_COUNTER_file_name_regex():
    """A regex for the naming convention of non-COUNTER usage files saved in S3.
    
    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"(\d+)_(\d{4})\.\w{3,4}")


def parquet_file_name_regex():
    """A regex for the naming convention of parquet usage files containing COUNTER data in S3.
    
    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"(\d+)_(\w{2}\d?)_((\d{4}\-\d{2}\-\d{2}T\d{2}\-\d{2}\-\d{2})|(NULL))\.parquet")


def empty_string_regex():
    """A regex for matching empty strings and whitespace-only strings.

    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"^\s*$")


def proprietary_ID_regex():
    """A regex for matching the proprietary ID label in a SUSHI JSON.

    Returns:
        re.Pattern: the regex object
    """
    return re.compile(r"[Pp]roprietary(_ID)?")


def author_regex():
    """A regex for matching the author label in a SUSHI JSON.

    Returns:
        re.Pattern: the regex object
    """
    return re.compile("[Aa]uthor")


def AWS_timestamp_format():
    """The `strftime()` format code to use with AWS names.

    ISO format cannot be used where AWS calls for datetimes--S3 file names can't contain colons, while Step Function execution names only accept alphanumeric characters, hyphens, and underscores.
    
    Returns:
        str: Python datetime format code
    """
    return '%Y-%m-%dT%H-%M-%S'


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


def format_ISSN(unformatted_ISSN):
    """Creates an ISSN matching `ISSN_regex()` from an unformatted ISSN string.

    Args:
        unformatted_ISSN (str or int): an ISSN without formatting
    
    Returns:
        str: the formatted ISSN
    """
    trimmed_ISSN = str(unformatted_ISSN).strip()
    if re.fullmatch(r"\d{7}[\dxX]", trimmed_ISSN):
        return trimmed_ISSN[:4] + "-" + trimmed_ISSN[-4:]
    else:
        log.warning(f"`{unformatted_ISSN}` isn't consistent with an ISSN, so it isn't being reformatted as an ISSN.")
        return unformatted_ISSN


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


def reports_with_no_usage_regex():
    """This regex object matches the return statements in `no_data_returned_by_SUSHI_statement()` and `failed_SUSHI_call_statement()` that indicate no usage data was returned.

    In the pytest modules, the statements using this function are looking just for those SUSHI responses with neither data nor a SUSHI error, but this regex matches all return values that indicate no usage data was returned; having the `skip_test_due_to_SUSHI_error_regex()` comparison first in test functions means `failed_SUSHI_call_statement()` return values indicating no usage data are never compared to this regex.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.load_data_into_database()`
    """
    return re.compile(r"The call to the `.+` endpoint for .+ returned no (usage )?data( because the SUSHI data didn't have a `Report_Items` section)?\.")


def skip_test_due_to_SUSHI_error_regex():
    """This regex object matches the return statements in `failed_SUSHI_call_statement()`.

    The `failed_SUSHI_call_statement()` return value can end so many different ways, so this regex is designed to capture the shared beginning of all those return statements and be used with the `re.match()` method.

    Returns:
        re.Pattern: the regex object for the success return statement for `failed_SUSHI_call_statement()`
    """
    return re.compile(r"The call to the `.+` endpoint for .+ raised the (SUSHI )?errors?")


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


#SUBSECTION: Result Statement Regexes
def load_data_into_database_success_regex():
    """This regex object matches the success return statement for `nolcat.app.load_data_into_database()`.

    The optional period at the end allows the regex to match when it's being used as the beginning of a statement.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.load_data_into_database()`
    """
    return re.compile(r"[Ss]uccessfully loaded (\d+) records into the (.+) relation\.?")


def update_database_success_regex():
    """This regex object matches the success return statement for `nolcat.app.update_database()`.

    The variable capitalization of the first letter allows the regex to match when it's being used as the latter half of a statement. The `re.DOTALL` flag is included because update statements include line breaks. The period at the end can be the period at the end of a sentence or the final period in the ellipsis from `nolcat.app.truncate_longer_lines()`.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.update_database()`
    """
    return re.compile(r"[Ss]uccessfully performed the update .+\.", flags=re.DOTALL)


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


def restore_boolean_values_to_boolean_field(series):
    """The function for converting the integer field used for Booleans in MySQL into a pandas `boolean` field.

    MySQL stores Boolean values in a `TINYINT(1)` field, so any Boolean fields read from the database into a pandas dataframe appear as integer or float fields with the values `1`, `0`, and, if nulls are allowed, `pd.NA`. For simplicity, clarity, and consistency, turning these fields back into pandas `boolean` fields is often a good idea.

    Args:
        series (pd.Series): a Boolean field with numeric values and a numeric dtype from MySQL
    
    Returns:
        pd.Series: a series object with the same information as the initial series but with Boolean values and a `boolean` dtype
    """
    return series.astype('boolean')


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
        return (df, None)  #ToDo: Calls impact second value of returned tuple--function will need to be redone to handle data movement from MySQL to S3


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


def upload_nonstandard_usage_file_success_regex():
    """This regex object matches the success return statement for `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()`.

    The `re.DOTALL` flag is included because update statements include line breaks.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()`
    """
    return re.compile(r"[Ss]uccessfully loaded the file (.+) into S3 location `.+/.+` and successfully performed the update (.+)\.", flags=re.DOTALL)


#SUBSECTION: S3 Interaction Functions
def file_extensions_and_mimetypes():
    """A dictionary of the file extensions for the types of files that can be downloaded to S3 via NoLCAT and their mimetypes.
    
    This helper function is called in `create_app()` and thus must be before that function.

    Returns:
        dict: the file extensions and their corresponding mimetypes
    """
    return {
        ".xlsx": "application/vnd.ms-excel",
        ".csv": "text/csv",
        ".tsv": "text/tab-separated-values",
        ".pdf": "application/pdf",
        ".docx": "application/msword",
        ".pptx": "application/vnd.ms-powerpoint",
        ".txt": "text/plain",
        ".jpeg": "image/jpeg",
        ".jpg":"image/jpeg",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".html": "text/html",
        ".htm": "text/html",
        ".xml": "text/xml",
        ".zip": "application/zip",
    }


def save_dataframe_to_S3_bucket(df, statistics_source_ID, report_type, bucket_path=PRODUCTION_COUNTER_FILE_PATH):
    """The function for saving COUNTER usage data to S3 in parquet format.

    Args:
        df (dataframe): the data to save in S3 as a parquet file
        statistics_source_ID (int): the primary key value of the statistics source the usage data is from (the `StatisticsSources.statistics_source_ID` attribute)
        report_type (str): the two-letter abbreviation for the report the usage data is from
        bucket_path (str, optional): the path within the bucket where the files will be saved; default is `nolcat.nolcat_glue_job.PRODUCTION_COUNTER_FILE_PATH`
    
    Returns:
        Exception: the error if a problem occurs while saving the data to S3
    """
    log.info(f"Starting `save_dataframe_to_S3_bucket()` for the {report_type} report from statistics source {statistics_source_ID} and S3 location `{BUCKET_NAME}/{bucket_path}`.")
    now = datetime.now()
    try:
        df.to_parquet(
            f"s3://{BUCKET_NAME}/{bucket_path}{statistics_source_ID}_{report_type}_{now.year}-{now.month}-{now.day}T{now.hour}-{now.minute}-{now.second}.parquet",
            index=False,
        )
    except Exception as error:
        log.error(f"")
        return error  #ToDo: When called, response should be handled as "if not null, then problem"


def upload_file_to_S3_bucket(file, file_name, bucket_path):
    """The function for uploading files to a S3 bucket.

    This function is wrapped in other functions for uploading both SUSHI pulls that can't be converted into dataframes and non-COUNTER usage files, which use different bucket paths, so the production file path is not set as a default here.

    Args:
        file (file-like or path-like object): the file being uploaded to the S3 bucket or the path to said file as a Python object
        file_name (str): the name the file will be saved under in the S3 bucket
        bucket_path (str): the path within the bucket where the files will be saved
    
    Returns:
        str: the logging statement to indicate if uploading the data succeeded or failed
    """
    log.info(f"Starting `upload_file_to_S3_bucket()` for the file named {file_name} and S3 location `{BUCKET_NAME}/{bucket_path}`.")
    #Section: Confirm Bucket Exists
    # The canonical way to check for a bucket's existence and the user's privilege to access it
    try:
        check_for_bucket = s3_client.head_bucket(Bucket=BUCKET_NAME)
    except botocore.exceptions.ClientError as error:
        message = f"Unable to upload files to S3 because the check for the S3 bucket designated for downloads raised the error {error}."
        log.error(message)
        return message
 

    #Section: Upload File to Bucket
    log.debug(f"Loading object {file} (type {type(file)}) with file name `{file_name}` into S3 location `{BUCKET_NAME}/{bucket_path}`.")
    #Subsection: Upload File with `upload_fileobj()`
    try:
        file_object = open(file, 'rb')
        log.debug(f"Successfully initialized {file_object} (type {type(file_object)}).")
        try:
            s3_client.upload_fileobj(
                Fileobj=file_object,
                Bucket=BUCKET_NAME,
                Key=bucket_path + file_name,
            )
            file_object.close()
            message = f"Successfully loaded the file {file_name} into S3 location `{BUCKET_NAME}/{bucket_path}`."
            log.info(message)
            return message
        except Exception as error:
            log.warning(f"Running the function `upload_fileobj()` on {file_object} (type {type(file_object)}) raised the error {error}. The system will now try to use `upload_file()`.")
            file_object.close()
    except Exception as error:
        log.warning(f"Running the function `open()` on {file} (type {type(file)}) raised the error {error}. The system will now try to use `upload_file()`.")
    
    #Subsection: Upload File with `upload_file()`
    try:
        if file.is_file():
            try:
                s3_client.upload_file(  # This uploads `file` like a path-like object
                    Filename=file,
                    Bucket=BUCKET_NAME,
                    Key=bucket_path + file_name,
                )
                message = f"Successfully loaded the file {file_name} into S3 location `{BUCKET_NAME}/{bucket_path}`."
                log.info(message)
                return message
            except Exception as error:
                message = f"Unable to load file {file} (type {type(file)}) into an S3 bucket because {error}."
                log.error(message)
                return message
        else:
            message = f"Unable to load file {file} (type {type(file)}) into an S3 bucket because {file} didn't point to an existing regular file."
            log.error(message)
            return message
    except AttributeError as error:
        message = f"Unable to load file {file} (type {type(file)}) into an S3 bucket because it relied on the ability for {file} to be a file-like or path-like object."
        log.error(message)
        return message


def save_unconverted_data_via_upload(data, file_name_stem, bucket_path=PRODUCTION_COUNTER_FILE_PATH):
    """A wrapper for the `upload_file_to_S3_bucket()` when saving SUSHI data that couldn't change data types when needed.

    Data going into the S3 bucket must be saved to a file because `upload_file_to_S3_bucket()` takes file-like objects or path-like objects that lead to file-like objects. These files have a specific naming convention, but the file name stem is an argument in the function call to simplify both this function and its testing. These files use the naming convention "{statistics_source_ID}_{report path with hyphen replacing slash}_{date range start in 'yyyy-mm' format}_{date range end in 'yyyy-mm' format}_{ISO timestamp}".

    Args:
        data (dict or str): the data to be saved to a file in S3
        file_name_stem (str): the stem of the name the file will be saved with in S3
        bucket_path (str, optional): the path within the bucket where the files will be saved; default is `nolcat.nolcat_glue_job.PRODUCTION_COUNTER_FILE_PATH`
    
    Returns:
        str: a message indicating success or including the error raised by the attempt to load the data
    """
    log.info(f"Starting `save_unconverted_data_via_upload()` for the file named {file_name_stem} and S3 location `{BUCKET_NAME}/{bucket_path}`.")

    #Section: Create Temporary File
    #Subsection: Create File Path
    if isinstance(data, dict):
        temp_file_name = 'temp.json'
    else:
        temp_file_name = 'temp.txt'
    temp_file_path = TOP_NOLCAT_DIRECTORY / temp_file_name
    temp_file_path.unlink(missing_ok=True)
    log.info(f"Contents of `{TOP_NOLCAT_DIRECTORY}` after `unlink()` at start of `save_unconverted_data_via_upload()`:\n{format_list_for_stdout(TOP_NOLCAT_DIRECTORY.iterdir())}")

    #Subsection: Save File
    if temp_file_name == 'temp.json':
        try:
            with open(temp_file_path, 'wb') as file:
                log.debug(f"About to write bytes JSON `data` (type {type(data)}) to file object {file}.")
                json.dump(data, file)
            log.debug(f"Data written as bytes JSON to file object {file}.")
        except Exception as TypeError:
            with open(temp_file_path, 'wt') as file:
                log.debug(f"About to write text JSON `data` (type {type(data)}) to file object {file}.")
                file.write(json.dumps(data))
                log.debug(f"Data written as text JSON to file object {file}.")
    else:
        try:
            with open(temp_file_path, 'wb') as file:
                log.debug(f"About to write bytes `data` (type {type(data)}) to file object {file}.")
                file.write(data)
                log.debug(f"Data written as bytes to file object {file}.")
        except Exception as binary_error:
            try:
                with open(temp_file_path, 'wt', encoding='utf-8', errors='backslashreplace') as file:
                    log.debug(f"About to write text `data` (type {type(data)}) to file object {file}.")
                    file.write(data)
                    log.debug(f"Data written as text to file object {file}.")
            except Exception as text_error:
                message = f"Writing data into a binary file raised the error {binary_error}; writing that data into a text file raised the error {text_error}."
                log.error(message)
                return message
    log.debug(f"File at {temp_file_path} successfully created.")

    #Section: Upload File to S3
    file_name = file_name_stem + temp_file_path.suffix
    log.debug(f"About to upload file '{file_name}' from temporary file location {temp_file_path} to S3 location `{BUCKET_NAME}/{bucket_path}`.")
    logging_message = upload_file_to_S3_bucket(
        temp_file_path,
        file_name,
        bucket_path=bucket_path,
    )
    log.info(f"Contents of `{TOP_NOLCAT_DIRECTORY}` before `unlink()` at end of `save_unconverted_data_via_upload()`:\n{format_list_for_stdout(TOP_NOLCAT_DIRECTORY.iterdir())}")
    temp_file_path.unlink()
    log.info(f"Contents of `{TOP_NOLCAT_DIRECTORY}` after `unlink()` at end of `save_unconverted_data_via_upload()`:\n{format_list_for_stdout(TOP_NOLCAT_DIRECTORY.iterdir())}")
    if isinstance(logging_message, str) and re.fullmatch(r'Running the function `.+\(\)` on .+ \(type .+\) raised the error .+\.', logging_message):
        message = f"Uploading the file {file_name} to S3 failed because {logging_message[0].lower()}{logging_message[1:]}"
        log.critical(message)
    else:
        message = logging_message
        log.debug(message)
    return message


class ConvertJSONDictToDataframe:
    """A class for transforming the Python dictionary versions of JSONs returned by a SUSHI API call into dataframes.

    SUSHI API calls return data in a JSON format, which is easily converted to a Python dictionary; this conversion is done in the `SUSHICallAndResponse.make_SUSHI_call()` method. The conversion from a heavily nested dictionary to a dataframe, however, is much more complicated, as none of the built-in dataframe constructors can be employed. This class exists to convert the SUSHI JSON-derived dictionaries into dataframes that can be loaded into the `COUNTERData` relation; since the desired behavior is more that of a function than a class, the would-be function becomes a class by separating the traditional `__init__` method, which instantiates the dictionary as a class attribute, from the methods which performs the actual transformation. This structure requires all instances of the class constructor to be prepended to a call to the `create_dataframe()` method, which means objects of the `ConvertJSONDictToDataframe` type are never instantiated.

    Attributes:
        self.SUSHI_JSON_dictionary (dict): the dictionary created by converting the JSON returned by the SUSHI API call into Python data types
        self.report_type (str): the two-letter abbreviation for the report being called
        self.statistics_source_ID (int): the primary key value of the statistics source the SUSHI API call is from (the `StatisticsSources.statistics_source_ID` attribute)

    Methods:
        create_dataframe: This method applies the appropriate private method to the dictionary derived from the SUSHI call response JSON to make it into a single dataframe ready to be loaded into the `COUNTERData` relation or saves the JSON as a file if it cannot be successfully converted into a dataframe.
        _transform_R5_JSON: This method transforms the data from the dictionary derived from a R5 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.
        _transform_R5b1_JSON: This method transforms the data from the dictionary derived from a R5.1 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.
        _serialize_dates: This method allows the `json.dumps()` method to serialize (convert) `datetime.datetime` and `datetime.date` attributes into strings.
        _extraction_start_logging_statement: This method creates the logging statement at the beginning of an attribute value extraction.
        _extraction_complete_logging_statement: This method creates the logging statement indicating a successful attribute value extraction.
        _increase_field_length_logging_statement: This method creates the logging statement indicating a field length needs to be increased.
    """
    def __init__(self, SUSHI_JSON_dictionary, report_type, statistics_source_ID):
        """The constructor method for `ConvertJSONDictToDataframe`, which instantiates the dictionary object and two additional variables.

        This constructor is not meant to be used alone; all class instantiations should have a `create_dataframe()` method call appended to it.

        Args:
            SUSHI_JSON_dictionary (dict): the dictionary created by converting the JSON returned by the SUSHI API call into Python data types
            report_type (str): the two-letter abbreviation for the report being called
            statistics_source_ID (int): the primary key value of the statistics source the SUSHI API call is from (the `StatisticsSources.statistics_source_ID` attribute)
        """
        self.SUSHI_JSON_dictionary = SUSHI_JSON_dictionary
        self.report_type = report_type
        self.statistics_source_ID = statistics_source_ID
    

    def create_dataframe(self):
        """This method applies the appropriate private method to the dictionary derived from the SUSHI call response JSON to make it into a single dataframe ready to be loaded into the `COUNTERData` relation or saves the JSON as a file if it cannot be successfully converted into a dataframe.

        This method is a wrapper that sends the JSON-like dictionaries containing all the data from the SUSHI API responses to either the `ConvertJSONDictToDataframe._transform_R5_JSON()` or the `ConvertJSONDictToDataframe._transform_R5b1_JSON()` methods depending on the release version of the API call. The `statistics_source_ID` and `report_type` fields are added after the dataframe is returned to the `StatisticsSources._harvest_R5_SUSHI()` method: the former because that information is proprietary to the NoLCAT instance; the latter because adding it there is less computing-intensive.

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation  #ToDo: PARQUET IN S3--`to_parquet()` returns `None`
            str: the error message if the conversion fails
        """
        log.info("Starting `ConvertJSONDictToDataframe.create_dataframe()`.")
        try:
            report_header_creation_date = parser.isoparse(self.SUSHI_JSON_dictionary.get('Report_Header').get('Created')).date()  # Saving as datetime.date data type removes the time data  
        except Exception as error:
            log.warning(f"Parsing the `Created` field from the SUSHI report header into a Python date data type returned the error {error}. The current date, which is the likely value, is being substituted.")
            report_header_creation_date = date.today()
        log.debug(f"Report creation date is {report_header_creation_date} of type {type(report_header_creation_date)}.")
        COUNTER_release = self.SUSHI_JSON_dictionary['Report_Header']['Release']
        if COUNTER_release == "5":
            try:
                df = self._transform_R5_JSON(report_header_creation_date)
            except Exception as error:
                message = f"Attempting to convert the JSON-like dictionary created from a R5 SUSHI call unexpectedly raised the error {error}, meaning the data couldn't be loaded into the database. The JSON data is being saved instead."  # Call to `nolcat.app.save_unconverted_data_via_upload()` occurs in `nolcat.models.StatisticsSources._harvest_single_report()` after call to this function
                log.error(message)
                return message
        elif COUNTER_release == "5.1":
            try:
                df = self._transform_R5b1_JSON(report_header_creation_date)
            except Exception as error:
                message = f"Attempting to convert the JSON-like dictionary created from a R5.1 SUSHI call unexpectedly raised the error {error}, meaning the data couldn't be loaded into the database. The JSON data is being saved instead."  # Call to `nolcat.app.save_unconverted_data_via_upload()` occurs in `nolcat.models.StatisticsSources._harvest_single_report()` after call to this function
                log.error(message)
                return message
        else:
            message = f"The release of the JSON-like dictionary couldn't be identified, meaning the data couldn't be loaded into the database. The JSON data is being saved instead."  # Call to `nolcat.app.save_unconverted_data_via_upload()` occurs in `nolcat.models.StatisticsSources._harvest_single_report()` after call to this function
            log.error(message)
            return message
        #ToDo: PARQUET IN S3--save `df` as parquet in S3 with file name "The file names will contain the statistics source ID, the exact report type, and the harvest date in ISO format, all separated by an underscore. If the harvest date wasn't recorded, `NULL` appears instead of the date value." matching regex `parquet_file_name_regex()`
        #ToDo: PARQUET IN S3--Add `df['statistics_source_ID'] = self.statistics_source_ID`
        #ToDo: PARQUET IN S3--Add `df['report_type'] = self.report_type`
        #ToDo: PARQUET IN S3--`df['report_type'] = df['report_type'].astype(COUNTERData.state_data_types()['report_type'])`--Add way to get above field to be string
        #ToDo: PARQUET IN S3--Data can be requested from a given source for a given report multiple times in a day (i.e. looping through one month at a time if given date range is partially in captured data)--how can data be added to existing parquet files?
        return df  # The method will only get here if one of the private harvest methods was successful
    

    def _transform_R5_JSON(self, report_creation_date):
        """This method transforms the data from the dictionary derived from a R5 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.

        Args:
            report_creation_date (datetime.date): The date the report was created

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation
            str: the error message if the conversion fails
        """
        log.info("Starting `ConvertJSONDictToDataframe._transform_R5_JSON()`.")
        records_orient_list = []

        #Section: Set Up Tracking of Fields to Include in `df_dtypes`
        include_in_df_dtypes = {  # Using `record_dict.get()` at the end doesn't work because any field with a null value in the last record won't be included
            'resource_name': False,
            'publisher': False,
            'publisher_ID': False,
            'authors': False,
            'publication_date': False,
            'article_version': False,
            'DOI': False,
            'proprietary_ID': False,
            'ISBN': False,
            'print_ISSN': False,
            'online_ISSN': False,
            'URI': False,
            'data_type': False,
            'section_type': False,
            'YOP': False,
            'access_type': False,
            'access_method': False,
            'parent_title': False,
            'parent_authors': False,
            'parent_publication_date': False,
            'parent_article_version': False,
            'parent_data_type': False,
            'parent_DOI': False,
            'parent_proprietary_ID': False,
            'parent_ISBN': False,
            'parent_print_ISSN': False,
            'parent_online_ISSN': False,
            'parent_URI': False,
        }

        #Section: Iterate Through JSON Records to Create Single-Level Dictionaries
        for record in self.SUSHI_JSON_dictionary['Report_Items']:
            record_dict = {"report_creation_date": report_creation_date}  # This resets the contents of `record_dict`, including removing any keys that might not get overwritten because they aren't included in the next iteration
            for key, value in record.items():

                #Subsection: Capture `resource_name` Value
                if key == "Database" or key == "Title" or key == "Item":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.resource_name`"))
                    if value is None or empty_string_regex().fullmatch(value):  # This value handled first because `len()` of null value raises an error
                        record_dict['resource_name'] = None
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("resource_name", record_dict['resource_name']))
                    elif len(value) > RESOURCE_NAME_LENGTH:
                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("resource_name", value)
                        log.critical(message)
                        return message
                    else:
                        record_dict['resource_name'] = value
                        include_in_df_dtypes['resource_name'] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("resource_name", record_dict['resource_name']))
                
                #Subsection: Capture `publisher` Value
                elif key == "Publisher":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.publisher`"))
                    if value is None or empty_string_regex().fullmatch(value):  # This value handled first because `len()` of null value raises an error
                        record_dict['publisher'] = None
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher", record_dict['publisher']))
                    elif len(value) > PUBLISHER_LENGTH:
                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("publisher", value)
                        log.critical(message)
                        return message
                    else:
                        record_dict['publisher'] = value
                        include_in_df_dtypes['publisher'] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher", record_dict['publisher']))
                
                #Subsection: Capture `publisher_ID` Value
                elif key == "Publisher_ID":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.publisher_ID`"))
                    if isinstance(value, list) and value != []:
                        if len(value) == 1 and proprietary_ID_regex().search(value[0]['Type']):
                            if len(value[0]['Value']) > PUBLISHER_ID_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("publisher_ID", value[0]['Value'])
                                log.critical(message)
                                return message
                            else:
                                record_dict['publisher_ID'] = value[0]['Value']
                                include_in_df_dtypes['publisher_ID'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher_ID", record_dict['publisher_ID']))
                        else:
                            for type_and_value in value:
                                if proprietary_ID_regex().search(type_and_value['Type']):
                                    if len(type_and_value['Value']) > PUBLISHER_ID_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("publisher_ID", type_and_value['Value'])
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['publisher_ID'] = type_and_value['Value']
                                        include_in_df_dtypes['publisher_ID'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher_ID", record_dict['publisher_ID']))
                
                #Subsection: Capture `platform` Value
                elif key == "Platform":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.platform`"))
                    if value is None or empty_string_regex().fullmatch(value):  # This value handled first because `len()` of null value raises an error
                        record_dict['platform'] = None
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("platform", record_dict['platform']))
                    elif len(value) > PLATFORM_LENGTH:
                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("platform", value)
                        log.critical(message)
                        return message
                    else:
                        record_dict['platform'] = value
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("platform", record_dict['platform']))
                
                #Subsection: Capture `authors` Value
                elif key == "Item_Contributors":  # `Item_Contributors` uses `Name` instead of `Value`
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.authors`"))
                    for type_and_value in value:
                        if author_regex().search(type_and_value['Type']):
                            if record_dict.get('authors'):  # If the author name value is null, this will never be true
                                if record_dict['authors'].endswith(" et al."):
                                    continue  # The `for type_and_value in value` loop
                                elif len(record_dict['authors']) + len(type_and_value['Name']) + 8 > AUTHORS_LENGTH:
                                    record_dict['authors'] = record_dict['authors'] + " et al."
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("authors", record_dict['authors']))
                                else:
                                    record_dict['authors'] = record_dict['authors'] + "; " + type_and_value['Name']
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("authors", record_dict['authors']))
                            
                            else:
                                if type_and_value['Name'] is None or empty_string_regex().fullmatch(type_and_value['Name']):  # This value handled first because `len()` of null value raises an error
                                    record_dict['authors'] = None
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("authors", record_dict['authors']))
                                elif len(type_and_value['Name']) > AUTHORS_LENGTH:
                                    message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("authors", type_and_value['Name'])
                                    log.critical(message)
                                    return message
                                else:
                                    record_dict['authors'] = type_and_value['Name']
                                    include_in_df_dtypes['authors'] = 'string'
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("authors", record_dict['authors']))
                
                #Subsection: Capture `publication_date` Value
                elif key == "Item_Dates":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.publication_date`"))
                    for type_and_value in value:
                        if type_and_value['Value'] == "1000-01-01" or type_and_value['Value'] == "1753-01-01" or type_and_value['Value'] == "1900-01-01":
                            continue  # The `for type_and_value in value` loop; these dates are common RDBMS/spreadsheet minimum date data type values and are generally placeholders for null values or bad data
                        if type_and_value['Type'] == "Publication_Date":  # Unlikely to be more than one; if there is, the field's date/datetime64 data type prevent duplicates from being preserved
                            try:
                                record_dict['publication_date'] = date.fromisoformat(type_and_value['Value'])
                                include_in_df_dtypes['publication_date'] = True
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publication_date", record_dict['publication_date']))
                            except:  # In case `type_and_value['Value']` is null, which would cause the conversion to a datetime data type to return a TypeError
                                continue  # The `for type_and_value in value` loop
                
                #Subsection: Capture `article_version` Value
                elif key == "Item_Attributes":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.article_version`"))
                    for type_and_value in value:
                        if type_and_value['Type'] == "Article_Version":  # Very unlikely to be more than one
                            record_dict['article_version'] = type_and_value['Value']
                            include_in_df_dtypes['article_version'] = 'string'
                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("article_version", record_dict['article_version']))
                
                #Subsection: Capture Standard Identifiers
                # Null value handling isn't needed because all null values are removed
                elif key == "Item_ID":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "the proprietary ID fields"))
                    for type_and_value in value:
                        
                        #Subsection: Capture `DOI` Value
                        if type_and_value['Type'] == "DOI":
                            if len(type_and_value['Value']) > DOI_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("DOI", type_and_value['Value'])
                                log.critical(message)
                                return message
                            else:
                                record_dict['DOI'] = type_and_value['Value']
                                include_in_df_dtypes['DOI'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("DOI", record_dict['DOI']))
                        
                        #Subsection: Capture `proprietary_ID` Value
                        elif proprietary_ID_regex().search(type_and_value['Type']):
                            if len(type_and_value['Value']) > PROPRIETARY_ID_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("proprietary_ID", type_and_value['Value'])
                                log.critical(message)
                                return message
                            else:
                                record_dict['proprietary_ID'] = type_and_value['Value']
                                include_in_df_dtypes['proprietary_ID'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("proprietary_ID", record_dict['proprietary_ID']))
                        
                        #Subsection: Capture `ISBN` Value
                        elif type_and_value['Type'] == "ISBN":
                            record_dict['ISBN'] = str(type_and_value['Value'])
                            include_in_df_dtypes['ISBN'] = 'string'
                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("ISBN", record_dict['ISBN']))
                        
                        #Subsection: Capture `print_ISSN` Value
                        elif type_and_value['Type'] == "Print_ISSN":
                            if ISSN_regex().fullmatch(type_and_value['Value']):
                                record_dict['print_ISSN'] = type_and_value['Value'].strip()
                                include_in_df_dtypes['print_ISSN'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("print_ISSN", record_dict['print_ISSN']))
                            else:
                                record_dict['print_ISSN'] = format_ISSN(type_and_value['Value'])
                                include_in_df_dtypes['print_ISSN'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("print_ISSN", record_dict['print_ISSN']))
                        
                        #Subsection: Capture `online_ISSN` Value
                        elif type_and_value['Type'] == "Online_ISSN":
                            if ISSN_regex().fullmatch(type_and_value['Value']):
                                record_dict['online_ISSN'] = type_and_value['Value'].strip()
                                include_in_df_dtypes['online_ISSN'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("online_ISSN", record_dict['online_ISSN']))
                            else:
                                record_dict['online_ISSN'] = format_ISSN(type_and_value['Value'])
                                include_in_df_dtypes['online_ISSN'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("online_ISSN", record_dict['online_ISSN']))
                        
                        #Subsection: Capture `URI` Value
                        elif type_and_value['Type'] == "URI":
                            if len(type_and_value['Value']) > URI_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("URI", type_and_value['Value'])
                                log.critical(message)
                                return message
                            else:
                                record_dict['URI'] = type_and_value['Value']
                                include_in_df_dtypes['URI'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("URI", record_dict['URI']))
                        
                        else:
                            continue  # The `for type_and_value in value` loop
                
                #Subsection: Capture `data_type` Value
                elif key == "Data_Type":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.data_type`"))
                    record_dict['data_type'] = value
                    include_in_df_dtypes['data_type'] = 'string'
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("data_type", record_dict['data_type']))
                
                #Subsection: Capture `section_Type` Value
                elif key == "Section_Type":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.section_type`"))
                    record_dict['section_type'] = value
                    include_in_df_dtypes['section_type'] = 'string'
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("section_type", record_dict['section_type']))

                #Subsection: Capture `YOP` Value
                elif key == "YOP":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.YOP`"))
                    try:
                        record_dict['YOP'] = int(value)  # The Int16 dtype doesn't have a constructor, so this value is saved as an int for now and transformed when when the dataframe is created
                        include_in_df_dtypes['YOP'] = 'Int16'  # `smallint` in database; using the pandas data type here because it allows null values
                    except:
                        record_dict['YOP'] = None  # The dtype conversion that occurs when this becomes a dataframe will change this to pandas' `NA`
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("YOP", record_dict['YOP']))
                
                #Subsection: Capture `access_type` Value
                elif key == "Access_Type":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.access_type`"))
                    record_dict['access_type'] = value
                    include_in_df_dtypes['access_type'] = 'string'
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("access_type", record_dict['access_type']))
                
                #Subsection: Capture `access_method` Value
                elif key == "Access_Method":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.access_method`"))
                    record_dict['access_method'] = value
                    include_in_df_dtypes['access_method'] = 'string'
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("access_method", record_dict['access_method']))
                
                #Subsection: Capture Parent Resource Metadata
                # Null value handling isn't needed because all null values are removed
                elif key == "Item_Parent":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "the parent metadata fields"))
                    if isinstance(value, list) and len(value) == 1:  # The `Item_Parent` value should be a dict, but sometimes that dict is within a one-item list; this removes the outer list
                        value = value[0]
                    for key_for_parent, value_for_parent in value.items():

                        #Subsection: Capture `parent_title` Value
                        if key_for_parent == "Item_Name":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value_for_parent, key_for_parent, "`COUNTERData.parent_title`"))
                            if len(value_for_parent) > RESOURCE_NAME_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("parent_title", value_for_parent)
                                log.critical(message)
                                return message
                            else:
                                record_dict['parent_title'] = value_for_parent
                                include_in_df_dtypes['parent_title'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_title", record_dict['parent_title']))
                        
                        #Subsection: Capture `parent_authors` Value
                        elif key_for_parent == "Item_Contributors":  # `Item_Contributors` uses `Name` instead of `Value`
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value_for_parent, key_for_parent, "`COUNTERData.parent_authors`"))
                            for type_and_value in value_for_parent:
                                if author_regex().search(type_and_value['Type']):
                                    if record_dict.get('parent_authors'):
                                        if record_dict['parent_authors'].endswith(" et al."):
                                            continue  # The `for type_and_value in value_for_parent` loop
                                        elif len(record_dict['parent_authors']) + len(type_and_value['Name']) + 8 > AUTHORS_LENGTH:
                                            record_dict['parent_authors'] = record_dict['parent_authors'] + " et al."
                                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_authors", record_dict['parent_authors']))
                                        else:
                                            record_dict['parent_authors'] = record_dict['parent_authors'] + "; " + type_and_value['Name']
                                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_authors", record_dict['parent_authors']))
                                    else:
                                        if len(type_and_value['Name']) > AUTHORS_LENGTH:
                                            message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("authors", type_and_value['Name'])
                                            log.critical(message)
                                            return message
                                        else:
                                            record_dict['parent_authors'] = type_and_value['Name']
                                            include_in_df_dtypes['parent_authors'] = 'string'
                                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_authors", record_dict['parent_authors']))
                        
                        #Subsection: Capture `parent_publication_date` Value
                        elif key_for_parent == "Item_Dates":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value_for_parent, key_for_parent, "`COUNTERData.parent_publication_date`"))
                            for type_and_value in value_for_parent:
                                if type_and_value['Value'] == "1000-01-01" or type_and_value['Value'] == "1753-01-01" or type_and_value['Value'] == "1900-01-01":
                                    continue  # The `for type_and_value in value` loop; these dates are common RDBMS/spreadsheet minimum date data type values and are generally placeholders for null values or bad data
                                if type_and_value['Type'] == "Publication_Date":  # Unlikely to be more than one; if there is, the field's date/datetime64 data type prevent duplicates from being preserved
                                    record_dict['parent_publication_date'] = date.fromisoformat(type_and_value['Value'])
                                    include_in_df_dtypes['parent_publication_date'] = True
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_publication_date", record_dict['parent_publication_date']))
                        
                        #Subsection: Capture `parent_article_version` Value
                        elif key_for_parent == "Item_Attributes":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value_for_parent, key_for_parent, "`COUNTERData.parent_article_version`"))
                            for type_and_value in value_for_parent:
                                if type_and_value['Type'] == "Article_Version":  # Very unlikely to be more than one
                                    record_dict['parent_article_version'] = type_and_value['Value']
                                    include_in_df_dtypes['parent_article_version'] = 'string'
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_article_version", record_dict['parent_article_version']))

                        #Subsection: Capture `parent_data_type` Value
                        elif key_for_parent == "Data_Type":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value_for_parent, key_for_parent, "`COUNTERData.parent_data_type`"))
                            record_dict['parent_data_type'] = value_for_parent
                            include_in_df_dtypes['parent_data_type'] = 'string'
                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_data_type", record_dict['parent_data_type']))
                        
                        #Subsection: Capture Parent Standard Identifiers
                        elif key_for_parent == "Item_ID":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value_for_parent, key_for_parent, "the parent proprietary ID fields"))
                            for type_and_value in value_for_parent:
                                
                                #Subsection: Capture `parent_DOI` Value
                                if type_and_value['Type'] == "DOI":
                                    if len(type_and_value['Value']) > DOI_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("parent_DOI", type_and_value['Value'])
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['parent_DOI'] = type_and_value['Value']
                                        include_in_df_dtypes['parent_DOI'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_DOI", record_dict['parent_DOI']))

                                #Subsection: Capture `parent_proprietary_ID` Value
                                elif proprietary_ID_regex().search(type_and_value['Type']):
                                    if len(type_and_value['Value']) > PROPRIETARY_ID_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("parent_proprietary_ID", type_and_value['Value'])
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['parent_proprietary_ID'] = type_and_value['Value']
                                        include_in_df_dtypes['parent_proprietary_ID'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_proprietary_ID", record_dict['parent_proprietary_ID']))

                                #Subsection: Capture `parent_ISBN` Value
                                elif type_and_value['Type'] == "ISBN":
                                    record_dict['parent_ISBN'] = str(type_and_value['Value'])
                                    include_in_df_dtypes['parent_ISBN'] = 'string'
                                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_ISBN", record_dict['parent_ISBN']))

                                #Subsection: Capture `parent_print_ISSN` Value
                                elif type_and_value['Type'] == "Print_ISSN":
                                    if ISSN_regex().fullmatch(type_and_value['Value']):
                                        record_dict['parent_print_ISSN'] = type_and_value['Value'].strip()
                                        include_in_df_dtypes['parent_print_ISSN'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_print_ISSN", record_dict['parent_print_ISSN']))
                                    else:
                                        record_dict['parent_print_ISSN'] = format_ISSN(type_and_value['Value'])
                                        include_in_df_dtypes['parent_print_ISSN'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_print_ISSN", record_dict['parent_print_ISSN']))

                                #Subsection: Capture `parent_online_ISSN` Value
                                elif type_and_value['Type'] == "Online_ISSN":
                                    if ISSN_regex().fullmatch(type_and_value['Value']):
                                        record_dict['parent_online_ISSN'] = type_and_value['Value'].strip()
                                        include_in_df_dtypes['parent_online_ISSN'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_online_ISSN", record_dict['parent_online_ISSN']))
                                    else:
                                        record_dict['parent_online_ISSN'] = format_ISSN(type_and_value['Value'])
                                        include_in_df_dtypes['parent_online_ISSN'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_online_ISSN", record_dict['parent_online_ISSN']))

                                #Subsection: Capture `parent_URI` Value
                                elif type_and_value['Type'] == "URI":
                                    if len(type_and_value['Value']) > URI_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("parent_URI", type_and_value['Value'])
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['parent_URI'] = type_and_value['Value']
                                        include_in_df_dtypes['parent_URI'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("parent_URI", record_dict['parent_URI']))

                        else:
                            continue  # The `for key_for_parent, value_for_parent in value.items()` loop

                elif key == "Performance":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "the temporary key for date, metric type, and usage count values"))
                    record_dict['temp'] = value

                else:
                    log.warning(f"The unexpected key `{key}` was found in the JSON response to a SUSHI API call.")
                    pass
            
            #Section: Create Records by Iterating Through `Performance` Section of SUSHI JSON
            performance = record_dict.pop('temp')
            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(performance, "temp", "the `COUNTERData.usage_date`, `COUNTERData.metric_type`, and `COUNTERData.usage_count` fields"))
            for period_grouping in performance:
                record_dict['usage_date'] = date.fromisoformat(period_grouping['Period']['Begin_Date'])
                for instance in period_grouping['Instance']:
                    record_dict['metric_type'] = instance['Metric_Type']
                    record_dict['usage_count'] = instance['Count']
                    records_orient_list.append(deepcopy(record_dict))  # Appending `record_dict` directly adds a reference to that variable, which changes with each iteration of the loop, meaning all the records for a given set of metadata have the `usage_date`, `metric_type`, and `usage_count` values of `record_dict` during the final iteration
                    log.debug(f"Added record {record_dict} to `COUNTERData` relation.")  # Set to logging level debug because when all these logging statements are sent to AWS stdout, the only pytest output visible is the error summary statements

        #Section: Create Dataframe
        log.info(f"Unfiltered `include_in_df_dtypes`: {include_in_df_dtypes}")
        include_in_df_dtypes = {k: v for (k, v) in include_in_df_dtypes.items() if v is not False}  # Using `is` for comparison because `1 != False` returns `True` in Python
        log.debug(f"Filtered `include_in_df_dtypes`: {include_in_df_dtypes}")
        df_dtypes = {k: v for (k, v) in include_in_df_dtypes.items() if v is not True}
        df_dtypes['platform'] = 'string'
        df_dtypes['metric_type'] = 'string'
        df_dtypes['usage_count'] = 'int'
        log.info(f"`df_dtypes`: {df_dtypes}")

        log.debug(f"`records_orient_list` before `json.dumps()`  is type {type(records_orient_list)}.")
        records_orient_list = json.dumps(  # `pd.read_json` takes a string, conversion done before method for ease in handling type conversions
            records_orient_list,
            default=ConvertJSONDictToDataframe._serialize_dates,
        )
        if len(records_orient_list) > 1500:
            log.debug(f"`records_orient_list` after `json.dumps()` (type {type(records_orient_list)}) is too long to display.")
        else:
            log.debug(f"`records_orient_list` after `json.dumps()` (type {type(records_orient_list)}):\n{records_orient_list}")
        df = pd.read_json(
            io.StringIO(records_orient_list),  # Originally from https://stackoverflow.com/a/63655099 in `except` block; now only option due to `FutureWarning: Passing literal json to 'read_json' is deprecated and will be removed in a future version. To read from a literal string, wrap it in a 'StringIO' object.`
            orient='records',
            dtype=df_dtypes,  # This only sets numeric data types
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        log.info(f"Dataframe info immediately after dataframe creation:\n{return_string_of_dataframe_info(df)}")

        df = df.astype(df_dtypes)  # This sets the string data types
        log.debug(f"Dataframe dtypes after conversion:\n{return_string_of_dataframe_info(df)}")
        if include_in_df_dtypes.get('publication_date'):  # Meaning the value was changed to `True`
            df['publication_date'] = pd.to_datetime(
                df['publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
            )
        if include_in_df_dtypes.get('parent_publication_date'):  # Meaning the value was changed to `True`
            df['parent_publication_date'] = pd.to_datetime(
                df['parent_publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
            )
        df['usage_date'] = pd.to_datetime(df['usage_date'])
        df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])#.dt.tz_localize(None)

        log.info(f"Dataframe info:\n{return_string_of_dataframe_info(df)}")
        return df
    

    def _transform_R5b1_JSON(self, report_creation_date):
        """This method transforms the data from the dictionary derived from a R5.1 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.

        Args:
            report_creation_date (datetime.date): The date the report was created

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation
            str: the error message if the conversion fails
        """
        log.info("Starting `ConvertJSONDictToDataframe._transform_R5b1_JSON()`.")
        report_type = self.SUSHI_JSON_dictionary['Report_Header']['Report_ID']
        
        #Section: Set Up Tracking of Fields to Include in `df_dtypes`
        include_in_df_dtypes = {
            'resource_name': False,
            'publisher': False,
            'publisher_ID': False,
            'authors': False,
            'publication_date': False,
            'article_version': False,
            'DOI': False,
            'proprietary_ID': False,
            'ISBN': False,
            'print_ISSN': False,
            'online_ISSN': False,
            'URI': False,
            'section_type': False,
            'YOP': False,
            'access_type': False,
            'access_method': False,
            'parent_title': False,
            'parent_authors': False,
            'parent_publication_date': False,
            'parent_article_version': False,
            'parent_data_type': False,
            'parent_DOI': False,
            'parent_proprietary_ID': False,
            'parent_ISBN': False,
            'parent_print_ISSN': False,
            'parent_online_ISSN': False,
            'parent_URI': False,
        }

        #Section: Iterate Through `Report_Items` Section of SUSHI JSON to Create Single-Level Dictionaries
        report_items_list = []
        for record in self.SUSHI_JSON_dictionary['Report_Items']:
            log.debug(f"Starting iteration for new JSON record {record}.")
            report_items_dict = {"report_creation_date": report_creation_date}  # This resets the contents of `report_items_dict`, including removing any keys that might not get overwritten because they aren't included in the next iteration
            for key, value in record.items():
                second_iteration_key_list = []

                #Subsection: Capture `resource_name` or `parent_title` Value
                if key == "Database" or key == "Title":
                    if report_type == "IR":
                        field = "parent_title"
                    else:
                        field = "resource_name"
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, f"`COUNTERData.{field}`"))
                    if value is None or empty_string_regex().fullmatch(value):  # This value handled first because `len()` of null value raises an error
                        report_items_dict[field] = None
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement(field, report_items_dict[field]))
                    elif len(value) > RESOURCE_NAME_LENGTH:
                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement(field, value)
                        log.critical(message)
                        return message
                    else:
                        report_items_dict[field] = value
                        include_in_df_dtypes[field] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement(field, report_items_dict[field]))

                #Subsection: Capture `publisher` Value
                elif key == "Publisher":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.publisher`"))
                    if value is None or empty_string_regex().fullmatch(value):  # This value handled first because `len()` of null value raises an error
                        report_items_dict['publisher'] = None
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher", report_items_dict['publisher']))
                    elif len(value) > PUBLISHER_LENGTH:
                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("publisher", value)
                        log.critical(message)
                        return message
                    else:
                        report_items_dict['publisher'] = value
                        include_in_df_dtypes['publisher'] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher", report_items_dict['publisher']))

                #Subsection: Capture `publisher_ID` Value
                elif key == "Publisher_ID":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.publisher_ID`"))
                    pass

                #Subsection: Capture `platform` Value
                elif key == "Platform":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.platform`"))
                    if value is None or empty_string_regex().fullmatch(value):  # This value handled first because `len()` of null value raises an error
                        report_items_dict['platform'] = None
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("platform", report_items_dict['platform']))
                    elif len(value) > PLATFORM_LENGTH:
                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("platform", value)
                        log.critical(message)
                        return message
                    else:
                        report_items_dict['platform'] = value
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("platform", report_items_dict['platform']))

                #Subsection: Capture `authors` or `parent_authors` Value
                elif key == "Authors":
                    if report_type == "IR":
                        field = "parent_authors"
                    else:
                        field = "authors"
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, f"`COUNTERData.{field}`"))
                    if not isinstance(value, list) or len(value) == 0:  # R5 SUSHI often had null values and empty strings as values for the author; this error checking serves the same purpose for R5.1 SUSHI
                        pass  # Lack of key in given record will become null value when converted to a dataframe
                    for label_and_author_name in value:
                        if label_and_author_name.get('Name'):
                            if field not in report_items_dict and len(label_and_author_name['Name']) > AUTHORS_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement(field, label_and_author_name['Name'])
                                log.critical(message)
                                return message
                            elif field not in report_items_dict:
                                report_items_dict[field] = label_and_author_name['Name'].strip()
                                include_in_df_dtypes[field] = 'string'
                            elif report_items_dict[field].endswith(" et al."):
                                break  # The loop of adding author names
                            elif len(report_items_dict[field]) + len(label_and_author_name['Name']) + 8 < AUTHORS_LENGTH:
                                report_items_dict[field] = report_items_dict[field] + "; " + label_and_author_name['Name'].strip()
                            else:
                                report_items_dict[field] = report_items_dict[field] + " et al."
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement(field, report_items_dict[field]))

                #Subsection: Capture `publication_date` or `parent_publication_date` Value
                elif key == "Item_Dates":
                    if report_type == "IR":
                        field = "parent_publication_date"
                    else:
                        field = "publication_date"
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, f"`COUNTERData.{field}`"))
                    pass

                #Subsection: Capture `article_version` or `parent_article_version` Value
                elif key == "Article_Version":
                    if report_type == "IR":
                        field = "parent_article_version"
                    else:
                        field = "article_version"
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, f"`COUNTERData.{field}`"))
                    pass

                #Subsection: Capture Standard Identifiers or Parent Standard Identifiers
                # Null value handling isn't needed because all null values are removed
                elif key == "Item_ID":
                    if report_type == "DR" or report_type == "TR":
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "the standard ID fields"))
                    else:
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "the parent standard ID fields"))
                    for ID_type, ID_value in value.items():

                        #Subsection: Capture `DOI` or `parent_DOI` Value
                        if ID_type == "DOI":
                            if report_type == "IR":
                                field = "parent_DOI"
                            else:
                                field = "DOI"
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, f"`COUNTERData.{field}`"))
                            if len(ID_value) > DOI_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("DOI", ID_value)
                                log.critical(message)
                                return message
                            else:
                                report_items_dict[field] = ID_value
                                include_in_df_dtypes[field] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement(field, report_items_dict[field]))

                        #Subsection: Capture `proprietary_ID` or `parent_proprietary_ID` Value
                        elif proprietary_ID_regex().search(ID_type):
                            if report_type == "IR":
                                field = "parent_proprietary_ID"
                            else:
                                field = "proprietary_ID"
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, f"`COUNTERData.{field}`"))
                            if len(ID_value) > PROPRIETARY_ID_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("proprietary_ID", ID_value)
                                log.critical(message)
                                return message
                            else:
                                report_items_dict[field] = ID_value
                                include_in_df_dtypes[field] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement(field, report_items_dict[field]))

                        #Subsection: Capture `ISBN` or `parent_ISBN` Value
                        elif ID_type == "ISBN":
                            if report_type == "IR":
                                field = "parent_ISBN"
                            else:
                                field = "ISBN"
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, f"`COUNTERData.{field}`"))
                            pass

                        #Subsection: Capture `print_ISSN` or `parent_print_ISSN` Value
                        elif ID_type == "Print_ISSN":
                            if report_type == "IR":
                                field = "parent_print_ISSN"
                            else:
                                field = "print_ISSN"
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, f"`COUNTERData.{field}`"))
                            if ISSN_regex().fullmatch(ID_value):
                                report_items_dict[field] = ID_value.strip()
                                include_in_df_dtypes[field] = 'string'
                            else:
                                report_items_dict[field] = format_ISSN(ID_value)
                                include_in_df_dtypes[field] = 'string'
                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement(field, report_items_dict[field]))

                        #Subsection: Capture `online_ISSN` or `parent_online_ISSN` Value
                        elif ID_type == "Online_ISSN":
                            if report_type == "IR":
                                field = "parent_online_ISSN"
                            else:
                                field = "online_ISSN"
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, f"`COUNTERData.{field}`"))
                            pass

                        #Subsection: Capture `URI` or `parent_URI` Value
                        elif ID_type == "URI":
                            if report_type == "IR":
                                field = "parent_URI"
                            else:
                                field = "URI"
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, f"`COUNTERData.{field}`"))
                            pass

                #Subsection: Capture `data_type` or `parent_data_type` Value
                elif key == "Data_Type":
                    if report_type == "IR":
                        field = "parent_data_type"
                    else:
                        field = "data_type"
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, f"`COUNTERData.{field}`"))
                    report_items_dict[field] = value
                    include_in_df_dtypes[field] = 'string'
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("data_type", report_items_dict[field]))

                #Subsection: Capture `YOP` Value
                elif key == "YOP":  # Based on sample data, `YOP` shouldn't be captured here; capture left in to handle possible edge cases
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.YOP`"))
                    try:
                        report_items_dict['YOP'] = int(value)  # The Int16 dtype doesn't have a constructor, so this value is saved as an int for now and transformed when when the dataframe is created
                        include_in_df_dtypes['YOP'] = 'Int16'  # `smallint` in database; using the pandas data type here because it allows null values
                    except:
                        report_items_dict['YOP'] = None  # The dtype conversion that occurs when this becomes a dataframe will change this to pandas' `NA`
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("YOP", report_items_dict['YOP']))

                #Subsection: Capture `access_type` Value
                elif key == "Access_Type":
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "`COUNTERData.access_type`"))
                    report_items_dict['access_type'] = value
                    include_in_df_dtypes['access_type'] = 'string'
                    log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("access_type", report_items_dict['access_type']))

                else:
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(value, key, "a placeholder for later unpacking"))
                    report_items_dict[key] = value
                    second_iteration_key_list.append(key)

            report_items_list.append(report_items_dict)
            log.debug(f"Record added to `report_items_list`: {report_items_list[-1]}")
        log.debug("`report_items_list` created by iteration through `Report_Items` section of SUSHI JSON.\n\n")

        #Section: Iterate Through `Items` Section of IR SUSHI JSON
        items_list = []
        if second_iteration_key_list == ["Items"] and report_type == "IR":
            for record in report_items_list:
                log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(record['Items'], "Items", "keys at the top level of the JSON"))
                for items in record['Items']:
                    items_dict = {k: v for (k, v) in record.items() if k not in second_iteration_key_list}
                    for items_key, items_value in items.items():
                        third_iteration_key_list = []

                        #Subsection: Capture `resource_name` Value
                        if items_key == "Item":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.resource_name`"))
                            if items_value is None or empty_string_regex().fullmatch(items_value):  # This value handled first because `len()` of null value raises an error
                                items_dict['resource_name'] = None
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("resource_name", items_dict['resource_name']))
                            elif len(value) > RESOURCE_NAME_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement(field, items_value)
                                log.critical(message)
                                return message
                            else:
                                items_dict['resource_name'] = items_value
                                include_in_df_dtypes['resource_name'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("resource_name", items_dict['resource_name']))

                        #Subsection: Capture `publisher` Value
                        elif items_key == "Publisher":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.publisher`"))
                            if items_value is None or empty_string_regex().fullmatch(items_value):  # This value handled first because `len()` of null value raises an error
                                items_dict['publisher'] = None
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher", items_dict['publisher']))
                            elif len(items_value) > PUBLISHER_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("publisher", items_value)
                                log.critical(message)
                                return message
                            else:
                                items_dict['publisher'] = items_value
                                include_in_df_dtypes['publisher'] = 'string'
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publisher", items_dict['publisher']))

                        #Subsection: Capture `publisher_ID` Value
                        elif items_key == "Publisher_ID":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.publisher_ID`"))
                            pass

                        #Subsection: Capture `platform` Value
                        elif items_key == "Platform":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.platform`"))
                            if items_value is None or empty_string_regex().fullmatch(items_value):  # This value handled first because `len()` of null value raises an error
                                items_dict['platform'] = None
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("platform", items_dict['platform']))
                            elif len(items_value) > PLATFORM_LENGTH:
                                message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("platform", items_value)
                                log.critical(message)
                                return message
                            else:
                                items_dict['platform'] = items_value
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("platform", items_dict['platform']))

                        #Subsection: Capture `authors` Value
                        elif items_key == "Authors":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.authors`"))
                            if not isinstance(value, list) or len(value) == 0:  # R5 SUSHI often had null values and empty strings as values for the author; this error checking serves the same purpose for R5.1 SUSHI
                                pass  # Lack of key in given record will become null value when converted to a dataframe
                            for label_and_author_name in items_value:
                                if label_and_author_name.get('Name'):
                                    if 'authors' not in items_dict and len(label_and_author_name['Name']) > AUTHORS_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("authors", label_and_author_name['Name'])
                                        log.critical(message)
                                        return message
                                    elif 'authors' not in items_dict:
                                        items_dict['authors'] = label_and_author_name['Name'].strip()
                                        include_in_df_dtypes['authors'] = 'string'
                                    elif items_dict['authors'].endswith(" et al."):
                                        break  # The loop of adding author names
                                    elif len(items_dict['authors']) + len(label_and_author_name['Name']) + 8 < AUTHORS_LENGTH:
                                        items_dict['authors'] = items_dict['authors'] + "; " + label_and_author_name['Name'].strip()
                                    else:
                                        items_dict['authors'] = items_dict['authors'] + " et al."
                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("authors", items_dict['authors']))

                        #Subsection: Capture `publication_date` Value
                        elif items_key == "Publication_Date":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.publication_date`"))
                            if items_value == "1000-01-01" or items_value == "1753-01-01" or items_value == "1900-01-01":
                                pass  # These dates are common RDBMS/spreadsheet minimum date data type values and are generally placeholders for null values or bad data
                            try:
                                items_dict['publication_date'] = date.fromisoformat(items_value)
                                include_in_df_dtypes['publication_date'] = True
                                log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("publication_date", items_dict['publication_date']))
                            except:
                                pass  # If the key-value pair is present but the value is null or a blank string, the conversion to a datetime data type would return a TypeError

                        #Subsection:  Capture `article_version` Value
                        elif items_key == "Article_Version":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "`COUNTERData.article_version`"))
                            items_dict['article_version'] = items_value
                            include_in_df_dtypes['article_version'] = 'string'
                            log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("article_version", items_dict['article_version']))

                        #Subsection: Capture Standard Identifiers
                        elif items_key == "Item_ID":
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "the standard ID fields"))
                            for ID_type, ID_value in items_value.items():

                                #Subsection: Capture `DOI` Value
                                if ID_type == "DOI":
                                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, "`COUNTERData.DOI`"))
                                    if len(ID_value) > DOI_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("DOI", ID_value)
                                        log.critical(message)
                                        return message
                                    else:
                                        items_dict['DOI'] = ID_value
                                        include_in_df_dtypes['DOI'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("DOI", items_dict['DOI']))

                                #Subsection: Capture `proprietary_ID` Value
                                elif proprietary_ID_regex().search(ID_type):
                                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, "`COUNTERData.proprietary_ID`"))
                                    if len(ID_value) > PROPRIETARY_ID_LENGTH:
                                        message = ConvertJSONDictToDataframe._increase_field_length_logging_statement("proprietary_ID", ID_value)
                                        log.critical(message)
                                        return message
                                    else:
                                        items_dict['proprietary_ID'] = ID_value
                                        include_in_df_dtypes['proprietary_ID'] = 'string'
                                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("proprietary_ID", items_dict['proprietary_ID']))

                                #Subsection: Capture `ISBN` Value
                                elif ID_type == "ISBN":
                                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, "`COUNTERData.ISBN`"))
                                    pass

                                #Subsection: Capture `print_ISSN` Value
                                elif ID_type == "Print_ISSN":
                                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, "`COUNTERData.print_ISSN`"))
                                    pass

                                #Subsection: Capture `online_ISSN` Value
                                elif ID_type == "Online_ISSN":
                                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, "`COUNTERData.online_ISSN`"))
                                    pass

                                #Subsection: Capture `URI` Value
                                elif ID_type == "URI":
                                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(ID_value, ID_type, "`COUNTERData.URI`"))
                                    pass

                        else:
                            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(items_value, items_key, "a placeholder for later unpacking"))
                            items_dict[items_key] = items_value
                            third_iteration_key_list.append(items_key)

                    items_list.append(items_dict)
                    log.debug(f"Record added to `items_list`: {items_list[-1]}")
            log.debug("`items_list` created by iteration through `Items` section of IR SUSHI JSON.\n\n")   

        #Section: Iterate Through `Attribute_Performance` Section of SUSHI JSON
        attribute_performance_list = []
        if second_iteration_key_list == ["Attribute_Performance"]:  # PR, DR, TR
            list_of_records = report_items_list
        elif third_iteration_key_list == ["Attribute_Performance"]:  # IR
            list_of_records = items_list
        else:
            message = f"The JSON is malformed, lacking the `Attribute_Performance` key."
            log.critical(message)
            return message

        for record in list_of_records:
            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(record['Attribute_Performance'], "Attribute_Performance", "keys at the top level of the JSON"))
            for attributes in record['Attribute_Performance']:
                attribute_performance_dict = {k: v for (k, v) in record.items() if k != "Attribute_Performance"}
                for attribute_performance_key, attribute_performance_value in attributes.items():
                    final_iteration_key_list = []

                    #Subsection: Capture `data_type` Value
                    if attribute_performance_key == "Data_Type":
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(attribute_performance_value, attribute_performance_key, "`COUNTERData.data_type`"))
                        attribute_performance_dict['data_type'] = attribute_performance_value
                        include_in_df_dtypes['data_type'] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("data_type", attribute_performance_dict['data_type']))

                    #Subsection: Capture `YOP` Value
                    elif attribute_performance_key == "YOP":
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(attribute_performance_value, attribute_performance_key, "`COUNTERData.YOP`"))
                        try:
                            attribute_performance_dict['YOP'] = int(attribute_performance_value)  # The Int16 dtype doesn't have a constructor, so this value is saved as an int for now and transformed when when the dataframe is created
                            include_in_df_dtypes['YOP'] = 'Int16'  # `smallint` in database; using the pandas data type here because it allows null values
                        except:
                            attribute_performance_dict['YOP'] = None  # The dtype conversion that occurs when this becomes a dataframe will change this to pandas' `NA`
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("YOP", attribute_performance_dict['YOP']))

                    #Subsection: Capture `access_type` Value
                    elif attribute_performance_key == "Access_Type":
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(attribute_performance_value, attribute_performance_key, "`COUNTERData.access_type`"))
                        attribute_performance_dict['access_type'] = attribute_performance_value
                        include_in_df_dtypes['access_type'] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("access_type", attribute_performance_dict['access_type']))

                    #Subsection: Capture `access_method` Value
                    elif attribute_performance_key == "Access_Method":
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(attribute_performance_value, attribute_performance_key, "`COUNTERData.access_method`"))
                        attribute_performance_dict['access_method'] = attribute_performance_value
                        include_in_df_dtypes['access_method'] = 'string'
                        log.debug(ConvertJSONDictToDataframe._extraction_complete_logging_statement("access_method", attribute_performance_dict['access_method']))

                    else:
                        log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(attribute_performance_value, attribute_performance_key, "a placeholder for later unpacking"))
                        attribute_performance_dict[attribute_performance_key] = attribute_performance_value
                        final_iteration_key_list.append(attribute_performance_key)

                attribute_performance_list.append(attribute_performance_dict)
                log.debug(f"Record added to `attribute_performance_list`: {attribute_performance_list[-1]}")
        log.debug("`attribute_performance_list` created by iteration through `Attribute_Performance` section of SUSHI JSON.\n\n")

        #Section:Iterate Through `Performance` Section of SUSHI JSON to Create Dataframe Lines
        performance_list = []
        for record in attribute_performance_list:
            log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(record['Performance'], "Performance", "keys at the top level of the JSON"))
            performance_dict = {k: v for (k, v) in record.items() if k != "Performance"}
            for performance_key, performance_value in record['Performance'].items():
                log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(performance_key, performance_key, "`COUNTERData.metric_type`"))
                performance_dict['metric_type'] = performance_key
                for usage_date, usage_count in performance_value.items():
                    log.debug(ConvertJSONDictToDataframe._extraction_start_logging_statement(f"{usage_date}' and '{usage_count}", performance_key, "the `COUNTERData.usage_date` and `COUNTERData.usage_count` fields"))
                    final_dict = {
                        **deepcopy(performance_dict),
                        'usage_date': datetime.strptime(usage_date, '%Y-%m').date(),
                        'usage_count': usage_count,
                    }
                    performance_list.append(final_dict)
                    log.debug(f"The {report_type} record {final_dict}  is being added to the `COUNTERData` relation.")  # Set to logging level debug because when all these logging statements are sent to AWS stdout, the only pytest output visible is the error summary statements
        log.debug("`performance_list` created by iteration through `Performance` section of SUSHI JSON.\n\n")

        #Section: Create Dataframe
        log.info(f"Unfiltered `include_in_df_dtypes`: {include_in_df_dtypes}")
        include_in_df_dtypes = {k: v for (k, v) in include_in_df_dtypes.items() if v is not False}  # Using `is` for comparison because `1 != False` returns `True` in Python
        log.debug(f"Filtered `include_in_df_dtypes`: {include_in_df_dtypes}")
        df_dtypes = {k: v for (k, v) in include_in_df_dtypes.items() if v is not True}
        df_dtypes['platform'] = 'string'
        df_dtypes['metric_type'] = 'string'
        df_dtypes['usage_count'] = 'int'
        log.info(f"`df_dtypes`: {df_dtypes}")

        log.debug(f"`performance_list` before `json.dumps()`  is type {type(performance_list)}.")
        records_orient_list = json.dumps(  # `pd.read_json` takes a string, conversion done before method for ease in handling type conversions
            performance_list,
            default=ConvertJSONDictToDataframe._serialize_dates,
        )
        if len(records_orient_list) > 1500:
            log.debug(f"`records_orient_list` after `json.dumps()` (type {type(records_orient_list)}) is too long to display.")
        else:
            log.debug(f"`records_orient_list` after `json.dumps()` (type {type(records_orient_list)}):\n{records_orient_list}")
        df = pd.read_json(
            io.StringIO(records_orient_list),  # Originally from https://stackoverflow.com/a/63655099 in `except` block; now only option due to `FutureWarning: Passing literal json to 'read_json' is deprecated and will be removed in a future version. To read from a literal string, wrap it in a 'StringIO' object.`
            orient='records',
            dtype=df_dtypes,  # This only sets numeric data types
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        log.info(f"Dataframe info immediately after dataframe creation:\n{return_string_of_dataframe_info(df)}")

        df = df.astype(df_dtypes)  # This sets the string data types
        log.debug(f"Dataframe dtypes after conversion:\n{return_string_of_dataframe_info(df)}")
        if include_in_df_dtypes.get('publication_date'):  # Meaning the value was changed to `True`
            df['publication_date'] = pd.to_datetime(
                df['publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
            )
        if include_in_df_dtypes.get('parent_publication_date'):  # Meaning the value was changed to `True`
            df['parent_publication_date'] = pd.to_datetime(
                df['parent_publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
            )
        df['usage_date'] = pd.to_datetime(df['usage_date'])
        df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])#.dt.tz_localize(None)

        log.info(f"Dataframe info:\n{return_string_of_dataframe_info(df)}")
        return df
    

    @staticmethod
    def _serialize_dates(dates):
        """This method allows the `json.dumps()` method to serialize (convert) `datetime.datetime` and `datetime.date` attributes into strings.

        This method and its use in are adapted from https://stackoverflow.com/a/22238613.

        Args:
            dates (datetime.datetime or datetime.date): A date or timestamp with a data type from Python's datetime library

        Returns:
            str: the date or timestamp in ISO format
        """
        if isinstance(dates,(date, datetime)):
            return dates.isoformat()
        else:
            raise TypeError  # So any unexpected non-serializable data types raise a type error
    

    @staticmethod
    def _extraction_start_logging_statement(value, key, field):
        """This method creates the logging statement at the beginning of an attribute value extraction.

        Args:
            value (str): the value being extracted
            key (str): the dictionary key of the value being extracted
            field (str): the `nolcat.methods.COUNTERData` field the value is being assigned to

        Returns:
            str: the logging statement
        """
        return f"Preparing to move '{value}' from the key '{key}' to {field}."
    

    @staticmethod
    def _extraction_complete_logging_statement(field, value):
        """This method creates the logging statement indicating a successful attribute value extraction.

        Args:
            field (str): the `nolcat.methods.COUNTERData` field the value is assigned to
            value (str): the extracted value

        Returns:
            str: the logging statement
        """
        return f"Added `COUNTERData.{field}` value '{value}' to the row dictionary."
    

    @staticmethod
    def _increase_field_length_logging_statement(field, length):
        """This method creates the logging statement indicating a field length needs to be increased.

        Args:
            field (str): the `nolcat.methods.COUNTERData` field to adjust
            length (int): the length of the field

        Returns:
            str: the logging statement
        """
        return f"Increase the `COUNTERData.{field}` max field length to {ceil(length * 1.1)}."