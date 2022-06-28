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
The data used for testing in the fixtures in "database_seeding_fixtures.py" and "\\tests\\bin" is meant as an example of the data that will be present in the database once loaded. The COUNTER R4 reports in "\\tests\\bin" are actual reports where the numbers have been changed for confidentiality and many of the resources have been removed for speed. The retained resources were selected to ensure as many edge cases as possible were accounted for.

Using Selenium
**************
Some of the tests use Selenium, which allows for interfacing with web browsers. for more information on Selenium and setting it up, see :ref:`"Using Selenium" on the page about COUNTER and SUSHI <using-selenium>`.

The fixture `sample_R4_RawCOUNTERReport` creates a MultiDict of FileStorage objects, all with the key `'R4_files'`, which matches the ImmutableMultiDict of FileStorage objects created when multiple files are passed to a route in the Flask app through the HTML-derived file selector in the web app. There are a few small differences between the FileStorage objects from the two sources: in the fixture, the `filename` attribute contains the file path starting from (but not including) `nolcat` and the `stream` attribute is a TextIOWrapper; when coming from Flask, `filename` is just the name of the file and `stream` is a `tempfile.SpooledTemporaryFile` object.

SUSHI Variations
****************
Compliance to the SUSHI standard is often inexact, featuring differences people have no problem reconciling but that computers cannot match. To ensure adequate coverage of fringe cases during testing, common issues and some vendors that display them are listed here so that the edge cases they represent can be covered while testing the ``SUSHICallAndResponse`` class.

* Requiring a requestor ID and an API key: Columbia International Affairs Online (CIAO), Company of Biologists, Portland Press, University of California Press, Rockefeller University Press, Films on Demand, ABC-CLIO Databases
* Requiring only a customer ID: Japan Science & Technology Agency (JST)
* Downloading a JSON file: 
* Variants on the ``Service_Active`` field in ``status`` call

  * Using a lowercase string in the field: OECD iLibrary
  * Naming the field ``ServiceActive``: Adam Matthew

* ``status`` call always has a key for SUSHI errors, which has an empty value if there aren't any errors

  * ``Alerts`` key at top level with list value: Adam Matthew

* Times out: Alexander Street Press
* Has no ``status`` endpoint: MathSciNet
* ``SSLCertVerificationError`` caused by hostname and certificate domain mismatch: AMS (American Meteorological Society) Journals Online
* Requires a ``platform`` parameter: de Gruyter, Sciendo, Loeb Classical Library
* Has Unicode charaacters
* No PR report offered:
* No DR report offered: Akademiai Kiado, Brill Books and Journals
* No TR report offered: Adam Matthew, Loeb Classical Library
* No IR report offered: Akademiai Kiado, Brill Books and Journals, Loeb Classical Library

Internally Inconsistent
=======================
These vendors show internal inconsistencies in testing:
* Adam Matthew: ``status`` call always has a top-level ``Alerts`` key, but ``handle_SUSHI_exceptions`` isn't always called; calls made 11 minutes apart returning the exact same data can behave differently in regards to the method call