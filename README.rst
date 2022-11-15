NoLCAT
######

Use Pandas to Transform COUNTER Binary Files
********************************************
Initially, the CSV, TSV, or binary files containing COUNTER data were to be transformed from a tabular layout to a normalized one with OpenRefine; further work, however, revealed that using pandas for this transformation would be better. The steps for this are:

1. Create `UploadCOUNTERReports` class
2. Have `initialization` blueprint use the new class
3. Have `ingest_usage` blueprint use the new class
4. Try to get a `werkzeug.datastructures.ImmutableMultiDict` object into the `UploadCOUNTERReports` test module

To-Do List
**********
Last updated: 2022-10-11

High Priority
=============
* Write `FiscalYears.create_usage_tracking_records_for_fiscal_year` method (creates AUCT records for the given FY)
* Confirm that test related to database I/O in `tests.test_flask_factory_pattern` work
* Rename `index.html` pages in blueprints

Branch: Complete Initialization Process
---------------------------------------
* Figure out layout and form iteration for page where manual matches are confirmed
* Finish creating routes, forms, and HTML pages for `nolcat.initialization`
* Write test for `RawCOUNTERReport.load_data_into_database` method
* Write tests for `RawCOUNTERReport`/`nolcat.initialization` blueprint

Branch: Complete SUSHI Call Functionality
-----------------------------------------
* Write `StatisticsSources.fetch_SUSHI_information` method
* Write `StatisticsSources._harvest_R5_SUSHI` method
* Write `StatisticsSources.collect_usage_statistics` method
* Create route/homepage in `ingest_usage` blueprint that let user run `StatisticsSources.collect_usage_statistics` or choose to add stats via a file upload type (links will be 404 at this point)
* Write tests for `StatisticsSources.fetch_SUSHI_information` method
* Write test for `StatisticsSources._harvest_R5_SUSHI` method
* Write test for `StatisticsSources.collect_usage_statistics` method

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
* Flesh out documentation on what situations are better tested with the `SUSHICallAndResponse` test suite vs. the `models.StatisticsSources` test suite
* Determine best way to test `models.StatisticsSources` methods, which 1) don't include API calls directly but make heavy use of the `SUSHICallAndResponse.make_SUSHI_call()` method and 2) are designed to not load data from the same statistics source, report, and month if it's already in the database
* Write test for `FiscalYears.create_usage_tracking_records_for_fiscal_year` method

Branch: Create Basic UI Pages
-----------------------------
* Create route in `annual_stats` blueprint for admin homepage
* Create admin homepage in `annual_stats` blueprint with links to FY details pages, homepages of `view_sources` and `view_vendors` blueprints
* Create test for route to `annual_stats` blueprint homepage

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

Branch: Develop Post-Initialization COUNTER File Ingest Capability
------------------------------------------------------------------
* Create route/page for uploading R4 reports in an Excel file
* Create route/page for uploading R5 reports in an Excel file
* Create test for route to choose type of upload
* Test uploading R4 report: upload file through webpage, get contents back via `pd.from_sql`, and compare that dataframe to the original uploaded data
* Test uploading R5 report: upload file through webpage, get contents back via `pd.from_sql`, and compare that dataframe to the original uploaded data

Branch: Develop Canned Queries and Usage Query Tests
----------------------------------------------------
* Create route/page for canned queries
* Create test for choosing canned queries on the webpage
* Create test to enter SQL into free SQL text box on the webpage

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
* Write `Vendors` method that pulls the constituant `StatisticsSources` records and runs `StatisticsSources.fetch_SUSHI_information` for each one
* Clean up/move contents of "notes_from_older_erd.rst"

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

Branch: Create `StatisticsSources._harvest_R5_SUSHI` Loop Methods
-----------------------------------------------------------------
* Write `FiscalYears.collect_fiscal_year_usage_statistics` method and test
* Write `AnnualUsageCollectionTracking.collect_annual_usage_statistics` method and test

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

Organize Documentation Layout
-----------------------------
* Create Sphinx index--organize custom pages on index
* Create Sphinx index--order documentation created automatically from docstrings

Improve UI
----------
* Clean up CSS file
* Create Jinja template header and footer in "nolcat/templates/layout.html"


TaDS Assistance Required
========================

Branch: Store File for Non-Standard Usage
-----------------------------------------
* Write `AnnualUsageCollectionTracking.upload_nonstandard_usage_file` method if such files are to be stored in container
* If non-COUNTER usage files are to be stored in the program, create route/page for uploading them
* Create test for route to upload non-COUNTER usage


Branch: Configure Flask-User
----------------------------
* Create route/page for login page with tests
* Establish if there's going to be a single user login and a single admin login, or if everyone has their own login

About This Repo
***************

Large File Support
==================

With Git alone, GitHub limits individual files to 100 MB (102,400 KB). To add larger files to the repository, up to 2 GB (2,097,152 KB) in GitHub's free service tier, Git Large File Storage (LFS) is required. For documentation on LFS in GitHub and links to relevant LFS documentation, go to https://docs.github.com/en/repositories/working-with-files/managing-large-files.