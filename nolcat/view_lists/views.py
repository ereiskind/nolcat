import logging
from flask import render_template
from flask import request
from flask import abort
import pandas as pd

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/<string:list>')
def view_lists_homepage(list):
    """Returns the homepage for the `view_lists` blueprint, which shows the list of resource sources, statistics sources, or vendors depending on the variable route value."""
    if request.method == 'GET':
        if list == "resources":
            title = "Resource Sources"
            SQL_query = #ToDo: Write query that provides all fields in human-understandable data
        elif list == "statistics":
            title = "Statistics Sources"
            SQL_query = #ToDo: Write query that provides all fields in human-understandable data
        elif list == "vendors":
            title = "Vendors"
            SQL_query = #ToDo: Write query that provides all fields in human-understandable data
        df = pd.read_sql(
            sql=SQL_query,
            con=db.engine,
        )
        #ToDo: Add field with links to see details for each record
        #ToDo: Display the returned dataframe
            # https://stackoverflow.com/q/52644035
            # https://stackoverflow.com/q/22180993
        return render_template('view_lists/index.html', title=title)
    else:
        return abort(404)


#ToDo: Route to view all fields and notes for a given record in `resourceSources`, `statisticsSources`, or `vendors`
    #ToDo: for vendors, this includes all affiliated resource and statistics sources
    #ToDo: This includes adding notes
    


#ToDo: Route to edit all fields and notes for a given record in `resourceSources`, `statisticsSources`, or `vendors`
    #ToDo: Adding records uses blank fields where editing resources prepopulates them and saves any changes
        # https://stackoverflow.com/q/35892144
        # https://stackoverflow.com/q/23712986
        # https://stackoverflow.com/q/42984453
        # https://stackoverflow.com/q/28941504
        #ToDo: Changing a statisticsSources-resourceSources connection means changing the non-PK field in statisticsResourceSources from true to false and creating a new record with the PKs of the new sources--does it makes sense to have a "if stats source changes, pick new one here" drop-down listing all stats sources but the current one on a resource source details page?