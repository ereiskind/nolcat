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
from fuzzywuzzy import fuzz

from . import bp
from .forms import *
from ..app import *
from ..models import *
from ..statements import *

log = logging.getLogger(__name__)

def fuzzy_search_on_field(value, field, report):
    """This function provides fuzzy matches for free text field input into the query wizard.

    The query wizard allows for free text input to use as a filter for some fields, but because SQL query string filters use exact matching, the chance that no results will be returned because the input isn't an exact match for what the SUSHI reports contain is high. To counter this problem, this function will pull all of the unique values in the field to be matched, perform fuzzy matching comparing those values to the value input into the query wizard, and returns all the existing values that are a fuzzy match.

    Args:
        value (str): the string input into the query wizard
        field (str): the `COUNTERData` field
        report (str): the abbreviation for the report being searched for

    Returns:
        list: the filed values that are fuzzy matches
        str: the error message if the query fails
    """
    log.info("Starting `fuzzy_search_on_field()`.")
    #Section: Get Existing Values from Database
    if report == "PR":
        query = f"SELECT DISTINCT {field} FROM COUNTERData WHERE report_type='PR' OR report_type='PR1';"
    elif report == "DR":
        query = f"SELECT DISTINCT {field} FROM COUNTERData WHERE report_type='DR' OR report_type='DB1' OR report_type='DB2';"
    elif report == "TR":
        query = f"SELECT DISTINCT {field} FROM COUNTERData WHERE report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1';"
    elif report == "IR":
        query = f"SELECT DISTINCT {field} FROM COUNTERData WHERE report_type='IR';"
    log.debug(f"Using the following query: {query}.")
    
    df = query_database(
        query=query,
        engine=db.engine,
    )
    if isinstance(df, str):
        message = database_query_fail_statement(df)
        log.error(message)
        return message

    #Section: Perform Matching
    df['partial_ratio'] = df.apply(lambda record: fuzz.partial_ratio(record[field], value), axis='columns')
    df['token_sort_ratio'] = df.apply(lambda record: fuzz.token_sort_ratio(record[field], value), axis='columns')
    df['token_set_ratio'] = df.apply(lambda record: fuzz.token_set_ratio(record[field], value), axis='columns')
    log.debug(f"Dataframe with all fuzzy matching values:\n{df}")
    df = df[
        (df['partial_ratio'] >= 70) |
        (df['token_sort_ratio'] >= 65) |
        (df['token_set_ratio'] >= 75)
    ]
    log.info(f"Dataframe filtered for matching values:\n{df}")
    return df[field].to_list()


@bp.route('/')
def view_usage_homepage():
    """Returns the homepage for the `view_usage` blueprint, which links to the usage query methods."""
    return render_template('view_usage/index.html')


@bp.route('/custom-query', methods=['GET', 'POST'])
def run_custom_SQL_query():
    """Returns a page that accepts a SQL query from the user and runs it against the database."""
    log.info("Starting `run_custom_SQL_query()`.")
    form = CustomSQLQueryForm()
    if request.method == 'GET':
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        log.debug(f"Before `unlink()`," + check_if_file_exists_statement(file_path, False))
        file_path.unlink(missing_ok=True)
        log.info(check_if_file_exists_statement(file_path))
        return render_template('view_usage/custom-query.html', form=form)
    elif form.validate_on_submit():
        df = query_database(
            query=form.SQL_query.data,  #ToDo: Figure out how to make this safe from SQL injection: https://stackoverflow.com/a/71604821
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
        return redirect(url_for('download_file', file_path=str(file_path)))  #TEST: `ValueError: I/O operation on closed file.` raised on `client.post` in `test_run_custom_SQL_query()`; above logging statements got to stdout indicating successful creation of `NoLCAT_download.csv`, but opening logging statement for `download_file()` route function isn't output at all
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('preset-query', methods=['GET', 'POST'])
def use_predefined_SQL_query():
    """Returns a page that offers pre-constructed queries and a query construction wizard."""
    log.info("Starting `use_predefined_SQL_query()`.")
    form = PresetQueryForm()
    if request.method == 'GET':
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        log.debug(f"Before `unlink()`," + check_if_file_exists_statement(file_path, False))
        file_path.unlink(missing_ok=True)
        log.info(check_if_file_exists_statement(file_path))
        return render_template('view_usage/preset-query.html', form=form)
    elif form.validate_on_submit():
        log.info(f"Querying NoLCAT for a {form.query_options.data} standard report with the begin date {form.begin_date.data} and the end date {form.end_date.data}.")
        begin_date = form.begin_date.data
        end_date = form.end_date.data
        if end_date < begin_date:
            message = attempted_SUSHI_call_with_invalid_dates_statement(end_date, begin_date)
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.use_predefined_SQL_query'))
        end_date = last_day_of_month(end_date)
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
        return redirect(url_for('download_file', file_path=str(file_path)))  #TEST: `ValueError: I/O operation on closed file.` raised on `client.post` in `test_use_predefined_SQL_query_with_COUNTER_standard_views()`; above logging statements got to stdout indicating successful creation of `NoLCAT_download.csv`, but opening logging statement for `download_file()` route function isn't output at all
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard', methods=['GET', 'POST'])
def start_query_wizard():
    """Collects the date range and report type for the query to be created."""
    log.info("Starting `start_query_wizard()`.")
    form = StartQueryWizardForm()
    if request.method == 'GET':
        fiscal_year_options = query_database(
            query="SELECT fiscal_year_ID, fiscal_year FROM fiscalYears;",
            engine=db.engine,
        )
        if isinstance(fiscal_year_options, str):
            flash(database_query_fail_statement(fiscal_year_options))
            return redirect(url_for('view_usage.view_usage_homepage'))
        form.fiscal_year.choices = list(fiscal_year_options.itertuples(index=False, name=None))
        return render_template('view_usage/query-wizard-start.html', form=form)
    elif form.validate_on_submit():
        if form.begin_date.data and form.end_date.data:
            logging.debug("Using custom date range.")
            end_date = last_day_of_month(form.end_date.data).isoformat()
            begin_date = form.begin_date.data.isoformat()
        elif not form.begin_date.data and not form.end_date.data:
            log.debug(f"Using the fiscal year with ID {form.fiscal_year.data} as the date range.")
            fiscal_year_dates = query_database(
                query=f"SELECT start_date, end_date FROM fiscalYears WHERE fiscal_year_ID={form.fiscal_year.data};",
                engine=db.engine,
            )
            if isinstance(fiscal_year_dates, str):
                flash(database_query_fail_statement(fiscal_year_dates))
                return redirect(url_for('view_usage.view_usage_homepage'))
            begin_date = fiscal_year_dates['start_date'][0].isoformat()
            end_date = fiscal_year_dates['end_date'][0].isoformat()
        else:
            message = f"Only one date was provided for the custom date range. Please try again, entering either two dates for a custom date range or no dates to use a fiscal year as the date range."
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.view_usage_homepage'))
        log.info(f"Setting up a query for {form.report_type.data} data from {begin_date} to {end_date}.")  #TEST: Getting expected results for both date input types here; why is it being rejected below?
        return redirect(url_for('view_usage.query_wizard_sort_redirect', report_type=form.report_type.data, begin_date=begin_date, end_date=end_date))
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard/<string:report_type>/<string:begin_date>/<string:end_date>')
def query_wizard_sort_redirect(report_type, begin_date, end_date):
    """This route function serves purely as a redirect to the route for the query wizard for the appropriate report type.
    
    Placing all this route's functionality in a route with the post-form submission processing for all four report types was raising a `werkzeug.routing.BuildError: Could not build url for endpoint 'view_usage.construct_query_with_wizard'` error at the `render_template()` statements at the end of the `request.method == 'GET'` section.

    Args:
        report_type (str): the COUNTER R5 report type abbreviation
        begin_date (str): the ISO string for the first day in the date range
        end_date (str): the ISO string for the last day in the date range
    """
    log.info("Starting `query_wizard_sort_redirect()`.")
    PRform = PRQueryWizardForm()
    DRform = DRQueryWizardForm()
    TRform = TRQueryWizardForm()
    IRform = IRQueryWizardForm()
    try:
        begin_date = date.fromisoformat(begin_date)
        end_date = date.fromisoformat(end_date)
        if begin_date > end_date:
            flash(attempted_SUSHI_call_with_invalid_dates_statement(end_date, begin_date).replace("will cause any SUSHI API calls to return errors; as a result, no SUSHI calls were made", "would have resulted in an error when querying the database"))
            return redirect(url_for('view_usage.start_query_wizard'))
        if begin_date < date.fromisoformat('2019-07-01'):
            flash_statement = "The usage data being requested includes COUNTER Release 4 data for all usage"
            if end_date < date.fromisoformat('2019-06-30'):
                flash_statement = flash_statement + "."
            else:
                flash_statement = flash_statement + " before 2019-07-01."
            flash(flash_statement)
        logging.debug(f"The query date range is {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        logging.debug(f"Rendering the query wizard form for a {report_type} query.")
        if report_type == "PR":
            PRform.begin_date.default = begin_date
            PRform.end_date.default = end_date
            PRform.process()  # Without this, the above defaults aren't sent to the form
            return render_template('view_usage/PR-query-wizard.html', form=PRform)
        elif report_type == "DR":
            DRform.begin_date.default = begin_date
            DRform.end_date.default = end_date
            DRform.process()  # Without this, the above defaults aren't sent to the form
            return render_template('view_usage/DR-query-wizard.html', form=DRform)
        elif report_type == "TR":
            TRform.begin_date.default = begin_date
            TRform.end_date.default = end_date
            TRform.process()  # Without this, the above defaults aren't sent to the form
            return render_template('view_usage/TR-query-wizard.html', form=TRform)
        elif report_type == "IR":
            IRform.begin_date.default = begin_date
            IRform.end_date.default = end_date
            IRform.process()  # Without this, the above defaults aren't sent to the form
            return render_template('view_usage/IR-query-wizard.html', form=IRform)
    except Exception as error:
        if not isinstance(error, dict):  # This check is needed because the usual is statements `request.method == 'GET'` and `form.validate_on_submit()` aren't being used
            error = vars(error)
        message = Flask_error_statement(error)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard/PR', methods=['GET', 'POST'])
def construct_PR_query_with_wizard():
    """Returns a page that allows a valid SQL query for platform usage data to be constructed through drop-downs and fuzzy text searches."""
    log.info("Starting `construct_PR_query_with_wizard()`.")
    form = PRQueryWizardForm()
    # Initial rendering of template is in `query_wizard_sort_redirect()`
    if form.validate_on_submit():
        #Section: Create SELECT Statement
        #Subsection: Create SELECT List
        display_fields = form.display_fields.data + ['metric_type'] + ['usage_date'] + ['SUM(usage_count)']
        display_fields = ", ".join([f"{field}" for field in display_fields])
        log.debug(f"The display fields are:\n{display_fields}")

        #Subsection: Create WHERE Filters for Strings
        if form.platform_filter.data:
            platform_filter_options = fuzzy_search_on_field(form.platform_filter.data, "platform", "PR")
            platform_filter_option_statement = " OR ".join([f"platform='{name}'" for name in platform_filter_options])
            log.debug(f"The platform filter statement is {platform_filter_option_statement}.")
            platform_filter_option_statement = f"AND ({platform_filter_option_statement})"
        else:
            platform_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.platform_filter.data` value
        
        #Subsection: Create WHERE Filters from Lists
        data_type_filter_list = [f"data_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.data_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The data type filter values are {data_type_filter_list}.")
        
        access_method_filter_list = [f"access_method='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.access_method_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The access method filter values are {access_method_filter_list}.")
        
        metric_type_filter_list = [f"metric_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.metric_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The metric type filter values are {metric_type_filter_list}.")

        #Subsection: Construct SQL Query
        # A f-string can be used because all of the values are from fixed text fields with program-supplied vocabularies, filtered by restrictive regexes, or derived from values already in the database
        query = f"""
            SELECT {display_fields}
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='{form.begin_date.data.strftime('%Y-%m-%d')}' AND usage_date<='{form.end_date.data.strftime('%Y-%m-%d')}'
                {platform_filter_option_statement}
                AND ({" OR ".join(data_type_filter_list)})
                AND ({" OR ".join(access_method_filter_list)})
                AND ({" OR ".join(metric_type_filter_list)})
            GROUP BY usage_count;
        """
        log.info(f"The query in SQL:\n{query}")

        #Section: Download Query Results
        df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = database_query_fail_statement(df)
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.view_usage_homepage'))
        log.debug(f"The result of the query:\n{df}")
        log.info(f"Dataframe info for the result of the query:\n{return_string_of_dataframe_info(df)}")
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        '''  COPIED FROM `use_predefined_SQL_query()`
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"After writing the dataframe to download to a CSV," + check_if_file_exists_statement(file_path, False))
        log.debug(list_folder_contents_statement(Path(__file__).parent))
        return redirect(url_for('download_file', file_path=str(file_path)))
        '''
        pass
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard/DR', methods=['GET', 'POST'])
def construct_DR_query_with_wizard():
    """Returns a page that allows a valid SQL query for database usage data to be constructed through drop-downs and fuzzy text searches."""
    log.info("Starting `construct_DR_query_with_wizard()`.")
    form = DRQueryWizardForm()
    # Initial rendering of template is in `query_wizard_sort_redirect()`
    if form.validate_on_submit():
        #Section: Create SELECT Statement
        #Subsection: Create SELECT List
        display_fields = form.display_fields.data + ['metric_type'] + ['usage_date'] + ['SUM(usage_count)']
        display_fields = ", ".join([f"{field}" for field in display_fields])
        log.debug(f"The display fields are:\n{display_fields}")

        #Subsection: Create WHERE Filters for Strings
        if form.resource_name_filter.data:
            resource_name_filter_options = fuzzy_search_on_field(form.resource_name_filter.data, "resource_name", "DR")
            resource_name_filter_option_statement = " OR ".join([f"resource_name='{name}'" for name in resource_name_filter_options])
            log.debug(f"The resource name filter statement is {resource_name_filter_option_statement}.")
            resource_name_filter_option_statement = f"AND ({resource_name_filter_option_statement})"
        else:
            resource_name_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.resource_name_filter.data` value
        
        if form.publisher_filter.data:
            publisher_filter_options = fuzzy_search_on_field(form.publisher_filter.data, "publisher", "DR")
            publisher_filter_option_statement = " OR ".join([f"publisher='{name}'" for name in publisher_filter_options])
            log.debug(f"The publisher filter statement is {publisher_filter_option_statement}.")
            publisher_filter_option_statement = f"AND ({publisher_filter_option_statement})"
        else:
            publisher_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.publisher_filter.data` value

        if form.platform_filter.data:
            platform_filter_options = fuzzy_search_on_field(form.platform_filter.data, "platform", "DR")
            platform_filter_option_statement = " OR ".join([f"platform='{name}'" for name in platform_filter_options])
            log.debug(f"The platform filter statement is {platform_filter_option_statement}.")
            platform_filter_option_statement = f"AND ({platform_filter_option_statement})"
        else:
            platform_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.platform_filter.data` value
        
        #Subsection: Create WHERE Filters from Lists
        data_type_filter_list = [f"data_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.data_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The data type filter values are {data_type_filter_list}.")
        
        access_method_filter_list = [f"access_method='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.access_method_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The access method filter values are {access_method_filter_list}.")
        
        metric_type_filter_list = [f"metric_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.metric_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The metric type filter values are {metric_type_filter_list}.")

        #Subsection: Construct SQL Query
        # A f-string can be used because all of the values are from fixed text fields with program-supplied vocabularies, filtered by restrictive regexes, or derived from values already in the database
        query = f"""
            SELECT {display_fields}
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='{form.begin_date.data.strftime('%Y-%m-%d')}' AND usage_date<='{form.end_date.data.strftime('%Y-%m-%d')}'
                {resource_name_filter_option_statement}
                {publisher_filter_option_statement}
                {platform_filter_option_statement}
                AND ({" OR ".join(data_type_filter_list)})
                AND ({" OR ".join(access_method_filter_list)})
                AND ({" OR ".join(metric_type_filter_list)})
            GROUP BY usage_count;
        """
        log.info(f"The query in SQL:\n{query}")

        #Section: Download Query Results
        df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = database_query_fail_statement(df)
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.view_usage_homepage'))
        log.debug(f"The result of the query:\n{df}")
        log.info(f"Dataframe info for the result of the query:\n{return_string_of_dataframe_info(df)}")
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        '''  COPIED FROM `use_predefined_SQL_query()`
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"After writing the dataframe to download to a CSV," + check_if_file_exists_statement(file_path, False))
        log.debug(list_folder_contents_statement(Path(__file__).parent))
        return redirect(url_for('download_file', file_path=str(file_path)))
        '''
        pass
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard/TR', methods=['GET', 'POST'])
def construct_TR_query_with_wizard():
    """Returns a page that allows a valid SQL query for title usage data to be constructed through drop-downs and fuzzy text searches."""
    log.info("Starting `construct_TR_query_with_wizard()`.")
    form = TRQueryWizardForm()
    # Initial rendering of template is in `query_wizard_sort_redirect()`
    if form.validate_on_submit():
        #ALERT: temp
        log.info(f"`begin_date` is {form.begin_date.data} (type {type(form.begin_date.data)})")
        log.info(f"`end_date` is {form.end_date.data} (type {type(form.end_date.data)})")
        log.info(f"`display_fields` is {form.display_fields.data} (type {type(form.display_fields.data)})")
        log.info(f"`resource_name_filter` is {form.resource_name_filter.data} (type {type(form.resource_name_filter.data)})")
        log.info(f"`publisher_filter` is {form.publisher_filter.data} (type {type(form.publisher_filter.data)})")
        log.info(f"`platform_filter` is {form.platform_filter.data} (type {type(form.platform_filter.data)})")
        #TEST: Use `978-1-56619-909-4` for testing below
        log.info(f"`ISBN_filter` is {form.ISBN_filter.data} (type {type(form.ISBN_filter.data)})")  #ALERT: With data, returns `AttributeError: 'function' object has no attribute 'match'`
        log.info(f"`ISSN_filter` is {form.ISSN_filter.data} (type {type(form.ISSN_filter.data)})")  #ALERT: With data, returns `AttributeError: 'function' object has no attribute 'match'`
        log.info(f"`data_type_filter` is {form.data_type_filter.data} (type {type(form.data_type_filter.data)})")
        log.info(f"`section_type_filter` is {form.section_type_filter.data} (type {type(form.section_type_filter.data)})")
        log.info(f"`YOP_start_filter` is {form.YOP_start_filter.data} (type {type(form.YOP_start_filter.data)})")
        log.info(f"`YOP_end_filter` is {form.YOP_end_filter.data} (type {type(form.YOP_end_filter.data)})")
        log.info(f"`access_type_filter` is {form.access_type_filter.data} (type {type(form.access_type_filter.data)})")
        log.info(f"`access_method_filter` is {form.access_method_filter.data} (type {type(form.access_method_filter.data)})")
        log.info(f"`metric_type_filter` is {form.metric_type_filter.data} (type {type(form.metric_type_filter.data)})")
        #ALERT: temp end
        #Section: Create SELECT Statement
        #Subsection: Create SELECT List
        display_fields = form.display_fields.data + ['metric_type'] + ['usage_date'] + ['SUM(usage_count)']
        display_fields = ", ".join([f"{field}" for field in display_fields])
        log.debug(f"The display fields are:\n{display_fields}")

        #Subsection: Create WHERE Filters for Strings
        if form.resource_name_filter.data:
            resource_name_filter_options = fuzzy_search_on_field(form.resource_name_filter.data, "resource_name", "TR")
            resource_name_filter_option_statement = " OR ".join([f"resource_name='{name}'" for name in resource_name_filter_options])
            log.debug(f"The resource name filter statement is {resource_name_filter_option_statement}.")
            resource_name_filter_option_statement = f"AND ({resource_name_filter_option_statement})"
        else:
            resource_name_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.resource_name_filter.data` value
        
        if form.publisher_filter.data:
            publisher_filter_options = fuzzy_search_on_field(form.publisher_filter.data, "publisher", "TR")
            publisher_filter_option_statement = " OR ".join([f"publisher='{name}'" for name in publisher_filter_options])
            log.debug(f"The publisher filter statement is {publisher_filter_option_statement}.")
            publisher_filter_option_statement = f"AND ({publisher_filter_option_statement})"
        else:
            publisher_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.publisher_filter.data` value

        if form.platform_filter.data:
            platform_filter_options = fuzzy_search_on_field(form.platform_filter.data, "platform", "TR")
            platform_filter_option_statement = " OR ".join([f"platform='{name}'" for name in platform_filter_options])
            log.debug(f"The platform filter statement is {platform_filter_option_statement}.")
            platform_filter_option_statement = f"AND ({platform_filter_option_statement})"
        else:
            platform_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.platform_filter.data` value
        
        if form.ISBN_filter.data:
            ISBN_filter_option_statement = f"AND ISBN='{form.ISBN_filter.data}'"
            log.debug(f"The ISBN filter statement is {ISBN_filter_option_statement}.")
        else:
            ISBN_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.ISBN_filter.data` value
        
        if form.ISSN_filter.data:
            ISSN_filter_option_statement = f"AND (print_ISSN='{form.ISSN_filter.data}' OR online_ISSN='{form.ISSN_filter.data}')"
            log.debug(f"The ISSN filter statement is {ISSN_filter_option_statement}.")
        else:
            ISSN_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.ISSN_filter.data` value
        
        #Subsection: Create WHERE Filters from Lists
        data_type_filter_list = [f"data_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.data_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The data type filter values are {data_type_filter_list}.")
        
        section_type_filter_list = [f"section_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.section_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The section type filter values are {section_type_filter_list}.")
        
        access_type_filter_list = [f"access_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.access_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The access type filter values are {access_type_filter_list}.")
        
        access_method_filter_list = [f"access_method='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.access_method_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The access method filter values are {access_method_filter_list}.")
        
        metric_type_filter_list = [f"metric_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.metric_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The metric type filter values are {metric_type_filter_list}.")

        #Subsection: Create WHERE Filters from Dates
        if form.YOP_start_filter.data and form.YOP_end_filter.data and form.YOP_end_filter.data > form.YOP_start_filter.data:
            YOP_filter_option_statement = f"AND YOP>='{form.YOP_start_filter.data}' AND publication_date<='{form.YOP_end_filter.data}'"
            log.debug(f"The YOP filter statement is {YOP_filter_option_statement}.")
        else:
            YOP_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there are YOP filters

        #Subsection: Construct SQL Query
        # A f-string can be used because all of the values are from fixed text fields with program-supplied vocabularies, filtered by restrictive regexes, or derived from values already in the database
        query = f"""
            SELECT {display_fields}
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='{form.begin_date.data.strftime('%Y-%m-%d')}' AND usage_date<='{form.end_date.data.strftime('%Y-%m-%d')}'
                {resource_name_filter_option_statement}
                {publisher_filter_option_statement}
                {platform_filter_option_statement}
                {ISBN_filter_option_statement}
                {ISSN_filter_option_statement}
                AND ({" OR ".join(data_type_filter_list)})
                AND ({"OR ".join(section_type_filter_list)})
                {YOP_filter_option_statement}
                AND ({"OR ".join(access_type_filter_list)})
                AND ({" OR ".join(access_method_filter_list)})
                AND ({" OR ".join(metric_type_filter_list)})
            GROUP BY usage_count;
        """
        log.info(f"The query in SQL:\n{query}")

        #Section: Download Query Results
        df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = database_query_fail_statement(df)
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.view_usage_homepage'))
        log.debug(f"The result of the query:\n{df}")
        log.info(f"Dataframe info for the result of the query:\n{return_string_of_dataframe_info(df)}")
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        '''  COPIED FROM `use_predefined_SQL_query()`
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"After writing the dataframe to download to a CSV," + check_if_file_exists_statement(file_path, False))
        log.debug(list_folder_contents_statement(Path(__file__).parent))
        return redirect(url_for('download_file', file_path=str(file_path)))
        '''
        pass
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


@bp.route('query-wizard/IR', methods=['GET', 'POST'])
def construct_IR_query_with_wizard():
    """Returns a page that allows a valid SQL query for item usage data to be constructed through drop-downs and fuzzy text searches."""
    log.info("Starting `construct_IR_query_with_wizard()`.")
    form = IRQueryWizardForm()
    # Initial rendering of template is in `query_wizard_sort_redirect()`
    if form.validate_on_submit():
        #ALERT: temp
        log.info(f"`begin_date` is {form.begin_date.data} (type {type(form.begin_date.data)})")
        log.info(f"`end_date` is {form.end_date.data} (type {type(form.end_date.data)})")
        log.info(f"`display_fields` is {form.display_fields.data} (type {type(form.display_fields.data)})")
        log.info(f"`resource_name_filter` is {form.resource_name_filter.data} (type {type(form.resource_name_filter.data)})")
        log.info(f"`publisher_filter` is {form.publisher_filter.data} (type {type(form.publisher_filter.data)})")
        log.info(f"`platform_filter` is {form.platform_filter.data} (type {type(form.platform_filter.data)})")
        log.info(f"`publication_date_start_filter` is {form.publication_date_start_filter.data} (type {type(form.publication_date_start_filter.data)})")
        log.info(f"`publication_date_end_filter` is {form.publication_date_end_filter.data} (type {type(form.publication_date_end_filter.data)})")
        log.info(f"`ISBN_filter` is {form.ISBN_filter.data} (type {type(form.ISBN_filter.data)})")  #ALERT: With data, returns `AttributeError: 'function' object has no attribute 'match'`
        log.info(f"`ISSN_filter` is {form.ISSN_filter.data} (type {type(form.ISSN_filter.data)})")  #ALERT: With data, returns `AttributeError: 'function' object has no attribute 'match'`
        log.info(f"`parent_title_filter` is {form.parent_title_filter.data} (type {type(form.parent_title_filter.data)})")
        log.info(f"`parent_ISBN_filter` is {form.parent_ISBN_filter.data} (type {type(form.parent_ISBN_filter.data)})")  #ALERT: With data, returns `AttributeError: 'function' object has no attribute 'match'`
        log.info(f"`parent_ISSN_filter` is {form.parent_ISSN_filter.data} (type {type(form.parent_ISSN_filter.data)})")  #ALERT: With data, returns `AttributeError: 'function' object has no attribute 'match'`
        log.info(f"`data_type_filter` is {form.data_type_filter.data} (type {type(form.data_type_filter.data)})")
        log.info(f"`YOP_start_filter` is {form.YOP_start_filter.data} (type {type(form.YOP_start_filter.data)})")
        log.info(f"`YOP_end_filter` is {form.YOP_end_filter.data} (type {type(form.YOP_end_filter.data)})")
        log.info(f"`access_type_filter` is {form.access_type_filter.data} (type {type(form.access_type_filter.data)})")
        log.info(f"`access_method_filter` is {form.access_method_filter.data} (type {type(form.access_method_filter.data)})")
        log.info(f"`metric_type_filter` is {form.metric_type_filter.data} (type {type(form.metric_type_filter.data)})")
        #ALERT: temp end
        #Section: Create SELECT Statement
        #Subsection: Create SELECT List
        display_fields = form.display_fields.data + ['metric_type'] + ['usage_date'] + ['SUM(usage_count)']
        display_fields = ", ".join([f"{field}" for field in display_fields])
        log.debug(f"The display fields are:\n{display_fields}")

        #Subsection: Create WHERE Filters for Strings
        if form.resource_name_filter.data:
            resource_name_filter_options = fuzzy_search_on_field(form.resource_name_filter.data, "resource_name", "IR")
            resource_name_filter_option_statement = " OR ".join([f"resource_name='{name}'" for name in resource_name_filter_options])
            log.debug(f"The resource_name filter statement is {resource_name_filter_option_statement}.")
            resource_name_filter_option_statement = f"AND ({resource_name_filter_option_statement})"
        else:
            resource_name_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.resource_name_filter.data` value
        
        if form.publisher_filter.data:
            publisher_filter_options = fuzzy_search_on_field(form.publisher_filter.data, "publisher", "IR")
            publisher_filter_option_statement = " OR ".join([f"publisher='{name}'" for name in publisher_filter_options])
            log.debug(f"The publisher filter statement is {publisher_filter_option_statement}.")
            publisher_filter_option_statement = f"AND ({publisher_filter_option_statement})"
        else:
            publisher_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.publisher_filter.data` value

        if form.platform_filter.data:
            platform_filter_options = fuzzy_search_on_field(form.platform_filter.data, "platform", "IR")
            platform_filter_option_statement = " OR ".join([f"platform='{name}'" for name in platform_filter_options])
            log.debug(f"The platform filter statement is {platform_filter_option_statement}.")
            platform_filter_option_statement = f"AND ({platform_filter_option_statement})"
        else:
            platform_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.platform_filter.data` value
        
        if form.parent_title_filter.data:
            parent_title_filter_options = fuzzy_search_on_field(form.parent_title_filter.data, "parent_title", "IR")
            parent_title_filter_option_statement = " OR ".join([f"parent_title='{name}'" for name in parent_title_filter_options])
            log.debug(f"The parent title filter statement is {parent_title_filter_option_statement}.")
            parent_title_filter_option_statement = f"AND ({parent_title_filter_option_statement})"
        else:
            parent_title_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.parent_title_filter.data` value
        
        if form.ISBN_filter.data:
            ISBN_filter_option_statement = f"AND ISBN='{form.ISBN_filter.data}'"
            log.debug(f"The ISBN filter statement is {ISBN_filter_option_statement}.")
        else:
            ISBN_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.ISBN_filter.data` value
        
        if form.ISSN_filter.data:
            ISSN_filter_option_statement = f"AND (print_ISSN='{form.ISSN_filter.data}' OR online_ISSN='{form.ISSN_filter.data}')"
            log.debug(f"The ISSN filter statement is {ISSN_filter_option_statement}.")
        else:
            ISSN_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.ISSN_filter.data` value
        
        if form.parent_ISBN_filter.data:
            parent_ISBN_filter_option_statement = f"AND parent_ISBN='{form.parent_ISBN_filter.data}'"
            log.debug(f"The parent ISBN filter statement is {parent_ISBN_filter_option_statement}.")
        else:
            parent_ISBN_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.ISBN_filter.data` value
        
        if form.parent_ISSN_filter.data:
            parent_ISSN_filter_option_statement = f"AND (parent_print_ISSN='{form.parent_ISSN_filter.data}' OR parent_online_ISSN='{form.parent_ISSN_filter.data}')"
            log.debug(f"The parent ISSN filter statement is {parent_ISSN_filter_option_statement}.")
        else:
            parent_ISSN_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there's a `form.ISSN_filter.data` value
        
        #Subsection: Create WHERE Filters from Lists
        data_type_filter_list = [f"data_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.data_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The data type filter values are {data_type_filter_list}.")
        
        access_type_filter_list = [f"access_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.access_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The access type filter values are {access_type_filter_list}.")
        
        access_method_filter_list = [f"access_method='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.access_method_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The access method filter values are {access_method_filter_list}.")
        
        metric_type_filter_list = [f"metric_type='{filter_value}'" for inner_comprehension_result in [form_value.split("|") if "|" in form_value else form_value for form_value in form.metric_type_filter.data] for filter_value in (inner_comprehension_result if isinstance(inner_comprehension_result, list) else [inner_comprehension_result])]
        log.debug(f"The metric type filter values are {metric_type_filter_list}.")

        #Subsection: Create WHERE Filters from Dates
        if form.publication_date_start_filter.data and form.publication_date_end_filter.data and form.publication_date_end_filter.data > form.publication_date_start_filter.data:
            publication_date_option_statement = f"AND publication_date>='{form.publication_date_start_filter.data.strftime('%Y-%m-%d')}' AND publication_date<='{form.publication_date_end_filter.data.strftime('%Y-%m-%d')}'"
            log.debug(f"The publication date filter statement is {publication_date_option_statement}.")
        else:
            publication_date_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there are publication date filters
        
        if form.YOP_start_filter.data and form.YOP_end_filter.data and form.YOP_end_filter.data > form.YOP_start_filter.data:
            YOP_filter_option_statement = f"AND YOP>='{form.YOP_start_filter.data}' AND publication_date<='{form.YOP_end_filter.data}'"
            log.debug(f"The YOP filter statement is {YOP_filter_option_statement}.")
        else:
            YOP_filter_option_statement = ""  # This allows the same f-string query constructor to be used regardless of if there are YOP filters

        #Subsection: Construct SQL Query
        # A f-string can be used because all of the values are from fixed text fields with program-supplied vocabularies, filtered by restrictive regexes, or derived from values already in the database
        query = f"""
            SELECT {display_fields}
            FROM COUNTERData
            WHERE
                report_type='IR'
                AND usage_date>='{form.begin_date.data.strftime('%Y-%m-%d')}' AND usage_date<='{form.end_date.data.strftime('%Y-%m-%d')}'
                {resource_name_filter_option_statement}
                {publisher_filter_option_statement}
                {platform_filter_option_statement}
                {parent_title_filter_option_statement}
                {publication_date_option_statement}
                {ISBN_filter_option_statement}
                {ISSN_filter_option_statement}
                {parent_ISBN_filter_option_statement}
                {parent_ISSN_filter_option_statement}
                AND ({" OR ".join(data_type_filter_list)})
                {YOP_filter_option_statement}
                AND ({"OR ".join(access_type_filter_list)})
                AND ({" OR ".join(access_method_filter_list)})
                AND ({" OR ".join(metric_type_filter_list)})
            GROUP BY usage_count;
        """
        log.info(f"The query in SQL:\n{query}")

        #Section: Download Query Results
        df = query_database(
            query=query,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = database_query_fail_statement(df)
            log.error(message)
            flash(message)
            return redirect(url_for('view_usage.view_usage_homepage'))
        log.debug(f"The result of the query:\n{df}")
        log.info(f"Dataframe info for the result of the query:\n{return_string_of_dataframe_info(df)}")
        #ToDo: What type juggling is needed to ensure numeric string values, integers, and dates are properly formatted in the CSV?
        '''  COPIED FROM `use_predefined_SQL_query()`
        file_path = Path(__file__).parent / 'NoLCAT_download.csv'
        df.to_csv(
            file_path,
            index_label="index",
            date_format='%Y-%m-%d',
            errors='backslashreplace',
        )
        log.info(f"After writing the dataframe to download to a CSV," + check_if_file_exists_statement(file_path, False))
        log.debug(list_folder_contents_statement(Path(__file__).parent))
        return redirect(url_for('download_file', file_path=str(file_path)))
        '''
        pass
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
        log.info(f"Dropdown selection is {form.AUCT_of_file_download.data} (type {type(form.AUCT_of_file_download.data)}).")
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
        return redirect(url_for('download_file', file_path=str(file_path)))  #TEST: `ValueError: I/O operation on closed file.` raised on `client.post` in `test_download_non_COUNTER_usage()`; above logging statements got to stdout indicating successful creation of file to download, but opening logging statement for `download_file()` route function isn't output at all
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)