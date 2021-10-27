Testing
#######

Running Tests
*************
There are two ways to run the test suite:

Running Tests From the CLI
==========================
Test modules are designed to be run from the root folder with the command ``python -m pytest``.

* To view logging statements in the pytest output, add ``-s --log-cli-level="info"`` (or whatever logging level is appropriate) to the command. (The `-s` flag is for showing standard terminal output, but it also gets all columns of dataframes to display.)
* To run the tests in a single module, end the command with the path from the root directory (which is the present working directory) to the module.

Using the Test Container
========================
The script "run_nolcat_tests.py" clones a given branch and runs either a given test script or all test scripts at a specified level of detail. The command, which should be run in the root folder, is ``python tests/run_nolcat_tests.py branch log_level test_script`` where ``branch`` is the name of the Git branch to be cloned, ``log_level`` is the descriptor for the level of logging detail that should be used (generally "info" or "debug" when details are needed), and ``test_script`` is optionally the test script that should run; if left off, all the test scripts will run.

The container was created because NoLCAT can only be used with Python versions 3.7 or 3.8; versions below that don't support f-strings and versions above that have a problem with installing numpy, a pandas dependency (see https://github.com/numpy/numpy/issues/17569). To accommodate this narrow range of comparable versions, neither of which is available with the binary installer (aka wizard), this script creates an image with Python 3.8 for testing.

Test Data
*********
All test data provided in this repository is based on the binary files in "\\tests\\bin", which are actual R4 COUNTER reports where the numbers have been changed for confidentiality and many of the resources have been removed for speed. The retained resources were selected to ensure as many edge cases as possible were accounted for.

For the purposes of the OpenRefine exports, the Statistics_Source_ID values as as follows
* EBSCO = 1
* ProQuest = 2
* Gale = 3
* iG Publishing/BEP = 4 (BR5 only)

Using Selenium
**************
Some of the tests use Selenium, which allows for interfacing with web browsers. for more information on Selenium and setting it up, see :ref:`"Using Selenium" on the page about COUNTER and SUSHI <using-selenium>`.

The fixture `sample_R4_RawCOUNTERReport` creates a MultiDict of FileStorage objects, all with the key `'R4_files'`, which matches the ImmutableMultiDict of FileStorage objects created when multiple files are passed to a route in the Flask app through the HTML-derived file selector in the web app. There are a few small differences between the FileStorage objects from the two sources: in the fixture, the `filename` attribute contains the file path starting from (but not including) `nolcat` and the `stream` attribute is a TextIOWrapper; when coming from Flask, `filename` is just the name of the file and `stream` is a `tempfile.SpooledTemporaryFile` object.