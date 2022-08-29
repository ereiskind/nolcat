"""Tests the routes in the `ingest_usage` blueprint."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.ingest_usage import *


#ToDo: Create test for route to homepage/page for choosing usage ingest type, which is static


#ToDo: Create test for route for loading R4 report into database by comparing pd.from_sql of relations where the data was loaded to dataframes used to make the initial fixtures with data from uploaded report manually added


#ToDo: Create test for route for loading R5 report into database by comparing pd.from_sql of relations where the data was loaded to dataframes used to make the initial fixtures with data from uploaded report manually added


#ToDo: Create test using Selenium to input the dates to use as arguments for StatisticsSources.collect_usage_statistics
    # https://pytest-selenium.readthedocs.io/en/latest/user_guide.html
    # https://www.lambdatest.com/blog/test-automation-using-pytest-and-selenium-webdriver/


#ToDo: Create test for route for adding non-COUNTER usage stats