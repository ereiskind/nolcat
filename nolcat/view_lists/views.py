import logging
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
import pandas as pd

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/<string:list>')
def view_lists_homepage(list):
    """Returns the homepage for the `view_lists` blueprint, which shows the list of resource sources, statistics sources, or vendors depending on the variable route value.

        Args:
            list (str): the relation whose records are being listed
    """
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


@bp.route('/<string:list>/<int:PK>')
def view_list_record(list, PK):
    """Returns the details and notes about a statistics source, resource source, or vendor.

    For a given record in the `resourceSources`, `statisticsSources`, or `vendors` relations, the value of all of the relation's fields and the notes are shown. For vendor records, the currently affiliated resource sources and statistics sources are shown as well. From this page, notes can be added, but not edited or deleted.

    Args:
        list (str): the relation the record comes from
        PK (int): the primary key of the record being viewed
    """
    form = #ToDo: Write form for adding notes
    if request.method == 'GET':
        SQL_query = #toDo: Write query returning all fields in human-understandable data and notes (and statistics and resource sources if a vendor) for the record with primary key `PK` in the relation indicated by `list`
        df = pd.read_sql(
            sql=SQL_query,
            con=db.engine,
        )
        #ToDo: Display the returned data
        return render_template('view_lists/page.html', form=form)
    elif form.validate_on_submit():
        #ToDo: Add the form data to the relevant notes relation
        return redirect(url_for('view_list_record', list=list, PK=PK))  #ToDo: Add message flashing about successful upload
    else:
        return abort(404)
    


#ToDo: Route to edit all fields and notes for a given record in `resourceSources`, `statisticsSources`, or `vendors`
    #ToDo: Adding records uses blank fields where editing resources prepopulates them and saves any changes
        # https://stackoverflow.com/q/35892144
        # https://stackoverflow.com/q/23712986
        # https://stackoverflow.com/q/42984453
        # https://stackoverflow.com/q/28941504
        #ToDo: Changing a statisticsSources-resourceSources connection means changing the non-PK field in statisticsResourceSources from true to false and creating a new record with the PKs of the new sources--does it makes sense to have a "if stats source changes, pick new one here" drop-down listing all stats sources but the current one on a resource source details page?