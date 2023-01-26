import logging
import datetime
import calendar
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import abort
from flask import Response
import pandas as pd

from . import bp
from ..app import db
from .forms import CustomSQLQueryForm, QueryWizardForm
#from ..models import <name of SQLAlchemy classes used in views below>


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
        return render_template('blueprint_name/page.html', form=form)
    elif form.validate_on_submit():
        df = pd.read_sql(
            sql=form.SQL_query.data,  #ToDo: Figure out how to make this safe from SQL injection
            con=db.engine,
        )
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
        return abort(404)


@bp.route('query-wizard', methods=['GET', 'POST'])
def use_predefined_SQL_query():
    """Returns a page that offers pre-constructed queries and a query construction wizard."""
    form = QueryWizardForm()
    if request.method == 'GET':
        return render_template('view_usage/query_wizard.html', form=form)
    elif form.validate_on_submit():
        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            return redirect(url_for('use_predefined_SQL_query'))  #ToDo: Add message flashing that the end date was before the begin date
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
        #ToDo: Create some queries with a single free text variable field where the entered data is used as a fuzzy search
        elif form.query_options.data == "w":
            query = f'''
            '''
            #ToDo: Determine how to write query and what fields to use
            #ToDo: Figure out how to do modern string formatting safe from SQL injection

        df = pd.read_sql(
            sql=query,
            con=db.engine,
        )
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
        return abort(404)