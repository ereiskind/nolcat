import logging

from flask_sqlalchemy import SQLAlchemy

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route for admin homepage
    # return index.html


#ToDo: Create route for details of a fiscal year
    # return fiscal_year_details.html


#ToDo: Create route for `annualUsageCollectionTracking` which uses a variable route to filter just a single fiscal year and displays all the records for that fiscal year