"""The repo features a wide variety of logging statements and log-like output statements. Many of these are consistent within a function or module, but others are standardized with a specific logging level and structure throughout the entire repository; to avoid repetition, such statements are established as functions here. All logging statements and log-like output statements are full sentences ending in periods.
"""

from pathlib import Path
import re


#Section: Simple Helper Functions
# These are helper functions that don't work as well in `nolcat.app` for various reasons

def file_extensions_and_mimetypes():
    """A dictionary of the file extensions for the types of files that can be downloaded to S3 via NoLCAT and their mimetypes.
    
    This helper function is called in `create_app()` and thus must be before that function.
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


#Section: General Statements
#Subsection: Logging/Output Statements
def initialize_relation_class_object_statement(relation_class_name, object_value):
    """This statement shows the value of a relation class object initialized using the values returned from a query.

    Args:
        relation_class_name (str): the name of the relation class
        object_value (nolcat.models): a relation class object

    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"The following {relation_class_name} object was initialized based on the query results:\n{object_value}"


#Subsection: Error Statements
def unable_to_get_updated_primary_key_values_statement(relation, error):
    """This statement prepares the error raised by `nolcat.app.first_new_PK_value()` for the logging output.

    Args:
        relation (str): the relation name
        error (Exception): the Python Exception raised by `nolcat.app.first_new_PK_value()`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Running the function `first_new_PK_value()` for the relation `{relation}` raised the error {error}."


#Section: Files, File Organization, and File I/O
#Subsection: Error Statements
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


#Subsection: Success Regexes
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


#Section: Database Interactions
#Subsection: Logging/Output Statements
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


#Subsection: Error Statements
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


#Subsection: Success Regexes
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