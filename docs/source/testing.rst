Testing
#######

Running Tests
*************
There are two ways to run the test suite:

Running Tests From the CLI
==========================
Test modules are designed to be run from the root folder with the command ``python -m pytest``.

* To view logging statements in the pytest output, add ``-s --log-cli-level="info"`` (or whatever logging level is appropriate) to the command. (The `-s` flag is for showing standard terminal output, but it also gets all columns of dataframes to display.)
* To save the pytest output to stdout, add ``-p pytest_session2file --session2file=logfile_name`` to the command, where ``logfile_name`` is the name of the logfile, including the file extension and the relative path from the root folder (the folder in which the command is being run) for the desired location.

  * In stdout, the test functions are reproduced until the point of the error, at which point the error is stated; in the log files, these reproductions contain a fair number of extra characters with no discernable meaning that can be removed by replacing the regex ``\[[\d;]*m`` with no characters.

* To run the tests in a single module, end the command with the path from the root directory (which is the present working directory) to the module.

Using the Test Container
========================
The script "run_nolcat_tests.py" clones a given branch and runs either a given test script or all test scripts at a specified level of detail. The command, which should be run in the root folder, is ``python tests/run_nolcat_tests.py branch log_level test_script`` where ``branch`` is the name of the Git branch to be cloned, ``log_level`` is the descriptor for the level of logging detail that should be used (generally "info" or "debug" when details are needed), and ``test_script`` is optionally the test script that should run; if left off, all the test scripts will run.

The container was created because NoLCAT can only be used with Python versions 3.7 or 3.8; versions below that don't support f-strings and versions above that have a problem with installing numpy, a pandas dependency (see https://github.com/numpy/numpy/issues/17569). To accommodate this narrow range of comparable versions, neither of which is available with the binary installer (aka wizard), this script creates an image with Python 3.8 for testing.

Test Data
*********
Since this application is about data--its collection, storage, organization, and retrieval--many parts of the application require sample data for testing. To that end, a set of sample test data is included in this repo, along with information about how it was constructed.

Test Data Folders and Modules
=============================

"\\tests\\bin\\"
----------------
This folder contains all the Excel files, most of which are stored in one of three subfolders:

* "\\tests\\bin\\all_COUNTER_workbooks_for_tests_in_order.xlsx": This workbook contains all the records from all the workbooks in "\\tests\\bin\\COUNTER_workbooks_for_tests\\" in the order in which they would be ingested.
* "\\tests\\bin\\COUNTER_workbooks_for_tests\\": The workbooks in this folder follow the formatting and naming rules for COUNTER reports to be uploaded. Any test related to COUNTER data ingest functionality will be getting their data from this folder.
* "\\tests\\bin\\sample_COUNTER_R4_reports\\": This folder contains all the R4 COUNTER reports used for testing sorted into workbooks by report type.
* "\\tests\\bin\\sample_COUNTER_R5_reports\\": This folder contains all the R4 COUNTER reports used for testing sorted into workbooks by report type.
* "\\tests\\bin\\workbooks_to_transform_into_JSONs\\": This folder contains all the Excel workbooks transformed by "tests\\data\\create_JSON_base.json" for use as input for "tests\\create_SUSHI_JSON_from_tabular_R5.py".


"\\tests\\data\\relations.py"
-----------------------------
This module contains the functions:

* ``fiscalYears_relation()``: The dataframe of test data for the `fiscalYears` relation.
* ``vendors_relation()``: The dataframe of test data for the `vendors` relation.
* ``vendorNotes_relation()``: The dataframe of test data for the `vendorNotes` relation.
* ``statisticsSources_relation()``: The dataframe of test data for the `statisticsSources` relation.
* ``statisticsSourceNotes_relation()``: The dataframe of test data for the `statisticsSourceNotes` relation.
* ``resourceSources_relation()``: The dataframe of test data for the `resourceSources` relation.
* ``resourceSourceNotes_relation()``: The dataframe of test data for the `resourceSourceNotes` relation.
* ``statisticsResourceSources_relation()``: The dataframe of test data for the `statisticsResourceSources` relation.
* ``annualUsageCollectionTracking_relation()``: The dataframe of test data for the `annualUsageCollectionTracking` relation.
* ``COUNTERData_relation()``: The dataframe of test data for the `COUNTERData` relation.

Creating the Test Data
======================
All test data provided in this repository is based on the workbooks in "\\tests\\bin\\sample_COUNTER_R4_reports" and "\\tests\\bin\\sample_COUNTER_R5_reports", which are actual COUNTER reports where the numbers have been changed for confidentiality and many of the resources have been removed for speed. The retained resources were selected to ensure as many edge cases as possible were accounted for. Creating this test data also includes creating the JSON format for the data, both for ease in applying the changes made to the tabular data to the JSON data and because COUNTER R5 data providers have been known to provide different data in tabular and JSON COUNTER reports pulled at nearly the same time with the same date range and parameters.

In the test data, the ``statistics_source_ID`` values are as follows

* ProQuest = 0
* EBSCO = 1
* Gale = 2
* Duke UP = 3

Create Tabular COUNTER Reports
------------------------------
1. Gather COUNTER reports from a small number of statistics sources and remove most of the resources, keeping as many edge cases as possible.
2. Change all non-zero usage numbers in the COUNTER reports for confidentiality, making them safe to add to the public repo.
3. Save all the COUNTER reports in the "\\tests\\bin\\COUNTER_workbooks_for_tests\\" folder, using the workbook and worksheet naming conventions required by "\\nolcat\\upload_COUNTER_reports.py".
4. Create the workbook "\\tests\\bin\\all_COUNTER_workbooks_for_tests_in_order.xlsx" and copy all usage into its single worksheet in the order in which the reports would be pulled from the "\\tests\\bin\\COUNTER_workbooks_for_tests\\" folder, aligning the data in the appropriate fields.

Create `COUNTERData` Relation Fixture Data
------------------------------------------
1. Load the sole worksheet in "\\tests\\bin\\all_COUNTER_workbooks_for_tests_in_order.xlsx" into OpenRefine to create project "nolcat_test_data".
2. Apply "\\tests\\data\\transform_test_data.json" to the "nolcat_test_data" project.
3. Download the "nolcat_test_data" project in Excel, then use the ``df`` column for the data in "data.relations.COUNTERData()".

Create R5 SUSHI Response JSON Reports
-------------------------------------
1. For each worksheet in "\\tests\\bin\\COUNTER_workbooks_for_tests\\" with an R5 report, load the worksheet into OpenRefine to create a project with a name that ends with an underscore and the two letter code for the type of report.
2. Apply "tests\\data\\create_JSON_base.json" to each of the projects created above.
3. Download each of the above projects in Excel and save to "\\tests\\bin\\workbooks_to_transform_into_JSONs\\" and adjust any pre-1900 publication dates if necessary (in creating test data, the date "1753-01-01" in OpenRefine became "-1" when exported to Excel, which in turn became Timestamp object with the value "1899-12-29" when the worksheet was uploaded).
4. For each type of report and vendor combination with a file in "\\tests\\bin\\workbooks_to_transform_into_JSONs\\", make a SUSHI API call in the browser, copy the result into a JSON file named with the statistics source ID, an underscore, and the report name abbreviation (the test data contains only one year of R5 reports, preventing repetitions with this naming convention) in the "\\tests\\data\\COUNTER_JSONs_for_tests" folder.
5. In each newly created JSON file, anonymize the data in ``Report_Header``, change the ``Created`` value in ``Report_Header`` to ``2019-07-01T00:00:00Z``, and delete the data in ``Report_Items``.
6. Use each workbook in "\\tests\\bin\\workbooks_to_transform_into_JSONs\\" as input into "tests\\create_SUSHI_JSON_from_tabular_R5.py", then take the ``data`` section of the output JSON and copy it into the ``Report_Header`` section of the corresponding JSON in "\\tests\\data\\COUNTER_JSONs_for_tests".
7. Unescape the slashes (/) in each JSON file via find and replace (replace ``\/`` with ``/``).

Create ``ConvertJSONDictToDataframe`` Test Fixtures
---------------------------------------------------
1. For each report to be used in testing the ``ConvertJSONDictToDataframe`` class, either open the corresponding OpenRefine project modified by "tests\\data\\create_JSON_base.json" or load the Excel workbook from "\\tests\\bin\\workbooks_to_transform_into_JSONs\\" into OpenRefine.
2. Apply "tests\\data\\create_dataframe_from_JSON.jsonc" to each project, remembering there's a manual step added via comment in the file.
3. Download each project in Excel, then use the ``df`` column for the data in the dataframe constructor in the appropriate fixture in "\\tests\\test_ConvertJSONDictToDataframe.py".

SUSHI Variations
****************
Compliance to the SUSHI standard is often inexact, featuring differences people have no problem reconciling but that computers cannot match. To ensure adequate coverage of fringe cases during testing, statistics sources are listed below with the edge case situations they represent. The list is organized by statistics source to facilitate testing the ``SUSHICallAndResponse`` class; if a particular edge case needs to be tested, an appropriate statistics source can be found via search.

* ABC-CLIO Databases

  * Requiring a requestor ID and an API key

* Adam Matthew

  * ``Service_Active`` field in ``status`` call doesn't contain underscore
  * ``status`` call always has ``Alerts`` key at top level with list value that seems to always be empty
  * Errors are listed in the ``Exceptions`` key, which is nested under the ``Report_Header`` key
  * Related to above, ``SUSHICallAndResponse._handle_SUSHI_exceptions()`` isn't always called: witnessed API calls made 11 minutes apart returning the exact same data behaving differently in regards to the method call
  * No TR offered
  * ``reports`` call is successful even if credentials are bad

* Akademiai Kiado

  * No DR offered
  * No IR offered

* Alexander Street Press

  * Times out

* Allen Press/Pinnacle Hosting

* ``HTTPSConnectionPool`` error caused by urllib3 ``NewConnectionError`` (``Failed to establish a new connection: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond'``)

* Ambrose Digital Streaming Video
* American Association for the Advancement of Science (AAAS)

  * Error responses use 4XX HTTP status code
  * Errors are listed in the ``Exception`` key, which is nested under the ``Report_Header`` key

* AMS (American Meteorological Society) Journals Online

  * ``SSLCertVerificationError`` caused by hostname and certificate domain mismatch

* BioScientifica

  * Dates 2021-06 to 2022-06 have no data

* Brepols Online

  * Contains unicode characters ``ç`` and ``É```
  * Errors are under the ``Exception`` key, which is on the same level as the report keys
  * Error responses use 4XX HTTP status code

* Brill Books and Journals

  * No DR offered
  * No IR offered
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Brill Scholarly Editions
* China National Knowledge Infrastructure (CNKI)
* Cochrane
* Columbia International Affairs Online (CIAO)

  * Requiring a requestor ID and an API key
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Company of Biologists

  * Requiring a requestor ID and an API key
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* de Gruyter

  * Requires a ``platform`` parameter
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Duke University Press

  * ``status`` call always has ``Alerts`` key at top level with list value that seems to always be empty
  * Downloads a JSON
  * No DR offered
  * Contains custom report forms with report IDs starting "CR_"
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Duxiu Knowledge Search Database
* Ebook Central
* EBSCOhost
* Érudit
* Films on Demand

  * Requiring a requestor ID and an API key
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Gale Cengage Learning
* HighWire
* J-STAGE

  * Requiring only a customer ID
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* JSTOR
* Loeb Classical Library

  * Requires a ``platform`` parameter
  * No TR offered
  * No IR offered
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Lyell Collection
* MathSciNet

  * ``reports`` call is successful even if credentials are bad
  * Error responses use 4XX HTTP status code
  * ``status`` call always results in 404 HTTP status code
  * 4XX pages display in browser with formatting

* Morgan & Claypool
* OECD iLibrary

  * ``Service_Active`` field in ``status`` call is all lowercase
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* Portland Press

  * Requiring a requestor ID and an API key
  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block

* ProQuest
* Rockefeller University Press

  * Requiring a requestor ID and an API key

* Royal Society of Chemistry

  * Errors reported by returning a dict with the contents of a COUNTER "Exceptions" block contained within a list

* SAGE Journals
* SAGE/CQ Press
* Sciendo

  * Requires a ``platform`` parameter

* Taylor & Francis
* Taylor & Francis eJournals
* University of California Press

  * Requiring a requestor ID and an API key

* Web of Science

Internally Inconsistent
=======================
These vendors show internal inconsistencies in testing:

* Adam Matthew: ``status`` call always has a top-level ``Alerts`` key, but ``handle_SUSHI_exceptions`` isn't always called; calls made 11 minutes apart returning the exact same data can behave differently in regards to the method call
