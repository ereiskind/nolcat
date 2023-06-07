import logging
import os
from pathlib import Path
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
from flask import current_app
from flask import send_from_directory
import pandas as pd

from . import bp
from .forms import *
from ..app import db
from ..app import date_parser
from ..models import *
from ..upload_COUNTER_reports import UploadCOUNTERReports


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#Section: Uploads and Downloads
@bp.route('/download/<path:filename>',  methods=['GET', 'POST'])
def download_file(filename):
    """This route function allows the user to access the file specified in the route name through a Jinja link."""
    return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], path='.', filename=filename, as_attachment=True)


#Section: Database Initialization Wizard
@bp.route('/', methods=['GET', 'POST'])
def collect_FY_and_vendor_data():
    """This route function ingests the files containing data going into the `fiscalYears`, `vendors`, and `vendorNotes` relations, then loads that data into the database.
    
    The route function renders the page showing the templates for the `fiscalYears`, `vendors`, and `vendorNotes` relations as well as the form for submitting the completed templates. When the CSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_sources_data()` route function. The creation of the initial relation CSVs is split into two route functions/pages to split up the instructions and to comply with the limit on the number of files that can be uploaded at once found in most browsers.
    """
    form = FYAndVendorsDataForm()
    if request.method == 'GET':
        return render_template('initialization/index.html', form=form)
    elif form.validate_on_submit():
        #Section: Ingest Data from Uploaded CSVs
        # For relations containing a record index (primary key) column when loaded, the primary key field name must be identified using the `index_col` keyword argument, otherwise pandas will create an `index` field for an auto-generated record index; this extra field will prevent the dataframe from being loaded into the database.
        # When Excel saves worksheets with non-Latin characters as CSVs, it defaults to UTF-16. The "save as" option "CSV UTF-8", which isn't available in all version of Excel, must be used. 
        #ALERT: An error in the encoding statement can cause the logging statement directly above it to not appear in the output
        #Subsection: Upload `fiscalYears` CSV File
        logging.debug(f"`fiscalYears` data:\n{form.fiscalYears_CSV.data}\n")
        fiscalYears_dataframe = pd.read_csv(
            form.fiscalYears_CSV.data,
            index_col='fiscal_year_ID',
            parse_dates=['start_date', 'end_date'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if fiscalYears_dataframe.isnull().all(axis=None) == True:
            logging.error("The `fiscalYears` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`fiscalYears`")
        
        fiscalYears_dataframe = fiscalYears_dataframe.astype({k: v for (k, v) in FiscalYears.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        logging.info(f"`fiscalYears` dataframe dtypes before encoding conversions:\n{fiscalYears_dataframe.dtypes}\n")
        fiscalYears_dataframe['notes_on_statisticsSources_used'] = fiscalYears_dataframe['notes_on_statisticsSources_used'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        fiscalYears_dataframe['notes_on_corrections_after_submission'] = fiscalYears_dataframe['notes_on_corrections_after_submission'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`fiscalYears` dataframe:\n{fiscalYears_dataframe}\n")

        #Subsection: Upload `vendors` CSV File
        logging.debug(f"`vendors` data:\n{form.vendors_CSV.data}\n")
        vendors_dataframe = pd.read_csv(
            form.vendors_CSV.data,
            index_col='vendor_ID',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if vendors_dataframe.isnull().all(axis=None) == True:
            logging.error("The `vendors` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`vendors`")
        
        vendors_dataframe = vendors_dataframe.astype({k: v for (k, v) in Vendors.state_data_types().items()})
        logging.info(f"`vendors` dataframe dtypes before encoding conversions:\n{vendors_dataframe.dtypes}\n")
        vendors_dataframe['vendor_name'] = vendors_dataframe['vendor_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`vendors` dataframe:\n{vendors_dataframe}\n")

        #Subsection: Upload `vendorNotes` CSV File
        logging.debug(f"`vendorNotes` data:\n{form.vendorNotes_CSV.data}\n")
        vendorNotes_dataframe = pd.read_csv(
            form.vendorNotes_CSV.data,
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if vendorNotes_dataframe.isnull().all(axis=None) == True:
            logging.error("The `vendorNotes` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`vendorNotes`")
        
        vendorNotes_dataframe = vendorNotes_dataframe.astype({k: v for (k, v) in VendorNotes.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        logging.info(f"`vendorNotes` dataframe dtypes before encoding conversions:\n{vendorNotes_dataframe.dtypes}\n")
        vendorNotes_dataframe['note'] = vendorNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`vendorNotes` dataframe:\n{vendorNotes_dataframe}\n")


        #Section: Load Data into Database
        try:
            fiscalYears_dataframe.to_sql(
                'fiscalYears',
                con=db.engine,
                if_exists='append',
                # Dataframe index and primary key field both named `fiscal_year_ID`
            )
            logging.debug("Relation `fiscalYears` loaded into the database")
            vendors_dataframe.to_sql(
                'vendors',
                con=db.engine,
                if_exists='append',
                # Dataframe index and primary key field both named `vendor_ID`
            )
            logging.debug("Relation `vendors` loaded into the database")
            vendorNotes_dataframe.to_sql(
                'vendorNotes',
                con=db.engine,
                if_exists='append',
                index=False,
            )
            logging.debug("Relation `vendorNotes` loaded into the database")
            logging.info("All relations loaded into the database")
        except Exception as error:
            logging.warning(f"The `to_sql` methods raised an error: {error}")
        
        return redirect(url_for('initialization.collect_sources_data'))

    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/initialization-page-2', methods=['GET', 'POST'])
def collect_sources_data():
    """This route function ingests the files containing data going into the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations, then loads that data into the database.

    The route function renders the page showing the templates for the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations as well as the form for submitting the completed templates. When the CSVs containing the data for those relations are submitted, the function saves the data by loading it into the database, then redirects to the `collect_AUCT_and_historical_COUNTER_data()` route function. The creation of the initial relation CSVs is split into two route functions/pages to split up the instructions and to comply with the limit on the number of files that can be uploaded at once found in most browsers.
    """
    form = SourcesDataForm()
    if request.method == 'GET':
        return render_template('initialization/initial-data-upload-2.html', form=form)
    elif form.validate_on_submit():
        #Section: Ingest Data from Uploaded CSVs
        #Subsection: Upload `statisticsSources` CSV File
        logging.debug(f"`statisticsSources` data:\n{form.statisticsSources_CSV.data}\n")
        statisticsSources_dataframe = pd.read_csv(
            form.statisticsSources_CSV.data,
            index_col='statistics_source_ID',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if statisticsSources_dataframe.isnull().all(axis=None) == True:
            logging.error("The `statisticsSources` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`statisticsSources`")
        
        statisticsSources_dataframe = statisticsSources_dataframe.astype({k: v for (k, v) in StatisticsSources.state_data_types().items()})
        logging.info(f"`statisticsSources` dataframe dtypes before encoding conversions:\n{statisticsSources_dataframe.dtypes}\n")
        statisticsSources_dataframe['statistics_source_name'] = statisticsSources_dataframe['statistics_source_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`statisticsSources` dataframe:\n{statisticsSources_dataframe}\n")

        #Subsection: Upload `statisticsSourceNotes` CSV File
        logging.debug(f"`statisticsSourceNotes` data:\n{form.statisticsSourceNotes_CSV.data}\n")
        statisticsSourceNotes_dataframe = pd.read_csv(
            form.statisticsSourceNotes_CSV.data,
            encoding='utf-8',
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding_errors='backslashreplace',
        )
        if statisticsSourceNotes_dataframe.isnull().all(axis=None) == True:
            logging.error("The `statisticsSourceNotes` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`statisticsSourceNotes`")
        
        statisticsSourceNotes_dataframe = statisticsSourceNotes_dataframe.astype({k: v for (k, v) in StatisticsSourceNotes.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        logging.info(f"`statisticsSourceNotes` dataframe dtypes before encoding conversions:\n{statisticsSourceNotes_dataframe.dtypes}\n")
        statisticsSourceNotes_dataframe['note'] = statisticsSourceNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`statisticsSourceNotes` dataframe:\n{statisticsSourceNotes_dataframe}\n")

        #Subsection: Upload `resourceSources` CSV File
        logging.debug(f"`resourceSources` data:\n{form.resourceSources_CSV.data}\n")
        resourceSources_dataframe = pd.read_csv(
            form.resourceSources_CSV.data,
            index_col='resource_source_ID',
            parse_dates=['use_stop_date'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if resourceSources_dataframe.isnull().all(axis=None) == True:
            logging.error("The `resourceSources` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`resourceSources`")
        
        resourceSources_dataframe = resourceSources_dataframe.astype({k: v for (k, v) in ResourceSources.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        logging.info(f"`resourceSources` dataframe dtypes before encoding conversions:\n{resourceSources_dataframe.dtypes}\n")
        resourceSources_dataframe['resource_source_name'] = resourceSources_dataframe['resource_source_name'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`resourceSources` dataframe:\n{resourceSources_dataframe}\n")

        #Subsection: Upload `resourceSourceNotes` CSV File
        logging.debug(f"`resourceSourceNotes` data:\n{form.resourceSourceNotes_CSV.data}\n")
        resourceSourceNotes_dataframe = pd.read_csv(
            form.resourceSourceNotes_CSV.data,
            parse_dates=['date_written'],
            date_parser=date_parser,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if resourceSourceNotes_dataframe.isnull().all(axis=None) == True:
            logging.error("The `resourceSourceNotes` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`resourceSourceNotes`")
        
        resourceSourceNotes_dataframe = resourceSourceNotes_dataframe.astype({k: v for (k, v) in ResourceSourceNotes.state_data_types().items() if v != "datetime64[ns]"})  # Datetimes are excluded because their data type was set with the `date_parser` argument
        logging.info(f"`resourceSourceNotes` dataframe dtypes before encoding conversions:\n{resourceSourceNotes_dataframe.dtypes}\n")
        resourceSourceNotes_dataframe['note'] = resourceSourceNotes_dataframe['note'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`resourceSourceNotes` dataframe:\n{resourceSourceNotes_dataframe}\n")

        #Subsection: Upload `statisticsResourceSources` CSV File
        logging.debug(f"`statisticsResourceSources` data:\n{form.statisticsResourceSources_CSV.data}\n")
        statisticsResourceSources_dataframe = pd.read_csv(
            form.statisticsResourceSources_CSV.data,
            index_col=['SRS_statistics_source', 'SRS_resource_source'],
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if statisticsResourceSources_dataframe.isnull().all(axis=None) == True:
            logging.error("The `statisticsResourceSources` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`statisticsResourceSources`")
        
        # Because there aren't any string dtypes in need of encoding correction, the logging statements for the dtypes and the dataframe have been combined
        logging.info(f"`statisticsResourceSources` dtypes and dataframe:\n{statisticsResourceSources_dataframe.dtypes}\n{statisticsResourceSources_dataframe}\n")


        #Section: Load Data into Database
        try:
            statisticsSources_dataframe.to_sql(
                'statisticsSources',
                con=db.engine,
                if_exists='append',
                # Dataframe index and primary key field both named `statistics_source_ID`
            )
            logging.debug("Relation `statisticsSources` loaded into the database")
            statisticsSourceNotes_dataframe.to_sql(
                'statisticsSourceNotes',
                con=db.engine,
                if_exists='append',
                index=False,
            )
            logging.debug("Relation `statisticsSourceNotes` loaded into the database")
            resourceSources_dataframe.to_sql(
                'resourceSources',
                con=db.engine,
                if_exists='append',
                # Dataframe index and primary key field both named `resource_source_ID`
            )
            logging.debug("Relation `resourceSources` loaded into the database")
            resourceSourceNotes_dataframe.to_sql(
                'resourceSourceNotes',
                con=db.engine,
                if_exists='append',
                index=False,
            )
            logging.debug("Relation `resourceSourceNotes` loaded into the database")
            statisticsResourceSources_dataframe.to_sql(
                'statisticsResourceSources',
                con=db.engine,
                if_exists='append',
                # Dataframe multiindex fields and composite primary key fields both named `SRS_statistics_source` and `SRS_resource_source`
            )
            logging.debug("Relation `statisticsResourceSources` loaded into the database")
            logging.info("All relations loaded into the database")
        except Exception as error:
            logging.warning(f"The `to_sql` methods raised an error: {error}")
        
        return redirect(url_for('initialization.collect_AUCT_and_historical_COUNTER_data'))

    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/initialization-page-3', methods=['GET', 'POST'])
def collect_AUCT_and_historical_COUNTER_data():
    """This route function creates the template for the `annualUsageCollectionTracking` relation and lets the user download it, then lets the user upload the `annualUsageCollectionTracking` relation data and the historical COUNTER reports into the database.

    Upon redirect, this route function renders the page for downloading the template for the `annualUsageCollectionTracking` relation and the form to upload that filled-out template and any tabular R4 and R5 COUNTER reports. When the `annualUsageCollectionTracking` relation and COUNTER reports are submitted, the function saves the `annualUsageCollectionTracking` relation data by loading it into the database, then processes the COUNTER reports by transforming them into a dataframe with `UploadCOUNTERReports.create_dataframe()` and loading the resulting dataframe into the database.
    """
    form = AUCTAndCOUNTERForm()
    
    #Section: Before Page Renders
    if request.method == 'GET':  # `POST` goes to HTTP status code 302 because of `redirect`, subsequent 200 is a GET
        #Subsection: Get Cartesian Product of `fiscalYears` and `statisticsSources` Primary Keys via Database Query
        df = pd.read_sql(
            sql='SELECT statisticsSources.statistics_source_ID, fiscalYears.fiscal_year_ID, statisticsSources.statistics_source_name, fiscalYears.fiscal_year FROM statisticsSources JOIN fiscalYears;',
            con=db.engine,
            index_col=["statistics_source_ID", "fiscal_year_ID"],
        )
        logging.debug(f"AUCT Cartesian product dataframe:\n{df}")

        #Subsection: Create `annualUsageConnectionTracking` Relation Template File
        df = df.rename_axis(index={
            "statistics_source_ID": "AUCT_statistics_source",
            "fiscal_year_ID": "AUCT_fiscal_year",
        })
        df = df.rename(columns={
            "statistics_source_name": "Statistics Source",
            "fiscal_year": "Fiscal Year",
        })
        logging.debug(f"AUCT dataframe with fields renamed:\n{df}")

        df['usage_is_being_collected'] = None
        df['manual_collection_required'] = None
        df['collection_via_email'] = None
        df['is_COUNTER_compliant'] = None
        df['collection_status'] = None
        df['usage_file_path'] = None
        df['notes'] = None
        logging.info(f"AUCT template dataframe:\n{df}")

        template_save_location = Path(os.path.dirname(os.path.realpath(__file__)), 'initialize_annualUsageCollectionTracking.csv')
        df.to_csv(
            template_save_location,
            index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
            encoding='utf-8',
            errors='backslashreplace',  # For encoding errors
        )
        logging.debug(f"The AUCT template CSV was created successfully: {os.path.isfile(template_save_location)}")
        #ToDo: Confirm above downloads successfully
        return render_template('initialization/initial-data-upload-3.html', form=form)

    #Section: After Form Submission
    elif form.validate_on_submit():
        #ToDo: remove file at `template_save_location`?
        #Subsection: Load `annualUsageCollectionTracking` into Database
        AUCT_dataframe = pd.read_csv(
            form.annualUsageCollectionTracking_CSV.data,
            index_col=['AUCT_statistics_source', 'AUCT_fiscal_year'],
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        if AUCT_dataframe.isnull().all(axis=None) == True:
            logging.error("The `annualUsageCollectionTracking` relation data file was read in with no data.")
            return render_template('initialization/empty-dataframes-warning.html', relation="`annualUsageCollectionTracking`")
        
        AUCT_dataframe = AUCT_dataframe.astype({k: v for (k, v) in AnnualUsageCollectionTracking.state_data_types().items()})
        logging.info(f"`annualUsageCollectionTracking` dataframe dtypes before encoding conversions:\n{AUCT_dataframe.dtypes}\n")
        AUCT_dataframe['usage_file_path'] = AUCT_dataframe['usage_file_path'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        AUCT_dataframe['notes'] = AUCT_dataframe['notes'].apply(lambda value: value if pd.isnull(value) == True else value.encode('utf-8').decode('unicode-escape'))
        logging.info(f"`annualUsageCollectionTracking` dataframe:\n{AUCT_dataframe}\n")

        AUCT_dataframe.to_sql(
            'annualUsageCollectionTracking',
            con=db.engine,
            if_exists='append',
            index_label=['AUCT_statistics_source', 'AUCT_fiscal_year'],
        )
        logging.debug("Relation `annualUsageCollectionTracking` loaded into the database")

        #Subsection: Load COUNTER Reports into Database
        #ToDo: Uncomment this subsection during Planned Iteration 2
        # COUNTER_reports_df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()
        #ToDo: Does there need to be a warning here about if the above method returns no data?
        # COUNTER_reports_df['report_creation_date'] = pd.to_datetime(None)
        # COUNTER_reports_df.index += first_new_PK_value('COUNTERData')
        # COUNTER_reports_df.to_sql(
        #     'COUNTERData',
        #     con=db.engine,
        #     if_exists='append',
        #     index_label='COUNTER_data_ID',
        # )
        # logging.debug("Relation `COUNTERData` loaded into the database")
        logging.info("All relations loaded into the database")

        # return redirect(url_for('initialization.upload_historical_non_COUNTER_usage'))  #ToDo: Replace below during Planned Iteration 3
        return redirect(url_for('initialization.data_load_complete'))

    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/initialization-page-4', methods=['GET', 'POST'])
def upload_historical_non_COUNTER_usage():
    """This route function allows the user to upload files containing non-COUNTER usage reports to the container hosting this program, placing the file paths within the COUNTER usage statistics database for easy retrieval in the future.
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    
    The route function renders the page showing <what the page shows>. When the <describe form> is submitted, the function saves the data by <how the data is processed and saved>, then redirects to the `<route function name>` route function.
    """
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
        return redirect(url_for('blueprint.name of the route function for the page that user should go to once form is submitted'))
    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)
    '''
    pass


@bp.route('/initialization-page-5', methods=['GET', 'POST'])
def data_load_complete():
    """This route function indicates the successful completion of the wizard and initialization of the database."""
    return render_template('initialization/show-loaded-data.html')