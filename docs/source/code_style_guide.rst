Source Code Style Guide
#######################

What follows are details about the style of the code and its documentation that have been recorded for the sake of consistent application across the code base.

Python Code
***********

Logging Statements
==================
Each set of circumstances needing a logging statement or a log-like output statement has a specific logging level and structure assigned to it. All such statements are full sentences ending in periods.

* "Starting `function_name()`" statements

  * Info logging statement
  * At the beginning of all functions and methods except for test functions, test fixtures, and those returning a value within five statements
  * Structure: "Starting `<name of function/method>()` for <relevant parameters>."

* Starting an iteration

  * Debug logging statement

* Adding an item to a dictionary

  * Debug logging statement

* Logging values returned from other functions that provide INFO-level logging statements with the values they return

  * Debug logging statement

* "Starting `function_name()`" statements

  * Info logging statement

* The statement with the value a function is returning

  * Info logging statement

* Status messages duplicated with message flashing

  * Info logging statement

* HTTP response code for API call

  * Info logging statement

* Statements triggered by failing API call

  * Warning logging statement

* SUSHI report errors

  * Warning logging statement

* A problem with MySQL I/O

  * Error logging statement

* A problem with file I/O

  * Error logging statement

* Failed API call

  * Error logging statement

* 404 Page not found

  * Error logging statement

* Finding values for a given field are longer than the field's max length

  * Critical logging statement

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