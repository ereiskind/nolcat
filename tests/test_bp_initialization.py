"""Tests the routes in the `initialization` blueprint."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.initialization import *


#ToDo: Create test using Selenium to confirm that form can successfully upload all CSV files
    #ToDo: Save CSV files with mock data in `tests/bin`
    #ToDo: Use Selenium to submit those CSVs with the form on the page
    #ToDo: Compare data from form submissions to dataframes with same data as in CSVs


#ToDo:Create test confirming the uploading of the data of the requested CSVs, the creation of the `annualUsageCollectionTracking` records, and the outputting of the CSV for that relation


#ToDo: Create test confirming route uploading CSV with data for `annualUsageCollectionTracking` records


#ToDo: Create test using Selenium to upload formatter R4 reports into single RawCOUNTERReport object, then RawCOUNTERReport.perform_deduplication_matching


#ToDo: Create test for route showing data in database at end of initialization wizard