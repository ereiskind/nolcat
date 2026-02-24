NoLCAT Development Roadmap
##########################
This page contains all the current to-dos and possible plans for the NoLCAT program.

Planned Iterations
******************
* Confirm the following functions work with SUSHI CSV

  * `nolcat.models.StatisticsSources.fetch_SUSHI_information()` and `tests.test_StatisticsSources.StatisticsSources_fixture()`
  * `nolcat.models.StatisticsSources.collect_usage_statistics()`, `nolcat.models.AnnualUsageCollectionTracking.collect_annual_usage_statistics()`, `nolcat.models.FiscalYears.collect_fiscal_year_usage_statistics()`
  * `tests.test_StatisticsSources.SUSHI_credentials_fixture_in_test_StatisticsSources()`, `tests.test_StatisticsSources.reports_offered_by_StatisticsSource_fixture()`, `tests.test_StatisticsSources.data_for_testing_harvest_single_report()`, `tests.test_StatisticsSources.harvest_R5_SUSHI_result()`

Move Code to Glue Jobs and Data to Parquet
==========================================
* Develop `nolcat.nolcat.models.COUNTERData` relation to parquet file transformer

  * Run `SELECT statistics_source_ID, report_type, usage_date, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, usage_date, report_creation_date;` on production data to confirm available production data and find out what parquet files need to be created

* Save `nolcat.nolcat_glue_job.ConvertJSONDictsToDataframe` output as parquet in S3

  * Adjust calls to `nolcat.nolcat_glue_job.ConvertJSONDictsToDataframe.create_dataframe()` to not expect return values (#ToDo: PARQUET IN S3--); adjusting tests and function call chain diagram to correspond with changes *bold functions are non-test functions confirmed to still expect dataframe as return value*

    * `nolcat.models.StatisticsSources._harvest_single_report()` with `tests.test_StatisticsSources.test_harvest_single_report()`, `tests.test_StatisticsSources.test_harvest_single_report_with_partial_date_range()`
    * **`nolcat.models.StatisticsSources._harvest_R5_SUSHI()`** with `tests.StatisticsSources.test_harvest_R5_SUSHI()`, `tests.StatisticsSources.test_harvest_R5_SUSHI_with_report_to_harvest()`, `tests.StatisticsSources.test_harvest_R5_SUSHI_with_invalid_dates()`, `tests.StatisticsSources.harvest_R5_SUSHI_result()`, `tests.test_AnnualUsageCollectionTracking.harvest_R5_SUSHI_result()`
    * `nolcat.models.StatisticsSources.collect_usage_statistics()` with `tests.StatisticsSources.test_collect_usage_statistics()`
    * `nolcat.models.AnnualUsageCollectionTracking.collect_annual_usage_statistics()` with `tests.test_AnnualUsageCollectionTracking.test_collect_annual_usage_statistics()`
    * `nolcat.models.FiscalYears.collect_fiscal_year_usage_statistics()` with `tests.test_FiscalYears.test_collect_fiscal_year_usage_statistics()`
    * `nolcat.ingest_usage.harvest_SUSHI_statistics()` with `tests.test_bp_ingest_usage.test_harvest_SUSHI_statistics()`
    * `nolcat.models.StatisticsSources.` with `tests.StatisticsSources.()`, `tests.StatisticsSources.()`

  * Add check for saved parquet or error file after call to `nolcat.nolcat_glue_job.ConvertJSONDictsToDataframe.create_dataframe()`
  * List all functions in function call chains ending in a call to `nolcat.nolcat_glue_job.ConvertJSONDictsToDataframe.create_dataframe()`
  * For all functions above, adjust to anticipate no return value if successful
  * Adjust tests and function call chain diagram to correspond with above changes
  * For all tests, get call chains and adjust caplog calls
  * Confirm all tests still pass

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
  * Move latter class into "nolcat/nolcat/nolcat_glue_job.py" with its own child logger
  * Update function call chain diagram to reflect above changes
  * Add `statistics_source_ID` as an attribute of both classes
  * Revise end of first new class to send dataframe converted to JSON to step function
  * Copy existing `nolcat.UploadCOUNTERReports` test functions and their relevant fixtures to "test_nolcat_glue_job.py"
  * Rename existing test function file for `nolcat.UploadCOUNTERReports` and update the test functions to match the revised class
  * Update function call chain diagram to reflect above changes
  * For all tests, get call chains and adjust caplog calls
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

* Move other functions and classes to be determined to "nolcat/nolcat/nolcat_glue_job.py" (adjusting call chain diagram, creating child loggers, and adjusting caplog calls as needed)
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

  * Functions with queries getting data from the `nolcat.models.COUNTERData` relation

    * `nolcat.models.FiscalYears.calculate_depreciated_ACRL_60b()`
    * `nolcat.models.FiscalYears.calculate_depreciated_ACRL_63()`
    * `nolcat.models.FiscalYears.calculate_ACRL_61a()`
    * `nolcat.models.FiscalYears.calculate_ACRL_61b()`
    * `nolcat.models.FiscalYears.calculate_ARL_18()`
    * `nolcat.models.FiscalYears.calculate_ARL_19()`
    * `nolcat.models.FiscalYears.calculate_ARL_20()`
    * `nolcat.models.StatisticsSources._check_if_data_in_database()`
    * `nolcat.nolcat_glue_job.check_if_data_already_in_COUNTERData()`
    * `nolcat.view_usage.use_predefined_SQL_query()`
    * `nolcat.view_usage.construct_PR_query_with_wizard()`
    * `nolcat.view_usage.construct_DR_query_with_wizard()`
    * `nolcat.view_usage.construct_TR_query_with_wizard()`
    * `nolcat.view_usage.construct_IR_query_with_wizard()`
    * `tests.conftest.match_direct_SUSHI_harvest_result()`
    * `tests.test_bp_ingest_usage.test_upload_COUNTER_data_via_Excel()`
    * `tests.test_bp_ingest_usage.test_upload_COUNTER_data_via_SQL_insert()`
    * `tests.test_bp_initialization.test_collect_AUCT_and_historical_COUNTER_data()`
    * `tests.test_bp_view_usage.test_run_custom_SQL_query()`
    * `tests.test_bp_view_usage.test_use_predefined_SQL_query()`
    * `tests.test_bp_view_usage.start_query_wizard_form_data()`
    * `tests.test_bp_view_usage.PR_parameters()`
    * `tests.test_bp_view_usage.DR_parameters()`
    * `tests.test_bp_view_usage.TR_parameters()`
    * `tests.test_bp_view_usage.IR_parameters()`
    * `tests.test_StatisticsSources.test_check_if_data_already_in_COUNTERData()`

  * Look out for fuzzy matching methods for strings in parquet files--current `(MATCH(<field>) AGAINST('<string>' IN NATURAL LANGUAGE MODE))` has an odd relationship with word boundaries (e.g. "Social Science Premium Collection->Education Collection->ERIC" can be found with the string "ollection->eric" but not the string "remium collectio")

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
* Convert error catches by returning strings to returning Python exception classes

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