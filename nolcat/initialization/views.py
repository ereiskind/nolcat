import logging
from pathlib import Path
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
from flask import flash
import pandas as pd

from . import bp
from .forms import *
from ..app import *
from ..models import *
from ..upload_COUNTER_reports import UploadCOUNTERReports

log = logging.getLogger(__name__)


#Section: Database Initialization Wizard
@bp.route('/', methods=['GET', 'POST'])
def collect_FY_and_vendor_data():
    """This route function ingests the files containing data going into the `fiscalYears`, `vendors`, and `vendorNotes` relations, then loads that data into the database.
    
    The route function renders the page showing the templates for the `fiscalYears`, `vendors`, and `vendorNotes` relations as well as the form for submitting the completed templates. When the CSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_sources_data()` route function. The creation of the initial relation CSVs is split into two route functions/pages to split up the instructions and to comply with the limit on the number of files that can be uploaded at once found in most browsers.
    """
    log.info("Starting `collect_FY_and_vendor_data()`.")
    form = FYAndVendorsDataForm()
    if request.method == 'GET':
        return render_template('initialization/index.html', form=form, CWD=str(Path(__file__).parent))
    elif form.validate_on_submit():
        #Section: Ingest Data from Uploaded CSVs
        # For relations containing a record index (primary key) column when loaded, the primary key field name must be identified using the `index_col` keyword argument, otherwise pandas will create an `index` field for an auto-generated record index; this extra field will prevent the dataframe from being loaded into the database.
        # When Excel saves worksheets with non-Latin characters as CSVs, it defaults to UTF-16. The "save as" option "CSV UTF-8", which isn't available in all version of Excel, must be used.
        #ALERT: An error in the encoding statement can cause the logging statement directly above it to not appear in the output
        #Subsection: Upload `fiscalYears` CSV File
        log.debug(f"The `fiscalYears` FileField data:\n{form.fiscalYears_CSV.data}\n")
        fiscalYears_dataframe = pd.read_csv(
            form.fiscalYears_CSV.data,
            index_col='fiscal_year_ID',
            parse_dates=['start_date', 'end_date'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if fiscalYears_dataframe.isnull().all(axis=None) == True:
            log.error("The `fiscalYears` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`fiscalYears`")
        
        fiscalYears_dataframe = fiscalYears_dataframe.astype({k: v for (k, v) in FiscalYears.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        log.debug(f"`fiscalYears` dataframe dtypes before encoding conversions:\n{fiscalYears_dataframe.dtypes}\n")
        fiscalYears_dataframe['notes_on_statisticsSources_used'] = fiscalYears_dataframe['notes_on_statisticsSources_used'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        fiscalYears_dataframe['notes_on_corrections_after_submission'] = fiscalYears_dataframe['notes_on_corrections_after_submission'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`fiscalYears` dataframe:\n{fiscalYears_dataframe}\n")

        #Subsection: Upload `vendors` CSV File
        log.debug(f"The `vendors` FileField data:\n{form.vendors_CSV.data}\n")
        vendors_dataframe = pd.read_csv(
            form.vendors_CSV.data,
            index_col='vendor_ID',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if vendors_dataframe.isnull().all(axis=None) == True:
            log.error("The `vendors` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`vendors`")
        
        vendors_dataframe = vendors_dataframe.astype({k: v for (k, v) in Vendors.state_data_types().items()})
        log.debug(f"`vendors` dataframe dtypes before encoding conversions:\n{vendors_dataframe.dtypes}\n")
        vendors_dataframe['vendor_name'] = vendors_dataframe['vendor_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`vendors` dataframe:\n{vendors_dataframe}\n")

        #Subsection: Upload `vendorNotes` CSV File
        log.debug(f"The `vendorNotes` FileField data:\n{form.vendorNotes_CSV.data}\n")
        vendorNotes_dataframe = pd.read_csv(
            form.vendorNotes_CSV.data,
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if vendorNotes_dataframe.isnull().all(axis=None) == True:
            log.error("The `vendorNotes` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`vendorNotes`")
        
        vendorNotes_dataframe = vendorNotes_dataframe.astype({k: v for (k, v) in VendorNotes.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        log.debug(f"`vendorNotes` dataframe dtypes before encoding conversions:\n{vendorNotes_dataframe.dtypes}\n")
        vendorNotes_dataframe['note'] = vendorNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`vendorNotes` dataframe:\n{vendorNotes_dataframe}\n")


        #Section: Load Data into Database
        data_load_errors = []
        fiscalYears_load_result = load_data_into_database(
            df=fiscalYears_dataframe,
            relation='fiscalYears',
            engine=db.engine,
        )
        if fiscalYears_load_result.startwith("Loading data into the fiscalYears relation raised the error"):
            data_load_errors.append(fiscalYears_load_result)
        vendors_load_result = load_data_into_database(
            df=vendors_dataframe,
            relation='vendors',
            engine=db.engine,
        )
        if vendors_load_result.startwith("Loading data into the vendors relation raised the error"):
            data_load_errors.append(vendors_load_result)
        vendorNotes_load_result = load_data_into_database(
            df=vendorNotes_dataframe,
            relation='vendorNotes',
            engine=db.engine,
            load_index=False,
        )
        if vendorNotes_load_result.startwith("Loading data into the vendorNotes relation raised the error"):
            data_load_errors.append(vendorNotes_load_result)
        if data_load_errors:
            flash(data_load_errors)
            return redirect(url_for('initialization.collect_FY_and_vendor_data'))
        
        return redirect(url_for('initialization.collect_sources_data'))

    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)


@bp.route('/initialization-page-2', methods=['GET', 'POST'])
def collect_sources_data():
    """This route function ingests the files containing data going into the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations, then loads that data into the database.

    The route function renders the page showing the templates for the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations as well as the form for submitting the completed templates. When the CSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_AUCT_and_historical_COUNTER_data()` route function. The creation of the initial relation CSVs is split into two route functions/pages to split up the instructions and to comply with the limit on the number of files that can be uploaded at once found in most browsers.
    """
    log.info("Starting `collect_sources_data()`.")
    form = SourcesDataForm()
    if request.method == 'GET':
        return render_template('initialization/initial-data-upload-2.html', form=form, CWD=str(Path(__file__).parent))
    elif form.validate_on_submit():
        #Section: Ingest Data from Uploaded CSVs
        #Subsection: Upload `statisticsSources` CSV File
        log.debug(f"The `statisticsSources` FileField data:\n{form.statisticsSources_CSV.data}\n")
        statisticsSources_dataframe = pd.read_csv(
            form.statisticsSources_CSV.data,
            index_col='statistics_source_ID',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if statisticsSources_dataframe.isnull().all(axis=None) == True:
            log.error("The `statisticsSources` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`statisticsSources`")
        
        statisticsSources_dataframe = statisticsSources_dataframe.astype({k: v for (k, v) in StatisticsSources.state_data_types().items()})
        log.debug(f"`statisticsSources` dataframe dtypes before encoding conversions:\n{statisticsSources_dataframe.dtypes}\n")
        statisticsSources_dataframe['statistics_source_name'] = statisticsSources_dataframe['statistics_source_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`statisticsSources` dataframe:\n{statisticsSources_dataframe}\n")

        #Subsection: Upload `statisticsSourceNotes` CSV File
        log.debug(f"The `statisticsSourceNotes` FileField data:\n{form.statisticsSourceNotes_CSV.data}\n")
        statisticsSourceNotes_dataframe = pd.read_csv(
            form.statisticsSourceNotes_CSV.data,
            encoding='utf-8',
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding_errors='backslashreplace',
        )
        if statisticsSourceNotes_dataframe.isnull().all(axis=None) == True:
            log.error("The `statisticsSourceNotes` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`statisticsSourceNotes`")
        
        statisticsSourceNotes_dataframe = statisticsSourceNotes_dataframe.astype({k: v for (k, v) in StatisticsSourceNotes.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        log.debug(f"`statisticsSourceNotes` dataframe dtypes before encoding conversions:\n{statisticsSourceNotes_dataframe.dtypes}\n")
        statisticsSourceNotes_dataframe['note'] = statisticsSourceNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`statisticsSourceNotes` dataframe:\n{statisticsSourceNotes_dataframe}\n")

        #Subsection: Upload `resourceSources` CSV File
        log.debug(f"The `resourceSources` FileField data:\n{form.resourceSources_CSV.data}\n")
        resourceSources_dataframe = pd.read_csv(
            form.resourceSources_CSV.data,
            index_col='resource_source_ID',
            parse_dates=['access_stop_date'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if resourceSources_dataframe.isnull().all(axis=None) == True:
            log.error("The `resourceSources` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`resourceSources`")
        
        resourceSources_dataframe = resourceSources_dataframe.astype({k: v for (k, v) in ResourceSources.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        log.debug(f"`resourceSources` dataframe dtypes before encoding conversions:\n{resourceSources_dataframe.dtypes}\n")
        resourceSources_dataframe['resource_source_name'] = resourceSources_dataframe['resource_source_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`resourceSources` dataframe:\n{resourceSources_dataframe}\n")

        #Subsection: Upload `resourceSourceNotes` CSV File
        log.debug(f"The `resourceSourceNotes` FileField data:\n{form.resourceSourceNotes_CSV.data}\n")
        resourceSourceNotes_dataframe = pd.read_csv(
            form.resourceSourceNotes_CSV.data,
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if resourceSourceNotes_dataframe.isnull().all(axis=None) == True:
            log.error("The `resourceSourceNotes` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`resourceSourceNotes`")
        
        resourceSourceNotes_dataframe = resourceSourceNotes_dataframe.astype({k: v for (k, v) in ResourceSourceNotes.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        log.debug(f"`resourceSourceNotes` dataframe dtypes before encoding conversions:\n{resourceSourceNotes_dataframe.dtypes}\n")
        resourceSourceNotes_dataframe['note'] = resourceSourceNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`resourceSourceNotes` dataframe:\n{resourceSourceNotes_dataframe}\n")

        #Subsection: Upload `statisticsResourceSources` CSV File
        log.debug(f"The `statisticsResourceSources` FileField data:\n{form.statisticsResourceSources_CSV.data}\n")
        statisticsResourceSources_dataframe = pd.read_csv(
            form.statisticsResourceSources_CSV.data,
            index_col=['SRS_statistics_source', 'SRS_resource_source'],
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if statisticsResourceSources_dataframe.isnull().all(axis=None) == True:
            log.error("The `statisticsResourceSources` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`statisticsResourceSources`")
        
        # Because there aren't any string dtypes in need of encoding correction, the logging statements for the dtypes and the dataframe have been combined
        log.info(f"`statisticsResourceSources` dtypes and dataframe:\n{statisticsResourceSources_dataframe.dtypes}\n{statisticsResourceSources_dataframe}\n")


        #Section: Load Data into Database
        data_load_errors = []
        statisticsSources_load_result = load_data_into_database(
            df=statisticsSources_dataframe,
            relation='statisticsSources',
            engine=db.engine,
        )
        if statisticsSources_load_result.startwith("Loading data into the statisticsSources relation raised the error"):
            data_load_errors.append(statisticsSources_load_result)
        statisticsSourceNotes_load_result = load_data_into_database(
            df=statisticsSourceNotes_dataframe,
            relation='statisticsSourceNotes',
            engine=db.engine,
            load_index=False,
        )
        if statisticsSourceNotes_load_result.startwith("Loading data into the statisticsSourceNotes relation raised the error"):
            data_load_errors.append(statisticsSourceNotes_load_result)
        resourceSources_load_result = load_data_into_database(
            df=resourceSources_dataframe,
            relation='resourceSources',
            engine=db.engine,
        )
        if resourceSources_load_result.startwith("Loading data into the resourceSources relation raised the error"):
            data_load_errors.append(resourceSources_load_result)
        resourceSourceNotes_load_result = load_data_into_database(
            df= resourceSourceNotes_dataframe,
            relation='resourceSourceNotes',
            engine=db.engine,
            load_index=False,
        )
        if resourceSourceNotes_load_result.startwith("Loading data into the resourceSourceNotes relation raised the error"):
            data_load_errors.append(resourceSourceNotes_load_result)
        statisticsResourceSources_load_result = load_data_into_database(
            df=statisticsResourceSources_dataframe,
            relation='statisticsResourceSources',
            engine=db.engine,
        )
        if statisticsResourceSources_load_result.startwith("Loading data into the statisticsResourceSources relation raised the error"):
            data_load_errors.append(statisticsResourceSources_load_result)
        if data_load_errors:
            flash(data_load_errors)
            return redirect(url_for('initialization.collect_sources_data'))
        
        return redirect(url_for('initialization.collect_AUCT_and_historical_COUNTER_data'))

    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)


@bp.route('/initialization-page-3', methods=['GET', 'POST'])
def collect_AUCT_and_historical_COUNTER_data():
    """This route function creates the template for the `annualUsageCollectionTracking` relation and lets the user download it, then lets the user upload the `annualUsageCollectionTracking` relation data and the historical COUNTER reports into the database.

    Upon redirect, this route function renders the page for downloading the template for the `annualUsageCollectionTracking` relation and the form to upload that filled-out template and any tabular R4 and R5 COUNTER reports. When the `annualUsageCollectionTracking` relation and COUNTER reports are submitted, the function saves the `annualUsageCollectionTracking` relation data by loading it into the database, then processes the COUNTER reports by transforming them into a dataframe with `UploadCOUNTERReports.create_dataframe()` and loading the resulting dataframe into the database.
    """
    log.info("Starting `collect_AUCT_and_historical_COUNTER_data()`.")
    form = AUCTAndCOUNTERForm()
    
    #Section: Before Page Renders
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #Subsection: Get Cartesian Product of `fiscalYears` and `statisticsSources` Primary Keys via Database Query
        df = query_database(
            query="SELECT statisticsSources.statistics_source_ID, fiscalYears.fiscal_year_ID, statisticsSources.statistics_source_name, fiscalYears.fiscal_year FROM statisticsSources JOIN fiscalYears;",
            engine=db.engine,
            index=["statistics_source_ID", "fiscal_year_ID"],
        )
        if isinstance(df, str):
            flash(f"Unable to load requested page because it relied on t{df[1:].replace(' raised', ', which raised')}")
            return redirect(url_for('initialization.collect_FY_and_vendor_data'))
        log.debug(f"The result of the query for the AUCT Cartesian product dataframe:\n{df}")

        #Subsection: Create `annualUsageConnectionTracking` Relation Template File
        df = df.rename_axis(index={
            "statistics_source_ID": "AUCT_statistics_source",
            "fiscal_year_ID": "AUCT_fiscal_year",
        })
        df = df.rename(columns={
            "statistics_source_name": "Statistics Source",
            "fiscal_year": "Fiscal Year",
        })
        log.debug(f"`annualUsageCollectionTracking` dataframe with fields renamed:\n{df}")

        df['usage_is_being_collected'] = None
        df['manual_collection_required'] = None
        df['collection_via_email'] = None
        df['is_COUNTER_compliant'] = None
        df['collection_status'] = None
        df['usage_file_path'] = None
        df['notes'] = None
        log.info(f"`annualUsageCollectionTracking` template dataframe:\n{df}")

        template_save_location = Path(__file__).parent / 'initialize_annualUsageCollectionTracking.csv'
        try:
            df.to_csv(
                template_save_location,
                index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
                encoding='utf-8',
                errors='backslashreplace',  # For encoding errors
            )
            log.debug(f"The AUCT template CSV was created successfully: {template_save_location.is_file()}")  #FileIO
        except Exception as error:
            log.error(f"The AUCT template CSV wasn't created because of the error {error}.")  #FileIOError
            if infinite_loop_error in locals():  # This is triggered the second time this code block is reached
                log.error("Multiple attempts to create the AUCT template CSV have failed. Please try uploading the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations again.")
                #ToDo: Truncate the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations
                #ToDo: Flash error
                # Use https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.Engine.execute for database update and delete operations
                return redirect(url_for('initialization.collect_sources_data'))
            infinite_loop_error = True
            return render_template('initialization/initial-data-upload-3.html', form=form)  # This will restart the route function
        
        #ToDo: Confirm AUCT template CSV downloads successfully
        return render_template('initialization/initial-data-upload-3.html', form=form, AUCT_file_path=str(template_save_location))

    #Section: After Form Submission
    elif form.validate_on_submit():
        if 'template_save_location' in locals():  # Submitting the form calls the function again, so the initialized variable isn't saved
            template_save_location.unlink(missing_ok=True)
        #Subsection: Ingest `annualUsageCollectionTracking` Data
        log.debug(f"The `annualUsageCollectionTracking` FileField data:\n{form.annualUsageCollectionTracking_CSV.data}\n")
        AUCT_dataframe = pd.read_csv(
            form.annualUsageCollectionTracking_CSV.data,
            index_col=['AUCT_statistics_source', 'AUCT_fiscal_year'],
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if AUCT_dataframe.isnull().all(axis=None) == True:
            log.error("The `annualUsageCollectionTracking` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`annualUsageCollectionTracking`")
        
        AUCT_dataframe = AUCT_dataframe.astype({k: v for (k, v) in AnnualUsageCollectionTracking.state_data_types().items()})
        log.debug(f"`annualUsageCollectionTracking` dataframe dtypes before encoding conversions:\n{AUCT_dataframe.dtypes}\n")
        AUCT_dataframe['usage_file_path'] = AUCT_dataframe['usage_file_path'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        AUCT_dataframe['notes'] = AUCT_dataframe['notes'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        log.info(f"`annualUsageCollectionTracking` dataframe:\n{AUCT_dataframe}\n")

        #Subsection: Ingest COUNTER Reports
        #ToDo: Uncomment this subsection during Planned Iteration 2
        #try:
        #    COUNTER_reports_df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()  # `form.COUNTER_reports.data` is a list of <class 'werkzeug.datastructures.FileStorage'> objects
        #    log.debug(f"`COUNTERData` data:\n{COUNTER_reports_df}\n")
        #    COUNTER_reports_df['report_creation_date'] = pd.to_datetime(None)
        #    COUNTER_reports_df.index += first_new_PK_value('COUNTERData')
        #    log.info(f"`COUNTERData` dataframe:\n{COUNTER_reports_df.head()}\n")
        #    log.debug(f"`COUNTERData` dataframe:\n{COUNTER_reports_df}\n")
        #except Exception as error:
        #    message = f"Trying to consolidate the uploaded COUNTER data into a single dataframe raised the error {error}."
        #    log.error(message)
        #    #ToDo: Flash message
        # ToDo: Run `check_if_data_already_in_COUNTERData()`

        #Subsection: Load Data into Database
        data_load_errors = []
        annualUsageCollectionTracking_load_result = load_data_into_database(
            df=AUCT_dataframe,
            relation='annualUsageCollectionTracking',
            engine=db.engine,
            index_field_name=['AUCT_statistics_source', 'AUCT_fiscal_year'],
        )
        if annualUsageCollectionTracking_load_result.startwith("Loading data into the annualUsageCollectionTracking relation raised the error"):
            data_load_errors.append(annualUsageCollectionTracking_load_result)
        #COUNTERData_load_result = load_data_into_database(
        #    df=COUNTER_reports_df,
        #    relation='COUNTERData',
        #    engine=db.engine,
        #    index_field_name='COUNTER_data_ID',
        #)
        #if COUNTERData_load_result.startwith("Loading data into the COUNTERData relation raised the error"):
        #    data_load_errors.append(COUNTERData_load_result)
        if data_load_errors:
            flash(data_load_errors)
            return redirect(url_for('initialization.collect_AUCT_and_historical_COUNTER_data'))

        # return redirect(url_for('initialization.upload_historical_non_COUNTER_usage'))  #ToDo: Replace below during Planned Iteration 3
        return redirect(url_for('initialization.data_load_complete'))

    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)


@bp.route('/initialization-page-4', methods=['GET', 'POST'])
def upload_historical_non_COUNTER_usage():
    """This route function allows the user to upload files containing non-COUNTER usage reports to the container hosting this program, placing the file paths within the COUNTER usage statistics database for easy retrieval in the future.
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function.
    """
    log.info("Starting `upload_historical_non_COUNTER_usage()`.")
    '''
    form = FormClass()
    if request.method == 'GET':
        #ToDo: `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';` to get all non-COUNTER stats source/date combos
        #ToDo: Create an iterable to pass all the records returned by the above to a form
        #ToDo: For each item in the above iterable, use `form` to provide the opportunity for a file upload
        return render_template('initialization/initial-data-upload-4.html', form=form)
    elif form.validate_on_submit():
        #ToDo: For each file uploaded in the form
            #ToDo: Save the file in a TBD location in the container using the AUCT_Statistics_Source and AUCT_Fiscal_Year values for the file name
            #ToDo: `UPDATE annualUsageCollectionTracking SET Usage_File_Path='<file path of the file saved above>' WHERE AUCT_Statistics_Source=<the composite PK value> AND AUCT_Fiscal_Year=<the composite PK value>`
            # Use https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.Engine.execute for database update and delete operations
        return redirect(url_for('blueprint.name of the route function for the page that user should go to once form is submitted'))
    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)
    '''
    pass


@bp.route('/initialization-page-5', methods=['GET', 'POST'])
def data_load_complete():
    """This route function indicates the successful completion of the wizard and initialization of the database."""
    return render_template('initialization/show-loaded-data.html')