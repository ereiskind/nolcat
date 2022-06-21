NoLCAT
######

To-Do List
**********

* Conform with Flask-SQLAlchemy, including editing documentation to reflect using Flask-SQLAlchemy to construct schema
* Create docstrings for model classes
* **Branch:** Test StatisticsSources fixtures in AWS
* **Branch:** Create database integration fixtures
* **Branch:** Write harvest methods in StatisticsSources
* **Branch:** Create page for R5 harvesting
* **Branch:** Create Jinja template
* Create Sphinx index--organize custom pages on index
* Create Sphinx index--order documentation created automatically from docstrings
* Write README
* Clean up/move contents of "notes_from_older_erd.rst"
* Determine if "CSRF_token.missing.rst" needs to be kept and, if not, if the StackOverflow resource links should be preserved elsewhere
* Create the HTML annotated bibliography
* "ToDo: Should the values in the `__table_args__` dictionaries [in the classes in "models.py"] be f-strings referencing `Database_Credentials.Database`?"
* Update `PATH_TO_CREDENTIALS_FILE` in "models.py" as necessary
* Decide if keeping "tests/titles_in_sample_R4_reports.txt"
* Correct "tests/database_seeding_fixtures.py" to match the current schema
* Clean up CSS file
* Remove "nolcat/templates/enter-data.html" and "nolcat/templates/ok.html"
* Create main homepage, including links to appropriate blueprint homepages
* Create Jinja template header and footer in "nolcat/templates/layout.html"


SQLAlchemy Engine
=================
*"SQLAlchemy_engine.py"*

* Have local SQLAlchemy engine use SQLite???
* Does this need a test file?


`nolcat/app.py`
===============
*"app.py"* with tests in *"test_flask_factory_pattern.py"*

* Create secure secret key
* Test module:

   * What pages besides the homepage and the 404 page should the test try to go to?
   * Create a test for making a Selenium webdriver object


Class `SUSHICallAndResponse`
============================
*"SUSHI_call_and_response.py"* with tests in *"test_SUSHICallAndResponse.py"*

* Add exception for MathSciNet, which doesn't have a `/status` endpoint but does return reports
* *SUSHICallAndResponse.make_SUSHI_call:* Determine how to get response object with Unicode replacement characters to encode properly
* *SUSHICallAndResponse.make_SUSHI_call:* "ToDo: Before reformatting, a `status` response with the key-value pair `'Alerts': []` didn't trigger any of the method calls below, but the exact same status call with the exact same response 11 minutes later did--investigate the issue"
* Write repr
* Test module:

   * Create note explaining in more detail when tests should be run here and when they should be run on `StatisticsSources._harvest_R5_SUSHI`
   * Are tests to see if invalid forms of COUNTER reports can be returned a good idea?
   * The class's private methods are for handling this that happen during the API call; are tests just for `_retrieve_downloaded_JSON`, `_handle_SUSHI_exceptions`, and/or `_create_error_query_text` needed?


Class `FiscalYears`
===================
*"nolcat.models.FiscalYears"* with tests in *"test_FiscalYears.py"*

* Create a new record for the FY every July 1
* Write repr
* Write ARL and ACRL/IPEDS number methods
* Write `create_usage_tracking_records_for_fiscal_year` method (creates AUCT records for the given FY)
* Write `collect_fiscal_year_usage_statistics` method
* Test module:

   * Write tests for ARL and ACRL/IPEDS number methods
   * Write test for `create_usage_tracking_records_for_fiscal_year` method
   * Write test for `collect_fiscal_year_usage_statistics` method


Class `Vendors`
===============
*"nolcat.models.Vendors"* with tests in *"test_Vendors.py"*

* Write repr
* Create `add_vendor` method???
* Write `get_SUSHI_credentials_from_Alma` method
* Write `get_SUSHI_credentials_from_JSON` method
* Write `add_note` method
* Test module:

   * Write test for `get_SUSHI_credentials_from_Alma` method
   * Write test for `get_SUSHI_credentials_from_JSON` method
   * Write test for `add_note` method
   * Write test for new `add_vendor` method???


Class `VendorNotes`
===================
*"nolcat.models.VendorNotes"* (no methods, so test not needed)

* Write repr


Class `StatisticsSources`
=========================
*"nolcat.models.StatisticsSources"* with tests in *"test_StatisticsSources.py"*

* Write repr
* Write `fetch_SUSHI_information` method
* Write `_harvest_R5_SUSHI` method
* Write `collect_usage_statistics` method
* Write `add_note` method
* Create a method for adding a StatisticsSources record, including making sure it has an associated StatisticsResourceSources record
* Test module:

   * Ensure credentials file path fixture works
   * Finish writing `StatisticsSources_fixture` which pulls SUSHI credentials for resources that haven't had the most recent month's data loaded so the test isn't stopped by the deduplication checker
   * Write `test_loading_into_relation`, which is about confirming database read/write is working (and should probably be renamed)
   * Write tests for `fetch_SUSHI_information` method
   * Write test for `_harvest_R5_SUSHI` method
   * Write test for `collect_usage_statistics` method
   * Create and write test for `add_note` method
   * Create and write test for adding StatisticsSources record


Class `StatisticsSourcesNotes`
==============================
*"nolcat.models.StatisticsSourcesNotes"* (no methods, so test not needed)

* Write repr


Class `StatisticsResourceSources`
=================================
*"nolcat.models.StatisticsResourceSources"* with no tests module yet

* Write repr
* Create method for changing `current_statistics_source` attribute
* Test module:

   * Create module "tests/test_StatisticsResourceSources.py"
   * Create and write test for method changing `current_statistics_source` attribute


Class `ResourceSources`
=======================
*"nolcat.models.ResourceSources"* with tests in *"test_ResourceSources.py"*

* Write repr
* Write `add_access_stop_date` method
* Write `remove_access_stop_date` method
* Write `add_note` method
* Create a method for adding a ResourceSources record, including making sure it has an associated StatisticsResourceSources record
* Test module:

   * Write test for `add_access_stop_date` method
   * Write test for `remove_access_stop_date` method
   * Write test for `add_note` method
   * Create and write test for adding ResourceSources record


Class `ResourceSourcesNotes`
============================
*"nolcat.models.ResourceSourcesNotes"* (no methods, so test not needed)

* Write repr


Class `AnnualUsageCollectionTracking`
=====================================
*"nolcat.models.AnnualUsageCollectionTracking"* with tests in *"test_AnnualUsageCollectionTracking.py"*

* Write repr
* Write `collect_annual_usage_statistics` method
* Write `upload_nonstandard_usage_file` method if such files are to be stored in container
* Test module:

   * Write test for `collect_annual_usage_statistics` method
   * Write test for `upload_nonstandard_usage_file` method


Class `Resources`
=================
*"nolcat.models.Resources"* (no methods, so tests not needed)

* Write repr
* Determine if `notes` attribute should be its own relation
* Should there be a method for showing a resource with all its metadata and platforms?


Class `ResourceMetadata`
========================
*"nolcat.models.ResourceMetadata"* (no methods, so tests not needed)

* Write repr
* "#ToDo: Should there be a data_type field to indicate if data is for/from database, title-level resource, or item-level resource to record granularity/report of origin"
* "#ToDo: Does there need to be a Boolean field for indicating the default value for a metadata field for a given resource? Is this how getting a title for deduping should be handled? Should the ISBN, ISSN, and eISSN, which are frequently multiple, be handled this way as well, instead of having them be in the `resources` relation? Would organizing the metadata in this way be better for deduping?"


Class `ResourcePlatform`
========================
*"nolcat.models.ResourcePlatform"* (no methods, so tests not needed)

* Write repr


Class `UsageData`
=================
*"nolcat.models.UsageData"* (no methods, so tests not needed)

* Write repr


Class `RawCOUNTERReport`
========================
*"raw_COUNTER_report.py"* with tests in *"test_RawCOUNTERReport.py"*

* "ToDo: Return an error with a message like the above [about CSV upload not having a file name matching the required convention] that exits the constructor method"
* "ToDo: Set all dates to first of month (https://stackoverflow.com/questions/42285130/how-floor-a-date-to-the-first-date-of-that-month)" (also in another test module)
* *perform_deduplication_matching* "#Alert: The existing program uses a dataframe that includes the resource name, but the resources are stored with the names in a separate relation; how should the names be recombined with the other resource data for deduping against newly loaded reports?"
* *perform_deduplication_matching* "#ToDo: When the metadata for matched resources doesn't match, the user should select what data goes in the resources relation; should that occur along with or after matches are determined?"
* *perform_deduplication_matching* "#ToDo: Should metadata elements not being kept in the resources relation be kept? Using them for resource matching purposes would be difficult, but they could be an alternative set of metadata against which searches for resources by ISBN or ISSN could be run."
* *perform_deduplication_matching* "#ToDo: Should anything be done to denote those titles where different stats sources assign different data types?"
* *perform_deduplication_matching* "#ToDo: Add filter that rejects match [based on ISBN] if one of the resource names contains regex `\sed\.?\s` or `\svol\.?\s`"
* Write `load_data_into_database` method
* Test module:

   * Create fixtures to mock the possible input types

      * *"<class 'werkzeug.datastructures.ImmutableMultiDict'>"* for uploaded Excel files
      * *API response object* for SUSHI calls
      * *"<class 'pandas.core.frame.DataFrame'>"* used for testing--added because unable to develop a way to mock ImmutableMultiDict object for testing

   * Write tests for constructor for all possible input types (replacing the single `test_RawCOUNTERReport_R4_constructor`)
   * Write tests ensuring that uploads can handle R4 and R5 transformations
   * Update/correct `test_perform_deduplication_matching`
   * Write test for `test_perform_deduplication_matching` where `normalized_resource_data` isn't None
   * Write test for `load_data_into_database` method


Blueprint `annual_stats`
========================
Tests in *"test_bp_annual_stats.py"*

* Create route for admin homepage
* Create admin homepage with links to FY details pages, homepages of `view_sources` and `view_vendors` blueprints
* Create route for fiscal year details
* Create page for fiscal year details including triggers to run most FiscalYears methods
* Create route/page to display all AUCT records for a given FY
* Test module:

   * Create test for route to homepage
   * Create test for route to page with details of a FY
   * Create test for route display a FY's AUCT records


Blueprint `ingest_usage`
========================
Tests in *"test_bp_ingest_usage.py"*

* Create route/page for choosing type of upload
* Create route/page for uploading R4 reports
* Create route/page for uploading R5 reports
* Create route/page for "ToDo: Create route for getting start and end dates for custom SUSHI range, then putting them into StatisticsSources.collect_usage_statistics"
* If non-COUNTER usage files are to be stored in the program, create route/page for uploading them
* Test module:

   * Create test for route to choose type of upload
   * "ToDo: Create test for route for loading R4 report into database by comparing pd.from_sql of relations where the data was loaded to dataframes used to make the initial fixtures with data from uploaded report manually added"
   * "ToDo: Create test for route for loading R5 report into database by comparing pd.from_sql of relations where the data was loaded to dataframes used to make the initial fixtures with data from uploaded report manually added"
   * "ToDo: Create test using Selenium to input the dates to use as arguments for StatisticsSources.collect_usage_statistics" and see if SUSHI call object is returned, but no need to actually make the calls
   * Create test for route to upload non-COUNTER usage


Blueprint `initialization`
==========================
Tests in *"test_bp_initialization.py"*

* Remove `nolcat.initialization.forms.TestForm`
* Finish route `save_historical_collection_tracking_info`
* Create route `upload_historical_COUNTER_usage`
* Create route `determine_if_resources_match`
* Figure out best format for metadata selector in "select-matches.html"
* Add uploads and downloads to "historical-collection-tracking.html"
* Create page for showing initial data
* Test module:

   * "ToDo: Create test using Selenium to confirm that form can successfully upload all CSV files"
   * "ToDo:Create test confirming the uploading of the data of the requested CSVs, the creation of the `annualUsageCollectionTracking` records, and the outputting of the CSV for that relation"
   * "ToDo: Create test confirming route uploading CSV with data for `annualUsageCollectionTracking` records"
   * "ToDo: Create test using Selenium to upload formatter R4 reports into single RawCOUNTERReport object, then RawCOUNTERReport.perform_deduplication_matching"
   * "ToDo: Create test for route showing data in database at end of initialization wizard"


Blueprint `login`
=================
Tests in *"test_bp_login.py"*

* Create route/page for login page
* Establish if there's going to be a single user login and a single admin login, or if everyone has their own login
* Create other routes and pages required by library
* Test module:

   * Create test to login as regular user
   * Create test to log in as admin user
   * Have note to do tests with and without Selenium--meaning programatically and by simulating UI interactions?


Blueprint `view_resources`
============================
Tests in *"test_bp_view_resources.py"*

* Create route for viewing resources list
* Create page for viewing resources list where all resources have their default metadata and links to a page with more details and, later on, a trigger for adding a record to the Resources relation
* Create route/page for adding or editing a resource (editing a resource is more important than adding a resource) (associated Vendor records are chosen here)
* Create route/page for viewing resource details
* Test module:

   * Create test for route to resources list
   * Create test for route to add a resource
   * Create test for route to edit a resource
   * Create test for route to view resource details


Blueprint `view_sources`
============================
Tests in *"test_bp_view_sources.py"*

* Create route for viewing list of StatisticsSources or ResourceSources records
* Create page listing all StatisticsSources or ResourceSources with their vendor, if they're active, and a link to more details as well as a trigger for the method to add a record to the relation being listed
* Create route to view record details
* Determine if StatisticsSources and ResourceSources are similar enough to use the same template to display details, then create one or two pages to show record details
* Work out details for route/page for adding and editing StatisticsSources and ResourceSources records
* Test module:

   * Create test for route to view list of records for both StatisticsSources and ResourceSources
   * Create test for route to add record for both StatisticsSources and ResourceSources
   * Create test for route to edit record for both StatisticsSources and ResourceSources
   * Create test for route to view record details for both StatisticsSources and ResourceSources


Blueprint `view_usage`
============================
Tests in *"test_bp_view_usage.py"*

* Create route/page for blueprint homepage for choosing how to construct query
* Create route/page where SQL string can be entered and run against database
* Create route/page for query wizard
* Create route/page for canned queries
* Create route/page for downloading/displaying query results
* Test module:

   * Create test for route to homepage
   * Create test using Selenium to enter SQL into free SQL text box
   * Create test using selenium for choosing canned queries
   * Create test using Selenium to make selections in query wizard to generate given SQL string
   * Create test using Selenium to make selections in query wizard to return a given result where the fixture module is the contents of the database
   * Create test for downloading query results


Blueprint `view_vendors`
============================
Tests in *"test_bp_view_vendors.py"*

* Create route/page for vendors list including link to notes and trigger to method for adding new record to Vendors relation
* Create route/page for adding or editing a vendor record
* Create route/page for viewing notes, only type of other details a Vendors record has
* Test module:

   * Create test for route to homepage
   * Create test for route to add new vendor
   * Create test for route to edit vendor
   * Create test for route to view vendor details