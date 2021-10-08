Testing
#######

Running Tests
*************
Tests are designed to run in the root folder with the command ``python -m pytest``.

* Code contains logging statements; to view in the pytest output, add ``-s --log-cli-level="info"`` (or whatever logging level is appropriate) to the command. (The `-s` flag is for showing standard terminal output, but it also gets all columns of dataframes to display.)

Test Data
*********
All test data provided in this repository is based on the binary files in "\\tests\\bin", which are actual R4 COUNTER reports where the numbers have been changed for confidentiality and many of the resources have been removed for speed. The retained resources were selected to ensure as many edge cases as possible were accounted for.

For the purposes of the OpenRefine exports, the Statistics_Source_ID values as as follows
* EBSCO = 1
* ProQuest = 2
* Gale = 3
* iG Publishing/BEP = 4 (BR5 only)

The fixture `sample_R4_RawCOUNTERReport` creates a MultiDict of FileStorage objects, all with the key `'R4_files'`, which matches the ImmutableMultiDict of FileStorage objects created when multiple files are passed to a route in the Flask app through the HTML-derived file selector in the web app. There are a few small differences between the FileStorage objects from the two sources: in the fixture, the `filename` attribute contains the file path starting from (but not including) `nolcat` and the `stream` attribute is a TextIOWrapper; when coming from Flask, `filename` is just the name of the file and `stream` is a `tempfile.SpooledTemporaryFile` object.