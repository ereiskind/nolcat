import logging
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
from flask import current_app
from flask import send_from_directory
from werkzeug.utils import secure_filename
import xlrd
import pandas as pd

from . import bp
from ..ingest import forms
from nolcat.app import engine
from nolcat.raw_COUNTER_report import *


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#Section: Uploads and Downloads
@bp.route('/download/<path:filename>',  methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], path='.', filename=filename, as_attachment=True)


#Section: Database Initialization Wizard
#ToDo: After creating the first account with ingest permissions, come here
@bp.route('/initialize-database')
def initialize_initial_relations():
    """Returns the page with for downloading the CSV templates for the `fiscalYears`, `vendors`, and `statisticsSources` relations and uploading the initial data for those relations."""
    form_being_filled_out = forms.InitialRelationDataForm()
    return render_template('start-database-initialization.html', form=form_being_filled_out)


@bp.route('/initialize-collection-tracking', methods=["GET","POST"])
def save_historical_collection_tracking_info():
    """Returns the page for downloading the CSV template for `annualUsageCollectionTracking` and uploading the initial data for that relation as well as formatting the historical R4 reports for upload."""
    form_being_submitted = forms.InitialRelationDataForm()
    if form_being_submitted.validate_on_submit():
        fiscalYears_dataframe = pd.read_csv(form_being_submitted.fiscalYears_CSV.data)
        vendors_dataframe = pd.read_csv(form_being_submitted.vendors_CSV.data)
        statisticsSources_dataframe = pd.read_csv(form_being_submitted.statisticsSources_CSV.data)

        db_connection = engine.connect()
        fiscalYears_dataframe.to_sql(
            'fiscalYears',
            con=db_connection,
            if_exists='replace',
        )
        vendors_dataframe.to_sql(
            'vendors',
            con=db_connection,
            if_exists='replace',
        )
        statisticsSources_dataframe.to_sql(
            'statisticsSources',
            con=db_connection,
            if_exists='replace',
        )
        db_connection.close()
        
        

        #ToDo: `SELECT statisticsSources.Statistics_Source_ID, fiscalYears.Fiscal_Year_ID, statisticsSources.Statistics_Source_Name, fiscalYears.Year FROM statisticsSources JOIN fiscalYears;` (this is an intentional cartesian product)
        #ToDo: Create downloadable CSV "initialize_annualUsageCollectionTracking.csv" with results of above as first four columns and the following field names in the rest of the first row
            # Usage_Is_Being_Collected
            # Manual_Collection_Required
            # Collection_Via_Email
            # Is_COUNTER_Compliant
            # Collection_Status
            # Usage_File_Path
            # Notes
        #ToDo: Download all R4 OpenRefine JSONs
        return render_template('historical-collection-tracking.html')
    return redirect(url_for('initialize_initial_relations'))  #ToDo: Add message flashing about upload not working


@bp.route('/historical-COUNTER-data')
def upload_historical_COUNTER_usage():
    """Returns the page for uploading reformatted COUNTER R4 CSVs."""
    #ToDo: Load "initialize_annualUsageCollectionTracking.csv" into titular relation
    return render_template('select-R4-CSVs.html')


@bp.route('/matching', methods=['GET', 'POST'])
def determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    #ToDo: historical_data = RawCOUNTERReport(uploaded files)
    #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = historical_data.perform_deduplication_matching
    #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same
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


#Section: Updating Information
#Subsection: Adding Data
#ToDo: Create route to and page for adding non-COUNTER compliant usage
#ToDo: How should non-COUNTER usage be stored? As BLOB in MySQL, as files in the container, as a Docker volume, in some other manner?
#ToDo: Find all resources to which this applies with `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';`
# render_template('upload-historical-non-COUNTER-data.html')


#ToDo: Create route to and page for creating new records in `vendors`


#ToDo: Create route to and page for creating new records in `statisticsSources`


#Subsection: Updating and Displaying Data
#ToDo: Create route to and page for using methods StatisticsSources.add_access_start_date and StatisticsSources.remove_access_start_date


#ToDo: Create route to and page for `fiscalYears` from which all FiscalYears methods can be run


#ToDo: Create route to and page for `annualUsageCollectionTracking` which uses a variable route to filter just a single fiscal year and displays all the records for that fiscal year