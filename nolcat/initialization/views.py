import logging
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
from flask import current_app
from flask import send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
from sqlalchemy.sql import text
from sqlalchemy import exc

from . import bp
from ..app import db, date_parser
from .forms import InitialRelationDataForm, AUCTAndCOUNTERForm
from ..upload_COUNTER_reports import UploadCOUNTERReports
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#Section: Uploads and Downloads
@bp.route('/download/<path:filename>',  methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], path='.', filename=filename, as_attachment=True)


#Section: Database Initialization Wizard
#ToDo: After creating the first account with ingest permissions, come here
@bp.route('/', methods=['GET', 'POST'])
def collect_initial_relation_data():
    """This route function ingests the files containing data going into the initial relations, then loads that data into the database.
    
    The route function renders the page showing the templates for the `fiscalYears`, `vendors`, `vendorNotes`, `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations as well as the form for submitting the completed templates. When the TSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_AUCT_and_historical_COUNTER_data()` route function.
    """
    form = InitialRelationDataForm()
    if request.method == 'GET':
        return render_template('initialization/index.html', form=form)
    elif form.validate_on_submit():
        #Section: Ingest Data from Uploaded TSVs
        #ToDo: Should a subsection for truncating all relations go here? Since the data being loaded includes primary keys, the relations seem to need explicit truncating before the data will successfully load.
        # For relations containing a record index (primary key) column when loaded, the primary key field name must be identified using the `index_col` keyword argument, otherwise pandas will create an `index` field for an auto-generated record index; this extra field will prevent the dataframe from being loaded into the database.
        #ToDo: The "Unicode Text" file format that preserves non-Latin script letter characters raises the errors `ValueError: Missing column provided to 'parse_dates': 'use_stop_date'` or `ValueError: Index resource_source_ID invalid` for no discernable reason with both the ".txt" and ".tsv" file extensions; a file saved as a standard text file with its extension changed from ".txt" to ".tsv" doesn't raise any errors, but all characters from scripts other than Latin become question marks. How can a file that saves the full scope of Unicode characters also be read into a dataframe?
        # TSV files containing data may be read in as completely null for no discernable reason; copying the data, pasting it into a new file, and saving the file according to the established instructions will fix the problem. Each `read_csv` method is followed by a check to confirm that the dataframe does contain data and instructions on how to perform the fix if it doesn't. 
        #ALERT: An error in the encoding statement can cause the logging statement directly above it to not appear in the output
        #Subsection: Upload `fiscalYears` TSV File
        logging.debug(f"`fiscalYears` data:\n{form.fiscalYears_TSV.data}\n")
        fiscalYears_dataframe = pd.read_csv(
            form.fiscalYears_TSV.data,
            sep='\t',
            index_col='fiscal_year_ID',
            parse_dates=['start_date', 'end_date'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if fiscalYears_dataframe.isnull().all(axis=None) == True:
            logging.error("The `fiscalYears` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`fiscalYears`")
        
        fiscalYears_dataframe['fiscal_year'] = fiscalYears_dataframe['fiscal_year'].astype("string")
        fiscalYears_dataframe['notes_on_statisticsSources_used'] = fiscalYears_dataframe['notes_on_statisticsSources_used'].astype("string")
        fiscalYears_dataframe['notes_on_corrections_after_submission'] = fiscalYears_dataframe['notes_on_corrections_after_submission'].astype("string")
        logging.info(f"`fiscalYears` dataframe dtypes before encoding conversions:\n{fiscalYears_dataframe.dtypes}\n")
        fiscalYears_dataframe['notes_on_statisticsSources_used'] = fiscalYears_dataframe['notes_on_statisticsSources_used'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        fiscalYears_dataframe['notes_on_corrections_after_submission'] = fiscalYears_dataframe['notes_on_corrections_after_submission'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`fiscalYears` dataframe:\n{fiscalYears_dataframe}\n")

        #Subsection: Upload `vendors` TSV File
        logging.debug(f"`vendors` data:\n{form.vendors_TSV.data}\n")
        vendors_dataframe = pd.read_csv(
            form.vendors_TSV.data,
            sep='\t',
            index_col='vendor_ID',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if vendors_dataframe.isnull().all(axis=None) == True:
            logging.error("The `vendors` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`vendors`")
        
        vendors_dataframe['vendor_name'] = vendors_dataframe['vendor_name'].astype("string")
        vendors_dataframe['alma_vendor_code'] = vendors_dataframe['alma_vendor_code'].astype("string")
        logging.info(f"`vendors` dataframe dtypes before encoding conversions:\n{vendors_dataframe.dtypes}\n")
        vendors_dataframe['vendor_name'] = vendors_dataframe['vendor_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`vendors` dataframe:\n{vendors_dataframe}\n")

        #Subsection: Upload `vendorNotes` TSV File
        logging.debug(f"`vendorNotes` data:\n{form.vendorNotes_TSV.data}\n")
        vendorNotes_dataframe = pd.read_csv(
            form.vendorNotes_TSV.data,
            sep='\t',
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if vendorNotes_dataframe.isnull().all(axis=None) == True:
            logging.error("The `vendorNotes` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`vendorNotes`")
        
        vendorNotes_dataframe['note'] = vendorNotes_dataframe['note'].astype("string")
        vendorNotes_dataframe['written_by'] = vendorNotes_dataframe['written_by'].astype("string")
        logging.info(f"`vendorNotes` dataframe dtypes before encoding conversions:\n{vendorNotes_dataframe.dtypes}\n")
        vendorNotes_dataframe['note'] = vendorNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`vendorNotes` dataframe:\n{vendorNotes_dataframe}\n")

        #Subsection: Upload `statisticsSources` TSV File
        logging.debug(f"`statisticsSources` data:\n{form.statisticsSources_TSV.data}\n")
        statisticsSources_dataframe = pd.read_csv(
            form.statisticsSources_TSV.data,
            sep='\t',
            index_col='statistics_source_ID',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if statisticsSources_dataframe.isnull().all(axis=None) == True:
            logging.error("The `statisticsSources` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`statisticsSources`")
        
        statisticsSources_dataframe['statistics_source_name'] = statisticsSources_dataframe['statistics_source_name'].astype("string")
        statisticsSources_dataframe['statistics_source_retrieval_code'] = statisticsSources_dataframe['statistics_source_retrieval_code'].astype("string")
        logging.info(f"`statisticsSources` dataframe dtypes before encoding conversions:\n{statisticsSources_dataframe.dtypes}\n")
        statisticsSources_dataframe['statistics_source_name'] = statisticsSources_dataframe['statistics_source_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`statisticsSources` dataframe:\n{statisticsSources_dataframe}\n")

        #Subsection: Upload `statisticsSourceNotes` TSV File
        logging.debug(f"`statisticsSourceNotes` data:\n{form.statisticsSourceNotes_TSV.data}\n")
        statisticsSourceNotes_dataframe = pd.read_csv(
            form.statisticsSourceNotes_TSV.data,
            sep='\t',
            encoding='utf-8',
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding_errors='backslashreplace',
        )
        if statisticsSourceNotes_dataframe.isnull().all(axis=None) == True:
            logging.error("The `statisticsSourceNotes` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`statisticsSourceNotes`")
        
        statisticsSourceNotes_dataframe['note'] = statisticsSourceNotes_dataframe['note'].astype("string")
        statisticsSourceNotes_dataframe['written_by'] = statisticsSourceNotes_dataframe['written_by'].astype("string")
        logging.info(f"`statisticsSourceNotes` dataframe dtypes before encoding conversions:\n{statisticsSourceNotes_dataframe.dtypes}\n")
        statisticsSourceNotes_dataframe['note'] = statisticsSourceNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`statisticsSourceNotes` dataframe:\n{statisticsSourceNotes_dataframe}\n")

        #Subsection: Upload `resourceSources` TSV File
        logging.debug(f"`resourceSources` data:\n{form.resourceSources_TSV.data}\n")
        resourceSources_dataframe = pd.read_csv(
            form.resourceSources_TSV.data,
            sep='\t',
            index_col='resource_source_ID',
            parse_dates=['use_stop_date'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if resourceSources_dataframe.isnull().all(axis=None) == True:
            logging.error("The `resourceSources` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`resourceSources`")
        
        resourceSources_dataframe['resource_source_name'] = resourceSources_dataframe['resource_source_name'].astype("string")
        logging.info(f"`resourceSources` dataframe dtypes before encoding conversions:\n{resourceSources_dataframe.dtypes}\n")
        resourceSources_dataframe['resource_source_name'] = resourceSources_dataframe['resource_source_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`resourceSources` dataframe:\n{resourceSources_dataframe}\n")

        #Subsection: Upload `resourceSourceNotes` TSV File
        logging.debug(f"`resourceSourceNotes` data:\n{form.resourceSourceNotes_TSV.data}\n")
        resourceSourceNotes_dataframe = pd.read_csv(
            form.resourceSourceNotes_TSV.data,
            sep='\t',
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if resourceSourceNotes_dataframe.isnull().all(axis=None) == True:
            logging.error("The `resourceSourceNotes` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`resourceSourceNotes`")
        
        resourceSourceNotes_dataframe['note'] = resourceSourceNotes_dataframe['note'].astype("string")
        resourceSourceNotes_dataframe['written_by'] = resourceSourceNotes_dataframe['written_by'].astype("string")
        logging.info(f"`resourceSourceNotes` dataframe dtypes before encoding conversions:\n{resourceSourceNotes_dataframe.dtypes}\n")
        resourceSourceNotes_dataframe['note'] = resourceSourceNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`resourceSourceNotes` dataframe:\n{resourceSourceNotes_dataframe}\n")

        #Subsection: Upload `statisticsResourceSources` TSV File
        logging.debug(f"`statisticsResourceSources` data:\n{form.statisticsResourceSources_TSV.data}\n")
        statisticsResourceSources_dataframe = pd.read_csv(
            form.statisticsResourceSources_TSV.data,
            sep='\t',
            index_col=['SRS_statistics_source', 'SRS_resource_source'],
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if statisticsResourceSources_dataframe.isnull().all(axis=None) == True:
            logging.error("The `statisticsResourceSources` relation data file was read in with no data.")
            return render_template('initialization/empty_dataframes_warning.html', relation="`statisticsResourceSources`")
        
        # Because there aren't any string dtypes in need of encoding correction, the logging statements for the dtypes and the dataframe have been combined
        logging.info(f"`statisticsResourceSources` dtypes and dataframe:\n{statisticsResourceSources_dataframe.dtypes}\n{statisticsResourceSources_dataframe}\n")


        #Section: Load Data into Database
        try:
            fiscalYears_dataframe.to_sql(
                'fiscalYears',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `fiscalYears` loaded into the database")
            vendors_dataframe.to_sql(
                'vendors',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `vendors` loaded into the database")
            vendorNotes_dataframe.to_sql(
                'vendorNotes',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `vendorNotes` loaded into the database")
            statisticsSources_dataframe.to_sql(
                'statisticsSources',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `statisticsSources` loaded into the database")
            statisticsSourceNotes_dataframe.to_sql(
                'statisticsSourceNotes',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `statisticsSourceNotes` loaded into the database")
            resourceSources_dataframe.to_sql(
                'resourceSources',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `resourceSources` loaded into the database")
            resourceSourceNotes_dataframe.to_sql(
                'resourceSourceNotes',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `resourceSourceNotes` loaded into the database")
            statisticsResourceSources_dataframe.to_sql(
                'statisticsResourceSources',
                con=db.engine,
                if_exists='append',
            )
            logging.debug("Relation `statisticsResourceSources` loaded into the database")
            logging.info("All relations loaded into the database")
            #ToDo: return redirect(url_for('collect_AUCT_and_historical_COUNTER_data'))
            return "placeholder for `return redirect(url_for('collect_AUCT_and_historical_COUNTER_data'))`"
        except exc.IntegrityError as error:
            logging.warning(f"The `to_sql` methods prompted an IntegrityError: {error.orig.args}")  # https://stackoverflow.com/a/55581428
            # https://stackoverflow.com/a/29614207 uses temp table
            # https://stackoverflow.com/q/24522290 talks about using `session.flush()`
    else:
        return abort(404)


@bp.route('/initialization-page-2', methods=['GET', 'POST'])
def collect_AUCT_and_historical_COUNTER_data():
    """This route function creates the template for the `annualUsageCollectionTracking` relation and lets the user download it, then lets the user upload the `annualUsageCollectionTracking` relation data and the reformatted historical COUNTER reports so the former is loaded into the database and the latter is divided and deduped.

    Upon redirect, this route function renders the page showing the template for the `annualUsageCollectionTracking` relation, the JSONs for transforming COUNTER R4 reports into formats that can be ingested by NoLCAT, and the form to upload the filled-out template and transformed COUNTER reports. When the `annualUsageCollectionTracking` relation and COUNTER reports are submitted, the function saves the `annualUsageCollectionTracking` relation data by loading it into the database, saves the COUNTER data as a `RawCOUNTERReport` object in a temporary file, then redirects to the `determine_if_resources_match` route function.
    """
    form = AUCTAndCOUNTERForm()
    
    #Section: Before Page Renders
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #Subsection: Get Cartesian Product of `fiscalYears` and `statisticsSources` Primary Keys via Database Query
        SELECT_statement = text('SELECT statisticsSources.statistics_source_ID, fiscalYears.fiscal_year_ID, statisticsSources.statistics_source_name, fiscalYears.fiscal_year FROM statisticsSources JOIN fiscalYears;')
        #ToDo: AUCT_values = db.engine.execute(SELECT_statement).values()  # Unable to determine exactly what is in the lists output by each method of https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.RowProxy
        #ToDo: From `AUCT_values`, generate the below
        #ToDo: AUCT_index_array = [
        #    [record1 statisticsSources.statistics_source_ID, record1 fiscalYears.fiscal_year_ID],
        #    [record2 statisticsSources.statistics_source_ID, record2 fiscalYears.fiscal_year_ID],
        #    ...
        #]
        #ToDo: AUCT_value_array = [
        #    [record1 statisticsSources.statistics_source_name, record1 fiscalYears.fiscal_year],
        #    [record2 statisticsSources.statistics_source_name, record2 fiscalYears.fiscal_year],
        #    ...
        #]

        #Subsection: Create `annualUsageConnectionTracking` Relation Template File
        #ToDo: multiindex = pd.DataFrame(
        #    AUCT_index_array,
        #    columns=["AUCT_statistics_source", "AUCT_fiscal_year"],
        #)
        #ToDo: multiindex = pd.MultiIndex.from_frame(multiindex)
        #ToDo: df = pd.DataFrame(
        #    AUCT_value_array,
        #    index=multiindex,
        #    columns=["Statistics Source", "Fiscal Year"],
        #)

        #ToDo: df['usage_is_being_collected'] = None
        #ToDo: df['manual_collection_required'] = None
        #ToDo: df['collection_via_email'] = None
        #ToDo: df['is_COUNTER_compliant'] = None
        #ToDo: df['collection_status'] = None
        #ToDo: df['usage_file_path'] = None
        #ToDo: df['notes'] = None

        #ToDo: df.to_csv(
        #    'initialize_annualUsageCollectionTracking.tsv',  #ToDo: Should it be saved in the `nolcat_db_data` folder instead?
        #    sep="\t",
        #    index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
        #    encoding='utf-8',
        #    errors='backslashreplace',  # For encoding errors
        #)
        #ToDo: Confirm above downloads successfully
        #ToDo: return render_template('initialization/initial-data-upload-2.html', form=form)

    #Section: After Form Submission
    elif form.validate_on_submit():
        #Subsection: Load `annualUsageCollectionTracking` into Database
        AUCT_dataframe = pd.read_csv(
            form.annualUsageCollectionTracking_TSV.data,
            sep='\t',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        #AUCT_dataframe['notes'] = AUCT_dataframe['notes'].encode('utf-8').decode('unicode-escape')

        AUCT_dataframe.to_sql(
            'annualUsageCollectionTracking',
            con=db.engine,
            if_exists='append',
        )

        #Subsection: Save COUNTER Reports in a Single Temp Tabular File
        COUNTER_reports_df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()
        COUNTER_reports_df.to_csv(
            'str of a file path',  #ToDo: Determine where to save file
            na_rep='`None`',
            index_label='index',
            encoding='utf-8',
            date_format='%Y-%m-%d',  #ToDo: Double check this is correct for setting ISO format
            errors='backslashreplace',
        )

        return redirect(url_for('determine_if_resources_match'))

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


@bp.route('/database-creation-complete', methods=['GET', 'POST'])
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