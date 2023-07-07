"""Tests the methods in Vendors."""
########## No tests written 2023-06-07 ##########

import pytest
import logging

# `conftest.py` fixtures are imported automatically
from nolcat.models import Vendors

log = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def session_scope():
    log.info("This is the log.info statement in `session_scope()`")
    yield "This is the yield statement for `session_scope()`"

@pytest.fixture(scope='module')
def module_scope():
    log.info("This is the log.info statement in `module_scope()`")
    yield "This is the yield statement for `module_scope()`"

def test_outputs(conftest_print, session_scope, module_scope):
    log.info("This is the print statement in `test_outputs()`")
    log.info(conftest_print.title())
    log.info(module_scope.title())
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