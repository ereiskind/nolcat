import logging
import datetime
import calendar
from pathlib import Path
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import abort
from flask import Response
import pandas as pd

from . import bp
from .forms import CustomSQLQueryForm, QueryWizardForm, ChooseNonCOUNTERDownloadForm
from ..app import db
from ..models import *


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')
def view_usage_homepage():
    """Returns the homepage for the `view_usage` blueprint, which links to the usage query methods."""
    return render_template('view_usage/index.html')


@bp.route('/custom-SQL', methods=['GET', 'POST'])
def run_custom_SQL_query():
    """Returns a page that accepts a SQL query from the user and runs it against the database."""
    form = CustomSQLQueryForm()
    if request.method == 'GET':
        return render_template('view_usage/write-SQL-queries.html', form=form)
    elif form.validate_on_submit():
        df = pd.read_sql(
            sql=form.SQL_query.data,  #ToDo: Figure out how to make this safe from SQL injection
            con=db.engine,
        )
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        return Response(
            df.to_csv(
                index_label="index",
                date_format='%Y-%m-%d',
                errors='backslashreplace',
            ),
            mimetype='text/csv',
            headers={'Content-disposition': 'attachment; filename=NoLCAT_download.csv'},
        )
    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('query-wizard', methods=['GET', 'POST'])
def use_predefined_SQL_query():
    """Returns a page that offers pre-constructed queries and a query construction wizard."""
    form = QueryWizardForm()
    if request.method == 'GET':
        return render_template('view_usage/query-wizard.html', form=form)
    elif form.validate_on_submit():
        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            return redirect(url_for('view_usage.use_predefined_SQL_query'))  #ToDo: Add message flashing that the end date was before the begin date
        end_date = datetime.date(
            end_date.year,
            end_date.month,
            calendar.monthrange(end_date.year, end_date.month)[1],
        )
        
        if form.query_options.data == "PR_P1":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='PR' AND access_method='Regular'
                AND (metric_type='Searches_Platform' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Requests');
            '''
        elif form.query_options.data == "DR_D1":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='DR' AND access_method='Regular'
                AND (metric_type='Searches_Automated' OR metric_type='Searches_Federated' OR metric_type='Searches_Regular' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests');
            '''
        elif form.query_options.data == "DR_D2":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='DR' AND access_method='Regular'
                AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
            '''
        elif form.query_options.data == "TR_B1":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            '''
        if form.query_options.data == "TR_B2":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Book' AND access_method='Regular'
                AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
            '''
        elif form.query_options.data == "TR_B3":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Book' AND access_method='Regular'
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests');
            '''
        elif form.query_options.data == "TR_J1":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            '''
        elif form.query_options.data == "TR_J2":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_method='Regular'
                AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
            '''
        elif form.query_options.data == "TR_J3":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_method='Regular'
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' Or metric_type='Unique_Item_Investigations' Or metric_type='Unique_Item_Requests');
            '''
        elif form.query_options.data == "TR_J4":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            '''
        elif form.query_options.data == "IR_A1":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='IR' AND data_type='Article' AND access_method='Regular' AND parent_data_type='Journal'
                AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
            '''
        elif form.query_options.data == "IR_M1":
            query = f'''
                SELECT * FROM COUNTERData
                WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
                AND report_type='IR' AND data_type='Multimedia' AND access_method='Regular'
                AND metric_type='Total_Item_Requests';
            '''
        #ToDo: Decide what other canned reports, if any, are needed
        elif form.query_options.data == "w":
            #ToDo: Create queries that filter on metrics with fixed vocabularies via checkboxes
            #ToDo: Create queries where a sanitized (safe from SQL injection) free text field is fuzzily matched against a COUNTER free text field
            query = f'''
            '''

        df = pd.read_sql(
            sql=query,
            con=db.engine,
        )
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        return Response(
            df.to_csv(
                index_label="index",
                date_format='%Y-%m-%d',
                errors='backslashreplace',
            ),
            mimetype='text/csv',
            headers={'Content-disposition': 'attachment; filename=NoLCAT_download.csv'},
        )
    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('non-COUNTER-downloads', methods=['GET', 'POST'])
def download_non_COUNTER_usage():
    """Returns a page that allows all non-COUNTER usage files uploaded to NoLCAT to be downloaded."""
    form = ChooseNonCOUNTERDownloadForm()
    if request.method == 'GET':
        SQL_query = f'''
            SELECT
                statisticsSources.statistics_source_name,
                fiscalYears.fiscal_year,
                annualUsageCollectionTracking.usage_file_path
            FROM annualUsageCollectionTracking
            JOIN statisticsSources ON statisticsSources.statistics_source_ID = annualUsageCollectionTracking.AUCT_statistics_source
            JOIN fiscalYears ON fiscalYears.fiscal_year_ID = annualUsageCollectionTracking.AUCT_fiscal_year
            WHERE annualUsageCollectionTracking.usage_file_path IS NOT NULL;
        '''
        file_download_options = pd.read_sql(
            sql=SQL_query,
            con=db.engine,
        )
        file_download_options['field_display'] = file_download_options[['statistics_source_name', 'fiscal_year']].apply("--FY ".join, axis='columns')  # Standard string concatenation with `astype` methods to ensure both values are strings raises `IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or Boolean arrays are valid indices`
        form.file_download.choices = list(file_download_options[['usage_file_path', 'field_display']].itertuples(index=False, name=None))
        return render_template('view_usage/download-non-COUNTER-usage.html', form=form)
    elif form.validate_on_submit():
        download = Path(form.file_download.data)
        download_name = download.name
        if download.suffix == "xlsx":
            download_mimetype = "application/vnd.ms-excel"
        elif download.suffix == "csv":
            download_mimetype = "text/csv"
        elif download.suffix == "tsv":
            download_mimetype = "text/tab-separated-values"
        elif download.suffix == "pdf":
            download_mimetype = "application/pdf"
        elif download.suffix == "docx":
            download_mimetype = "application/msword"
        elif download.suffix == "pptx":
            download_mimetype = "application/vnd.ms-powerpoint"
        elif download.suffix == "txt":
            download_mimetype = "text/plain"
        elif download.suffix == "jpeg" or download.suffix == "jpg":
            download_mimetype = "image/jpeg"
        elif download.suffix == "png":
            download_mimetype = "image/png"
        elif download.suffix == "svg":
            download_mimetype = "image/svg+xml"
        elif download.suffix == "json":
            download_mimetype = "application/json"
        elif download.suffix == "html" or download.suffix == "htm":
            download_mimetype = "text/html"
        elif download.suffix == "xml":
            download_mimetype = "text/xml"
        elif download.suffix == "zip":
            download_mimetype = "application/zip"
        
        return Response(
            download,
            mimetype=download_mimetype,
            headers={'Content-disposition': f'attachment; filename={download_name}'},
        )
    else:
        logging.warning(f"`form.errors`: {form.errors}")
        return abort(404)