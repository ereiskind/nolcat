import logging
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
import pandas as pd
from . import bp
from ingest.forms import *
from nolcat.raw_COUNTER_report import *


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: After creating the first account with ingest permissions, come here
@bp.route('/initialize-database')
def initialize_initial_relations():
    """Returns the page where the CSVs with R4 data are selected."""
    return render_template('start-database-initialization.html')


@bp.route('/initialize-collection-tracking')
def save_historical_collection_tracking_info():
    #ToDo: Load "initialize_fiscalYears.csv" into titular relation
    #ToDo: Load "initialize_vendors.csv" into titular relation
    #ToDo: Load "initialize_statisticsSources.csv" into titular relation
    #ToDo: `SELECT statisticsSources.Statistics_Source_ID, fiscalYears.Fiscal_Year_ID, statisticsSources.Statistics_Source_Name, fiscalYears.Year FROM statisticsSources JOIN fiscalYears;` (this is an intentional cartesian product)
    #ToDo: Create downloadable CSV "initialize_annualUsageCollectionTracking.csv" with results of above as first four columns and the following field names in the rest of the first row
        # Usage_Is_Being_Collected
        # Manual_Collection_Required
        # Collection_Via_Email
        # Is_COUNTER_Compliant
        # Collection_Status
        # Usage_File_Path
        # Notes
    return render_template('historical-collection-tracking.html')


@bp.route('/historical-non-COUNTER-data')
def upload_historical_non_COUNTER_usage():
    #ToDo: Load "initialize_annualUsageCollectionTracking.csv" into titular relation
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    #ToDo: `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';`
    #ToDo: Create an iterable to pass all the records returned by the above to a form
    render_template('upload-historical-non-COUNTER-data.html')


@bp.route('/historical-COUNTER-data')
def upload_historical_COUNTER_usage():
    """Saves non-COUNTER compliant usage data files and their locations, then returns the page for uploading reformatted COUNTER R4 CSVs."""
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    #ToDo: For each file uploaded in the form
        #ToDo: Save the file in a TBD location in the container using the AUCT_Statistics_Source and AUCT_Fiscal_Year values for the file name
        #ToDo: `UPDATE annualUsageCollectionTracking SET Usage_File_Path='<file path of the file saved above>' WHERE AUCT_Statistics_Source=<the composite PK value> AND AUCT_Fiscal_Year=<the composite PK value>`
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
        return abort(404)


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')