import logging
from flask import render_template

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')
def login_homepage():
    """Returns the homepage for the `login` blueprint."""
    #ToDo: Should this be the page for logging in (entering existing credentials) with Flask-User?
    return render_template('login/index.html')


#ToDo: If individual accounts are to be used, create route to account creation page with Flask-User