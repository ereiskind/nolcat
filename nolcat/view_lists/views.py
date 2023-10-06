import logging
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
from flask import flash
import pandas as pd

from . import bp
from .forms import *
from ..app import *
from ..models import *

log = logging.getLogger(__name__)


@bp.route('/<string:list>')
def view_lists_homepage(list):
    """Returns the homepage for the `view_lists` blueprint, which shows the list of resource sources, statistics sources, or vendors depending on the variable route value.

        Args:
            list (str): the relation whose records are being listed
    """
    log.info(f"Starting `view_lists_homepage()` for {list}.")
    if list == "resources":
        title = "Resource Sources"
        #ToDo: SQL_query = Write query that provides all fields in human-understandable data
    elif list == "statistics":
        title = "Statistics Sources"
        #ToDo: SQL_query = Write query that provides all fields in human-understandable data
    elif list == "vendors":
        title = "Vendors"
        #ToDo: SQL_query = Write query that provides all fields in human-understandable data
    else:
        log.error(f"The route function didn't understand the argument `{list}`.")  #404
        return abort(404)
    
    #ToDo: df = query_database(
    #ToDo:     query=SQL_query,
    #ToDo:     engine=db.engine,
    #ToDo: )
    #ToDo: if isinstance(df, str):
    #ToDo:     #HomepageSQLError
    #ToDo: df = df.astype({dict setting correct dtypes})
    #ToDo: Add field with links to see details for each record
    #ToDo: Display the returned dataframe
        # https://stackoverflow.com/q/52644035
        # https://stackoverflow.com/q/22180993
    return render_template('view_lists/index.html', title=title)


@bp.route('/<string:list>/<int:PK>')
def view_list_record(list, PK):
    """Returns the details and notes about a statistics source, resource source, or vendor.

    For a given record in the `resourceSources`, `statisticsSources`, or `vendors` relations, the value of all of the relation's fields and the notes are shown. For vendor records, the currently affiliated resource sources and statistics sources are shown as well. From this page, notes can be added, but not edited or deleted.

    Args:
        list (str): the relation the record comes from
        PK (int): the primary key of the record being viewed
    """
    log.info(f"Starting `view_list_record()` for {list}.")
    #ToDo: form = Write form for adding notes
    if request.method == 'GET':
        #ToDo: df = query_database(
        #ToDo:     query=Write query returning all fields in human-understandable data and notes (and statistics and resource sources if a vendor) for the record with primary key `PK` in the relation indicated by `list`,
        #ToDo:     engine=db.engine,
        #ToDo: )
        #ToDo: df = df.astype({dict setting correct dtypes})
        return render_template('view_lists/page.html')#ToDo:, form=form)
    #ToDo: elif form.validate_on_submit():
        #ToDo: Run one of the methods below based on the list type
            # Vendors.add_note()
            # StatisticsSources.add_note()
            # ResourceSources.add_note()
        return redirect(url_for('view_lists.view_list_record', list=list, PK=PK))
    else:
        #ToDo: log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)
    


@bp.route('/edit/<string:list>/<int:PK>')
def edit_list_record(list, PK):
    """Returns a page for editing records in the `resourceSources`, `statisticsSources`, or `vendors` relations.

    Adding a record is done by creating a `PK` value that matches what's next in the auto-generated count list, adding new values to all the fields available for edit, which are then committed to the relation as a new record. Editing the `resourceSources` relation is also the method for updating the `statisticsResourceSources` junction table, which is never directly visible or directly accessed.

    Args:
        list (_type_): _description_
        PK (_type_): _description_
    """
    log.info(f"Starting `edit_list_record()` for {list}.")
    #ToDo: Write form for adding/editing record and for adding or editing notes
    if request.method == 'GET':
        #ToDo: if request came from adding new record link/PK not in relation:
            #ToDo: Show page without prefilled values
            return render_template('view_lists/page.html')#ToDo:, form=form)
        #ToDo: if `PK` is in the relation
            #ToDo: df = query_database(
            #ToDo:     query=Write query returning all fields in human-understandable data and notes (and statistics and resource sources if a vendor) for the record with primary key `PK` in the relation indicated by `list`,
            #ToDo:     engine=db.engine,
            #ToDo: )
            #ToDo: if isinstance(df, str):
            #ToDo:     flash(f"Unable to load requested page because it relied on t{df[1:].replace(' raised', ', which raised')}")
            #ToDo:     return redirect(url_for(view_lists.view_lists_homepage))
            #ToDo: df = df.astype({dict setting correct dtypes})
            #ToDo: Prepopulate the fields
                # https://stackoverflow.com/q/35892144
                # https://stackoverflow.com/q/23712986
                # https://stackoverflow.com/q/42984453
                # https://stackoverflow.com/q/28941504
        #ToDo: return render_template('view_lists/page.html', form=form)
    #ToDo: elif form.validate_on_submit():
        #ToDo: add_access_stop_date()
        #ToDo: remove_access_stop_date()
        #ToDo: change_StatisticsSource()
            #ToDo: Above has a statistics source PK as its argument--provide a drop-down of names of all statistics sources via "if stats source changes, pick new one here" drop-down listing on a resource source details page which triggers this method
        #ToDo: Use `update_database()` as necessary for any other edits
        #ToDo: return redirect(url_for('view_lists.view_list_record', list=list, PK=PK))  #ToDo: Add message flashing about successful upload
    else:
        #ToDo: log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)