NoLCAT
######

Integration Branch
******************
This branch is based off of the 2022-10-06 state of `main` and exists so other branches can be merged into it.

* Branch `refactor_route_functions` includes the current test data
* Branch `add_WSGI_file_to_repo`
* Branch `recreate_test_bin_files_and_fixtures`
* Branch `write_harvest_methods_in_StatisticsSources`
* Branch `create_page_for_R5_harvesting`
* Branch `create_jinja_template`


To-Do List
**********

High Priority
=============
* Write `FiscalYears.create_usage_tracking_records_for_fiscal_year` method (creates AUCT records for the given FY)
* OpenRefine exports were Excel files to preserve encoding, but some data will be too large for Excel--how can te encoding be preserved when exporting as CSV?
* Library `mysqlclient` installed after `db.engine` line in `session` pytest fixture triggered `ModuleNotFoundError: No module named 'MySQLdb'` error; does this replace the `PyMySQL` library?

Branch: Configure Flask-User
----------------------------
* Create route/page for login page with tests
* Establish if there's going to be a single user login and a single admin login, or if everyone has their own login

Branch: Configure Flask-SQLAlchemy
----------------------------------
* **Question:** Does a module that just creates Flask-SQLAlchemy config variables and SQLAlchemy variables need tests?
* Move `tests.test_StatisticsSources.test_loading_into_relation` to `tests.test_flask_factory_pattern` with a new name indicating it tests database read/write, then confirm the test does exactly that

Branch: Import Data from Secret Files
-------------------------------------
* Import file path to JSON with R5 SUSHI credentials

Branch: Complete Initialization Process
---------------------------------------
* In `RawCOUNTERReport` constructor for uploaded files, make all dates the first of the month
* Write `RawCOUNTERReport.load_data_into_database` method
* Finish route `nolcat.initialization.views.wizard_page_2`
* Create route `nolcat.initialization.views.wizard_page_3`
* Create route `nolcat.initialization.views.wizard_page_4`
* Figure out best format for metadata selector in "select-matches.html"

Branch: Create Basic UI Pages
-----------------------------
* Create route in `annual_stats` blueprint for admin homepage
* Create admin homepage in `annual_stats` blueprint with links to FY details pages, homepages of `view_sources` and `view_vendors` blueprints
* Create test for route to `annual_stats` blueprint homepage

Branch: Complete SUSHI Call Functionality
-----------------------------------------
* Write `StatisticsSources.fetch_SUSHI_information` method
* Write `StatisticsSources._harvest_R5_SUSHI` method *branch exists*
* Write `StatisticsSources.collect_usage_statistics` method
* Create route/homepage in `ingest_usage` blueprint that let user run `StatisticsSources.collect_usage_statistics` or choose to add stats via a file upload type (links will be 404 at this point) 

Branch: Create Query Result Download Capability
-----------------------------------------------
* Create route/page for blueprint homepage for choosing how to construct query
* Create route/page where SQL string can be entered and run against database
* Create test for route to homepage
* Create test for downloading query results

Branch: Create Basic Record Display Methods
-------------------------------------------
* Create route for viewing resources list
* Create page for viewing resources list where all resources have their default metadata and links to a page with more details and, later on, a trigger for adding a record to the Resources relation
* Create route for viewing list of StatisticsSources or ResourceSources records
* Create page listing all StatisticsSources or ResourceSources with their vendor, if they're active, and a link to more details as well as a trigger for the method to add a record to the relation being listed
* Create route/page for vendors list including link to notes and trigger to method for adding new record to Vendors relation

Branch: Create Current Resource Attribute Management Methods
------------------------------------------------------------
* Create method for changing `StatisticsResourceSources.current_statistics_source` attribute
* Write `ResourceSources.add_access_stop_date` method
* Write `ResourceSources.remove_access_stop_date` method


Medium Priority
===============
* Certain Requests response object, upon being transformed with the `json()` method in `SUSHICallAndResponse.make_SUSHI_call`, will contain Unicode replacement characters; encoding-related transformations on the JSON don't help. Is there a way to change this, or are the replacement characters likely the result of issues with the data itself?
* Flesh out documentation on what situations are better tested with the `SUSHICallAndResponse` test suite vs. the `models.StatisticsSources` test suite
* Determine best way to test `models.StatisticsSources` methods, which 1) don't include API calls directly but make heavy use of the `SUSHICallAndResponse.make_SUSHI_call()` method and 2) are designed to not load data from the same statistics source, report, and month if it's already in the database
* Write test for `FiscalYears.create_usage_tracking_records_for_fiscal_year` method

Branch: View and Edit Record Details and Notes
----------------------------------------------

Create `add_note` Methods
^^^^^^^^^^^^^^^^^^^^^^^^^
* Write `Vendors.add_note` method
* Write `StatisticsSources.add_note` method
* Write `ResourceSources.add_note` method

Create View and Edit Details Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create route to view record details
* Determine if StatisticsSources and ResourceSources are similar enough to use the same template to display details, then create one or two pages to show record details
* Work out details for route/page for adding and editing StatisticsSources and ResourceSources records
* Create route/page for adding or editing a vendor record
* Create route/page for viewing notes, only type of other details a Vendors record has

Create Tests for Record View, Detail, and Editing Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create test for route to resources list
* Create test for route to view list of records for both StatisticsSources and ResourceSources
* Create test for route to add record for both StatisticsSources and ResourceSources
* Create test for route to edit record for both StatisticsSources and ResourceSources
* Create test for route to view record details for both StatisticsSources and ResourceSources
* Create test for route to `view_vendors` blueprint homepage
* Create test for route to add new vendor
* Create test for route to edit vendor
* Create test for route to view vendor details
* Write test for `Vendors.add_note` method
* Create and write test for `StatisticsSources.add_note` method
* Write test for `ResourceSources.add_note` method

Branch: Develop Post-Initialization COUNTER Ingest Capability
-------------------------------------------------------------
* Create route/page for uploading R4 reports in an Excel or CSV file
* Create route/page for uploading R5 reports in an Excel or CSV file
* Create test for route to choose type of upload
* Test uploading R4 report: upload file through webpage, get contents back via `pd.from_sql`, and compare that dataframe to the original uploaded data
* Test uploading R5 report: upload file through webpage, get contents back via `pd.from_sql`, and compare that dataframe to the original uploaded data

Branch: Develop Canned Queries and Usage Query Tests
----------------------------------------------------
* Create route/page for canned queries
* Create test for choosing canned queries on the webpage
* Create test to enter SQL into free SQL text box on the webpage

Branch: Develop Testing for Initialization Process
--------------------------------------------------
* Figure out how to get a `werkzeug.datastructures.ImmutableMultiDict` object into the `RawCOUNTERReport` test module
* Write test for `RawCOUNTERReport.load_data_into_database` method
* "ToDo: Create test to confirm that form can successfully upload all TSV files"
* "ToDo:Create test confirming the uploading of the data of the requested TSVs, the creation of the `annualUsageCollectionTracking` records, and the outputting of the TSV for that relation"
* "ToDo: Create test confirming route uploading TSV with data for `annualUsageCollectionTracking` records"
* "ToDo: Create test to upload formatter R4 reports into single RawCOUNTERReport object, then RawCOUNTERReport.perform_deduplication_matching"
* "ToDo: Create test for route showing data in database at end of initialization wizard"

Branch: Develop Testing for SUSHI Call Functionality
----------------------------------------------------
* Write tests for `StatisticsSources.fetch_SUSHI_information` method
* Write test for `StatisticsSources._harvest_R5_SUSHI` method
* Write test for `StatisticsSources.collect_usage_statistics` method

Branch: Develop Testing for Current Resource Attribute Management Methods
-------------------------------------------------------------------------
* Create module "tests/test_StatisticsResourceSources.py"
* Create and write test for method changing `StatisticsResourceSources.current_statistics_source` attribute
* Write test for `ResourceSources.add_access_stop_date` method
* Write test for `ResourceSources.remove_access_stop_date` method

Branch: Display AUCT Records for a FY
-------------------------------------
* Create route/page to display all AUCT records for a given FY
* Create test for route display a FY's AUCT records


Low Priority
============
* Write README
* Create the HTML annotated bibliography
* Write `__repr__` values
* Add exception in `nolcat.models.SUSHICallAndResponse` for MathSciNet, which doesn't have a `/status` endpoint but does return reports
* **Question:** Will the `models.Resources.notes` attribute contain enough data to justify becoming a separate relation?
* **Question:** How should the program handle a resource from multiple stats sources when those sources don't agree on the data type?

Branch: Create Query Wizard and Query Results Output in UI
----------------------------------------------------------
* Create route/page for query wizard
* Create route/page for displaying query results
* Create test for make selections in query wizard to generate given SQL string

Branch: ARL and ACRL/IPEDS Calculations
---------------------------------------
* Write ARL and ACRL/IPEDS number methods for `nolcat.models.FiscalYears`
* Create route in blueprint `annual_stats` for fiscal year details
* Create page in blueprint `annual_stats` for fiscal year details including triggers to run most FiscalYears methods
* Create test for route to page with details of a FY
* Write tests for ARL and ACRL/IPEDS number methods in `FiscalYears`

Branch: Obtain SUSHI Credentials by Vendor
------------------------------------------
* Determine if these methods are needed or if `StatisticsSources.fetch_SUSHI_information` is enough
* Write `Vendors.get_SUSHI_credentials_from_JSON` method
* Write test for `Vendors.get_SUSHI_credentials_from_JSON` method
* Write `Vendors.get_SUSHI_credentials_from_Alma` method and test

Branch: Create `StatisticsSources._harvest_R5_SUSHI` Loop Methods
-----------------------------------------------------------------
* Write `FiscalYears.collect_fiscal_year_usage_statistics` method and test
* Write `AnnualUsageCollectionTracking.collect_annual_usage_statistics` method and test

Branch: Store File for Non-Standard Usage
-----------------------------------------
* Write `AnnualUsageCollectionTracking.upload_nonstandard_usage_file` method if such files are to be stored in container
* If non-COUNTER usage files are to be stored in the program, create route/page for uploading them
* Create test for route to upload non-COUNTER usage

Branch: Finish `view_resources` Blueprint
-----------------------------------------
* Create route/page for adding or editing a resource (associated Vendor records are chosen here)
* Create route/page for viewing resource details
* Add search functionality to view resource page
* Create test for route to add a resource
* Create test for route to edit a resource
* Create test for route to view resource details

Low-Priority Methods
--------------------
* Create a method that automatically creates a new record for the FY every July 1
*  (`StatisticsSources.collect_usage_statistics` method with the FY dates plus updating the `AnnualUsageCollectionTracking.collection_status` attribute, both of which can be done manually in conjunction)
* Write method inheriting from Python error class for when uploaded files don't meet the naming convention

Possible Additional Tests
-------------------------
* **Question:** *"test_flask_factory_pattern.py"* Should any GET requests besides root (to the homepage) and a nonexistent route (to the 404 page) be tested?
* **Question** *"test_SUSHICallAndResponse.py"* Are tests just for `_handle_SUSHI_exceptions` and/or `_create_error_query_text` needed?

Organize Documentation Layout
-----------------------------
* Create Sphinx index--organize custom pages on index
* Create Sphinx index--order documentation created automatically from docstrings

Remove Unneeded Files
---------------------
* Determine if "CSRF_token.missing.rst" needs to be kept and, if not, if the StackOverflow resource links should be preserved elsewhere
* Decide if keeping "tests/titles_in_sample_R4_reports.txt"
* Clean up/move contents of "notes_from_older_erd.rst"

Improve UI
----------
* Clean up CSS file
* Create Jinja template header and footer in "nolcat/templates/layout.html" *branch exists*
