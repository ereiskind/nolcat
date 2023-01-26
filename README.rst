NoLCAT
######

NoLCAT Simplification
*********************
At this time, the environment is unable to support the matching and deduplication needed for the distinct identification of all the resources included in the COUNTER reports, which enabled most of NoLCAT's more advanced features. As a result, COUNTER data from uploaded tabular R4 reports, uploaded tabular R5 reports, and R5 SUSHI calls will be loaded into a single relation without further processing. 

About This Repo
***************

The Hosting Instance
====================
NoLCAT is a containerized application: it exists within a Docker container which is built on an AWS EC2 instance. The host instance, a Linux-based t3.2xlarge, contains files with Docker build instructions and private information that cannot be committed to GitHub.

Working with the Web Server
---------------------------
NoLCAT is a web application, meaning the program is accessed through the internet and controlled through a web browser. It uses Flask as the web framework, Gunicorn as the WSGI (web service gateway interface), and nginx as the web server. Gunicorn and nginx are added to the instance as part of the Docker build process and connect to the overall codebase through the "nolcat/wsgi.py" file, which contains an instantiated Flask object.
The public IP address used to access the web app is ultimately that of the instance.

Working with MySQL
------------------
The instance can access the external MySQL database server, which serves as the RDBMS for NoLCAT. The MySQL command line can be accessed from the instance command line.

Encodings and File Types
========================
E-resources involves working with scholarly content in a wide variety of languages, requiring the use of Unicode to accommodate multiple alphabets/character sets. NoLCAT uses the UTF-8 encoding for a variety of reasons, including its ubiquity, backwards compatibility, and inclusion as a requirement of the COUNTER 5 Code of Practice. Since Microsoft Excel can explicitly save files as CSV files with an UTF-8 encoding, NoLCAT will use the CSV format for plain text file uploads and downloads.

To-Do List
**********
Last updated: 2023-01-24

TaDS Assistance Required
========================
* Perform setup to allow files to be saved to and downloaded from the container

Configure Flask-User
----------------------------
* Establish if there's going to be a single user login and a single admin login, or if everyone has their own login
* Create route/page for login page with tests

To Make NoLCAT Viable with Command Line SQL
===========================================

Test Modules
------------
* Finish pytest configuration and/or fixtures so data loaded into database during tests automatically rolls back once pytest session finishes

``nolcat.initialization`` Blueprint
-----------------------------------
* Finish writing creation of AUCT template file
* Finish writing ingest of dataframe from tabular COUNTER reports into database
* Write ``upload_historical_non_COUNTER_usage()`` route
* Write form class for non-COUNTER usage downloads
* Write "initial-data-upload-3.html" page
* Write tests for ``nolcat.initialization`` blueprint

``nolcat.modules.StatisticsSources`` Class
------------------------------------------
* Finish ``StatisticsSources.fetch_SUSHI_information()``
* Finish ``StatisticsSources._harvest_R5_SUSHI()``, including an exception for MathSciNet, which doesn't have a `/status` endpoint but does return reports
* Finish ``StatisticsSources.collect_usage_statistics()``
* Write ``StatisticsSources.add_note`` method
* Write tests for ``models.StatisticsSources``: ``fetch_SUSHI_information()`` for both API and display, ``_harvest_R5_SUSHI()``, ``collect_usage_statistics()``, ``add_note()``

``nolcat.modules.AnnualUsageCollectionTracking`` Class
------------------------------------------------------
* Finish ``AnnualUsageCollectionTracking.collect_annual_usage_statistics()``
* Write tests for ``models.AnnualUsageCollectionTracking``: ``collect_annual_usage_statistics()``

``nolcat.modules.FiscalYears`` Class
------------------------------------
* Finish ``FiscalYears.collect_fiscal_year_usage_statistics()``
* Finish ``FiscalYears.create_usage_tracking_records_for_fiscal_year()``
* Write tests for ``models.FiscalYears``: ``collect_fiscal_year_usage_statistics()``, ``FiscalYears.create_usage_tracking_records_for_fiscal_year()``

``nolcat.ingest_usage`` Blueprint
---------------------------------
* Finish ``upload_COUNTER_reports()``, ``harvest_SUSHI_statistics()``, ``upload_non_COUNTER_reports()`` routes
* Finish the ``SUSHIParametersForm()`` class
* Create "make-SUSHI-call.html", "upload-COUNTER-reports.html", and "save-non-COUNTER-usage.html" pages
* Write tests for all functions

To Complete NoLCAT
==================

``nolcat`` Modules
------------------
* Write ``__repr__`` values in ``nolcat.models``

``nolcat.models.Vendors`` Class
-------------------------------
* Finish ``Vendors.get_statisticsSources()`` method
* Finish ``Vendors.get_resourceSources()`` method
* Write ``Vendors.add_note()`` method
* Write tests for ``models.Vendors``: ``get_statisticsSources()``, ``get_resourceSources()``, ``add_note()``

``nolcat.models.ResourceSources`` Class
---------------------------------------
* Finish ``ResourceSources.change_StatisticsSource()`` method
* Write ``ResourceSources.add_access_stop_date()`` method
* Write ``ResourceSources.remove_access_stop_date()`` method
* Write ``ResourceSources.add_note()`` method
* Write tests for ``models.ResourceSources``: ``change_StatisticsSource()``, ``add_access_stop_date()``, ``remove_access_stop_date()``, ``add_note()``

``nolcat.annual_stats`` Blueprint
---------------------------------
* Determine the best method to add a record for the new fiscal year to the ``FiscalYears`` relation (ideally with automatic execution each July 1)
* Finish ``annual_stats_homepage()``, ``show_fiscal_year_details()`` routes
* Finish the blueprint's "index.html" by adjusting the links to the ``view_sources`` and ``view_vendors`` blueprints
* Finish ``RunAnnualStatsMethodsForm``, ``EditFiscalYearForm``, and ``EditAUCTForm`` field classes
* Finish "fiscal_year_details.html"
* Write tests for ``nolcat.annual_stats`` blueprint

``nolcat.view_usage`` Blueprint
-------------------------------
* Possibly add group by statements to standard view SQL queries
* Finish ``run_custom_SQL_query()`` route by figuring out how to prevent SQL injection with complete SQL statement
* Add descriptions of standard views to canned query form
* Finish ``use_predefined_SQL_query()`` route
* Finish "query_wizard.html"
* Finish tests for ``nolcat.view_usage`` blueprint