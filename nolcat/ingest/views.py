import logging
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from . import bp
from ingest.forms import *

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/initialize-database')
def start_R4_data_load():
    """Returns the page where the CSVs with R4 data are selected."""
    return render_template('select-R4-CSVs.html')


@bp.route('/matching', methods=['GET', 'POST'])
def determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    form = TestForm()
    logging.info(f"\nerrors before if-else: {form.errors}\n")
    if form.validate_on_submit():  # This is when the form has been submitted
        logging.info(f"\nerrors in validate_on_submit: {form.errors}\n")
        return redirect(url_for('data_load_complete'))
    elif request.method == 'POST':  # This is when the function is receiving the data to render the form
        logging.info(f"\nerrors in method==POST: {form.errors}\n")
        return render_template('select-matches.html', form=form)
    else:
        return "404 page"


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')