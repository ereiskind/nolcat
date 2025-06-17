NoLCAT Development Roadmap
##########################
This page contains all the current to-dos and possible plans for the NoLCAT program.

To Investigate
**************
This is a list of issues encountered over the course of development that require further investigation.

* A ScienceDirect SUSHI call returned `401 Client Error: Unauthorized for url`; since Elsevier manages SUSHI out of the developer/API portal for all their products, the credentials can't be easily checked and/or reset
* J-STAGE uses a customer ID and the institutional IP ranges for authentication, so SUSHI calls from AWS are denied access
* Morgan & Claypool raised `HTTPSConnectionPool(host='www.morganclaypool.com', port=443): Max retries exceeded with url: /reports?... (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x7f838d4b84f0>, 'Connection to www.morganclaypool.com timed out. (connect timeout=90)')) and HTTPSConnectionPool(host='www.morganclaypool.com', port=443): Max retries exceeded with url: /reports?... (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f838d4b8eb0>: Failed to establish a new connection: [Errno 110] Connection timed out'))`
* Certificate issues raising errors with

  * *Allen Press/Pinnacle Hosting*: `HTTPSConnectionPool(host='pinnacle-secure.allenpress.com', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'pinnacle-secure.allenpress.com' doesn't match either of '*.literatumonline.com', 'literatumonline.com'")))`
  * *Grain Science Library*: `HTTPSConnectionPool(host='aaccipublications.aaccnet.org', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'aaccipublications.aaccnet.org' doesn't match either of '*.scientificsocieties.org', 'scientificsocieties.org'")))`
  * *Adam matthew*: `HTTPSConnectionPool(host='www.counter.amdigital.co.uk', port=443): Max retries exceeded with url: /CounterSushi5Api/status?... (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1131)')))`
  * *Sciendo*: `HTTPSConnectionPool(host='ams.degruyter.com', port=443): Max retries exceeded with url: /rest/COUNTER/v5/status?... (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fb5414a4520>: Failed to establish a new connection: [Errno -2] Name or service not known'))`

Planned Iterations
******************

Move Code to Glue Jobs and Data to Parquet
==========================================
* Create main Glue job file

  * Move functions in "nolcat/statements.py" and non-Flask functions in "nolcat/app.py" to "nolcat_glue_job.py"
  * Update function call chain diagram to reflect above changes
  * Move test functions corresponding to the functions above, along with all necessary fixtures, to "test_nolcat_glue_job.py"
  * Update function call chain diagram to reflect above changes
  * For all tests, get call chains and adjust conftest calls
  * Push changes to repo, then pull changes into Glue
  * Confirm all tests still pass

* Review placement of functions in conftest
* Develop `nolcat.nolcat.models.COUNTERData` relation to parquet file transformer

  * Develop method to switch data storage format
  * Save test data in parquet format
  * Run `SELECT statistics_source_ID, report_type, usage_date, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, usage_date, report_creation_date;` on production data to confirm available production data and find out what parquet files need to be created
  * Determine how files with production data lacking timestamps should be named (null? get dates from shared files?)

* Move `nolcat.ConvertJSONDictsToDataframe` to Glue job

  * Move class `nolcat.ConvertJSONDictsToDataframe` into "nolcat/nolcat/nolcat_glue_job.py"
  * Update function call chain diagram to reflect above changes
  * Move length constants out of class, then update reference to them in "nolcat/nolcat/models.py"
  * Move test functions corresponding to the class, along with all necessary fixtures, to "test_nolcat_glue_job.py"
  * Update function call chain diagram to reflect above changes
  * For all tests, get call chains and adjust conftest calls
  * Delete files with all content moved elsewhere
  * Confirm all tests still pass
  * Pull file into Glue job
  * Confirm configs still set properly

* Save `nolcat.ConvertJSONDictsToDataframe` output as parquet in S3

  * Confirm all methods of `nolcat.ConvertJSONDictsToDataframe` except `nolcat.ConvertJSONDictsToDataframe.create_dataframe()` are private
  * Get list of all calls to `nolcat.ConvertJSONDictsToDataframe.create_dataframe()`
  * Add `statistics_source_ID` and `report_type` to class inputs
  * End `nolcat.ConvertJSONDictsToDataframe.create_dataframe()` by saving a parquet file to S3 (confirm S3 file name can be created at saving and can include stats source ID and report creation timestamp)
  * Adjust calls to `nolcat.ConvertJSONDictsToDataframe.create_dataframe()` to not expect return values
  * Adjust tests and function call chain diagram to correspond with above changes
  * Add check for saved parquet or error file after call to `nolcat.ConvertJSONDictsToDataframe.create_dataframe()`
  * List all functions in function call chains ending in a call to `nolcat.ConvertJSONDictsToDataframe.create_dataframe()`
  * For all functions above, adjust to anticipate no return value if successful
  * Adjust tests and function call chain diagram to correspond with above changes

* Determine if testing in Glue is needed, and if so, save parameters to use for tests to test files
* Create function to check S3 file existence and type with fuzzy matching

  * Frame function in "nolcat/nolcat/nolcat_glue_job.py"
  * Write code for checking if a timestamp is between two times, with bounds as `now()` calls before the SUSHI call and just before the file check
  * Write function checking if S3 file with matching stats source ID and timestamp passing check above exists and returning its file type
  * Have function read, output the content of, and delete the file if the type isn't parquet
  * Write a test for this in "test_nolcat_glue_job.py"

* Figure out how to move a dataframe to a step function

  * Data passed from flask to step functions must be in JSON format, but data types <class 'werkzeug.datastructures.file_storage.FileStorage'>, <class 'openpyxl.workbook.workbook.Workbook'>, <class 'openpyxl.worksheet._read_only.ReadOnlyWorksheet'>, and <class 'pandas.core.frame.DataFrame'> aren't JSON serializable, so files with tabular data must be converted to JSON to be passed to a step function and reverted to a dataframe once in a Glue job
  * https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html changes a dataframe into a JSON
  * JSONs can be turned back into dataframes with https://pandas.pydata.org/docs/reference/api/pandas.read_json.html (does `FutureWarning: Passing literal json to 'read_json' is deprecated and will be removed in a future version. To read from a literal string, wrap it in a 'StringIO' object.` need to be addressed?) (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html or https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_records.html can also be used, but `to_json()` output of string must be converted to dict with `json.loads()`)

* Move `nolcat.UploadCOUNTERReports` to Glue job

  * Split class `nolcat.UploadCOUNTERReports` into separate classes for tabular COUNTER to dataframe and manipulation of dataframe for saving to S3
  * Move latter class into "nolcat/nolcat/nolcat_glue_job.py"
  * Update function call chain diagram to reflect above changes
  * Add `statistics_source_ID` as an attribute of both classes
  * Revise end of first new class to send dataframe converted to JSON to step function
  * Copy existing `nolcat.UploadCOUNTERReports` test functions and their relevant fixtures to "test_nolcat_glue_job.py"
  * Rename existing test function file for `nolcat.UploadCOUNTERReports` and update the test functions to match the revised class
  * Update function call chain diagram to reflect above changes
  * For all tests, get call chains and adjust conftest calls
  * Confirm all tests still pass
  * Pull file into Glue job
  * Confirm configs still set properly

* Save `nolcat.UploadCOUNTERReports` output as parquet in S3

  * Update second class made from `nolcat.UploadCOUNTERReports` to take in a JSON made from a dataframe and end with saving a parquet file to S3 (confirm S3 file name can be created at saving and can include stats source ID and report creation timestamp)
  * Get list of all calls to second class made from `nolcat.UploadCOUNTERReports`
  * Adjust above calls to not expect return values
  * Adjust function call chain diagram to correspond with above changes
  * Adjust tests and their relevant fixtures for changed calls to reflect changes
  * Adjust function call chain diagram to correspond with above changes
  * Add check for saved parquet or error file after call to second class made from `nolcat.UploadCOUNTERReports`
  * List all functions in function call chains ending in a call to second class made from `nolcat.UploadCOUNTERReports`
  * For all functions above, adjust to anticipate no return value if successful
  * Adjust tests and function call chain diagram to correspond with above changes

* Move other functions and classes to be determined to "nolcat/nolcat/nolcat_glue_job.py"
* Remove `nolcat.models.COUNTERData` class

  * Move sole class method to "nolcat/nolcat/nolcat_glue_job.py"
  * Update function call chain diagram to reflect above change
  * Update all references to former method
  * Remove connections to class from other relation classes
  * Change any remaining references to class attributes
  * Delete class
  * Update function call chain diagram to reflect above change

* Delete any statement functions no longer in use
* Change functions querying only the `nolcat.models.COUNTERData` relation to querying the parquet files in S3 with Athena

  * Look out for fuzzy matching methods for strings in parquet files--current `(MATCH(<field>) AGAINST('<string>' IN NATURAL LANGUAGE MODE))` has an odd relationship with word boundaries (e.g. "Social Science Premium Collection->Education Collection->ERIC" can be found with the string "ollection->eric" but not the string "remium collectio")

* Figure out how to have Athena execute queries requesting data from both the relational database and parquet files in S3

Iteration 3: Minimum Viable Product
===================================
* Add documentation about adding records to `fiscalYears` relation via SQL command line

Iteration 4: Minimum Viable Product with Tests and Test Database
================================================================
* Create the temporary database for testing: Per Flask's documentation on testing, tests interacting with a database should be able to use a testing database separate from but built using the same factory as the production database. The resources to consult are in `tests.conftest`.

Basic Enhancement Iterations
****************************
These iterations make NoLCAT more robust and easier to use through relatively small adjustments. Many of these iterations move functionality from the SQL command line to the GUI.

Iteration 1: View Lists
=======================
* Confirm variable routes in "annual_stats/index.html" work
* Finish `nolcat.view_lists.views.view_lists_homepage()`
* Write "view_lists/index.html" page
* Finish `tests.test_bp_view_list.test_view_lists_homepage()`
* Write `tests.test_bp_view_list.test_GET_request_for_view_list_record()`
* Finish `nolcat.view_lists.views.view_list_record()`
* Create "view_lists/view-record.html" page
* Write `tests.test_bp_view_list.test_GET_request_for_edit_list_record_for_existing_record()`

Iteration 2: Edit Lists
=======================
* Create form classes needed for editing
* Finish `nolcat.view_lists.views.edit_list_record()`
* Create "view_lists/edit-record.html" page
* Write `tests.test_bp_view_list.test_GET_request_for_edit_list_record_for_new_record()`
* Write `tests.test_bp_view_list.test_edit_list_record()`
* Write `tests.test_ResourceSources.test_change_StatisticsSource()`
* Write `tests.test_ResourceSources.test_add_access_stop_date()`
* Write `tests.test_ResourceSources.test_remove_access_stop_date()`

Iteration 3: Add Notes
======================
* Write form class for adding notes
* Add form for adding notes to "view_lists/view_record.html"
* Write `nolcat.models.StatisticsSources.add_note()`
* Write `tests.test_StatisticsSources.test_add_note()`
* Write `nolcat.models.Vendors.add_note()`
* Write `tests.test_Vendors.test_add_note()`
* Write `nolcat.models.ResourceSources.add_note()`
* Write `tests.test_ResourceSources.test_add_note()`
* Write `nolcat.models.VendorNotes.__repr__()`
* Write `nolcat.models.StatisticsSourceNotes.__repr__()`
* Write `nolcat.models.ResourceSourceNotes.__repr__()`
* Write `nolcat.models.AnnualUsageCollectionTracking.__repr__()`

Iteration 4: Show and Edit Fiscal Year Information
==================================================
* Finish `nolcat.annual_stats.forms.RunAnnualStatsMethodsForm()`
* Finish `nolcat.annual_stats.forms.EditFiscalYearForm()`
* Finish `nolcat.annual_stats.forms.EditAUCTForm()`
* Finish `nolcat.annual_stats.views.show_fiscal_year_details()`
* Finish "annual_stats/fiscal-year-details.html"
* Finish `tests.test_bp_annual_stats.test_GET_request_for_annual_stats_homepage()`
* Write `tests.test_bp_annual_stats.test_GET_request_for_show_fiscal_year_details()`
* Write `tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_RunAnnualStatsMethodsForm()`
* Write `tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditFiscalYearForm()`
* Write `tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditAUCTForm()`
* Write `nolcat.models.AnnualStatistics.add_annual_statistic_value()`
* Write `tests.test_AnnualStatistics_test_add_annual_statistic_value()`

Iteration 5: Switch Message Display from Stdout to Flask
=========================================================
* Make second return statement in `nolcat.models.StatisticsSources.fetch_SUSHI_information()` display in Flask

Iteration 6: Miscellaneous
==================================================
* Clean up CSS file
* Create CSS class for flashed messages
* Add FSU Libraries wordmark as link to library homepage in footer
* Consolidate `nolcat.models.StatisticsSources._check_if_data_in_database()` and `nolcat.app.check_if_data_already_in_COUNTERData()`

Iteration 7: Interact with Host File System
============================================
* Figure out how tests run in the instance can get metadata about and interact with the file system of the host/host workstation
* Finish `tests.test_app.default_download_folder()`
* Update `tests.test_app.test_download_file()` to use `tests.test_app.default_download_folder()`

Open Source Iterations
**********************
These iterations contain updates necessary for NoLCAT to be used as an open source program.

Iteration 1: Formalize Documentation
====================================
* Update and flesh out README according to best practices
* Run command line operations `sphinx-apidoc -o docs/source/ nolcat` and `make html` for Sphinx
* Organize custom documentation pages on Sphinx index

Iteration 2: Display Data Uploaded at End of Initialization
===========================================================
* Add display of all data in the database to "initialization/show-loaded-data.html"
* Update `tests.test_bp_initialization.test_upload_historical_non_COUNTER_usage()` to check for displayed data

Aspirational Iterations
***********************
These iterations would create features that would be nice to have but aren't necessary to basic functionality. Some are fairly simple; others are quite ambitious.

Iteration: View All Associated Resource and Statistics Sources in a Vendor Record
=================================================================================
* Finish `nolcat.models.Vendors.get_statisticsSources()`
* Write `tests.test_Vendors.test_get_statisticsSources_records()`
* Finish `nolcat.models.Vendors.get_resourceSources()`
* Write `tests.test_Vendors.test_get_resourceSources_records()`
* Add `nolcat.models.Vendors.get_statisticsSources()` and `nolcat.models.Vendors.get_resourceSources()` to `nolcat.view_lists.views.view_list_record()` when vendors are being displayed

Iteration: Create Method for Adding New Fiscal Years to the Relation
====================================================================
* Determine the best method to add a record for the new fiscal year to the `FiscalYears` relation (ideally with automatic execution each July 1)

Iteration: Display Results of Usage Data Requests in Browser
============================================================
* Modify routes in `nolcat.view_usage.views` that return CSVs to return HTML pages from which those CSVs can be downloaded
* Show dataframes used to create CSVs in browser (see https://stackoverflow.com/q/52644035 and https://stackoverflow.com/q/22180993 for info about adding dataframes to Flask display)

Iteration: Display Data Visualization of Usage Data Requests in Browser
=======================================================================
* Make final decision between Plotly/Dash and Bokeh
* Change dataframes displayed as tables in browser to data visualizations

Iteration: Get SUSHI Credentials from Alma
==========================================
* Add way to determine if data should be fetched from Alma or the JSON file at the beginning of `nolcat.models.StatisticsSources.fetch_SUSHI_information()`
* Write "Retrieve Data from Alma" subsection of `nolcat.models.StatisticsSources.fetch_SUSHI_information()`

Iteration: Add User Accounts to Restrict Access
===============================================
* Add "Flask-User" library
* Establish if there's going to be a single user login and a single admin login, or if everyone has their own login
* Write `tests.test_bp_login.test_logging_in()`
* Write `tests.test_bp_login.test_logging_in_as_admin()`
* Write `tests.test_bp_login.test_creating_an_account()`
* Create redirect to `nolcat.initialization.views.collect_FY_and_vendor_data()` after the creation of the first account with data ingest permissions

Iteration: Deduplicate Resources
================================
* Review the main branch of the repo as of commit 207c4a14b521b7f247f5249a080b4a725963b599 (made 2023-01-20)
* Remove hyphens from all ISBNs to handle their inconsistency in usage and placement

Iteration: Handle Reports Without Corresponding Customizable Reports
====================================================================
* Figure out how to view reports found in subsection "Add Any Standard Reports Not Corresponding to a Customizable Report" of `nolcat.models.StatisticsSources._harvest_R5_SUSHI()`

Iteration: Incorporate Springshare Databases A-Z Statistics
===========================================================
* Create relation with the databases in the Springshare Databases A-Z list
* Connect values in the above relation with `resourceSources` records through a foreign key in the new relation or a junction table
* Create other relation(s) to hold the usage data in a normalized fashion
* Add relation classes to `nolcat.models` for all the newly created relations

Iteration: Incorporate OpenAthens Statistics
============================================
* Create relation with the activated resources in the OpenAthens resource catalog
* Connect values in the above relation with `resourceSources` records through a foreign key in the new relation or a junction table
* Create other relation(s) to hold the usage data in a normalized fashion
* Add relation classes to `nolcat.models` for all the newly created relations

Iteration: Incorporate Embargo and Paywall Data
===============================================
* Add fields to relation for resources for the embargo and paywall data
* Create templates in query wizard that separates usage into before and after embargo and/or paywall dates based on the `YOP` field

Iteration: Automatically Reharvest SUSHI
========================================
* Initiate automated reharvesting for statistics sources which take first calls as prompts to run query later and gives data on subsequent call