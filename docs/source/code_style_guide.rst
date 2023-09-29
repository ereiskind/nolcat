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

* Finding values for a given field are longer than the field's max length

  * Critical logging statement
  * In the ``ConvertJSONDictToDataframe`` class
  * Structure: "Increase the `<attribute name>` max field length to <length of the value found + 10%>."

* File input and output --> #FileIOError, #FileIO

  * Info and debug logging statements; errors are error logging statement
  * *Needs to be divided into subcategories*
  * Structure:

    * S3 delete file operation failed: ""

* Unable to convert file or JSON into dataframe --> #create_dataframeError
* Unable to convert data types --> #ConversionError
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
    * Multiple reports: "All of the calls to <statistics source name> returned no usage data."

* SUSHI COUNTER error returned --> #SUSHIErrors

  * Warning logging statement

* SUSHI call attempted with invalid dates --> #SUSHIDateError

  * Error logging statement

* Report other than customizable reports --> #UnknownSUSHIReport

  * Warning logging statement


MySQL I/O
---------
* Load data into MySQL database

  * Info logging statement; errors are error logging statement
  * In the ``load_data_into_database()`` function
  * Structure:

    * Input success: "Successfully loaded <number of loaded records> records into the <name of relation> relation."
    * Input failure: "Loading data into the <name of relation> relation raised the error <Python exception>."

* Query database

  * Debug logging statement; errors are error logging statement
  * In the ``query_database()`` function
  * Structure:

    * Successful query: "The complete response to <query text>:\n<dataframe returned by query>"
    * Failed query: "The query <query text> raised the error <Python exception>."

* Indication of query result in calling function --> #SQLErrorReturn, #QueryReturn, #QueryToRelationClass

  * **???** logging statement; errors are **???** logging statement
  * In the function that called ``query_database()``
  * Structure:

    * Successful dataframe output: ""
    * Successful single-value output: ""
    * Successful statistics resource source: ""

* Replace with database update function to be written --> #ReplaceWithUpdateFunction

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