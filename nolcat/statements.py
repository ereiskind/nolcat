"""The repo features a wide variety of logging statements and log-like output statements. Many of these are consistent within a function or module, but others are standardized with a specific logging level and structure throughout the entire repository; to avoid repetition, such statements are established as functions here. All logging statements and log-like output statements are full sentences ending in periods.
"""


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


def fixture_variable_value_declaration_statement():
    '''Statements at the start of fixture functions adding the variables to stdout/logging for troubleshooting purposes
    
    Debug logging statement
    When the value is a pathlib.Path object, ``.resolve()`` is added to output an absolute file path
    '''
    #"In `<fixture function name>()`, the `<variable name>` is <value>."
    pass


#Subsection: Error Statements
def unable_to_convert_SUSHI_data_to_dataframe_statement():
    '''Unable to convert file or JSON into dataframe

    Error logging statement
    '''
    # "Changing the <JSON-like dictionary of <report type> for <statistics source name>/uploaded COUNTER data workbooks> into a dataframe raised the error <error>."
    pass


def unable_to_get_updated_primary_key_values_statement():
    '''Unable to get updated primary key values
    
    Warning logging statement
    In the function that called ``nolcat.app.first_new_PK_value()``
    '''
    #"Running the function `first_new_PK_value()` for the relation `<relation>` raised the error <Python exception>."
    pass


def Flask_error_statement():
    '''Page not found

    Error logging statement
    '''
    pass


def database_function_skip_statements():
    '''Indication that ``query_database()``, ``load_data_into_database()``, or ``update_database()`` failed, so the fixture or test is being skipped to avoid it doing the same
    
    ?
    '''
    #"Unable to <create fixture/run test> because it relied on <slightly modified return value for database function>"
    pass


#Section: Files, File Organization, and File I/O
#Subsection: Logging/Output Statements
def file_IO_statement():
    ''' About to upload or download a file
    
    Info logging statement
    '''
    #"About to <upload/download> file '<name of file>' from <origin location> to <destination location>."
    pass


def list_folder_contents_statement():
    '''Lists contents of folder

    Debug logging statement
    Information about the logging statement's relative location in a function can be added at the very beginning of the statement 
    '''
    #"The files in the folder <absolute path to folder>\n<list of files in folder separated by newlines>"
    pass


def check_if_folder_exists_statement():
    '''Checks if file at given path exists

    Debug logging statement
    Information about the logging statement's relative location in a function can be added at the very beginning of the statement
    '''
    #"There's a file at <absolute path to file>: <Boolean>."
    pass


#Subsection: Error Statements
def failed_upload_to_S3_statement():
    '''Indication of upload to S3 in calling function

    Critical logging statement
    In the function that called ``nolcat.app.upload_file_to_S3_bucket()``
    '''
    #"Uploading the file <file name> to S3 in `<function name, including path>()` failed because <error message starting with lowercase letter> NoLCAT HAS NOT SAVED THIS DATA IN ANY WAY!"
    pass


def unable_to_delete_test_file_in_S3_statement():
    '''Unable to delete file in S3 bucket after tests
    
    Error logging statement
    '''
    #"Trying to remove file `<file name>` from the S3 bucket raised the error <error>."
    pass


#Section: Database Interactions
#Subsection: Logging/Output Statements
def return_value_from_query_statement():
    '''Individual value or sequence of values returned by SQL query

    Debug logging statement
    In the function that called ``query_database()``
    '''
    #"The <type of query, optional> query returned a dataframe from which <value from dataframe> (type <type of data from dataframe>) was extracted."
    #For multiple value, repeat the statement of the values and their data types and end with "were extracted."
    pass


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