import logging
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import abort
from flask import Response
import pandas as pd

from . import bp
from ..app import db
from .forms import CustomSQLQueryForm
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


#ToDo: Create route for query wizard
    # return query_wizard.html


#ToDo: Create route for saved queries
    #ToDo: Include same text boxes with fuzzy search that allow pre-screening of results that will be pulled up for resource titles and vendor names (possibly sources as well) as in query wizard
    #ToDo: Include calculating annual numbers, not not the methods--methods save to relation
    #ToDo: Decide what other canned queries to provide

PR_P1_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='PR' AND access_method='Regular'
    AND (metric_type='Searches_Platform' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Requests');
'''

DR_D1_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='DR' AND access_method='Regular'
    AND (metric_type='Searches_Automated' OR metric_type='Searches_Federated' OR metric_type='Searches_Regular' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests');
'''

DR_D2_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='DR' AND access_method='Regular'
    AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
'''

TR_B1_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular'
    AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
'''

TR_B2_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Book' AND access_method='Regular'
    AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
'''

TR_B3_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Book' AND access_method='Regular'
    AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests');
'''

TR_J1_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'
    AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
'''

TR_J2_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Journal' AND access_method='Regular'
    AND (metric_type='Limit_Exceeded' OR metric_type='No_License');
'''

TR_J3_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Journal' AND access_method='Regular'
    AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' Or metric_type='Unique_Item_Investigations' Or metric_type='Unique_Item_Requests');
'''

TR_J4_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular'
    AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
'''

IR_A1_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='IR' AND data_type='Article' AND access_method='Regular' AND parent_data_type='Journal'
    AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');
'''

IR_M1_query = f'''
    SELECT * FROM COUNTERData
    WHERE usage_date>='{begin_date.strftime('%Y-%m-%d')}' AND usage_date<='{end_date.strftime('%Y-%m-%d')}'
    AND report_type='IR' AND data_type='Multimedia' AND access_method='Regular'
    AND metric_type='Total_Item_Requests';
'''