import logging
import datetime
import calendar
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
from flask import flash
import pandas as pd

from . import bp
from .forms import *
from ..app import db
from ..app import first_new_PK_value
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
    form = COUNTERReportsForm()
    if request.method == 'GET':
        return render_template('ingest_usage/upload-COUNTER-reports.html', form=form)
    elif form.validate_on_submit():
        try:
            log.info(f"In the view function, `form.COUNTER_reports` is {form.COUNTER_reports} (type {repr(type(form.COUNTER_reports))})")
            log.info(f"In the view function, `form.COUNTER_reports.data` is {form.COUNTER_reports.data} (type {repr(type(form.COUNTER_reports.data))})")
            log.info(f"In the view function, `form.COUNTER_reports.__dict__` is {form.COUNTER_reports.__dict__}")
            df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()
            df['report_creation_date'] = pd.to_datetime(None)
            df.index += first_new_PK_value('COUNTERData')
            df.to_sql(
                'COUNTERData',
                con=db.engine,
                if_exists='append',
                index_label='COUNTER_data_ID',
            )
            flash("Successfully loaded the data from the tabular COUNTER reports into the `COUNTERData` relation")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            log.error(f"Loading the data from the tabular COUNTER reports into the `COUNTERData` relation failed due to the following error: {error}")  #TEST: `test_bp_ingest_usage.test_upload_COUNTER_reports()` raises `'list' object has no attribute 'name'`
            flash(f"Loading the data from the tabular COUNTER reports into the `COUNTERData` relation failed due to the following error: {error}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/harvest', methods=['GET', 'POST'])
def harvest_SUSHI_statistics():
    """A page for initiating R5 SUSHI usage statistics harvesting.
    
    This page lets the user input custom parameters for an R5 SUSHI call, then executes the `StatisticsSources.collect_usage_statistics()` method. From this page, SUSHI calls for specific statistics sources with date ranges other than the fiscal year can be performed. 
    """
    form = SUSHIParametersForm()
    if request.method == 'GET':
        statistics_source_options = pd.read_sql(
            sql="SELECT statistics_source_ID, statistics_source_name FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
            con=db.engine,
        )
        form.statistics_source.choices = list(statistics_source_options.itertuples(index=False, name=None))
        return render_template('ingest_usage/make-SUSHI-call.html', form=form)
    elif form.validate_on_submit():
        try:
            df = pd.read_sql(
                sql=f"SELECT * FROM statisticsSources WHERE statistics_source_ID = {form.statistics_source.data};",
                con=db.engine,
            )
        except Exception as error:
            log.error(f"The query for the statistics source record failed due to the following error: {error}")
            flash(f"The query for the statistics source record failed due to the following error: {error}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        
        stats_source = StatisticsSources(  # Even with one value, the field of a single-record dataframe is still considered a series, making type juggling necessary
            statistics_source_ID = int(df['statistics_source_ID'][0]),
            statistics_source_name = str(df['statistics_source_name'][0]),
            statistics_source_retrieval_code = str(df['statistics_source_retrieval_code'][0]).split(".")[0],  #String created is of a float (aka `n.0`), so the decimal and everything after it need to be removed
            vendor_ID = int(df['vendor_ID'][0]),
        )  # Without the `int` constructors, a numpy int type is used

        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            flash(f"The entered date range is invalid: the end date ({end_date}) is before the begin date ({begin_date}).")
            return redirect(url_for('ingest_usage.harvest_SUSHI_statistics'))
        end_date = datetime.date(
            end_date.year,
            end_date.month,
            calendar.monthrange(end_date.year, end_date.month)[1],
        )

        log.info(f"Preparing to make SUSHI call to statistics source {stats_source} for the date range {begin_date} to {end_date}.")
        try:
            result_message = stats_source.collect_usage_statistics(form.begin_date.data, form.end_date.data)
            log.info(result_message)
            flash(result_message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            log.error(f"The SUSHI request form submission failed due to the following error: {error}")
            flash(f"The SUSHI request form submission failed due to the following error: {error}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/upload-non-COUNTER', methods=['GET', 'POST'])
def upload_non_COUNTER_reports():
    """The route function for uploading files containing non-COUNTER data into the container."""
    form = UsageFileForm()
    if request.method == 'GET':
        SQL_query = f'''
            SELECT
                annualUsageCollectionTracking.AUCT_statistics_source,
                annualUsageCollectionTracking.AUCT_fiscal_year,
                statisticsSources.statistics_source_name,
                fiscalYears.fiscal_year,
                annualUsageCollectionTracking.notes
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
        '''
        non_COUNTER_files_needed = pd.read_sql(
            sql=SQL_query,
            con=db.engine,
        )
        non_COUNTER_files_needed['index'] =  list(non_COUNTER_files_needed[['AUCT_statistics_source', 'AUCT_fiscal_year']].itertuples(index=False, name=None))
        non_COUNTER_files_needed['AUCT_option'] = non_COUNTER_files_needed['statistics_source_name'] + " " + non_COUNTER_files_needed['fiscal_year']
        log.debug(f"Form choices and their corresponding AUCT multiindex values:\n{non_COUNTER_files_needed[['AUCT_option', 'index']]}")
        form.AUCT_option.choices = list(non_COUNTER_files_needed[['index', 'AUCT_option']].itertuples(index=False, name=None))
        return render_template('ingest_usage/upload-non-COUNTER-usage.html', form=form)
    elif form.validate_on_submit():
        try:
            #ToDo: file_path_of_record = Path(file path to folder where non-COUNTER usage files will be saved)
            #ToDo: Uploaded files must be of extension types
                # "xlsx"
                # "csv"
                # "tsv"
                # "pdf"
                # "docx"
                # "pptx"
                # "txt"
                # "jpeg"
                # "jpg"
                # "png"
                # "svg"
                # "json"
                # "html"
                # "htm"
                # "xml"
                # "zip"
            #ToDo: record_matching_uploaded_file = non_COUNTER_files_needed.loc[form.AUCT_options.data]
            #ToDo: int_PK_for_stats_source = record_matching_uploaded_file['AUCT_statistics_source']
            #ToDo: int_PK_for_fiscal_year = record_matching_uploaded_file['AUCT_fiscal_year']
            #ToDo: SQL_query = f'''
            #ToDo:     UPDATE annualUsageCollectionTracking
            #ToDo:     SET usage_file_path = {file_path_of_record}
            #ToDo:     WHERE AUCT_statistics_source = {int_PK_for_stats_source} AND AUCT_fiscal_year = {int_PK_for_fiscal_year};
            #ToDo: '''
            #ToDo: Run SQL query
            #ToDo: flash(f"Usage file for {record_matching_uploaded_file['statistics_source_name']} during FY {record_matching_uploaded_file['fiscal_year']} uploaded successfully")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))  #ToDo: Add message flashing about successful upload
        except Exception as error:
            log.error(f"The file upload failed due to the following error: {error}")
            flash(f"The file upload failed due to the following error: {error}")
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.warning(f"`form.errors`: {form.errors}")
        return abort(404)