import logging
import datetime
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

log = logging.getLogger(__name__)


@bp.route('/')
def view_usage_homepage():
    """Returns the homepage for the `view_usage` blueprint, which links to the usage query methods."""
    return render_template('view_usage/index.html')


@bp.route('/custom-SQL', methods=['GET', 'POST'])
def run_custom_SQL_query():
    """Returns a page that accepts a SQL query from the user and runs it against the database."""
    form = CustomSQLQueryForm()
    if request.method == 'GET':
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        log.debug(f"Before `unlink()`, the `NoLCAT_download.csv` file exists: {file_path.is_file()}")
        file_path.unlink(missing_ok=True)
        log.info(f"The `NoLCAT_download.csv` file exists: {file_path.is_file()}")
        return render_template('view_usage/write-SQL-queries.html', form=form)
    elif form.validate_on_submit():
        #ToDo: Set up handling for invalid query
        df = pd.read_sql(
            sql=form.SQL_query.data,  #ToDo: Figure out how to make this safe from SQL injection
            con=db.engine,
        )
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"The `NoLCAT_download.csv` file was created successfully: {file_path.is_file()}")
        return redirect(url_for('download_file', file_path=str(file_path)))
    else:
        log.error(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('query-wizard', methods=['GET', 'POST'])
def use_predefined_SQL_query():
    """Returns a page that offers pre-constructed queries and a query construction wizard."""
    form = QueryWizardForm()
    if request.method == 'GET':
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        log.debug(f"Before `unlink()`, the `NoLCAT_download.csv` file exists: {file_path.is_file()}")
        file_path.unlink(missing_ok=True)
        log.info(f"The `NoLCAT_download.csv` file exists: {file_path.is_file()}")
        return render_template('view_usage/query-wizard.html', form=form)
    elif form.validate_on_submit():
        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            message = "The last day of the provided date range was before the beginning of the date range. Please correct the dates and try again."
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.use_predefined_SQL_query'))
        end_date = datetime.date(
            end_date.year,
            end_date.month,
            calendar.monthrange(end_date.year, end_date.month)[1],
        )
        
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

        df = pd.read_sql(
            sql=query,
            con=db.engine,
        )
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"The `NoLCAT_download.csv` file was created successfully: {file_path.is_file()}")
        return redirect(url_for('download_file', file_path=str(file_path)))
    else:
        log.error(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('non-COUNTER-downloads', methods=['GET', 'POST'])
def download_non_COUNTER_usage():
    """Returns a page that allows all non-COUNTER usage files uploaded to NoLCAT to be downloaded."""
    form = ChooseNonCOUNTERDownloadForm()
    if request.method == 'GET':
        file_name_format = re.compile(r'\d*_\d{4}\.\w{3,4}')
        log.debug(f"Before `unlink()`, `{str(Path(__file__).parent)}` contains the following files:\n{[file.name for file in Path(__file__).parent.iterdir()]}")
        for file in Path(__file__).parent.iterdir():
            if file_name_format.fullmatch(str(file.name)):
                file.unlink()
                log.info(f"The `{str(file.name)}` file exists: {file.is_file()}")

        file_download_options = pd.read_sql(
            sql=f"""
                SELECT
                    statisticsSources.statistics_source_name,
                    fiscalYears.fiscal_year,
                    annualUsageCollectionTracking.AUCT_statistics_source,
                    annualUsageCollectionTracking.AUCT_fiscal_year
                FROM annualUsageCollectionTracking
                JOIN statisticsSources ON statisticsSources.statistics_source_ID = annualUsageCollectionTracking.AUCT_statistics_source
                JOIN fiscalYears ON fiscalYears.fiscal_year_ID = annualUsageCollectionTracking.AUCT_fiscal_year
                WHERE annualUsageCollectionTracking.usage_file_path IS NOT NULL;
            """,
            con=db.engine,
        )
        form.AUCT_of_file_download.choices = create_AUCT_SelectField_options(file_download_options)
        return render_template('view_usage/download-non-COUNTER-usage.html', form=form)
    elif form.validate_on_submit():
        log.info(f"`form.AUCT_of_file_download.data` is {form.AUCT_of_file_download.data} (type {type(form.AUCT_of_file_download.data)}).")
        statistics_source_ID, fiscal_year_ID = literal_eval(form.AUCT_of_file_download.data)
        #ToDo: Create `AUCT_object` based on `annualUsageCollectionTracking` record with the PK above

        #ToDo: file_path = AUCT_object.download_nonstandard_usage_file(Path(__file__).parent)
        #ToDo: return redirect(url_for('download_file', file_path=str(file_path)))
        pass
    else:
        log.error(f"`form.errors`: {form.errors}")
        return abort(404)