Source Code Style Guide
#######################

What follows are details about the style of the code and its documentation that have been recorded for the sake of consistent application across the code base.

Python Code
***********

Logging Statements
==================
The repo features a wide variety of logging statements and log-like output statements. Many of these are consistent within a function or module, but others are standardized with a specific logging level and structure throughout the entire repository; statements with very specific standardizations are recorded here. All logging statements and log-like output statements are full sentences ending in periods.

Logging Markers
---------------
* "Starting `function_name()`" statements

  * Info logging statement
  * At the beginning of all functions and methods except for test functions, test fixtures, and those returning a value within five statements
  * Structure: "Starting `<name of function/method>()` for <relevant parameters>."

* Signpost

  * Debug logging statement
  * These are meant to both provide information and provide extra guidance in determining the location of errors
  * As informational statements, there's no common structure, but they have an asterisk at the beginning and end of the statement

* Adding to dictionary in the ``ConvertJSONDictToDataframe.create_dataframe()`` method

  * Debug logging statement
  * Structure: "Added `COUNTERData.<dictionary key>` value <dictionary value> to `<name of dict>`."

* About to take an action --> #AboutTo

  * Debug or info logging statement
  * A marker that something is about to happen, so if the program crashes immediately after that log statement, what the program was doing when it crashed is clear
  * Includes starting iterations
  * Structure: **???**

General Errors and In-Test Issues
---------------------------------
* Pytest skips

  * Requested report not offered: "<report> not offered by this statistics source."
  * Requested report returned a SUSHI error: "The test is being skipped because the API call returned a server-based SUSHI error."
  * Requested report returned no data: "The test is being skipped because the API call returned no data."

* Variable value declarations in fixtures

  * Debug logging statement
  * Statements at the start of fixture functions adding the variables to stdout/logging for troubleshooting purposes
  * When the value is a pathlib.Path object, ``.resolve()`` is added to output an absolute file path
  * Structure: "In `<fixture function name>()`, the `<variable name>` is <value>."

* Finding values for a given field are longer than the field's max length

  * Critical logging statement
  * In the ``ConvertJSONDictToDataframe`` class
  * Structure: "Increase the `<attribute name>` max field length to <length of the value found + 10%>."

* Managing data files in the repo --> #FileIOError, #FileIO

  * Structure:

    * Success:

      * Check for a previously existing file in repo:

        * Debug logging statement
        * Information about the logging statement's relative location in a function can be added at the very beginning of the statement
        * Structure:

          * Check for a single file: "There's a file at <absolute path to file>: <Boolean>."
          * Check the contents of a folder: "The files in the folder <absolute path to folder>\n<list of files in folder separated by newlines>"

      * File successfully created:
      * File name successfully created:
      * Other:

    * Failure:

      * Other:

* File I/O with the host machine --> #FileIOError, #FileIO

  * Structure:

    * Success:

      * File uploaded:
      * WTForms FileField value ingested

        * Debug logging statement
        * In the ``nolcat.initialization.views`` module
        * Structure: "The `<relation name>` FileField data:\n<FileField object>"

      * File downloaded:

    * Failure:

      * Upload features invalid file extension:

        * Error logging statement
        * Structure: "The file extension of <full file path of uploaded file> is invalid. Please convert the file to use one of the following extensions and try again:\n<list of valid file extension from ``file_extensions_and_mimetypes()``>"

      * Blank file uploaded

        * Error logging statement
        * In the ``nolcat.initialization.views`` module
        * Structure: "The `<relation name>` relation data file was read in with no data."

* File I/O with S3 --> #FileIOError, #FileIO

  * Structure:

    * Success:

      * File loaded into S3:

        * Info logging statement
        * In the ``nolcat.app.upload_file_to_S3_bucket()`` function
        * Structure: "Successfully loaded the file <name given to file> into the <name of bucket> S3 bucket."

    * Failure:

      * Unable to upload file to S3 bucket:

        * Error logging statement if final; warning logging statement if not
        * In the ``nolcat.app.upload_file_to_S3_bucket()`` function
        * Structure: "Running the function `<function>()` on <variable on which the function was run> (type <variable on which the function was run>) raised the error <Python exception>."
        * If the logging statement isn't final, a statement that another function will be tried is added to the end

      * Unable to delete file in S3 bucket:

* Unable to convert file or JSON into dataframe

  * Warning logging statement
  * Structure:

    * From SUSHI: "JSON-like dictionary of <report type> for <statistics source name> couldn't be converted into a dataframe."
    * From workbooks: "Trying to consolidate the uploaded COUNTER data workbooks into a single dataframe raised the error <error>."

* Page not found --> #404

  * Error logging statement

SUSHI Calls
-----------
* API call responses

  * Info logging statement; errors are error logging statement
  * In the ``SUSHICallAndResponse._make_API_call()`` method
  * Structure:

    * HTTP response codes through the object: "<HTTP verb> response code: <HTTP response object>"
    * Successful request: "<HTTP verb> request to <plain text location called> at <URL> successful."
    * HTTP errors returned: "<HTTP verb> request to <plain text location called> raised <list errors>."

* Successful SUSHI status or reports call via the ``SUSHICallAndResponse.make_SUSHI_call()`` method

  * Info logging statement
  * Structure: "Call to `<type of endpoint>` endpoint for <statistics source name> successful."

* Failed ``StatisticsSources._harvest_single_report()`` or ``SUSHICallAndResponse.make_SUSHI_call()`` methods

  * Warning logging statement
  * Structure: "The call to the `<name of report>` endpoint for <statistics source name> raised the error <SUSHI error>."

    * Additionally, when part of a month-by-month gathering: "None of the SUSHI data for that endpoint and statistics source will be loaded into the database."

* Responses to the ``StatisticsSources._harvest_R5_SUSHI()`` method

  * Debug logging statement; errors are warning logging statement
  * Structure:

    * Success: "The SUSHI harvest for statistics source <statistics source name> <<for FY <FY year> (if there's a specific fiscal year for the harvest)>> successfully found <number of records> records."
    * Failure: "SUSHI harvesting for statistics source <statistics source name> <<for FY <FY year> (if there's a specific fiscal year for the harvest)>> raised the error <error>."

* No data returned by SUSHI call
  
  * Warning logging statement
  * Structure:

    * Single report: "The call<s> to the `<name of report>` endpoint for <statistics source name> returned no usage data."
    * Single report without `Report_Items` section: "The call to the `<name of report>` endpoint for <statistics source name> returned no usage data because the SUSHI data didn't have a `Report_Items` section."
    * Single report was empty string (error logging statement): "The call to the `<name of report>` endpoint for <statistics source name> returned no data."
    * Multiple reports: "All of the calls to <statistics source name> returned no usage data."

* SUSHI COUNTER error returned

  * Warning logging statement
  * Structure:

    * Basic: "The call to the `<name of report>` endpoint for <statistics source name> raised the SUSHI error(s) <SUSHI error message; if more than one, line breaks before, after, and in between each error statement>"
    * Errors resulting in no usage data: "The call to the `<name of report>` endpoint for <statistics source name> returned no usage data because the call raised the following error(s):<list of SUSHI error messages, each on its own line, with a line break before>"

      * Additionally, if any listed error is causing API calls to stop: "API calls to <statistics source name> have stopped and no other calls will be made."

* SUSHI call attempted with invalid dates

  * Error logging statement
  * Structure: "The given end date of <end date> is before the given start date of <start date>, which will cause any SUSHI API calls to return errors; as a result, no SUSHI calls were made. Please correct the dates and try again."

MySQL I/O
---------
* Load data into MySQL database

  * Info logging statement; errors are error logging statement
  * In the ``load_data_into_database()`` function
  * Structure:

    * Input success: "Successfully loaded <number of loaded records> records into the <name of relation> relation."
    * Input failure: "Loading data into the <name of relation> relation raised the error <Python exception>."

* Query database

  * Info logging statement; errors are error logging statement
  * In the ``query_database()`` function
  * Structure:

    * Successful query: "The complete response to `<query text>`:\n<dataframe returned by query>"
    * Failed query: "Running the query `<query text>` raised the error <Python exception>."

* Update database

  * Info logging statement; errors are error logging statement
  * In the ``update_database()`` function
  * Structure:

    * Successful update: "Successfully preformed the update `<update statement text>`."
    * Failed update: "Running the update statement `<update statement text>` raised the error <Python exception>."

* Indication of data loading result in calling function

  * Debug logging statement; errors are warning logging statement
  * In the function that called ``load_data_into_database()``
  * Structure:

    * Success: *Return value that will indicate to "view_lists/edit_record.html" that the record was updated*
    * Failure: *Return value that will indicate to "view_lists/edit_record.html" that the attempted change failed*

* Indication of query result in calling function

  * Debug logging statement; errors are warning logging statement
  * In the function that called ``query_database()``
  * Structure:

    * Success:

      * Successful individual value(s) output: "The <type of query, optional> query returned a dataframe from which <value from dataframe> (type <type of data from dataframe>) was extracted."

        * For multiple value, repeat the statement of the values and their data types and end with "were extracted."

      * Successful dataframe output: "The result of the query for <what was being queried for>:\n<dataframe>"
      * Successful initialization of a relation class object: "The following `<name of relation class>` object was initialized based on the query results:\n<object>"
      * Successful initialization of a relation class object in a fixture (info): "`<fixture function name>()` returning the following `<name of relation class>` object which was initialized based on the query results:\n{yield_object}."

    * Failure:

      * Returning string: Repeat the ``query_database()`` error message
      * Helper function: Pass the ``query_database()`` error message to the database that called the helper function --> #ToDo:: Have calls handle string return indicating error
      * Returning integer: "Unable to return requested sum because it relied on <slightly modified error message>"
      * Fixture function: "Unable to create fixture because it relied on <slightly modified error message>" in ``pytest.skip()``
      * Test function: "Unable to run test because it relied on <slightly modified error message>" in ``pytest.skip()``
      * Non-homepage view function: "Unable to load requested page because it relied on <slightly modified error message>" in flashed message, return to blueprint homepage
      * Homepage view function: page outside of blueprints for sharing this message--> #HomepageSQLError
      * Replace when methods in `Vendors` relation class are written --> #SQLDataframeReturnError

* Indication of update result in calling function

  * Debug logging statement; errors are warning logging statement
  * In the function that called ``update_database()``
  * Structure:

    * Success:

      * Database updated to reflect successfully loaded data: ``load_data_into_database()`` response followed by ``update_database()`` response
      * *Return value that will indicate to "view_lists/edit_record.html" that the record was updated*

    * Failure:

      * Failure of database updates that reflect successfully loaded data:

        * Logging statement: "Updating the `<name of relation>` relation automatically failed, so the SQL update statement needs to be submitted via the SQL command line:\n<SQL update statement>"
        * Overall function return value features ``load_data_into_database()`` response followed by the above logging statement

      * *Return value that will indicate to "view_lists/edit_record.html" that the attempted change failed*
      * *Return value that will indicate to "view_lists/edit_record.html" that there was a problem*

reStructured Text
*****************

* Code snippets are marked with double backticks
* Per the Python style guide,

  * h1 uses hashes: ``#``
  * h2 uses asterisks: ``*``
  * h3 uses equals: ``=``
  * h4 uses dashes: ``-``
  * h5 uses carats: ``^``
  * h6 uses double quotes: ``"``

Naming Conventions
******************

* Database naming conventions are used in the codebase and the documentation

  * The Flask-SQLAlchemy relation classes are named in PascalCase, also called UpperCamelCase
  * The database itself, through the ``__tablename__`` attribute, use camelCase
  * Field names are lowercase_with_underscores

Naming Flask Routes and Webpages
================================

* Flask routes that handle data ingestion from a form will contain at least two ``return`` statements with the ``render_template`` function: one for the page the form is on, and one for each form representing the page the web app will go to when the form is submitted
* Each blueprint will have a homepage with the route ``/`` and the function name ``homepage``; Flask works best when all HTML pages have unique names