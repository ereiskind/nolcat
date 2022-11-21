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
@bp.route('/', methods=["GET","POST"])
def collect_initial_relation_data():
    """This route function ingests the files containing data going into the initial relations, then loads that data into the database.
    
    The route function renders the page showing the templates for the `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `statisticsResourceSources`, `resourceSources`, and `resourceSourceNotes` relations as well as the form for submitting the completed templates. When the TSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_AUCT_and_historical_COUNTER_data()` route function.
    """
    form = InitialRelationDataForm()
    if request.method == 'GET':
        return render_template('initialization/index.html', form=form)
    elif form.validate_on_submit():
        #Section: Ingest Data from Uploaded TSVs
        #ToDo: `.encode('utf-8').decode('unicode-escape')` statements cause HTTP 500 error in Flask--figure out another way to ensure Unicode characters are properly encoded
        fiscalYears_dataframe = pd.read_csv(
            form.fiscalYears_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #fiscalYears_dataframe['Notes_on_statisticsSources_Used'] = fiscalYears_dataframe['Notes_on_statisticsSources_Used'].encode('utf-8').decode('unicode-escape')
        #fiscalYears_dataframe['Notes_on_Corrections_After_Submission'] = fiscalYears_dataframe['Notes_on_Corrections_After_Submission'].encode('utf-8').decode('unicode-escape')

        vendors_dataframe = pd.read_csv(
            form.vendors_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #vendors_dataframe['Vendor_Name'] = vendors_dataframe['Vendor_Name'].encode('utf-8').decode('unicode-escape')

        vendorNotes_dataframe = pd.read_csv(
            form.vendorNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #vendorNotes_dataframe['Note'] = vendorNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

        statisticsSources_dataframe = pd.read_csv(
            form.statisticsSources_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #statisticsSources_dataframe['Statistics_Source_Name'] = statisticsSources_dataframe['Statistics_Source_Name'].encode('utf-8').decode('unicode-escape')

        statisticsSourceNotes_dataframe = pd.read_csv(
            form.statisticsSourceNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #statisticsSourceNotes_dataframe['Note'] = statisticsSourceNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

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
        #resourceSources_dataframe['Resource_Source_Name'] = resourceSources_dataframe['Resource_Source_Name'].encode('utf-8').decode('unicode-escape')

        resourceSourceNotes_dataframe = pd.read_csv(
            form.resourceSourceNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #resourceSourceNotes_dataframe['Note'] = resourceSourceNotes_dataframe['Note'].encode('utf-8').decode('unicode-escape')

        #Section: Load Data into Database
        
        return redirect(url_for('collect_AUCT_and_historical_COUNTER_data'))
    else:
        return abort(404)


@bp.route('/initialization-page-2', methods=["GET","POST"])
def collect_AUCT_and_historical_COUNTER_data():
    """This route function creates the template for the `annualUsageCollectionTracking` relation and lets the user download it, then lets the user upload the `annualUsageCollectionTracking` relation data and the reformatted historical COUNTER reports sot he former is loaded into the database and the latter is divided and deduped.

    Upon redirect, this route function renders the page showing the template for the `annualUsageCollectionTracking` relation, the JSONs for transforming COUNTER R4 reports into formats that can be ingested by NoLCAT, and the form to upload the filled-out template and transformed COUNTER reports. When the `annualUsageCollectionTracking` relation and COUNTER reports are submitted, the function saves the `annualUsageCollectionTracking` relation data by loading it into the database, saves the COUNTER data as a `RawCOUNTERReport` object in a temporary file, then redirects to the `determine_if_resources_match` route function.
    """
    form = AUCTAndCOUNTERForm()
    
    #Section: Before Page Renders
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #ToDo: #Subsection: Create `annualUsageConnectionTracking` Relation Template File
        #ToDo: #Subsection: Add Cartesian Product of `fiscalYears` and `statisticsSources` to Template
        #ToDo: return render_template('initialization/initial-data-upload-2.html', form=form)
        return "initialization page 2"

    #Section: After Form Submission
    elif form.validate_on_submit():
        #ToDo: #Subsection: Load `annualUsageCollectionTracking` into Database
        #ToDo: #Subsection: Change Uploaded TSV Files into Single RawCOUNTERReport Object
        #ToDo: return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
        return "initialization page 2 after form submission"

    else:
        return abort(404)


@bp.route('/initialization-page-3', methods=['GET', 'POST'])
def determine_if_resources_match():
    #ToDo: Write actual docstring
    """Basic description of what the function does
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function.
    """
    '''
    form = FormClass()
    if request.method == 'GET':
        #ToDo: Anything that's needed before the page the form is on renders
        return render_template('blueprint_name/page-the-form-is-on.html', form=form)
    elif form.validate_on_submit():
        #ToDo: Process data from `form`
        return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
    else:
        return abort(404)
    '''
    pass


#ToDo: Create a route and page for picking default metadata values


#ToDo: @bp.route('/historical-non-COUNTER-data')
#ToDo: def upload_historical_non_COUNTER_usage():
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    '''
    form = FormClass()
    if request.method == 'GET':
        #ToDo: Anything that's needed before the page the form is on renders
        return render_template('blueprint_name/page-the-form-is-on.html', form=form)
    elif form.validate_on_submit():
        #ToDo: Process data from `form`
        return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
    else:
        return abort(404)
    '''


@bp.route('/database-creation-complete', methods=['GET','POST'])
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    #ToDo: Write actual docstring
    """Basic description of what the function does
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function.
    """
    '''
    form = FormClass()
    if request.method == 'GET':
        #ToDo: Anything that's needed before the page the form is on renders
        return render_template('blueprint_name/page-the-form-is-on.html', form=form)
    elif form.validate_on_submit():
        #ToDo: Process data from `form`
        return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
    else:
        return abort(404)
    '''
    pass