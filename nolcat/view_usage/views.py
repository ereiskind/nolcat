import logging
from flask import render_template

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')
def homepage():
    """Returns the homepage for the `view_usage` blueprint, which links to the usage query methods."""
    return render_template('index.html')


#ToDo: Create route for page allowing writing SQL queries
    #ToDo: Input from this field's text box is run as query against database
    # return write_SQL_queries.html


#ToDo: Create route for query wizard
    # return query_wizard.html


#ToDo: Create route for saved queries
    #ToDo: Include same text boxes with fuzzy search that allow pre-screening of results that will be pulled up for resource titles and vendor names (possibly sources as well) as in query wizard
    #ToDo: Include calculating annual numbers, not not the methods--methods save to relation
    #ToDo: Decide what other canned queries to provide