import logging
import datetime
import calendar
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
import pandas as pd

from . import bp
from ..app import db
from .forms import COUNTERReportsForm, SUSHIParametersForm, UsageFileForm
from ..models import StatisticsSources


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')
def ingest_usage_homepage():
    """Returns the homepage for the `ingest_usage` blueprint, which has links to the different usage upload options."""
    return render_template('ingest_usage/index.html')


@bp.route('/upload-COUNTER', methods=['GET', 'POST'])
def upload_COUNTER_reports():
    """The route function for uploading tabular COUNTER reports into the `COUNTERData` relation."""
    form = COUNTERReportsForm()
    if request.method == 'GET':
        #ToDo: return render_template('upload-COUNTER-reports.html', form=form)
        pass
    elif form.validate_on_submit():
        #ToDo: df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()
        #ToDo: df['report_creation_date'] = pd.to_datetime(None)
        #ToDo: df.index += first_new_PK_value('COUNTERData')
        #ToDo: df.to_sql(
        #     'COUNTERData',
        #     con=db.engine,
        #     if_exists='append',
        # )
        return redirect(url_for('ingest_usage_homepage'))  #ToDo: Add message flashing about successful upload
    else:
        return abort(404)


@bp.route('/harvest', methods=['GET', 'POST'])
def harvest_SUSHI_statistics():
    """A page for initiating R5 SUSHI usage statistics harvesting.
    
    This page lets the user input custom parameters for an R5 SUSHI call, then executes the `StatisticsSources.collect_usage_statistics()` method. From this page, SUSHI calls for specific statistics sources with date ranges other than the fiscal year can be performed. 
    """
    form = SUSHIParametersForm()
    if request.method == 'GET':
        statistics_source_options = pd.read_sql(
            sql="SELECT * FROM statisticsSources WHERE statistics_source_retrieval_code IS NOT NULL;",
            con=db.engine,
        )
        form.statistics_source.choices = list(statistics_source_options[['statistics_source_ID', 'statistics_source_name']].itertuples(index=False, name=None))
        return render_template('ingest_usage/make-SUSHI-call.html', form=form)
    elif form.validate_on_submit():
        df = pd.read_sql(
            sql=f"SELECT * FROM statisticsSources WHERE statistics_source_ID = {form.statistics_source.data};",
            con=db.engine,
        )
        stats_source = StatisticsSources(
            statistics_source_ID = df['statistics_source_ID'],
            statistics_source_name = df['statistics_source_name'],
            statistics_source_retrieval_code = df['statistics_source_retrieval_code'],
            vendor_ID = df['vendor_ID'],
        )

        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            return redirect(url_for('harvest_SUSHI_statistics'))  #ToDo: Add message flashing that the end date was before the begin date
        end_date = datetime.date(
            end_date.year,
            end_date.month,
            calendar.monthrange(end_date.year, end_date.month)[1],
        )
        logging.info(f"Preparing to make to SUSHI call to statistics source {stats_source} for the date range {begin_date} to {end_date}.")

        result_message = stats_source.collect_usage_statistics(form.begin_date.data, form.end_date.data)
        logging.info(result_message)
        return redirect(url_for('ingest_usage_homepage'))  #ToDo: Flash `result_message` with message flashing
    else:
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
        logging.info(f"Initial load:\n{non_COUNTER_files_needed}\n{non_COUNTER_files_needed.info()}")
        non_COUNTER_files_needed['index'] =  list(non_COUNTER_files_needed[['AUCT_statistics_source', 'AUCT_fiscal_year']].itertuples(index=False, name=None))
        logging.info(f"After `index` creation:\n{non_COUNTER_files_needed}")
        non_COUNTER_files_needed['AUCT_option'] = non_COUNTER_files_needed['fiscal_year'].apply(lambda value: value.dtype('string'))
        logging.info(f"After `AUCT_option` field creation:\n{non_COUNTER_files_needed}\n{non_COUNTER_files_needed.info()}")
        non_COUNTER_files_needed['AUCT_option'] = non_COUNTER_files_needed['statistics_source_name'] + " " + non_COUNTER_files_needed['AUCT_option']
        logging.info(f"After string concatenation in `AUCT_option`:\n{non_COUNTER_files_needed}")
        form.AUCT_option.choices = list(non_COUNTER_files_needed[['index', 'AUCT_option']].itertuples(index=False, name=None))
        return render_template('ingest_usage/upload-non-COUNTER-usage.html', form=form)
    elif form.validate_on_submit():
        #ToDo: Save uploaded file to location `file_path_of_record` in container
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
        #ToDo: series_data_type = non_COUNTER_files_needed.loc[form.AUCT_options.data]
        #ToDo: series_data_type['annualUsageCollectionTracking.AUCT_statistics_source'] = int_PK_for_stats_source
        #ToDo: series_data_type['annualUsageCollectionTracking.AUCT_fiscal_year'] = int_PK_for_fiscal_year
        #ToDo: SQL_query = f'''
        #ToDo:     UPDATE annualUsageCollectionTracking
        #ToDo:     SET usage_file_path = {file_path_of_record}
        #ToDo:     WHERE AUCT_statistics_source = {int_PK_for_stats_source} AND AUCT_fiscal_year = {int_PK_for_fiscal_year};
        #ToDo: '''
        return redirect(url_for('ingest_usage_homepage'))  #ToDo: Add message flashing about successful upload
    else:
        return abort(404)