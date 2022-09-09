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
from sqlalchemy.sql import text
import csv

from . import bp
from ..app import db
from .forms import InitialRelationDataForm, AUCTForm
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#Section: Uploads and Downloads
@bp.route('/download/<path:filename>',  methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], path='.', filename=filename, as_attachment=True)


#Section: Database Initialization Wizard
#ToDo: After creating the first account with ingest permissions, come here
@bp.route('/')
def collect_initial_relation_data():
    """This route function ingests the files containing data going into the initial relations, then loads that data into the database.
    
    The route function renders the page showing the templates for the `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `statisticsResourceSources`, `resourceSources`, and `resourceSourceNotes` relations as well as the form for submitting the completed templates. When the TSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_annualUsageCollectionTracking_data` route function.
    """
    #ALERT: Refactored form hasn't been tested
    form = InitialRelationDataForm()
    if form.validate_on_submit():
        fiscalYears_dataframe = pd.read_csv(form.fiscalYears_CSV.data)
        vendors_dataframe = pd.read_csv(form.vendors_CSV.data)
        vendorNotes_dataframe = pd.read_csv(form.vendorNotes_CSV.data)
        statisticsSources_dataframe = pd.read_csv(form.statisticsSources_CSV.data)
        statisticsSourceNotes_dataframe = pd.read_csv(form.statisticsSourceNotes_CSV.data)
        statisticsResourceSources_dataframe = pd.read_csv(form.statisticsResourceSources_CSV.data)
        resourceSources_dataframe = pd.read_csv(form.resourceSources_CSV.data)
        resourceSourceNotes_dataframe = pd.read_csv(form.resourceSourceNotes_CSV.data)

        #ToDo: Does a Flask-SQLAlchemy engine connection object corresponding to SQLAlchemy's `engine.connect()` and pairing with `db.engine.close()`?
        fiscalYears_dataframe.to_sql(
            'fiscalYears',
            con=db.engine,
            if_exists='replace',
        )
        vendors_dataframe.to_sql(
            'vendors',
            con=db.engine,
            if_exists='replace',
        )
        vendorNotes_dataframe.to_sql(
            'vendorNotes',
            con=db.engine,
            if_exists='replace',
        )
        statisticsSources_dataframe.to_sql(
            'statisticsSources',
            con=db.engine,
            if_exists='replace',
        )
        statisticsSourceNotes_dataframe.to_sql(
            'statisticsSourceNotes',
            con=db.engine,
            if_exists='replace',
        )
        statisticsResourceSources_dataframe.to_sql(
            'statisticsResourceSources',
            con=db.engine,
            if_exists='replace',
        )
        resourceSources_dataframe.to_sql(
            'resourceSources',
            con=db.engine,
            if_exists='replace',
        )
        resourceSourceNotes_dataframe.to_sql(
            'resourceSourceNotes',
            con=db.engine,
            if_exists='replace',
        )
        db.engine.close()  #ToDo: Confirm that this is appropriate and/or necessary
        return redirect(url_for('collect_annualUsageCollectionTracking_data'))

    return render_template('index.html', form=form)


@bp.route('/placeholder', methods=["GET","POST"])
def collect_annualUsageCollectionTracking_data():  #ToDo: Handling data for `annualUsageCollectionTracking` relation
    """Basic description of what the function does
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function."""
    pass


@bp.route('/initialize-collection-tracking', methods=["GET","POST"])
def save_historical_collection_tracking_info():
    """Returns the page for downloading the CSV template for `annualUsageCollectionTracking` and uploading the initial data for that relation as well as formatting the historical R4 reports for upload."""
    form_being_submitted = InitialRelationDataForm()
    if form_being_submitted.validate_on_submit():

        #ALERT: Due to database unavailability, code from this point forward is untested
        #ToDo: CSV_file = open('initialize_annualUsageCollectionTracking.csv', 'w', newline='')
        #ToDo: dict_writer = csv.DictWriter(CSV_file, [
            #ToDo: "AUCT_statistics_source",
            #ToDo: "AUCT_fiscal_year",
            #ToDo: "Statistics Source",
            #ToDo: "Fiscal Year",
            #ToDo: "usage_is_being_collected",
            #ToDo: "manual_collection_required",
            #ToDo: "collection_via_email",
            #ToDo: "is_COUNTER_compliant",
            #ToDo: "collection_status",
            #ToDo: "usage_file_path",
            #ToDo: "notes",
        #ToDo: ])
        #ToDo: dict_writer.writeheader()

        with db.engine.connect() as connection:  # Code based on https://stackoverflow.com/a/67420458
            #ToDo: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.MultiIndex.from_product.html creates a multiindex from the cartesian product of lists--is changing fiscalYears_dataframe['Fiscal_Year_ID'] and statisticsSources_dataframe['Statistics_Source_ID'] to lists then using those lists in this method faster than a cartesian product query?
            AUCT_records = connection.execute(text("SELECT statisticsSources.statistics_source_ID, fiscalYears.fiscal_year_ID, statisticsSources.statistics_source_name, fiscalYears.fiscal_year FROM statisticsSources JOIN fiscalYears;"))
            for record in AUCT_records:
                #ToDo: Determine how to break up instance of `record` to get the individual fields returned
                #ToDo: dict_writer.writerow({
                    #ToDo: "AUCT_statistics_source": statisticsSources.statistics_source_ID,
                    #ToDo: "AUCT_fiscal_year": fiscalYears.fiscal_year_ID,
                    #ToDo: "Statistics Source": statisticsSources.statistics_source_name,
                    #ToDo: "Fiscal Year": fiscalYears.fiscal_year,
                #ToDo: })
                continue  # To close the block at runtime
        #ToDo: CSV_file.close()
        #ToDo: return render_template('historical-collection-tracking.html')

    #ToDo: return render_template(page to go to when reaching this route through means other than submitting form of CSVs with basic data for database)


@bp.route('/historical-COUNTER-data')
def upload_historical_COUNTER_usage():  #ToDo: Transform and upload COUNTER R4 reports
    """Returns the page for uploading reformatted COUNTER R4 CSVs."""
    #ToDo: Load "initialize_annualUsageCollectionTracking.csv" into titular relation
    return render_template('select-R4-CSVs.html')


@bp.route('/matching', methods=['GET', 'POST'])
def determine_if_resources_match():  #ToDo: Verify dedupe matches and choose default metadata values
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    #ToDo: historical_data = RawCOUNTERReport(uploaded files)
    #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = historical_data.perform_deduplication_matching
    #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same
    return render_template('select-matches.html')


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')
