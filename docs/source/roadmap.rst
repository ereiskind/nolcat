NoLCAT Development Roadmap
##########################
This page contains all the current to-dos and possible plans for the NoLCAT program.

To Investigate
**************
This is a list of issues encountered over the course of development that require further investigation.

* A ScienceDirect SUSHI call returned ``401 Client Error: Unauthorized for url``; since Elsevier manages SUSHI out of the developer/API portal for all their products, the credentials can't be easily checked and/or reset
* J-STAGE uses a customer ID and the institutional IP ranges for authentication, so SUSHI calls from AWS are denied access
* Morgan & Claypool raised ``HTTPSConnectionPool(host='www.morganclaypool.com', port=443): Max retries exceeded with url: /reports?... (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x7f838d4b84f0>, 'Connection to www.morganclaypool.com timed out. (connect timeout=90)')) and HTTPSConnectionPool(host='www.morganclaypool.com', port=443): Max retries exceeded with url: /reports?... (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f838d4b8eb0>: Failed to establish a new connection: [Errno 110] Connection timed out'))``
* Certificate issues raising errors with

  * *Allen Press/Pinnacle Hosting*: ``HTTPSConnectionPool(host='pinnacle-secure.allenpress.com', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'pinnacle-secure.allenpress.com' doesn't match either of '*.literatumonline.com', 'literatumonline.com'")))``
  * *Grain Science Library*: ``HTTPSConnectionPool(host='aaccipublications.aaccnet.org', port=443): Max retries exceeded with url: /status?... (Caused by SSLError(CertificateError("hostname 'aaccipublications.aaccnet.org' doesn't match either of '*.scientificsocieties.org', 'scientificsocieties.org'")))``
  * *Adam matthew*: ``HTTPSConnectionPool(host='www.counter.amdigital.co.uk', port=443): Max retries exceeded with url: /CounterSushi5Api/status?... (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1131)')))``
  * *Sciendo*: ``HTTPSConnectionPool(host='ams.degruyter.com', port=443): Max retries exceeded with url: /rest/COUNTER/v5/status?... (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fb5414a4520>: Failed to establish a new connection: [Errno -2] Name or service not known'))``

Planned Iterations
******************
* Figure out how to make fuzzy matching work--as of now, test including fuzzy search for "EBSCO" passes but doesn't return "EBSCOhost" as a match

Prepare for COUNTER R5.1
========================
* Develop the procedures for "Create R5.1 SUSHI Response JSON Reports" in the testing documentation
* Add the data to the files in "tests/data/R5.1_COUNTER_JSONs_for_tests"
* Write ``ConvertJSONDictToDataframe._create_dataframe_from_R5b1_JSON()``
* Add fixtures for the new files in ``tests.test_ConvertJSONDictToDataframe``
* Write ``tests.test_ConvertJSONDictToDataframe.test_create_dataframe_from_R5b1_JSON()``

Move COUNTER Data to Parquet Files in S3
========================================
* Create constant for use in determining location of parquet files
* Create function for making S3 folder for each ``statisticsSource`` instance, with name of PK number, at first SUSHI pull for that source
* Create function to save COUNTER dataframe into a parquet file
* Adjust functions below to use parquet instead of MySQL

  * ``nolcat.ingest_usage.upload_COUNTER_data()``
  * ``tests.test_bp_ingest_usage.test_upload_COUNTER_data_via_Excel()``
  * ``nolcat.initialization.collect_AUCT_and_historical_COUNTER_data()``
  * ``tests.test_bp_initialization.test_GET_request_for_collect_AUCT_and_historical_COUNTER_data()``
  * ``nolcat.models.fiscalYears.collect_fiscal_year_usage_statistics()``
  * ``tests.test_FiscalYears.FY2022_FiscalYears_object()``
  * ``tests.test_FiscalYears.test_collect_fiscal_year_usage_statistics()``
  * ``nolcat.models.statisticsSources.collect_usage_statistics()``
  * ``tests.test_StatisticsSources.test_collect_usage_statistics()``
  * ``nolcat.models.annualUsageCollectionTracking.collect_annual_usage_statistics()``
  * ``tests.test_AnnualUsageCollectionTracking.test_collect_annual_usage_statistics()``

* Modify or create alternate versions of functions below and modify calls to them to adjust for parquet

  * ``nolcat.statements.add_data_success_and_update_database_fail_statement()``
  * ``nolcat.statements.database_function_skip_statements()``
  * ``nolcat.statements.load_data_into_database_success_regex()``
  * ``nolcat.statements.reports_with_no_usage_regex()``

* Determine what code, if any, is needed in Step Functions to let Glue combine parquet with MySQL of other relations
* Have SQL queries including ``COUNTERData`` relation use Athena instead of pandas/SQLAlchemy/MySQL

Iteration 3: Minimum Viable Product
===================================
* Adjust form in "view_usage/download-non-COUNTER-usage.html" so all the options can be selected
* Add documentation about adding records to ``fiscalYears`` relation via SQL command line

Iteration 4: Minimum Viable Product with Tests and Test Database
================================================================
* Create the temporary database for testing: Per Flask's documentation on testing, tests interacting with a database should be able to use a testing database separate from but built using the same factory as the production database. The resources to consult are in ``tests.conftest``.

Basic Enhancement Iterations
****************************
These iterations make NoLCAT more robust and easier to use through relatively small adjustments. Many of these iterations move functionality from the SQL command line to the GUI.

Iteration 1: View Lists
=======================
* Finish ``tests.test_bp_view_list.test_view_lists_homepage()``
* Write ``tests.test_bp_view_list.test_GET_request_for_view_list_record()``
* Finish ``nolcat.view_lists.views.view_list_record()``
* Create "view_lists/view-record.html" page
* Write ``tests.test_bp_view_list.test_GET_request_for_edit_list_record_for_existing_record()``

Iteration 2: Edit Lists
=======================
* Create form classes needed for editing
* Add link for creating new record to "view_lists/index.html" page
* Finish ``nolcat.view_lists.views.edit_list_record()``
* Create "view_lists/edit-record.html" page
* Write ``tests.test_bp_view_list.test_GET_request_for_edit_list_record_for_new_record()``
* Write ``tests.test_bp_view_list.test_edit_list_record()``
* Write ``tests.test_ResourceSources.test_change_StatisticsSource()``
* Write ``tests.test_ResourceSources.test_add_access_stop_date()``
* Write ``tests.test_ResourceSources.test_remove_access_stop_date()``

Iteration 3: Add Notes
======================
* Write form class for adding notes
* Add form for adding notes to "view_lists/view_record.html"
* Write ``nolcat.models.StatisticsSources.add_note()``
* Write ``tests.test_StatisticsSources.test_add_note()``
* Write ``nolcat.models.Vendors.add_note()``
* Write ``tests.test_Vendors.test_add_note()``
* Write ``nolcat.models.ResourceSources.add_note()``
* Write ``tests.test_ResourceSources.test_add_note()``
* Write ``nolcat.models.VendorNotes.__repr__()``
* Write ``nolcat.models.StatisticsSourceNotes.__repr__()``
* Write ``nolcat.models.ResourceSourceNotes.__repr__()``
* Write ``nolcat.models.AnnualUsageCollectionTracking.__repr__()``

Iteration 4: Show and Edit Fiscal Year Information
==================================================
* Finish ``nolcat.annual_stats.forms.RunAnnualStatsMethodsForm()``
* Finish ``nolcat.annual_stats.forms.EditFiscalYearForm()``
* Finish ``nolcat.annual_stats.forms.EditAUCTForm()``
* Finish ``nolcat.annual_stats.views.show_fiscal_year_details()``
* Finish "annual_stats/fiscal-year-details.html"
* Finish ``tests.test_bp_annual_stats.test_GET_request_for_annual_stats_homepage()``
* Write ``tests.test_bp_annual_stats.test_GET_request_for_show_fiscal_year_details()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_RunAnnualStatsMethodsForm()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditFiscalYearForm()``
* Write ``tests.test_bp_annual_stats.test_show_fiscal_year_details_submitting_EditAUCTForm()``
* Write ``nolcat.models.AnnualStatistics.add_annual_statistic_value()``
* Write ``tests.test_AnnualStatistics_test_add_annual_statistic_value()``

Iteration 5: Switch Message Display from Stdout to Flask
=========================================================
* Make second return statement in ``nolcat.models.StatisticsSources.fetch_SUSHI_information()`` display in Flask

Iteration 6: Miscellaneous
==================================================
* Clean up CSS file
* Create CSS class for flashed messages
* Add FSU Libraries wordmark as link to library homepage in footer
* Consolidate ``nolcat.models.StatisticsSources._check_if_data_in_database()`` and ``nolcat.app.check_if_data_already_in_COUNTERData()``

Iteration 7: Interact with Host File System
============================================
* Figure out how tests run in the instance can get metadata about and interact with the file system of the host/host workstation
* Finish ``tests.test_app.default_download_folder()``
* Update ``tests.test_app.test_download_file()`` to use ``tests.test_app.default_download_folder()``

Open Source Iterations
**********************
These iterations contain updates necessary for NoLCAT to be used as an open source program.

Iteration 1: Formalize Documentation
====================================
* Update and flesh out README according to best practices
* Run command line operations ``sphinx-apidoc -o docs/source/ nolcat`` and ``make html`` for Sphinx
* Organize custom documentation pages on Sphinx index

Iteration 2: Display Data Uploaded at End of Initialization
===========================================================
* Add display of all data in the database to "initialization/show-loaded-data.html"
* Update ``tests.test_bp_initialization.test_upload_historical_non_COUNTER_usage()`` to check for displayed data

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

Iteration: Automatically Reharvest SUSHI
========================================
* Initiate automated reharvesting for statistics sources which take first calls as prompts to run query later and gives data on subsequent call