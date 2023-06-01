NoLCAT Development Roadmap
##########################
This page contains all the current to-dos and possible plans for the NoLCAT program.

To Investigate
**************
This is a list of issues encountered over the course of development that require further investigation.

* A ScienceDirect SUSHI call returned ``401 Client Error: Unauthorized for url``; since Elsevier manages SUSHI out of the developer/API portal for all their products, the credentials can't be easily checked and/or reset
* Certificate issues raising errors with

  * *Allen Press/Pinnacle Hosting*: ``HTTPSConnectionPool(host='pinnacle-secure.allenpress.com', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'pinnacle-secure.allenpress.com' doesn't match either of '*.literatumonline.com', 'literatumonline.com'")))``
  * *Grain Science Library*: ``HTTPSConnectionPool(host='aaccipublications.aaccnet.org', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'aaccipublications.aaccnet.org' doesn't match either of '*.scientificsocieties.org', 'scientificsocieties.org'")))``
  * *Adam matthew*: ``HTTPSConnectionPool(host='www.counter.amdigital.co.uk', port=443): Max retries exceeded with url: /CounterSushi5Api/status?... (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1131)')))``

Planned Iterations
******************
* Write ``nolcat.app.upload_file_to_S3_bucket()``
* Write ``tests.test_app.test_upload_file_to_S3_bucket()``
* Create R5.1 test data JSONs

  * Develop the procedures for "Create R5.1 SUSHI Response JSON Reports" in the testing documentation
  * Add the data to the files in "tests/data/R5.1_COUNTER_JSONs_for_tests"
  * Add fixtures for the new files in ``tests.test_ConvertJSONDictToDataframe``
  * Add test for the new files in ``tests.test_ConvertJSONDictToDataframe``

* Write ``ConvertJSONDictToDataframe._create_dataframe_from_R5b1_JSON()``
* Investigate ways to get list of plain text and JSON files saved in S3 bucket due to inability to load into database, load files with ``json.load(<class '_io.TextIOWrapper'>)``, and manipulate contents so they can be added to database

Iteration 2: COUNTER Only Product
=================================
* Write ``tests.test_bp_ingest_usage.test_upload_COUNTER_reports()``
* Create ability to ingest SQL file with proper insert statements [Line starts with ``INSERT INTO `COUNTERData` VALUES (`` and ends with ``);``, in between should be split at each instance of ``),(`` to create the individual insert statements, which can be turned into records in a dataframe that can go into the database via ``to_sql()``]
* Create "ingest_usage/upload-COUNTER-reports.html" page
* Update "initialization/initial-data-upload-3.html" by removing commented out field and adding instructions for tabular COUNTER ingest
* Remove commenting out from end of ``nolcat.initialization.views.collect_AUCT_and_historical_COUNTER_data()``
* Remove commenting out from ``tests.test_bp_initialization.test_collect_AUCT_and_historical_COUNTER_data()``
* Remove commenting out from ``tests.test_bp_initialization.test_COUNTERData_relation_to_database()``

Iteration 3: Minimum Viable Product
===================================
* Set redirect at end of ``nolcat.initialization.views.collect_AUCT_and_historical_COUNTER_data()`` to ``nolcat.initialization.views.upload_historical_non_COUNTER_usage()``
* Remove commenting out from end of ``tests.test_bp_initialization.test_collect_AUCT_and_historical_COUNTER_data()``
* Write form class for non-COUNTER usage downloads
* Write "initialization/initial-data-upload-4.html" page
* Write ``nolcat.initialization.views.upload_historical_non_COUNTER_usage()`` with ``nolcat.app.upload_file_to_S3_bucket()``
* Write ``tests.test_bp_initialization.test_GET_request_for_upload_historical_non_COUNTER_usage()``
* Write ``tests.test_bp_initialization.test_upload_historical_non_COUNTER_usage()``
* Write ``nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()``
* Write ``tests.test_AnnualUsageCollectionTracking.test_upload_nonstandard_usage_file()``
* Finish ``nolcat.ingest_usage.views.upload_non_COUNTER_reports()`` with ``nolcat.ingest_usage.forms.UsageFileForm.AUCT_option`` as two separate int fields if needed
* Write ``tests.test_bp_ingest_usage.test_upload_non_COUNTER_reports()``
* If able to get drop-down working, finish ``tests.test_bp_ingest_usage.test_GET_request_for_upload_non_COUNTER_reports()``
* Create "ingest_usage/save-non-COUNTER-usage.html" page
* Adjust form in "view_usage/download-non-COUNTER-usage.html" so all the options can be selected
* Add documentation about adding records to ``fiscalYears`` relation via SQL command line
* Figure out how to get "Check if Usage Is Already in Database" subsection of ``nolcat.models.StatisticsSources._harvest_R5_SUSHI()`` to work

Iteration 4: Minimum Viable Product with Tests and Test Database
================================================================
* Create the temporary database for testing: Per Flask's documentation on testing, tests interacting with a database should be able to use a testing database separate from but built using the same factory as the production database. The resources below have been consulted in multiple attempts to get this set up, but have thus far proven unsuccessful.

    * https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
    * https://flask.palletsprojects.com/en/2.0.x/testing/
    * https://porter.codes/2020/07/24/Pytest-Sqlalchemy-Test-Fixutres.html
    * https://spotofdata.com/flask-testing/
    * http://alexmic.net/flask-sqlalchemy-pytest/
    * https://www.patricksoftwareblog.com/unit-testing-a-flask-application/ (this uses unittest instead of pytest)
    * Possibly https://stackoverflow.com/questions/67255653/how-to-set-up-and-tear-down-a-database-between-tests-in-fastapi
    * Possibly https://github.com/ClearcodeHQ/pytest-mysql
    * Possibly https://pypi.org/project/pytest-sqlalchemy/
    * https://medium.com/@geoffreykoh/fun-with-fixtures-for-database-applications-8253eaf1a6d
    * Add https://pypi.org/project/pycodestyle/ at this point?
    * Possibly use https://pypi.org/project/pytest-order/ ?

* Finish ``tests.test_bp_view_usage.test_GET_request_for_download_non_COUNTER_usage()``
* Write ``tests.test_FiscalYears.test_calculate_ACRL_60b()``
* Write ``tests.test_FiscalYears.test_calculate_ACRL_63()``
* Write ``tests.test_FiscalYears.test_calculate_ARL_18()``
* Write ``tests.test_FiscalYears.test_calculate_ARL_19()``
* Write ``tests.test_FiscalYears.test_calculate_ARL_20()``
* Write ``tests.test_bp_view_usage.test_download_non_COUNTER_usage()``
* Write ``tests.test_AnnualUsageCollectionTracking.test_collect_annual_usage_statistics()``--how should this be different from the check for the SUSHI call class beyond checking to see if the ``annualUsageCollectionTracking.collection_status`` value updated?
* Write test for ``nolcat.app.upload_file_to_S3_bucket()``

Basic Enhancement Iterations
****************************
These iterations make NoLCAT more robust and easier to use through relatively small adjustments. Many of these iterations move functionality from the SQL command line to the GUI.

Iteration 1: View Lists
=======================
* Confirm variable routes in "annual_stats/index.html" work
* Finish ``nolcat.view_lists.views.view_lists_homepage()``
* Create "view_lists/index.html" page
* Write ``tests.test_bp_view_list.test_view_lists_homepage()``
* Write ``tests.test_bp_view_list.test_GET_request_for_view_list_record()``
* Finish ``nolcat.view_lists.views.view_list_record()``
* Create "view_lists/view_record.html" page
* Finish ``nolcat.view_lists.views.edit_list_record()``
* Create "view_lists/edit_record.html" page
* Create form classes needed for editing
* Write ``tests.test_bp_view_list.test_GET_request_for_edit_list_record_for_existing_record()``
* Write ``tests.test_bp_view_list.test_GET_request_for_edit_list_record_for_new_record()``
* Write ``tests.test_bp_view_list.test_edit_list_record()``

Iteration 2: Update Statistics Sources to Resource Sources Relationship
=======================================================================
* Finish ``nolcat.models.ResourceSources.change_StatisticsSource()``
* Update "view_lists/edit_record.html" and accompanying form as necessary
* Write ``tests.test_ResourceSources.test_change_StatisticsSource()``

Iteration 3: Update Access Stop Date Attribute
==============================================
* Write ``nolcat.models.ResourceSources.add_access_stop_date()``
* Write ``nolcat.models.ResourceSources.remove_access_stop_date()``
* Update "view_lists/edit_record.html" and accompanying form as necessary
* Write ``tests.test_ResourceSources.test_add_access_stop_date()``
* Write ``tests.test_ResourceSources.test_remove_access_stop_date()``

Iteration 4: Add Notes
======================
* Write form class for adding notes
* Add form for adding notes to "view_lists/view_record.html"
* Write ``tests.test_bp_view_list.test_view_list_record()``
* Write ``nolcat.models.StatisticsSources.add_note()``
* Write ``tests.test_StatisticsSources.test_add_note()``
* Write ``nolcat.models.Vendors.add_note()``
* Write ``tests.test_Vendors.test_add_note()``
* Write ``nolcat.models.ResourceSources.add_note()``
* Write ``tests.test_ResourceSources.test_add_note()``

Iteration 5: Create CSV Downloads from COUNTER Data
===================================================
* Finish ``nolcat.view_usage.views.use_predefined_SQL_query()``
* Finish "query-wizard.html"
* Write ``tests.test_bp_view_usage.test_use_predefined_SQL_query_with_COUNTER_standard_views()``
* Write ``tests.test_bp_view_usage.test_use_predefined_SQL_query_with_wizard()``
* Add names and descriptions of standard views to ``nolcat.view_usage.forms.QueryWizardForm()``

Iteration 6: Create Drop-Down Lists
===================================
* If unable to previously get drop-downs to work, make ``nolcat.ingest_usage.forms.UsageFileForm.AUCT_option`` a drop-down field and adjust ``nolcat.ingest_usage.views.upload_non_COUNTER_reports()`` as needed
* If unable to previously get drop-downs to work, finish ``tests.test_bp_ingest_usage.test_GET_request_for_upload_non_COUNTER_reports()``
* Make ``nolcat.ingest_usage.forms.SUSHIParametersForm.statistics_source`` a drop-down field

Iteration 7: Create Query Wizard
================================
* Craft queries to use
* Create drop-down fields for COUNTER elements in ``nolcat.view_usage.forms.QueryWizardForm()``

Iteration 8: Show Fiscal Year Information
=========================================
* Finish ``nolcat.annual_stats.views.annual_stats_homepage()``
* Finish ``nolcat.annual_stats.views.show_fiscal_year_details()``
* Finish ``nolcat.annual_stats.forms.RunAnnualStatsMethodsForm()``
* Finish ``nolcat.annual_stats.forms.EditFiscalYearForm()``
* Finish "annual_stats/fiscal-year-details.html"
* Write ``tests.test_bp_annual_stats.test_GET_request_for_show_fiscal_year_details()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_RunAnnualStatsMethodsForm()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditFiscalYearForm()``

Iteration 9: Show Annual Usage Collection Tracking Information
==============================================================
* Finish ``nolcat.annual_stats.views.annual_stats_homepage()``
* Finish ``nolcat.annual_stats.forms.EditAUCTForm()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditAUCTForm()``

Iteration 10: Initiate All SUSHI Collection for Fiscal Year
===========================================================
* Finish ``nolcat.models.FiscalYears.collect_fiscal_year_usage_statistics()``
* Write ``tests.test_FiscalYears.test_collect_fiscal_year_usage_statistics()``

Iteration 11: Switch Message Display from Stdout to Flask
=========================================================
* Make second return statement in ``nolcat.models.StatisticsSources.fetch_SUSHI_information()`` display in Flask
* Write ``tests.test_StatisticsSources.test_fetch_SUSHI_information_for_display()``
* Make return statements with strings in ``nolcat.models.StatisticsSources._harvest_R5_SUSHI()`` display in Flask
* Make return statements with key "ERROR" in ``nolcat.SUSHI_call_and_response.SUSHICallAndResponse.make_SUSHI_call()`` display in Flask
* Use tkinter messagebox to get information from user in ``nolcat.SUSHI_call_and_response.SUSHICallAndResponse._handle_SUSHI_exceptions()``

Iteration 12: Create UI Design and Jinja Templates
==================================================
* Clean up CSS file
* Create CSS class for flashed messages
* Create Jinja template header and footer in "nolcat/templates/layout.html"

Open Source Iterations
**********************
These iterations contain updates necessary for NoLCAT to be used as an open source program.

Iteration 1: Create Downloadable AUCT Template
==============================================
* Finish creation of "initialize_annualUsageCollectionTracking.csv" in ``nolcat.initialization.views.collect_AUCT_and_historical_COUNTER_data()``
* Update ``tests.test_bp_initialization.test_GET_request_for_collect_AUCT_and_historical_COUNTER_data()``

Iteration 2: Make Initialization Forms Downloadable
===================================================
* Get Jinja download to work in "initialization/index.html", "initialization/initial-data-upload-2.html", and "initialization/initial-data-upload-3.html"
* Write ``tests.test_bp_initialization.test_download_file()``

Iteration 3: Write ``__repr__`` Methods
=======================================
* Write ``nolcat.models.FiscalYears.__repr__()``
* Write ``nolcat.models.Vendors.__repr__()``
* Write ``nolcat.models.VendorNotes.__repr__()``
* Write ``nolcat.models.StatisticsSourceNotes.__repr__()``
* Write ``nolcat.models.ResourceSources.__repr__()``
* Write ``nolcat.models.ResourceSourceNotes.__repr__()``
* Write ``nolcat.models.StatisticsResourceSources.__repr__()``
* Write ``nolcat.models.AnnualUsageCollectionTracking.__repr__()``
* Write ``nolcat.models.COUNTERData.__repr__()``

Iteration 4: Formalize Documentation
====================================
* Update and flesh out README according to best practices
* Run command line operations ``sphinx-apidoc -o docs/source/ nolcat`` and ``make html`` for Sphinx
* Organize custom documentation pages on Sphinx index

Iteration 5: Display Data Uploaded at End of Initialization
===========================================================
* Add display of all data in the database to "initialization/show-loaded-data.html"
* Write ``tests.test_bp_initialization.test_data_load_complete()``

Iteration 6: Correct 500 Error Function
=======================================
* Get HTTP 500 error handler to work

Iteration 7: Confirm Flask-SQLAlchemy Enum
==========================================
* Confirm that ``nolcat.models.AnnualUsageCollectionTracking.collection_status`` properly creates and behaves as an enum

Aspirational Iterations
***********************
These iterations would create features that would be nice to have but aren't necessary to basic functionality. Some are fairly simple; others are quite ambitious.

Iteration: View All Associated Resource and Statistics Sources in a Vendor Record
=================================================================================
* Finish ``nolcat.models.Vendors.get_statisticsSources()``
* Write ``tests.test_Vendors.test_get_statisticsSources_records()``
* Finish ``nolcat.models.Vendors.get_resourceSources()``
* Write ``tests.test_Vendors.test_get_resourceSources_records()``
* Add ``nolcat.models.Vendors.get_statisticsSources()`` and ``nolcat.models.Vendors.get_resourceSources()`` to ``nolcat.view_lists.views.view_list_record()`` when vendors are being displayed

Iteration: Create Method for Adding New Fiscal Years to the Relation
====================================================================
* Determine the best method to add a record for the new fiscal year to the ``FiscalYears`` relation (ideally with automatic execution each July 1)

Iteration: Allow User-Created SQL Queries
=========================================
* Figure out how to prevent SQL injection in ``nolcat.view_usage.views.run_custom_SQL_query()``
* Write ``tests.test_bp_view_usage.test_run_custom_SQL_query()``

Iteration: Display Results of Usage Data Requests in Browser
============================================================
* Modify routes in ``nolcat.view_usage.views`` that return CSVs to return HTML pages from which those CSVs can be downloaded
* Show dataframes used to create CSVs in browser (see https://stackoverflow.com/q/52644035 and https://stackoverflow.com/q/22180993 for info about adding dataframes to Flask display)

Iteration: Display Data Visualization of Usage Data Requests in Browser
=======================================================================
* Make final decision between Plotly/Dash and Bokeh
* Change dataframes displayed as tables in browser to data visualizations

Iteration: Get SUSHI Credentials from Alma
==========================================
* Add way to determine if data should be fetched from Alma or the JSON file at the beginning of ``nolcat.models.StatisticsSources.fetch_SUSHI_information()``
* Write "Retrieve Data from Alma" subsection of ``nolcat.models.StatisticsSources.fetch_SUSHI_information()``

Iteration: Add User Accounts to Restrict Access
===============================================
* Add "Flask-User" library
* Establish if there's going to be a single user login and a single admin login, or if everyone has their own login
* Write ``tests.test_bp_login.test_logging_in()``
* Write ``tests.test_bp_login.test_logging_in_as_admin()``
* Write ``tests.test_bp_login.test_creating_an_account()``
* Create redirect to ``nolcat.initialization.views.collect_FY_and_vendor_data()`` after the creation of the first account with data ingest permissions

Iteration: Deduplicate Resources
================================
* Review the main branch of the repo as of commit 207c4a14b521b7f247f5249a080b4a725963b599 (made 2023-01-20)
* Remove hyphens from all ISBNs to handle their inconsistency in usage and placement

Iteration: Handle Reports Without Corresponding Customizable Reports
====================================================================
* Figure out how to view reports found in subsection "Add Any Standard Reports Not Corresponding to a Customizable Report" of ``nolcat.models.StatisticsSources._harvest_R5_SUSHI()``

Iteration: Incorporate Springshare Databases A-Z Statistics
===========================================================
* Create relation with the databases in the Springshare Databases A-Z list
* Connect values in the above relation with ``resourceSources`` records through a foreign key in the new relation or a junction table
* Create other relation(s) to hold the usage data in a normalized fashion
* Add relation classes to ``nolcat.models`` for all the newly created relations

Iteration: Incorporate OpenAthens Statistics
============================================
* Create relation with the activated resources in the OpenAthens resource catalog
* Connect values in the above relation with ``resourceSources`` records through a foreign key in the new relation or a junction table
* Create other relation(s) to hold the usage data in a normalized fashion
* Add relation classes to ``nolcat.models`` for all the newly created relations

Iteration: Incorporate Embargo and Paywall Data
===============================================
* Add fields to relation for resources for the embargo and paywall data
* Create templates in query wizard that separates usage into before and after embargo and/or paywall dates based on the ``YOP`` field