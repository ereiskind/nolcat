import logging
from datetime import date
import calendar
from itertools import product
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
    form = COUNTERReportsForm()
    if request.method == 'GET':
        return render_template('ingest_usage/upload-COUNTER-reports.html', form=form)
    elif form.validate_on_submit():
        try:
            df = UploadCOUNTERReports(form.COUNTER_reports.data).create_dataframe()  # `form.COUNTER_reports.data` is a list of <class 'werkzeug.datastructures.FileStorage'> objects
            df['report_creation_date'] = pd.to_datetime(None)
            try:
                # `uniques()` method returns a numpy array, so numpy's `tolist()` method is used
                log.debug(f"`df['statistics_source_ID']`: {df['statistics_source_ID']} (type {type(df['statistics_source_ID'])}).")
                log.debug(f"`df['statistics_source_ID'].unique()`: {df['statistics_source_ID'].unique()} (type {type(df['statistics_source_ID'].unique())}).")
                statistics_sources_in_dataframe = df['statistics_source_ID'].unique().tolist()
                log.debug(f"`df['report_type']`: {df['report_type']} (type {type(df['report_type'])}).")
                log.debug(f"`df['report_type'].unique()`: {df['report_type'].unique()} (type {type(df['report_type'].unique())}).")
                report_types_in_dataframe = df['report_type'].unique().tolist()
                log.debug(f"`df['usage_date']`: {df['usage_date']} (type {type(df['usage_date'])}).")
                log.debug(f"`df['usage_date'].unique()`: {df['usage_date'].unique()} (type {type(df['usage_date'].unique())}).")
                dates_in_dataframe = df['usage_date'].unique().tolist()
                combinations_to_check = tuple(product(statistics_sources_in_dataframe, report_types_in_dataframe, dates_in_dataframe))
                log.info(f"Checking the database for the existence of records with the following statistics source ID, report, and date combinations: {combinations_to_check}")
                total_number_of_matching_records = 0
                matching_record_instances = []
                for combo in combinations_to_check:
                    number_of_matching_records = pd.read_sql(
                        sql=f"SELECT COUNT(*) FROM COUNTERData WHERE statistics_source_ID={combo[0]} AND report_type={combo[1]} AND usage_date={combo[2].strftime('%Y-%m-%d')};",
                        con=db.engine,
                    )
                    number_of_matching_records = number_of_matching_records.iloc[0][0]
                    log.debug(f"The {combo} combination matched {number_of_matching_records} records in the database.")
                    if number_of_matching_records > 0:
                        matching_record_instances.append({
                            'statistics_source_ID': combo[0],
                            'report_type': combo[1],
                            'date': combo[2],
                        })
                        log.debug(f"The combination {matching_record_instances[-1]} was added to `matching_record_instances`.")
                        total_number_of_matching_records = total_number_of_matching_records + number_of_matching_records
                if total_number_of_matching_records > 0:
                    for instance in matching_record_instances:
                        statistics_source_name = pd.read_sql(
                            sql=f"SELECT statistics_source_name FROM statisticsSources WHERE statistics_source_ID={instance['statistics_source_ID']};",
                            con=db.engine,
                        )
                        instance['statistics_source_name'] = statistics_source_name.iloc[0][0]
                    message = f"Usage statistics for the statistics source, report, and date combination(s) below, which were included in the upload, are already in the database. Please try the upload again without that data. If the data needs to be re-uploaded, please remove the existing data from the database first.\n{matching_record_instances}"
                    log.error(message)
                    flash(message)
                    return redirect(url_for('ingest_usage.ingest_usage_homepage'))
            except Exception as error:
                message = f"The uploaded data wasn't added to the database because the check for possible duplication raised {error}."
                log.error(message)
                flash(message)
                return redirect(url_for('ingest_usage.ingest_usage_homepage'))
            df.index += first_new_PK_value('COUNTERData')
            df.to_sql(
                'COUNTERData',
                con=db.engine,
                if_exists='append',
                index_label='COUNTER_data_ID',
            )
            message = "Successfully loaded the data from the tabular COUNTER reports into the `COUNTERData` relation."
            log.info(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            message = f"Loading the data from the tabular COUNTER reports into the `COUNTERData` relation failed due to the error {error}."
            log.error(message)  #TEST: 2023-08-08 - Loading the data from the tabular COUNTER reports into the `COUNTERData` relation failed due to the error type object 'datetime.datetime' has no attribute 'datetime'.
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.error(f"`form.errors`: {form.errors}")
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
            message = f"The query for the statistics source record failed due to the error {error}."
            log.error(message)
            flash(message)
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
            message = f"The entered date range is invalid: the end date ({end_date}) is before the begin date ({begin_date})."
            log.warning(message)
            flash(message)
            return redirect(url_for('ingest_usage.harvest_SUSHI_statistics'))
        log.info(f"`end_date.year` is {end_date.year} (type {type(end_date.year)}")
        log.info(f"`end_date.month` is {end_date.month} (type {type(end_date.month)}")
        log.info(f"`calendar.monthrange(end_date.year, end_date.month)[1]` is {calendar.monthrange(end_date.year, end_date.month)[1]} (type {type(calendar.monthrange(end_date.year, end_date.month)[1])}")
        end_date = date(  #TEST: 2023-08-10 - TypeError: descriptor 'date' for 'datetime.datetime' objects doesn't apply to a 'int' object
            end_date.year,
            end_date.month,
            calendar.monthrange(end_date.year, end_date.month)[1],
        )

        if form.report_to_harvest.data == 'null':  # All possible responses returned by a select field must be the same data type, so `None` can't be returned
            report_to_harvest = None
            log.debug(f"Preparing to make SUSHI call to statistics source {stats_source} for the date range {begin_date} to {end_date}.")
        else:
            report_to_harvest = form.report_to_harvest.data
            log.debug(f"Preparing to make SUSHI call to statistics source {stats_source} for the {report_to_harvest} the date range {begin_date} to {end_date}.")
        
        try:
            result_message = stats_source.collect_usage_statistics(begin_date, end_date, report_to_harvest)
            log.info(result_message)
            flash(result_message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            message = f"The SUSHI request form submission failed due to the error {error}."
            log.warning(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.error(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/upload-non-COUNTER', methods=['GET', 'POST'])
def upload_non_COUNTER_reports():
    """The route function for uploading files containing non-COUNTER data into the container."""
    form = UsageFileForm()
    if request.method == 'GET':
        non_COUNTER_files_needed = pd.read_sql(
            sql=f"""
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
            con=db.engine,
        )
        form.AUCT_option.choices = create_AUCT_ChoiceField_options(non_COUNTER_files_needed)
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
                message = f"The file type of `{form.usage_file.data.filename}` is invalid. Please convert the file to one of the following file types and try again:\n{valid_file_extensions}"
                log.error(message)
                flash(message)
                return redirect(url_for('ingest_usage.ingest_usage_homepage'))
            file_name = f"{statistics_source_ID}_{fiscal_year_ID}.{file_extension}"
            log.debug(f"The non-COUNTER usage file will be named `{file_name}`.")
            
            logging_message = upload_file_to_S3_bucket(
                form.usage_file.data,
                file_name,
            )
            if re.fullmatch(r'The file `.*` has been successfully uploaded to the `.*` S3 bucket\.') is None:  # Meaning `upload_file_to_S3_bucket()` returned an error message
                message = f"As a result, the usage file for {non_COUNTER_files_needed.loc[form.AUCT_options.data]} hasn't been saved."
                log.error(message)
                flash(f"{logging_message} {message}")
                return redirect(url_for('ingest_usage.ingest_usage_homepage'))

            update_query = pd.read_sql(  #ToDo: Can an UPDATE query be run like this?
                sql=f'''
                    UPDATE annualUsageCollectionTracking
                    SET usage_file_path = {file_name}
                    WHERE AUCT_statistics_source = {statistics_source_ID} AND AUCT_fiscal_year = {fiscal_year_ID};
                ''',
                con=db.engine,  # In pytest tests started at the command line, calls to `db.engine` raise `RuntimeError: No application found. Either work inside a view function or push an application context. See http://flask-sqlalchemy.pocoo.org/contexts/.`
            )
            message = f"Usage file for {non_COUNTER_files_needed.loc[form.AUCT_options.data]} uploaded successfully."
            log.debug(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
        except Exception as error:
            message = f"The file upload failed due to the error {error}."
            log.error(message)
            flash(message)
            return redirect(url_for('ingest_usage.ingest_usage_homepage'))
    else:
        log.error(f"`form.errors`: {form.errors}")
        return abort(404)