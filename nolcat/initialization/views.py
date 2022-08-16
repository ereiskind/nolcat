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
def homepage():
    """Returns the page with for downloading the TSV templates for the fiscal year, vendor, resource source, and statistics source relations and uploading the initial data for those relations."""
    form_being_filled_out = InitialRelationDataForm()
    return render_template('index.html', form=form_being_filled_out)


@bp.route('/initialization-wizard-page-2', methods=['GET','POST'])
def wizard_page_2():
    """Intakes form with data for the initial relations and returns the page for downloading the TSV template for `annualUsageCollectionTracking` and the JSONs for formatting the historical R4 reports for upload and then uploading the `annualUsageCollectionTracking` relation data."""
    form_being_submitted = InitialRelationDataForm()
    form_being_filled_out = AUCTForm()
    if form_being_submitted.validate_on_submit():
        
        #Section: Ingest Data from Uploaded TSVs
        fiscalYears_dataframe = pd.read_csv(
            form_being_submitted.fiscalYears_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        fiscalYears_dataframe['Notes_on_statisticsSources_Used'] = fiscalYears_dataframe['Notes_on_statisticsSources_Used'].encode('utf-8').decode('unicode-escape')
        fiscalYears_dataframe['Notes_on_Corrections_After_Submission'] = fiscalYears_dataframe['Notes_on_Corrections_After_Submission'].encode('utf-8').decode('unicode-escape')

        vendors_dataframe = pd.read_csv(
            form_being_submitted.vendors_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        vendors_dataframe['Vendor_Name'] = vendors_dataframe['Vendor_Name'].encode('utf-8').decode('unicode-escape')
        

        vendorNotes_dataframe = pd.read_csv(
            form_being_submitted.vendorNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        vendorNotes_dataframe['Note'] = vendorNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

        statisticsSources_dataframe = pd.read_csv(
            form_being_submitted.statisticsSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        statisticsSources_dataframe['Statistics_Source_Name'] = statisticsSources_dataframe['Statistics_Source_Name'].encode('utf-8').decode('unicode-escape')

        statisticsSourceNotes_dataframe = pd.read_csv(
            form_being_submitted.statisticsSourceNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        statisticsSourceNotes_dataframe['Note'] = statisticsSourceNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

        statisticsResourceSources_dataframe = pd.read_csv(
            form_being_submitted.statisticsResourceSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )

        resourceSources_dataframe = pd.read_csv(
            form_being_submitted.resourceSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        resourceSources_dataframe['Resource_Source_Name'] = resourceSources_dataframe['Resource_Source_Name'].encode('utf-8').decode('unicode-escape')

        resourceSourceNotes_dataframe = pd.read_csv(
            form_being_submitted.resourceSourceNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        resourceSourceNotes_dataframe['Note'] = resourceSourceNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')


        #Section: Load Data into Database
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
        

        #Section: Create TSV Template for `annualUsageCollectionTracking`
        #ALERT: Due to database unavailability, code from this point forward is untested
        #ToDo: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.MultiIndex.from_product.html creates a multiindex from the cartesian product of lists--is changing fiscalYears_dataframe['Fiscal_Year_ID'] and statisticsSources_dataframe['Statistics_Source_ID'] to lists then using those lists in this method faster than a cartesian product query?
        with db.engine.connect() as connection:  # Code based on https://stackoverflow.com/a/67420458
            AUCT_records = connection.execute(text("SELECT statisticsSources.Statistics_Source_ID, fiscalYears.Fiscal_Year_ID, statisticsSources.Statistics_Source_Name, fiscalYears.Year FROM statisticsSources JOIN fiscalYears;"))
            for record in AUCT_records:
                print(repr(type(record)))
                print(record)
        
        #ToDo: Create downloadable TSV "initialize_annualUsageCollectionTracking.tsv" with results of above as first four columns and the following field names in the rest of the first row
            # Usage_Is_Being_Collected
            # Manual_Collection_Required
            # Collection_Via_Email
            # Is_COUNTER_Compliant
            # Collection_Status
            # Usage_File_Path
            # Notes
        #ToDo: Download all R4 OpenRefine JSONs
        return render_template('historical-collection-tracking.html', form=form_being_filled_out)
    else:
        #ToDo: Should an error about attempting to bypass part of wizard be used?
        return redirect(url_for('homepage'))


@bp.route('/initialization-wizard-page-3', methods=['GET','POST'])
def wizard_page_3():
    """Intakes form with the `annualUsageCollectionTracking` relation data and returns the page for uploading the reformatted COUNTER R4 reports."""
    #ToDo: Load "initialize_annualUsageCollectionTracking.csv" into titular relation
    #ToDo: Set up form for intake of R4 data
    return render_template('select-R4-CSVs.html')


@bp.route('/initialization-wizard-page-4', methods=['GET','POST'])
def wizard_page_4():
    """Intakes form with the reformatted COUNTER R4 reports and returns the page for choosing if pairs of records found by `RawCOUNTERReport.perform_deduplication_matching` refer to the same resource, and if so, what non-matching metadata should be set as the default."""
    #ToDo: historical_data = RawCOUNTERReport(uploaded files)
    #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = historical_data.perform_deduplication_matching
    #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same
    form = TestForm()
    logging.info(f"\nerrors before if-else: {form.errors}\n")
    if form.validate_on_submit():  # This is when the form has been submitted
        logging.info(f"\nerrors in validate_on_submit: {form.errors}\n")
        return redirect(url_for('wizard_page_5'))
    elif request.method == 'POST':  # This is when the function is receiving the data to render the form
        logging.info(f"\nerrors in method==POST: {form.errors}\n")
        return render_template('select-matches.html', form=form)
    else:
        return abort(404)


@bp.route('/initialization-wizard-page-5', methods=['GET','POST'])
def wizard_page_5():
    """Intakes form with confirmation of matches needing manual checking and the default metadata for the matched resources and returns the page showing the data just successfully loaded into the database."""
    return render_template('show-loaded-data.html')