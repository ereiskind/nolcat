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


#ToDo: Reconfigure all routes based on the structure below
'''
form = FormClass()
if request.method == 'GET':
    #ToDo: Anything that's needed before the page the form is on renders
    return render_template('page-the-form-is-on.html', form=form)
elif form.validate_on_submit():
    #ToDo: Process data from `form`
    return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
else:
    return abort(404)
'''
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
        #Section: Ingest Data from Uploaded TSVs
        fiscalYears_dataframe = pd.read_csv(
            form.fiscalYears_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        fiscalYears_dataframe['Notes_on_statisticsSources_Used'] = fiscalYears_dataframe['Notes_on_statisticsSources_Used'].encode('utf-8').decode('unicode-escape')
        fiscalYears_dataframe['Notes_on_Corrections_After_Submission'] = fiscalYears_dataframe['Notes_on_Corrections_After_Submission'].encode('utf-8').decode('unicode-escape')

        vendors_dataframe = pd.read_csv(
            form.vendors_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        vendors_dataframe['Vendor_Name'] = vendors_dataframe['Vendor_Name'].encode('utf-8').decode('unicode-escape')

        vendorNotes_dataframe = pd.read_csv(
            form.vendorNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        vendorNotes_dataframe['Note'] = vendorNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

        statisticsSources_dataframe = pd.read_csv(
            form.statisticsSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        statisticsSources_dataframe['Statistics_Source_Name'] = statisticsSources_dataframe['Statistics_Source_Name'].encode('utf-8').decode('unicode-escape')

        statisticsSourceNotes_dataframe = pd.read_csv(
            form.statisticsSourceNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        statisticsSourceNotes_dataframe['Note'] = statisticsSourceNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

        statisticsResourceSources_dataframe = pd.read_csv(
            form.statisticsResourceSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )

        resourceSources_dataframe = pd.read_csv(
            form.resourceSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        resourceSources_dataframe['Resource_Source_Name'] = resourceSources_dataframe['Resource_Source_Name'].encode('utf-8').decode('unicode-escape')

        resourceSourceNotes_dataframe = pd.read_csv(
            form.resourceSourceNotes_TSV.data,
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
        return redirect(url_for('collect_annualUsageCollectionTracking_data'))

    return render_template('index.html', form=form)


@bp.route('/initialization-page-2', methods=["GET","POST"])
def collect_AUCT_and_historical_COUNTER_data():
    """This route function creates the template for the `annualUsageCollectionTracking` relation and lets the user download it, then lets the user upload the `annualUsageCollectionTracking` relation data and the reformatted historical COUNTER reports sot he former is loaded into the database and the latter is divided and deduped.

    Upon redirect, this route function renders the page showing the template for the `annualUsageCollectionTracking` relation, the JSONs for transforming COUNTER R4 reports into formats that can be ingested by NoLCAT, and the form to upload the filled-out template and transformed COUNTER reports. When the `annualUsageCollectionTracking` relation and COUNTER reports are submitted, the function saves the `annualUsageCollectionTracking` relation data by loading it into the database, saves the COUNTER data as a `RawCOUNTERReport` object in a temporary file, then redirects to the `determine_if_resources_match` route function.
    """
    #ALERT: Due to database unavailability, code from this point forward is entirely untested
    form = AUCTAndCOUNTERForm()
    
    #Section: Before Page Renders
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #Subsection: Create `annualUsageConnectionTracking` Relation Template File
        #ToDo: TSV_file = open('initialize_annualUsageCollectionTracking.tsv', 'w', newline='')
        #ToDo: dict_writer = csv.DictWriter(TSV_file, delimiter="\t", [
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
                print(repr(type(record)))
                print(record)
                #ToDo: Determine how to break up instance of `record` to get the individual fields returned
                #ToDo: dict_writer.writerow({
                    #ToDo: "AUCT_statistics_source": statisticsSources.statistics_source_ID,
                    #ToDo: "AUCT_fiscal_year": fiscalYears.fiscal_year_ID,
                    #ToDo: "Statistics Source": statisticsSources.statistics_source_name,
                    #ToDo: "Fiscal Year": fiscalYears.fiscal_year,
                #ToDo: })
                continue  # To close the block at runtime
        #ToDo: TSV_file.close()
        return render_template('initial-data-upload-2.html', form=form)
    
    #Section: After Form Submission
    elif form.validate_on_submit():
        #Subsection: Load `annualUsageCollectionTracking` into Database
        annualUsageCollectionTracking_dataframe = pd.read_csv(
            form.annualUsageCollectionTracking_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        annualUsageCollectionTracking_dataframe['Notes'] = annualUsageCollectionTracking_dataframe['Notes'].encode('utf-8').decode('unicode-escape')
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

    #Section: Before Page Renders
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #ToDo: import temp file containing `historical_data` from `collect_AUCT_and_historical_COUNTER_data`
        #ToDo: historical_data = contents of file containing `historical_data` (in other words, recreate the variable)
        #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = historical_data.perform_deduplication_matching()
        #ToDo: for metadata_pair in dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata.keys():  #ToDo: May need to change depending on connections via network library
            #ToDo: form.<name of field in form class>.choices = [a list comprehension creating a list of tuples ("the value passed on if the option is selected", "the value displayed as the label attribute in the form")] where the display value comes from `metadata_pair`
        #ToDo: return render_template('select-matches.html', form=form)
        pass
    
    #Section: After Form Submission
    elif form.validate_on_submit():
        #ToDo: things related to saving and transforming form data
        #ToDo: return redirect(url_for('the_next_route_function'))
        pass
    
    else:
        return abort(404)  # The file to be imported above, which is created directly before the redirect to this route function, couldn't be imported if the code gets here, hence an error is raised--404 isn't the most accurate HTTP error for the situation, but it's the one with an existing page


#ToDo: Create a route and page for picking default metadata values


#ToDo: @bp.route('/historical-non-COUNTER-data')
#ToDo: def upload_historical_non_COUNTER_usage():
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    #ToDo: form = FileUploadForNon-COUNTERResources()
    #ToDo: if request.method == 'GET':
        #ToDo: `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';` to get all non-COUNTER stats source/date combos
        #ToDo: Create an iterable to pass all the records returned by the above to a form
        #ToDo: For each item in the above iterable, use `form` to provide the opportunity for a file upload
        #ToDo: return render_template('page-the-form-is-on.html', form=form)
    #ToDo: elif form.validate_on_submit():
        #ToDo: For each file uploaded in the form
            #ToDo: Save the file in a TBD location in the container using the AUCT_Statistics_Source and AUCT_Fiscal_Year values for the file name
            #ToDo: `UPDATE annualUsageCollectionTracking SET Usage_File_Path='<file path of the file saved above>' WHERE AUCT_Statistics_Source=<the composite PK value> AND AUCT_Fiscal_Year=<the composite PK value>`
        #ToDo: return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
    #ToDo: else:
        #ToDo: return abort(404)


@bp.route('/database-creation-complete', methods=['GET','POST'])
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    #ToDo: Write actual docstring
    """Basic description of what the function does
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function.
    """
    return render_template('show-loaded-data.html')