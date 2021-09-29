from flask import render_template
from flask import request
from flask import abort
import pandas as pd
from . import bp


@bp.route('/initialize-database')
def start_R4_data_load():
    """Returns the page where the CSVs with R4 data are selected."""
    return render_template('select-R4-CSVs.html')


@bp.route('/matching', methods=['GET', 'POST'])
def determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    if request.method == "POST":
        #ToDo: Consolidate the data in request.files.getlist('R4_files') into a single dataframe
        #ToDo: Return data for presenting resource matches that need to be manually confirmed
        return render_template('select-matches.html')
    else:
        return abort(404)


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')