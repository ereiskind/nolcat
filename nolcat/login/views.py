import logging
from flask import render_template

from . import bp
#from .forms import *
from ..app import *
from ..models import *
from ..statements import *

log = logging.getLogger(__name__)


@bp.route('/')
def login_homepage():
    """Returns the homepage for the `login` blueprint."""
    # log.info("Starting `login_homepage()`.")
    #ToDo: Should this be the page for logging in (entering existing credentials) with Flask-User?
    return render_template('login/index.html')


#ToDo: If individual accounts are to be used, create route to account creation page with Flask-User