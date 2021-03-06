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
The test suite makes use of data saved in "\\tests\\bin" or in the fixtures in "tests\\conftest.py" which actually contain the same data as is found in "tests\\bin\\RawCOUNTERReport_constructor_output.xlsx." That data is actually based off of the COUNTER R4 reports in "\\tests\\bin," which are actual reports where the numbers have been changed for confidentiality and many of the resources have been removed for speed. The retained resources were selected to ensure as many edge cases as possible were accounted for.

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

  * Contains unicode characters ``??`` and ``??```
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
* ??rudit
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