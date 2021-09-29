Testing
#######

Running Tests
*************
Tests are designed to run in the root folder with the command ``python -m pytest``.

* Code contains logging statements; to view in the pytest output, add ``-s --log-cli-level="info"`` (or whatever logging level is appropriate) to the command. (The `-s` flag is for showing standard terminal output, but it also gets all columns of dataframes to display.)

Test Data
*********
The test data provided in this repository uses excerpts from actual COUNTER reports where the usage numbers have been falsified. A few minor changes were made to some resources to ensure as many edge cases as possible were accounted for, but the vast majority of the resource metadata comes directly from COUNTER reports.