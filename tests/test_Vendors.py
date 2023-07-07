"""Tests the methods in Vendors."""
########## No tests written 2023-06-07 ##########

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.models import Vendors

@pytest.fixture(scope='session')
def session_scope():
    print("This is the print statement in `session_scope()`")
    yield "This is the yield statement for `session_scope()`"

@pytest.fixture(scope='module')
def module_scope():
    print("This is the print statement in `module_scope()`")
    yield "This is the yield statement for `module_scope()`"

def test_outputs(conftest_print, session_scope, module_scope):
    print("This is the print statement in `test_outputs()`")
    conftest_print.title()
    session_scope.title()
    module_scope.title()
    print(conftest_print.lower())
    print(session_scope.lower())
    print(module_scope.lower())
    assert True

def test_get_statisticsSources_records():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_get_resourceSources_records():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_add_note():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass