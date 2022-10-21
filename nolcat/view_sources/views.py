import logging
from flask import render_template

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')  #ToDo: Update to include variable route to determine if viewing resourceSources or statisticsSources
def view_sources_homepage():
    """Returns the homepage for the `view_sources` blueprint, which shows the list of resourceSources or statisticsSources records depending on the variable route value."""
    return render_template('index.html')


#ToDo: Create route to view source details
    #ToDo: Details includes all linked other sources and notes
    # Are the source types similar enough that they can use the same template?


#ToDo: Create routes to pages to
    # Add statisticsSources
    # Edit statisticsSources details
    # Add resourceSources
    # Edit resourceSources details
    #ToDo: Adding sources uses blank fields where editing resources prepopulates them and saves any changes--are the source types similar enough that they can use the same template?
    #ToDo: This includes adding to notes relations for sources
    #ToDo: Changing a statisticsSources-resourceSources connection means changing the non-PK field in statisticsResourceSources from true to false and creating a new record with the PKs of the new sources--does it makes sense to have a "if stats source changes, pick new one here" drop-down listing all stats sources but the current one on a resource source details page?