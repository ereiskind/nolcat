import logging
from datetime import date
import calendar
from pathlib import Path
import re
from ast import literal_eval
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import abort
from flask import flash
import pandas as pd

from . import bp
from .forms import *
from ..app import *
from ..models import *
from ..statements import *

log = logging.getLogger(__name__)


@bp.route('/')
def view_usage_homepage():
    """Returns the homepage for the `view_usage` blueprint, which links to the usage query methods."""
    return render_template('view_usage/index.html')


@bp.route('/custom-SQL', methods=['GET', 'POST'])
def run_custom_SQL_query():
    """Returns a page that accepts a SQL query from the user and runs it against the database."""
    log.info("Starting `run_custom_SQL_query()`.")
    form = CustomSQLQueryForm()
    if request.method == 'GET':
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        log.debug(f"Before `unlink()`," + check_if_file_exists_statement(file_path, False))
        file_path.unlink(missing_ok=True)
        log.info(check_if_file_exists_statement(file_path))
        return render_template('view_usage/write-SQL-queries.html', form=form)
    elif form.validate_on_submit():
        df = query_database(
            query=form.SQL_query.data,  #ToDo: Figure out how to make this safe from SQL injection
            engine=db.engine,
        )
        if isinstance(df, str):
            flash(database_query_fail_statement(df))
            return redirect(url_for('view_usage.view_usage_homepage'))
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"The `NoLCAT_download.csv` file was created successfully: {file_path.is_file()}")
        log.debug(f"Contents of `{Path(__file__).parent}`:\n{format_list_for_stdout(Path(__file__).parent.iterdir())}")
        return redirect(url_for('download_file', file_path=str(file_path)))  #TEST: `ValueError: I/O operation on closed file.` raised on `client.post` in `test_run_custom_SQL_query()`, but above logging statement is output with value True; opening logging statement for `download_file()` route function isn't output at all
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard', methods=['GET', 'POST'])
def use_predefined_SQL_query():
    """Returns a page that offers pre-constructed queries and a query construction wizard."""
    log.info("Starting `use_predefined_SQL_query()`.")
    form = QueryWizardForm()
    if request.method == 'GET':
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        log.debug(f"Before `unlink()`," + check_if_file_exists_statement(file_path, False))
        file_path.unlink(missing_ok=True)
        log.info(check_if_file_exists_statement(file_path))
        return render_template('view_usage/query-wizard.html', form=form)
    elif form.validate_on_submit():
        log.info(f"Querying NoLCAT for a {form.query_options.data} standard report with the begin date {form.begin_date.data} and the end date {form.end_date.data}.")
        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            message = attempted_SUSHI_call_with_invalid_dates_statement(end_date, begin_date)
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.use_predefined_SQL_query'))
        end_date = date(
            end_date.year,
            end_date.month,
            calendar.monthrange(end_date.year, end_date.month)[1],
        )
        log.debug(f"The date range for the request is {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
        
        if form.query_options.data == "PR_P1":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='PR' AND access_method='Regular'
                AND (metric_type='Searches_Platform' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Requests');
            """
        elif form.query_options.data == "DR_D1":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='DR' AND access_method='Regular'
                AND (metric_type='Searches_Automated' OR metric_type='Searches_Federated' OR metric_type='Searches_Regular' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests');
            """
        elif form.query_options.data == "DR_D2":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='DR' AND access_method='Regular'
                AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
            """
        elif form.query_options.data == "TR_B1":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            """
        elif form.query_options.data == "TR_B2":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Book' AND access_method='Regular'
                AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
            """
        elif form.query_options.data == "TR_B3":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Book' AND access_method='Regular'
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests');
            """
        elif form.query_options.data == "TR_J1":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            """
        elif form.query_options.data == "TR_J2":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_method='Regular'
                AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
            """
        elif form.query_options.data == "TR_J3":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_method='Regular'
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' Or metric_type='Unique_Item_Investigations' Or metric_type='Unique_Item_Requests');
            """
        elif form.query_options.data == "TR_J4":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            """
        elif form.query_options.data == "IR_A1":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='IR' AND data_type='Article' AND access_method='Regular' AND parent_data_type='Journal'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            """
        elif form.query_options.data == "IR_M1":
            query = f"""
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='IR' AND data_type='Multimedia' AND access_method='Regular'
                AND metric_type='Total_Item_Requests';
            """
        #ToDo: Decide what other canned reports, if any, are needed
        elif form.query_options.data == "w":
            #ToDo: Create queries that filter on metrics with fixed vocabularies via checkboxes
            #ToDo: Create queries where a sanitized (safe from SQL injection) free text field is fuzzily matched against a COUNTER free text field
            query = f"""
            """

        df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(df, str):
            flash(database_query_fail_statement(df))
            return redirect(url_for('view_usage.view_usage_homepage'))
        log.debug(f"The result of the query:\n{df}")
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"After writing the dataframe to download to a CSV," + check_if_file_exists_statement(file_path, False))
        log.debug(list_folder_contents_statement(Path(__file__).parent))
        return redirect(url_for('download_file', file_path=str(file_path)))  #TEST: `ValueError: I/O operation on closed file.` raised on `client.post` in `test_use_predefined_SQL_query_with_COUNTER_standard_views()`, but above logging statement is output with value True; opening logging statement for `download_file()` route function isn't output at all
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('non-COUNTER-downloads', methods=['GET', 'POST'])
def download_non_COUNTER_usage():
    """Returns a page that allows all non-COUNTER usage files uploaded to NoLCAT to be downloaded."""
    log.info("Starting `download_non_COUNTER_usage()`.")
    form = ChooseNonCOUNTERDownloadForm()
    if request.method == 'GET':
        file_name_format = re.compile(r"\d*_\d{4}\.\w{3,4}")
        log.debug("Before `unlink()`," + list_folder_contents_statement(Path(__file__).parent, False))
        for file in Path(__file__).parent.iterdir():
            if file_name_format.fullmatch(str(file.name)):
                file.unlink()
                log.debug(check_if_file_exists_statement(file))

        file_download_options = query_database(
            query=f"""
                SELECT
                    statisticsSources.statistics_source_name,
                    fiscalYears.fiscal_year,
                    annualUsageCollectionTracking.AUCT_statistics_source,
                    annualUsageCollectionTracking.AUCT_fiscal_year
                FROM annualUsageCollectionTracking
                JOIN statisticsSources ON statisticsSources.statistics_source_ID=annualUsageCollectionTracking.AUCT_statistics_source
                JOIN fiscalYears ON fiscalYears.fiscal_year_ID=annualUsageCollectionTracking.AUCT_fiscal_year
                WHERE annualUsageCollectionTracking.usage_file_path IS NOT NULL;
            """,
            engine=db.engine,
        )
        if isinstance(file_download_options, str):
            flash(database_query_fail_statement(file_download_options))
            return redirect(url_for('view_usage.view_usage_homepage'))
        form.AUCT_of_file_download.choices = create_AUCT_SelectField_options(file_download_options)
        return render_template('view_usage/download-non-COUNTER-usage.html', form=form)
    elif form.validate_on_submit():
        log.info(f"`dir(form.AUCT_of_file_download)`:\n{dir(form.AUCT_of_file_download)}")
        log.info(f"`vars(form.AUCT_of_file_download)`:\n{vars(form.AUCT_of_file_download)}")
        log.info(f"`dir(form.AUCT_of_file_download.data)`:\n{dir(form.AUCT_of_file_download.data)}")
        log.info(f"`vars(form.AUCT_of_file_download.data)`:\n{vars(form.AUCT_of_file_download.data)}")
        log.info(f"`form.AUCT_of_file_download.data` is {form.AUCT_of_file_download.data} (type {type(form.AUCT_of_file_download.data)}).")  #TEST: `form.AUCT_of_file_download.data` is <FileStorage: 'Ulrichsweb--FY 2021' ('application/octet-stream')> (type <class 'str'>).
        statistics_source_ID, fiscal_year_ID = literal_eval(form.AUCT_of_file_download.data)
        AUCT_object = pd.read_sql(
            sql=f"""
                SELECT
                    usage_is_being_collected,
                    manual_collection_required,
                    collection_via_email,
                    is_COUNTER_compliant,
                    collection_status,
                    usage_file_path,
                    notes
                FROM annualUsageCollectionTracking
                WHERE AUCT_statistics_source={statistics_source_ID} AND AUCT_fiscal_year={fiscal_year_ID};
            """,
            con=db.engine,
        )
        AUCT_object['usage_is_being_collected'] = restore_boolean_values_to_boolean_field(AUCT_object['usage_is_being_collected'])
        AUCT_object['manual_collection_required'] = restore_boolean_values_to_boolean_field(AUCT_object['manual_collection_required'])
        AUCT_object['collection_via_email'] = restore_boolean_values_to_boolean_field(AUCT_object['collection_via_email'])
        AUCT_object['is_COUNTER_compliant'] = restore_boolean_values_to_boolean_field(AUCT_object['is_COUNTER_compliant'])
        AUCT_object = AUCT_object.astype(AnnualUsageCollectionTracking.state_data_types())
        AUCT_object = AnnualUsageCollectionTracking(
            AUCT_statistics_source=statistics_source_ID,
            AUCT_fiscal_year=fiscal_year_ID,
            usage_is_being_collected=AUCT_object['usage_is_being_collected'][0],
            manual_collection_required=AUCT_object['manual_collection_required'][0],
            collection_via_email=AUCT_object['collection_via_email'][0],
            is_COUNTER_compliant=AUCT_object['is_COUNTER_compliant'][0],
            collection_status=AUCT_object['collection_status'][0],
            usage_file_path=AUCT_object['usage_file_path'][0],
            notes=AUCT_object['notes'][0],
        )
        log.info(f"`AnnualUsageCollectionTracking` object: {AUCT_object}")

        file_path = AUCT_object.download_nonstandard_usage_file(Path(__file__).parent)
        log.info(f"The `{file_path.name}` file was created successfully: {file_path.is_file()}")
        return redirect(url_for('download_file', file_path=str(file_path)))
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)