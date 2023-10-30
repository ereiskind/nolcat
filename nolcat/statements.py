"""The repo features a wide variety of logging statements and log-like output statements. Many of these are consistent within a function or module, but others are standardized with a specific logging level and structure throughout the entire repository; to avoid repetition, such statements are established as functions here. All logging statements and log-like output statements are full sentences ending in periods.
"""

from pathlib import Path


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


def format_list_for_stdout(stdout_list):
    """Changes a list into a string which places each item of the list on its own line.

    Using the list comprehension allows the function to accept generators, which are transformed into lists by the comprehension, and to handle both lists and generators with individual items that aren't strings by type juggling.

    Args:
        stdout_list (list or generator): a list for pretty printing to stdout
    
    Returns:
        str: the list contents with a line break between each item
    """
    return '\n'.join([str(file_path) for file_path in stdout_list])


#Section: General Statements
#Subsection: Logging/Output Statements
def about_to_statement():
    '''A marker that something is about to happen, so if the program crashes immediately after that log statement, what the program was doing when it crashed is clear 
    
    Debug logging statement
    '''
    pass


def initialize_relation_class_object_statement():
    '''Successful initialization of a relation class object
    
    In the function that called ``query_database()``
        Debug logging statement
    Fixture:
        Info logging statement
    '''
    #"The following `<name of relation class>` object was initialized based on the query results:\n<object>"
    #"`<fixture function name>()` returning the following `<name of relation class>` object which was initialized based on the query results:\n<object>."
    pass


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


#Subsection: Error Statements
def unable_to_convert_SUSHI_data_to_dataframe_statement():
    '''Unable to convert file or JSON into dataframe

    Error logging statement
    '''
    # "Changing the <JSON-like dictionary of <report type> for <statistics source name>/uploaded COUNTER data workbooks> into a dataframe raised the error <error>."
    pass


def unable_to_get_updated_primary_key_values_statement(relation, error):
    """This statement prepares the error raised by `nolcat.app.first_new_PK_value()` for the logging output.

    Args:
        relation (str): the relation name
        error (Exception): the Python Exception raised by `nolcat.app.first_new_PK_value()`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Running the function `first_new_PK_value()` for the relation `{relation}` raised the error {error}."


def Flask_error_statement():
    '''Page not found

    Error logging statement
    '''
    pass


#Section: Files, File Organization, and File I/O
#Subsection: Logging/Output Statements
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
        alone (bool, optional): indicates if any of the aforementioned information about the statement's location is included; defaults to `True`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    main_value = f"he files in the folder {file_path.resolve()}\n{format_list_for_stdout(file_path.iterdir())}"
    if alone:
        return "T" + main_value
    else:
        return " t" + main_value


def check_if_folder_exists_statement(file_path, alone=True):
    """This statement indicates if there's a file at the given file path for the logging output.

   Information about the logging statement's relative location in a function can be added at the very beginning of the statement.

    Args:
        file_path (pathlib.Path): the path to the file being checked
        alone (bool, optional): indicates if any of the aforementioned information about the statement's location is included; defaults to `True`

    Returns:
        str: the statement for outputting the arguments to logging
    """
    main_value = f"here's a file at {file_path.resolve()}: {file_path.is_file()}"
    if alone:
        return "T" + main_value
    else:
        return " t" + main_value


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


#Section: Database Interactions
#Subsection: Logging/Output Statements
def return_value_from_query_statement(return_value, type_of_query=None):
    """This statement shows an individual value or sequence of values returned by a call to `nolcat.app.query_database()`.

    Args:
        return_value (str, int, or tuple): the value(s) returned by `nolcat.app.query_database()`
        type_of_query (str, optional): some descriptive information about the query; defaults to `None`

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
            main_value = f"{main_value}{return_value} (type {type(return_value)}), "
            i += 1
        return f"{main_value[:-2]} were extracted."
    else:
        return f"{main_value}{return_value} (type {type(return_value)}) was extracted."


def return_database_from_query_statement():
    '''Dataframe returned by SQL query

    Debug logging statement
    In the function that called ``query_database()``
    '''
    #"The result of the query for <what was being queried for>:\n<dataframe>"
    pass


def add_data_and_update_database_success_statement():
    '''Indication that adding COUNTER data to database and updating corresponding values succeeded

    Debug logging statement
    '''
    #``load_data_into_database()`` or ``upload_file_to_S3_bucket()`` response followed by ``update_database()`` response
    pass


#Subsection: Error Statements
def database_query_fail_statement():
    '''Indication that database query failed

    Warning logging statement
    In the function that called ``query_database()``
    Options:
        * Individual value = "return requested value"
        * Dataframe = "requested dataframe"
        * Flask page = "load requested page"
    '''
    #"Unable to <see above> because <slightly modified return value for ``query_database()``>"
    #In Flask functions, messages are flashed
    pass


def database_update_fail_statement():
    '''Indication that database update failed

    Warning logging statement
    In the function that called ``update_database()``
    '''
    pass


def add_data_success_and_update_database_fail_statement():
    '''Indication that adding records to database succeeded, but updating corresponding values failed
    
    Warning logging statement
    '''
    #"<``load_data_into_database()`` or ``upload_file_to_S3_bucket()`` response>, but updating the `<name of relation>` relation automatically failed, so the SQL update statement needs to be submitted via the SQL command line:\n<SQL update statement>"
    pass


def database_function_skip_statements(return_value, is_test_function=True):
    """This statement provides the logging output when a pytest skip is initiated after a `nolcat.app.query_database()`, `nolcat.app.load_data_into_database()`, or `nolcat.app.update_database()` function fails.
    
    Args:
        return_value (str): the error message returned by the database helper function
        is_test_function (bool, optional): indicates if this function is being called within a test function; defaults to `True` 
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    if is_test_function:
        return f"Unable to run test because it relied on {return_value[0].lower()}{return_value[1:].replace(' raised', ', which raised')}"
    else:
        return f"Unable to create fixture because it relied on {return_value[0].lower()}{return_value[1:].replace(' raised', ', which raised')}"


#Section: SUSHI API Calls
#Subsection: Logging/Output Statements
def successful_SUSHI_call_statement():
    '''Successful SUSHI call

    Info logging statement
    In the ``SUSHICallAndResponse.make_SUSHI_call()`` method
    '''
    #"Call to `<type of endpoint>` endpoint for <statistics source name> successful."
    pass


def _harvest_R5_SUSHI_success_statement():
    '''Responses to the ``StatisticsSources._harvest_R5_SUSHI()`` method

    Debug logging statement
    '''
    #"The SUSHI harvest for statistics source <statistics source name> <<for FY <FY year> (if there's a specific fiscal year for the harvest)>> successfully found <number of records> records."
    pass


#Subsection: Error Statements
def failed_SUSHI_call_statement_statement():
    '''Failed ``SUSHICallAndResponse.make_SUSHI_call()`` methods

    Warning logging statement
    "SUSHI" is included when the error is a SUSHI error handled by the program
    "returned no usage data because the call" is included when the SUSHI error indicates no usage is being returned
    '''
    #"The call to the `<name of report>` endpoint for <statistics source name> <returned no usage data because the call> raised the <SUSHI> error<s> <error; in the case of multiple SUSHI error message, line breaks before, after, and in between each error statement>."
    #Additionally, when part of a month-by-month gathering: "None of the SUSHI data for that endpoint and statistics source will be loaded into the database."
    #Additionally, if any listed SUSHI error is causing API calls to stop: "API calls to <statistics source name> have stopped and no other calls will be made."
    pass


def no_data_returned_by_SUSHI_statement():
    '''Indicates a report that returned no data without a SUSHI error indicating why

    Warning logging statement
    In the ``StatisticsSources._harvest_R5_SUSHI()`` method
    "because the SUSHI data didn't have a `Report_Items` section" included only if true
    "usage" is excluded if the SUSHI call returns an empty string
    '''
    #"The call to the `<name of report>` endpoint for <statistics source name> returned no <usage> data <because the SUSHI data didn't have a `Report_Items` section>."
    pass


def attempted_SUSHI_call_with_invalid_dates_statement():
    '''SUSHI call attempted with invalid dates

    Error logging statement
    '''
    #"The given end date of <end date> is before the given start date of <start date>, which will cause any SUSHI API calls to return errors; as a result, no SUSHI calls were made. Please correct the dates and try again."
    pass


"""Other standardized logging statements, including those in a single class:

* "Starting `function_name()`" statements
    * Info logging statement
    * At the beginning of all functions and methods except for test functions, test fixtures, and those returning a value within five statements
    * Structure: "Starting `<name of function/method>()` for <relevant parameters>."

* Adding to dictionary in the ``ConvertJSONDictToDataframe.create_dataframe()`` method
    * Debug logging statement
    * Structure: "Added `COUNTERData.<dictionary key>` value <dictionary value> to `<name of dict>`."

* Finding values for a given field are longer than the field's max length
    * Critical logging statement
    * In the ``ConvertJSONDictToDataframe`` class
    * Structure: "Increase the `<attribute name>` max field length to <length of the value found + 10%>."

* Upload database initialization relations
    * Debug logging statement; errors are error logging statement
    * In the ``nolcat.initialization.views`` module
    * Success structure: "The `<relation name>` FileField data:\n<FileField object>"
    * Blank file uploaded (failure) structure: "The `<relation name>` relation data file was read in with no data."
"""