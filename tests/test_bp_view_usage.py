"""Tests the routes in the `view_usage` blueprint."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.app import create_app
from nolcat.view_usage import *


#ToDo: Create test for route to homepage, which is static


#ToDo: Create test using Selenium for entering SQL into SQL query text box in form on SQL page and having the query run


#ToDo: Create tests for some of the saved queries, using Selenium to choose specific options and comparing the returned value to what's known as the returned value in the database


#ToDo: Create test for the query wizard, confirming that Selenium selecting specific options sends a given SQL string to the database


#ToDo: Create a test for the query wizard, making specific selections with Selenium and comparing the returned value to what's known as the returned value in the database