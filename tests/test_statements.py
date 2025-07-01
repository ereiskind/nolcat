"""This module contains the tests for setting up the Flask web app, which roughly correspond to the functions in `nolcat\\app.py`. Each blueprint's own `views.py` module has a corresponding test module."""
########## Passing 2025-06-12 ##########

import pytest

# `conftest.py` fixtures are imported automatically
from nolcat.logging_config import *
from nolcat.app import *
from nolcat.models import *
from nolcat.statements import *

log = logging.getLogger(__name__)