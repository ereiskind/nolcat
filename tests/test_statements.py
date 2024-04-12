"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Passing 2024-04-12 ##########

import pytest
import logging

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *
from nolcat.statements import *

log = logging.getLogger(__name__)


def test_format_list_for_stdout_with_list():
    """Test pretty printing a list by adding a line break between each item."""
    assert format_list_for_stdout(['a', 'b', 'c']) == "a\nb\nc"


def test_format_list_for_stdout_with_generator():
    """Test pretty printing a list created by a generator object by adding a line break between each item.
    
    The `file_path` variable is created because using the `iterdir()` method on the end of that file path won't work; the method just executes on the string that should be the final component of the path. The assert statements, which look for every file that should be in the created string and then check that there are only that many items in the string, is used to compensate for `iterdir()` not outputting the files in an exact order.
    """
    file_path = TOP_NOLCAT_DIRECTORY / 'tests' / 'bin' / 'COUNTER_workbooks_for_tests'
    result = format_list_for_stdout(file_path.iterdir())
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2017.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2018.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2020.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2017.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2018.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2020.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2017.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2018.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2020.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/3_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/3_2020.xlsx" in result
    assert len(result.split('\n')) == 14