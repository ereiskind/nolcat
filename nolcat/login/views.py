import logging

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route for login page with Flask-User
#ToDo: returns login_page.html


#ToDo: If individual accounts are to be used, create route to account creation page with Flask-User