from flask import render_template
from . import bp


@bp.route('/initialize-database')
def start_R4_data_load():
    """Returns the page where the CSVs with R4 data are selected."""
    return render_template('select-R4-CSVs.html')


@bp.route('/matching')
def determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    return render_template('select-matches.html')


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')