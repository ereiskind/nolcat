"""Test using `UploadCOUNTERReports`."""

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.upload_COUNTER_reports import UploadCOUNTERReports
from data import COUNTER_reports_LFS


#Section: Fixtures
@pytest.fixture
def sample_COUNTER_reports():
    """Creates a dataframe with the data from all the COUNTER reports."""
    yield COUNTER_reports_LFS.sample_COUNTER_reports()


#Section: Tests