import logging
from datetime import date
import calendar
from ast import literal_eval
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
from flask import flash
import pandas as pd

from . import bp
from .forms import *
from ..app import *
from ..models import *
from ..upload_COUNTER_reports import UploadCOUNTERReports

log = logging.getLogger(__name__)


@bp.route('/')
def ingest_usage_homepage():
    """Returns the homepage for the `ingest_usage` blueprint, which has links to the different usage upload options."""
    return render_template('ingest_usage/index.html')


@bp.route('/upload-COUNTER', methods=['GET', 'POST'])
def upload_COUNTER_reports():
    """The route function for uploading tabular COUNTER reports into the `COUNTERData` relation."""
    log.info("Starting `upload_COUNTER_reports()`.")
    form = COUNTERReportsForm()
    if request.method == 'GET':
        return render_template('ingest_usage/upload-COUNTER-reports.html', form=form)
    elif form.validate_on_submit():
        try:
            df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()  # `form.COUNTER_reports.data` is a list of <class 'werkzeug.datastructures.FileStorage'> objects
            df['report_creation_date'] = pd.to_datetime(None)
        except Exception as error:
            message = f"Trying to consolidate the uploaded COUNTER data workbooks into a single dataframe raised the error {error}."
            log.error(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        
        try:
            df, message = check_if_data_already_in_COUNTERData(df)
        except Exception as error:
            message = f"The uploaded data wasn't added to the database because the check for possible duplication raised {error}."
            log.error(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        
        df.index += first_new_PK_value('COUNTERData')
        load_result = load_data_into_database(
            df=df,
            relation='COUNTERData',
            engine=db.engine,
            index_field_name='COUNTER_data_ID',
        )
        flash(load_result)
        return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)


@bp.route('/harvest', methods=['GET', 'POST'])
def harvest_SUSHI_statistics():
    """A page for initiating R5 SUSHI usage statistics harvesting.
    
    This page lets the user input custom parameters for an R5 SUSHI call, then executes the `StatisticsSources.collect_usage_statistics()` method. From this page, SUSHI calls for specific statistics sources with date ranges other than the fiscal year can be performed. 
    """
    log.info("Starting `harvest_SUSHI_statistics()`.")
    form = SUSHIParametersForm()
    if request.method == 'GET':
        statistics_source_options = query_database(
            query="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
            engine=db.engine,
        )
        if isinstance(statistics_source_options, str):
            flash(f"Unable to load requested page because it relied on t{statistics_source_options[1:].replace(' raised', ', which raised')}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        form.statistics_source.choices = list(statistics_source_options.itertuples(index=False, name=None))
        return render_template('ingest_usage/make-SUSHI-call.html', form=form)
    elif form.validate_on_submit():
        df = query_database(
            query=f"SELECT * FROM statisticsSources WHERE statistics_source_ID = {form.statistics_source.data};",
            engine=db.engine,
        )
        if isinstance(df, str):
            flash(f"Unable to load requested page because it relied on t{df[1:].replace(' raised', ', which raised')}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        
        stats_source = StatisticsSources(  # Even with one value, the field of a single-record dataframe is still considered a series, making type juggling necessary
            statistics_source_ID = int(df['statistics_source_ID'][0]),
            statistics_source_name = str(df['statistics_source_name'][0]),
            statistics_source_retrieval_code = str(df['statistics_source_retrieval_code'][0]).split(".")[0],  #String created is of a float (aka `n.0`), so the decimal and everything after it need to be removed
            vendor_ID = int(df['vendor_ID'][0]),
        )  # Without the `int` constructors, a numpy int type is used
        log.info(f"The following `StatisticsSources` object was initialized based on the query results:\n{statistics_source}.")

        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if form.report_to_harvest.data == 'null':  # All possible responses returned by a select field must be the same data type, so `None` can't be returned
            report_to_harvest = None
            log.debug(f"Preparing to make SUSHI call to statistics source {stats_source} for the date range {begin_date} to {end_date}.")  #AboutTo
        else:
            report_to_harvest = form.report_to_harvest.data
            log.debug(f"Preparing to make SUSHI call to statistics source {stats_source} for the {report_to_harvest} the date range {begin_date} to {end_date}.")  #AboutTo
        
        try:
            result_message, flash_messages = stats_source.collect_usage_statistics(begin_date, end_date, report_to_harvest)
            log.info(result_message)
            flash(flash_messages)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            message = f"The SUSHI call raised {error}."
            log.warning(message)  #TEST: The SUSHI request form submission failed due to the error 'NoneType' object has no attribute 'get'.
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)


@bp.route('/upload-non-COUNTER', methods=['GET', 'POST'])
def upload_non_COUNTER_reports():
    """The route function for uploading files containing non-COUNTER data into the container."""
    log.info("Starting `upload_non_COUNTER_reports()`.")
    form = UsageFileForm()
    if request.method == 'GET':
        non_COUNTER_files_needed = query_database(
            query=f"""
                SELECT
                    annualUsageCollectionTracking.AUCT_statistics_source,
                    annualUsageCollectionTracking.AUCT_fiscal_year,
                    statisticsSources.statistics_source_name,
                    fiscalYears.fiscal_year
                FROM annualUsageCollectionTracking
                JOIN statisticsSources ON statisticsSources.statistics_source_ID = annualUsageCollectionTracking.AUCT_statistics_source
                JOIN fiscalYears ON fiscalYears.fiscal_year_ID = annualUsageCollectionTracking.AUCT_fiscal_year
                WHERE
                    annualUsageCollectionTracking.usage_is_being_collected = true AND
                    annualUsageCollectionTracking.is_COUNTER_compliant = false AND
                    annualUsageCollectionTracking.usage_file_path IS NULL AND
                    (
                        annualUsageCollectionTracking.collection_status = 'Collection not started' OR
                        annualUsageCollectionTracking.collection_status = 'Collection in process (see notes)' OR
                        annualUsageCollectionTracking.collection_status = 'Collection issues requiring resolution'
                    );
            """,
            engine=db.engine,
        )
        if isinstance(non_COUNTER_files_needed, str):
            flash(f"Unable to load requested page because it relied on t{non_COUNTER_files_needed[1:].replace(' raised', ', which raised')}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        form.AUCT_option.choices = create_AUCT_SelectField_options(non_COUNTER_files_needed)
        return render_template('ingest_usage/upload-non-COUNTER-usage.html', form=form)
    elif form.validate_on_submit():
        try:
            valid_file_extensions = (  # File types allowed are limited to those that can be downloaded in `nolcat.view_usage.views.download_non_COUNTER_usage()`
                "xlsx",
                "csv",
                "tsv",
                "pdf",
                "docx",
                "pptx",
                "txt",
                "jpeg",
                "jpg",
                "png",
                "svg",
                "json",
                "html",
                "htm",
                "xml",
                "zip",
            )
            statistics_source_ID, fiscal_year_ID = literal_eval(form.AUCT_options.data) # Since `AUCT_option_choices` had a multiindex, the select field using it returns a tuple
            file_extension = Path(form.usage_file.data.filename).suffix
            if file_extension not in valid_file_extensions:
                message = f"The file type of `{form.usage_file.data.filename}` is invalid. Please convert the file to one of the following file types and try again:\n{valid_file_extensions}"  #FileIOError
                log.error(message)
                flash(message)
                return redirect(url_for('ingest_usage.ingest_usage_homepage'))
            file_name = f"{statistics_source_ID}_{fiscal_year_ID}.{file_extension}"
            log.debug(f"The non-COUNTER usage file will be named `{file_name}`.")  #FileIO
            
            logging_message = upload_file_to_S3_bucket(
                form.usage_file.data,
                file_name,
            )
            if re.fullmatch(r'The file `.*` has been successfully uploaded to the `.*` S3 bucket\.') is None:  # Meaning `upload_file_to_S3_bucket()` returned an error message
                message = f"As a result, the usage file for {non_COUNTER_files_needed.loc[form.AUCT_options.data]} hasn't been saved."  #FileIOError
                log.error(message)
                flash(logging_message + " " + message)
                return redirect(url_for('ingest_usage.ingest_usage_homepage'))

            # Use https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.Engine.execute for database update and delete operations
            # update_query = query_database(
            #    query=f"""
            #        UPDATE annualUsageCollectionTracking
            #        SET usage_file_path = '{file_name}'
            #        WHERE AUCT_statistics_source = {statistics_source_ID} AND AUCT_fiscal_year = {fiscal_year_ID};
            #    """,
            #    con=db.engine,
            #)
            message = f"Usage file for {non_COUNTER_files_needed.loc[form.AUCT_options.data]} uploaded successfully."  #ReplaceWithUpdateFunction
            log.debug(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            message = f"The file upload failed due to the error {error}."  #ReplaceWithUpdateFunction
            log.error(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)