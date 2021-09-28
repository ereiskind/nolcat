Testing
#######

Running Tests
*************
Tests are designed to run in the root folder with the command ``python -m pytest``.

* Code contains logging statements; to view in the pytest output, add ``--log-cli-level="info"`` (or whatever logging level is appropriate) to the command.

Test Data
*********
The test data provided in this repository uses excerpts from actual COUNTER reports where the usage numbers have been falsified. A few minor changes were made to some resources to ensure as many edge cases as possible were accounted for, but the vast majority of the resource metadata comes directly from COUNTER reports.