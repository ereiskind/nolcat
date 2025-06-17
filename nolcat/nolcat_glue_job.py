from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import boto3

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
# app.last_day_of_month

# app.ISSN_regex

# app.ISBN_regex

# app.AWS_timestamp_format

# app.non_COUNTER_file_name_regex

# app.empty_string_regex

#SUBSECTION: Formatting Changes
# app.return_string_of_dataframe_info

# statements.format_list_for_stdout

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