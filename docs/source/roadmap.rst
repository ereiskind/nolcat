NoLCAT Development Roadmap
##########################
This page contains all the current to-dos and possible plans for the NoLCAT program.

To Investigate
**************
This is a list of issues encountered over the course of development that require further investigation.

* A ScienceDirect SUSHI call returned ``401 Client Error: Unauthorized for url``; since Elsevier manages SUSHI out of the developer/API portal for all their products, the credentials can't be easily checked and/or reset
* J-STAGE uses a customer ID and the institutional IP ranges for authentication, so SUSHI calls from AWS are denied access
* JSTOR status call returned ``None`` 2023-06-08
* Morgan & Claypool raised ``HTTPSConnectionPool(host='www.morganclaypool.com', port=443): Max retries exceeded with url: /reports?... (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x7f838d4b84f0>, 'Connection to www.morganclaypool.com timed out. (connect timeout=90)')) and HTTPSConnectionPool(host='www.morganclaypool.com', port=443): Max retries exceeded with url: /reports?... (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f838d4b8eb0>: Failed to establish a new connection: [Errno 110] Connection timed out'))``
* Certificate issues raising errors with

  * *Allen Press/Pinnacle Hosting*: ``HTTPSConnectionPool(host='pinnacle-secure.allenpress.com', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'pinnacle-secure.allenpress.com' doesn't match either of '*.literatumonline.com', 'literatumonline.com'")))``
  * *Grain Science Library*: ``HTTPSConnectionPool(host='aaccipublications.aaccnet.org', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'aaccipublications.aaccnet.org' doesn't match either of '*.scientificsocieties.org', 'scientificsocieties.org'")))``
  * *Adam matthew*: ``HTTPSConnectionPool(host='www.counter.amdigital.co.uk', port=443): Max retries exceeded with url: /CounterSushi5Api/status?... (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1131)')))``
  * *Sciendo*: ``HTTPSConnectionPool(host='ams.degruyter.com', port=443): Max retries exceeded with url: /rest/COUNTER/v5/status?... (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fb5414a4520>: Failed to establish a new connection: [Errno -2] Name or service not known'))``

Planned Iterations
******************
* Add documentation about adding records to ``fiscalYears`` relation via SQL command line
* Resolve HTTP response 502/upload gateway error when uploading COUNTER reports via web app

  * https://stackoverflow.com/questions/27396248/uwsgi-nginx-flask-upstream-prematurely-closed
  * https://stackoverflow.com/questions/49162420/upstream-prematurely-closed-connection-while-reading-response-header-from-upstr
  * https://serverfault.com/questions/926642/uwsgi-and-nginx-502-upstream-prematurely-closed-connection

Iteration 1: Complete Current Data I/O
======================================
* Create ability to ingest SQL file with proper insert statements [Search file, extract lines matching regex ``^INSERT INTO `COUNTERData` VALUES.*;$``, and load them into database]
* Add instructions to "ingest_usage/upload-COUNTER-reports.html" page
* Write ``tests.test_AnnualUsageCollectionTracking.test_upload_nonstandard_usage_file()``
* Finish ``nolcat.view_usage.views.use_predefined_SQL_query()`` for the standard views
* Finish "query-wizard.html"
* Write ``tests.test_bp_view_usage.test_use_predefined_SQL_query_with_COUNTER_standard_views()``
* Add names and descriptions of standard views to ``nolcat.view_usage.forms.QueryWizardForm()``

Iteration 2: Add Historical Data
================================
* Update "initialization/initial-data-upload-3.html" by removing commented out field and adding instructions for tabular COUNTER ingest
* Remove commenting out from end of ``nolcat.initialization.views.collect_AUCT_and_historical_COUNTER_data()``
* Set redirect at end of ``nolcat.initialization.views.collect_AUCT_and_historical_COUNTER_data()`` to ``nolcat.initialization.views.upload_historical_non_COUNTER_usage()``
* Remove commenting out from end of ``tests.test_bp_initialization.test_collect_AUCT_and_historical_COUNTER_data()``
* Copy ``nolcat.ingest_usage.forms.UsageFileForm()`` to ``nolcat.initialization.forms``
* Write "initialization/initial-data-upload-4.html" page
* Write ``initialization.views.upload_historical_non_COUNTER_usage()`` with ``nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_files()``
* Remove commenting out from ``tests.test_bp_initialization.test_collect_AUCT_and_historical_COUNTER_data()``
* Remove commenting out from ``tests.test_bp_initialization.test_COUNTERData_relation_to_database()``
* Write ``tests.test_bp_initialization.test_GET_request_for_upload_historical_non_COUNTER_usage()``
* Write ``tests.test_bp_initialization.test_upload_historical_non_COUNTER_usage()``
* Finish ``nolcat.ingest_usage.views.upload_non_COUNTER_reports()`` with ``nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_files()``
* Write ``tests.test_bp_ingest_usage.test_upload_non_COUNTER_reports()``
* Finish ``tests.test_bp_ingest_usage.test_GET_request_for_upload_non_COUNTER_reports()``
* Write "ingest_usage/upload-non-COUNTER-usage.html" page
* Get drop-down in "view_usage/download-non-COUNTER-usage.html" to work

Iteration 3: Minimum Viable Product with Tests and Test Database
================================================================
* Create the temporary database for testing: Per Flask's documentation on testing, tests interacting with a database should be able to use a testing database separate from but built using the same factory as the production database. The resources to consult are in ``tests.conftest``.
* Finish ``tests.test_bp_view_usage.test_GET_request_for_download_non_COUNTER_usage()``, including altering test data so one of the records in the AUCT relation has a non-null value in ``annualUsageCollectionTracking.usage_file_path``
* Write ``tests.test_FiscalYears.test_calculate_ACRL_60b()``
* Write ``tests.test_FiscalYears.test_calculate_ACRL_63()``
* Write ``tests.test_FiscalYears.test_calculate_ARL_18()``
* Write ``tests.test_FiscalYears.test_calculate_ARL_19()``
* Write ``tests.test_FiscalYears.test_calculate_ARL_20()``
* Write ``tests.test_bp_view_usage.test_download_non_COUNTER_usage()``
* Write ``tests.test_AnnualUsageCollectionTracking.test_collect_annual_usage_statistics()``--how should this be different from the check for the SUSHI call class beyond checking to see if the ``annualUsageCollectionTracking.collection_status`` value updated?

Basic Enhancement Iterations
****************************
These iterations make NoLCAT more robust and easier to use through relatively small adjustments. Many of these iterations move functionality from the SQL command line to the GUI.

Iteration 0: Prepare for COUNTER R5.1
=====================================
* Develop the procedures for "Create R5.1 SUSHI Response JSON Reports" in the testing documentation
* Add the data to the files in "tests/data/R5.1_COUNTER_JSONs_for_tests"
* Write ``ConvertJSONDictToDataframe._create_dataframe_from_R5b1_JSON()``
* Add fixtures for the new files in ``tests.test_ConvertJSONDictToDataframe``
* Write ``tests.test_ConvertJSONDictToDataframe.test_create_dataframe_from_R5b1_JSON()``

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

Iteration 5: Create Drop-Down Lists
===================================
* If unable to previously get drop-downs to work, make ``nolcat.ingest_usage.forms.UsageFileForm.AUCT_option`` a drop-down field and adjust ``nolcat.ingest_usage.views.upload_non_COUNTER_reports()`` as needed
* If unable to previously get drop-downs to work, finish ``tests.test_bp_ingest_usage.test_GET_request_for_upload_non_COUNTER_reports()``
* Make ``nolcat.ingest_usage.forms.SUSHIParametersForm.statistics_source`` a drop-down field

Iteration 6: Create Query Wizard
================================
* Finish ``nolcat.view_usage.views.use_predefined_SQL_query()``
* Craft queries to use
* Create drop-down fields for COUNTER elements in ``nolcat.view_usage.forms.QueryWizardForm()``
* Write ``tests.test_bp_view_usage.test_use_predefined_SQL_query_with_wizard()``

Iteration 7: Show Fiscal Year Information
=========================================
* Finish ``nolcat.annual_stats.views.annual_stats_homepage()``
* Finish ``nolcat.annual_stats.views.show_fiscal_year_details()``
* Finish ``nolcat.annual_stats.forms.RunAnnualStatsMethodsForm()``
* Finish ``nolcat.annual_stats.forms.EditFiscalYearForm()``
* Finish "annual_stats/fiscal-year-details.html"
* Write ``tests.test_bp_annual_stats.test_GET_request_for_show_fiscal_year_details()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_RunAnnualStatsMethodsForm()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditFiscalYearForm()``

Iteration 8: Show Annual Usage Collection Tracking Information
==============================================================
* Finish ``nolcat.annual_stats.views.annual_stats_homepage()``
* Finish ``nolcat.annual_stats.forms.EditAUCTForm()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditAUCTForm()``

Iteration 9: Initiate All SUSHI Collection for Fiscal Year
===========================================================
* Finish ``nolcat.models.FiscalYears.collect_fiscal_year_usage_statistics()``
* Write ``tests.test_FiscalYears.test_collect_fiscal_year_usage_statistics()``

Iteration 10: Switch Message Display from Stdout to Flask
=========================================================
* Make second return statement in ``nolcat.models.StatisticsSources.fetch_SUSHI_information()`` display in Flask
* Write ``tests.test_StatisticsSources.test_fetch_SUSHI_information_for_display()``
* Use tkinter messagebox to get information from user in ``nolcat.SUSHI_call_and_response.SUSHICallAndResponse._handle_SUSHI_exceptions()``

Iteration 11: Create UI Design and Jinja Templates
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