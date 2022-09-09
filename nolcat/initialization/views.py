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
from .forms import InitialRelationDataForm, AUCTAndCOUNTERForm
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


@bp.route('/initialization-page-2', methods=["GET","POST"])
def collect_AUCT_and_historical_COUNTER_data():
    """This route function creates the template for the `annualUsageCollectionTracking` relation and lets the user download it, then lets the user upload the `annualUsageCollectionTracking` relation data and the reformatted historical COUNTER reports sot he former is loaded into the database and the latter is divided and deduped.

    Upon redirect, this route function renders the page showing the template for the `annualUsageCollectionTracking` relation, the JSONs for transforming COUNTER R4 reports into formats that can be ingested by NoLCAT, and the form to upload the filled-out template and transformed COUNTER reports. When the `annualUsageCollectionTracking` relation and COUNTER reports are submitted, the function saves the `annualUsageCollectionTracking` relation data by loading it into the database, saves the COUNTER data as a `RawCOUNTERReport` object in a temporary file, then redirects to the `determine_if_resources_match` route function.
    """
    #ALERT: Due to database unavailability, code from this point forward is entirely untested
    form = AUCTAndCOUNTERForm()
    
    #Section: Before Form Submission
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #Subsection: Create `annualUsageConnectionTracking` Relation Template File
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

        #Subsection: Add Cartesian Product of `fiscalYears` and `statisticsSources` to Template
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

        #ToDo: return render_template('initial-data-upload-2.html', form=form)
    
    #Section: After Form Submission
    elif form.validate_on_submit():
        #Subsection: Load `annualUsageCollectionTracking` into Database
        annualUsageCollectionTracking_dataframe = pd.read_csv(form.annualUsageCollectionTracking_TSV.data)  #ToDo: Correct to handle TSV file properly
        #ToDo: Does a Flask-SQLAlchemy engine connection object corresponding to SQLAlchemy's `engine.connect()` and pairing with `db.engine.close()`?
        annualUsageCollectionTracking_dataframe.to_sql(
            'annualUsageCollectionTracking',
            con=db.engine,
            if_exists='replace',
        )
        #ToDo: Make any other necessary additions or changes for data to be saved to the database

        #Subsection: Change Uploaded TSV Files into Single RawCOUNTERReport Object
        #ToDo: Make sure that `RawCOUNTERReport.__init__` can handle an object of whatever type `form.COUNTER_TSVs.data` is--if said type is "<class 'werkzeug.datastructures.ImmutableMultiDict'>", then completing the existing to-dos should make the constructor below good to go
        #ToDo: historical_data = RawCOUNTERReport(form.COUNTER_TSVs.data)
        #ToDo: Save `historical_data` into a temp file
        #ToDo: return redirect(url_for('determine_if_resources_match'))
    
    else:
        return abort(404)  # References the `page_not_found` function referenced in the Flask factory pattern


@bp.route('/initialization-page-3', methods=['GET', 'POST'])
def determine_if_resources_match():
    #ToDo: Write actual docstring
    """Basic description of what the function does
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function.
    """
    #ToDo: form = imported_form_class()
    try:
        #ToDo: import temp file containing `historical_data` from `collect_AUCT_and_historical_COUNTER_data`
        #ToDo: historical_data = contents of file containing `historical_data` (in other words, recreate the variable)
        #ToDo: for each radio button field in the form:
            #ToDo: form.<name of field in form class>.choices = [a list comprehension creating a list of tuples ("the value passed on if the option is selected", "the value displayed as the label attribute in the form")]
    except:
        return abort(404)  # The file to be imported above, which is created directly before the redirect to this route function, couldn't be imported if the code gets here, hence an error is raised--404 isn't the most accurate HTTP error for the situation, but it's the one with an existing page

    #Section: Before Form Submission
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = historical_data.perform_deduplication_matching()
        #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same--this probably will involve dynamic radio button choice creation above
        #ToDo: return render_template('select-matches.html', form=form)
    
    #Section: After Form Submission
    elif form.validate_on_submit():
        #ToDo: things related to saving and transforming form data
        #ToDo: return redirect(url_for('the_next_route_function'))
    
    else:
        return abort(404)  # References the `page_not_found` function referenced in the Flask factory pattern


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')
