"""Tests the routes in the `view_usage` blueprint."""
########## Failing 2024-01-12 ##########

import pytest
import logging
from pathlib import Path
import os
from random import choice
import re
from bs4 import BeautifulSoup
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from conftest import prepare_HTML_page_for_comparison
from nolcat.app import *
from nolcat.models import *
from nolcat.statements import *
from nolcat.view_usage import *

log = logging.getLogger(__name__)


@pytest.fixture
def COUNTER_download_CSV():
    """Provides the file path for a CSV download of COUNTER usage data, then removes that CSV at the end of the test.

    This fixture provides a constant name for all the CSVs being created, which is then used as the file removal target; a constant name is required because fixtures only accept other fixtures as arguments.

    Yields:
        pathlib.Path: an absolute file path to a CSV download of COUNTER usage data
    """
    file_path = views.create_downloads_folder() / 'NoLCAT_download.csv'
    log.debug(f"The file path `{file_path}` is type {type(file_path)}.")
    yield file_path
    try:
        file_path.unlink(missing_ok=True)
    except Exception as error:
        log.error(unable_to_delete_test_file_in_S3_statement(file_path, error).replace("S3 bucket", "instance"))  # The statement function and replacement keep the language of this unique statement consistent with similar situations


def test_fuzzy_search_on_field(client):
    """Tests the fuzzy match of a string to values in a given `COUNTERData` field."""
    with client:
        Gale_test = views.fuzzy_search_on_field("Gale", "publisher", "TR")
        TF_test = views.fuzzy_search_on_field("Taylor and Francis", "publisher", "TR")
        ERIC_test = views.fuzzy_search_on_field("ERIC", "resource_name", "DR")
    assert "Gale" in Gale_test
    assert "Gale a Cengage Company" in Gale_test
    assert "Gale, a Cengage Company" in Gale_test
    assert "Taylor & Francis Ltd" in TF_test
    assert "ERIC" in ERIC_test
    assert "ERIC (Module)" in ERIC_test
    assert "ERICdata Higher Education Knowledge" in ERIC_test
    assert "ProQuest Social Sciences Premium Collection->ERIC" in ERIC_test
    assert "Social Science Premium Collection->Education Collection->ERIC" in ERIC_test


def test_create_COUNTER_fixed_vocab_list():
    """Tests creating a single-level list from individual strings and pipe-delimited lists."""
    assert views.create_COUNTER_fixed_vocab_list(["a", "b", "c|d|e", "f"]) == ["a", "b", "c", "d", "e", "f"]


def test_set_encoding():
    """Tests that the Boolean values return the expected strings."""
    assert views.set_encoding(True) == 'utf-8-sig'
    assert views.set_encoding(False) == 'utf-8' 


def test_view_usage_homepage(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    page = client.get('/view_usage/')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'view_usage' / 'templates' / 'view_usage' / 'index.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    
    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title


def test_run_custom_SQL_query(client, header_value, COUNTER_download_CSV, caplog):
    """Tests running a user-written SQL query against the database and returning a CSV download."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.run_custom_SQL_query()`
    form_input = {
        'SQL_query': "SELECT COUNT(*) FROM COUNTERData;",
        'open_in_Excel': False,
    }
    POST_response = client.post(
        '/view_usage/custom-query',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    assert POST_response.status == "200 OK"
    assert COUNTER_download_CSV.is_file()
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


def test_use_predefined_SQL_query(engine, client, header_value, COUNTER_download_CSV, caplog):
    """Tests running one of the provided SQL queries which match the definitions of the COUNTER R5 standard views against the database and returning a CSV download."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.use_predefined_SQL_query()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`

    query_options = choice((
        ("PR_P1", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='PR' AND access_method='Regular' AND (metric_type='Searches_Platform' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("DR_D1", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='DR' AND access_method='Regular' AND (metric_type='Searches_Automated' OR metric_type='Searches_Federated' OR metric_type='Searches_Regular' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests');"),
        ("DR_D2", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='DR' AND access_method='Regular' AND (metric_type='Limit_Exceeded' OR metric_type='No_License');"),
        ("TR_B1", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='TR' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular' AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        # No TR_B2: no R5 resources have access denial metric types
        ("TR_B3", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='TR' AND data_type='Book' AND access_method='Regular' AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests');"),
        ("TR_J1", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular' AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        # No TR_J2: no R5 resources have access denial metric types
        ("TR_J3", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='TR' AND data_type='Journal' AND access_method='Regular' AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' Or metric_type='Unique_Item_Investigations' Or metric_type='Unique_Item_Requests');"),
        ("TR_J4", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='TR' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular' AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        ("IR_A1", "SELECT * FROM COUNTERData WHERE usage_date>='2016-07-01' AND usage_date<='2020-06-01' AND report_type='IR' AND data_type='Article' AND access_method='Regular' AND parent_data_type='Journal' AND (metric_type='Total_Item_Requests' OR metric_type='Unique_Title_Requests');"),
        # No IR_M1: no R5 resources have multimedia data type
    ))
    form_input = {
        'begin_date': '2016-07-01',
        'end_date': '2020-06-01',
        'query_options': query_options[0],
        'open_in_Excel': False,
    }
    POST_response = client.post(
        '/view_usage/preset-query',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    CSV_df = pd.read_csv(
        COUNTER_download_CSV,
        index_col='COUNTER_data_ID',
        parse_dates=['publication_date', 'parent_publication_date', 'usage_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    CSV_df = CSV_df.astype(COUNTERData.state_data_types())
    database_df = query_database(
        query=query_options[1],
        engine=engine,
        index='COUNTER_data_ID',
    )
    if isinstance(database_df, str):
        pytest.skip(database_function_skip_statements(database_df))
    database_df = database_df.astype(COUNTERData.state_data_types())

    assert POST_response.status == "200 OK"
    assert COUNTER_download_CSV.is_file()
    assert_frame_equal(CSV_df, database_df)
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


@pytest.fixture
def start_query_wizard_form_data(engine):
    """Creates the form data for `start_query_wizard()`.
    
    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine

    Yields:
        dict: form input for the form on "query-wizard-start.html"
    """
    df = query_database(
        query="SELECT usage_date, report_type FROM COUNTERData WHERE report_type='PR' OR report_type='DR' OR report_type='TR' OR report_type='IR' GROUP BY usage_date, report_type;",
        engine=engine,
    )
    if isinstance(df, str):
        pytest.skip(database_function_skip_statements(df))
    df = df.sample().reset_index()
    yield {
        'begin_date': df.at[0,'usage_date'],
        'end_date': last_day_of_month(df.at[0,'usage_date']),
        'fiscal_year': 0,
        'report_type': df.at[0,'report_type'],
    }


def test_start_query_wizard(client, header_value, start_query_wizard_form_data):
    """Tests the submission of the report type and date range to the query wizard."""
    POST_response = client.post(
        '/view_usage/query-wizard',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        headers=header_value,
        data=start_query_wizard_form_data,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    assert POST_response.status == "302 FOUND"  # This confirms there would've been a redirect if the `post()` method allowed it
    assert POST_response.headers['Location'] == f"http://localhost/view_usage/query-wizard/{start_query_wizard_form_data['report_type']}/{start_query_wizard_form_data['begin_date'].strftime('%Y-%m-%d')}/{start_query_wizard_form_data['end_date'].strftime('%Y-%m-%d')}"  # This is the redirect destination


def test_GET_query_wizard_sort_redirect(client, header_value, start_query_wizard_form_data):
    """Tests that the query wizard accepts the report type and date range and redirects to the page showing the appropriate form.
    
    Because the function begin tested gets its input from the `start_query_wizard()` route function, the function being tested is accessed through a redirect from that route function. The same form input data is used as when testing that function for efficiency and to reduce the number of places the error could possibly originate if this test fails.
    """
    POST_response = client.post(
        '/view_usage/query-wizard',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=start_query_wizard_form_data,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    POST_soup = BeautifulSoup(POST_response.data, 'lxml')
    POST_response_title = POST_soup.head.title.string.encode('utf-8')
    POST_response_begin_date_field = POST_soup.find_all(id='begin_date')[0]['value']
    POST_response_end_date_field = POST_soup.find_all(id='end_date')[0]['value']

    assert POST_response.history[0].status == "302 FOUND"  # This confirms there was a redirect
    assert POST_response.status == "200 OK"
    assert f"{start_query_wizard_form_data['report_type']} Query Wizard".encode('utf-8') in POST_response_title
    assert POST_response_begin_date_field == start_query_wizard_form_data['begin_date'].strftime('%Y-%m-%d')
    assert POST_response_end_date_field == start_query_wizard_form_data['end_date'].strftime('%Y-%m-%d')


@pytest.fixture(params=[
    "Filter by fixed vocabulary fields",
    #"Filter by platform name",
])
def PR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    The `werkzeug.test.EnvironBuilder` class creates a WSGI environment for testing Flask applications without actually starting a server, which makes it useful for testing; the `data` attribute accepts a dict with the values of form data. If the form data values are collections, the `add_file()` method is called, meaning the values for SelectMultipleFields CANNOT contain multiple selections.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    if request.param == "Filter by fixed vocabulary fields":
        form_input = {
            'begin_date': date.fromisoformat('2016-07-01'),
            'end_date': date.fromisoformat('2017-06-30'),
            'display_fields': 'platform',
            'platform_filter': "",
            'data_type_filter': forms.data_type_values['Platform'][0],
            'access_method_filter': 'Regular',
            'metric_type_filter': forms.metric_type_values['Searches_Platform'][0],
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='2016-07-01' AND usage_date<='2017-06-30'
                AND (data_type='Platform')
                AND (access_method='Regular' OR access_method IS NULL)
                AND (metric_type='Searches_Platform' OR metric_type='Regular Searches')
            GROUP BY usage_count, platform;
        """
        yield (form_input, query)
    elif request.param == "Filter by platform name":  #TEST: FileNotFoundError: [Errno 2] No such file or directory: 'Platform' --> self = FileMultiDict([('display_fields', <FileStorage: ('data_type', 'Data Type') ("('access_method', 'Access Method')")>)]), name = 'data_type_filter', file = 'Platform', filename = 'Platform' content_type = None
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('platform', "Platform"),
                ('data_type', "Data Type"),
                ('access_method', "Access Method"),
            ),
            'platform_filter': "EBSCO",
            'data_type_filter': (forms.data_type_values['Platform'][0]),  #TEST: Using index operator to get only the data value, not the display value
            'access_method_filter': (('Regular', "Regular")),
            'metric_type_filter': (
                forms.metric_type_values['Searches_Platform'],
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Total_Item_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, data_type, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND platform LIKE 'EBSCOhost'
                AND (data_type='Platform')
                AND (access_method='Regular')
                AND (metric_type='Searches_Platform' OR metric_type='Regular Searches' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Successful Full-text Article Requests' OR metric_type='Successful Title Requests' OR metric_type='Successful Section Requests' OR metric_type='Successful Content Unit Requests')
            GROUP BY usage_count;
        """  # With the test data, the only fuzzy match to `EBSCO` will be `EBSCOhost`
        yield (form_input, query)



def test_construct_PR_query_with_wizard(engine, client, header_value, PR_parameters, COUNTER_download_CSV, caplog):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.construct_PR_query_with_wizard()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`

    form_input, query = PR_parameters
    log.debug(f"The form input is type {type(form_input)} and the query is type {type(query)}.")
    POST_response = client.post(  #TEST: Errors raised here
        '/view_usage/query-wizard/PR',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    log.debug(check_if_file_exists_statement(COUNTER_download_CSV))
    CSV_df = pd.read_csv(
        COUNTER_download_CSV,
        index=False,
        parse_dates=['usage_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    CSV_df = CSV_df.astype(COUNTERData.state_data_types())
    database_df = query_database(
        query=query,
        engine=engine,
        index='COUNTER_data_ID',
    )
    if isinstance(database_df, str):
        pytest.skip(database_function_skip_statements(database_df))
    database_df = database_df.astype(COUNTERData.state_data_types())

    assert POST_response.status == "200 OK"
    assert COUNTER_download_CSV.is_file()
    assert_frame_equal(CSV_df, database_df)
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


@pytest.fixture(params=[
    "Filter by fixed vocabulary fields",
    #"Filter by resource name",
    #"Filter by publisher name",
])
def DR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    The `werkzeug.test.EnvironBuilder` class creates a WSGI environment for testing Flask applications without actually starting a server, which makes it useful for testing; the `data` attribute accepts a dict with the values of form data. If the form data values are collections, the `add_file()` method is called, meaning the values for SelectMultipleFields CANNOT contain multiple selections.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    if request.param == "Filter by fixed vocabulary fields":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': 'resource_name',
            'resource_name_filter': "",
            'publisher_filter': "",
            'platform_filter': "",
            'data_type_filter': forms.data_type_values['Database'][0],
            'access_method_filter': 'Regular',
            'metric_type_filter': forms.metric_type_values['Searches_Automated'][0],
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (data_type='Database')
                AND (access_method='Regular' OR access_method IS NULL)
                AND (metric_type='Searches_Automated' OR metric_type='Searches-federated and automated' OR metric_type='Searches: federated and automated')
            GROUP BY usage_count, resource_name, publisher, platform;
        """
        yield (form_input, query)
    elif request.param == "Filter by resource name":  #TEST: TypeError: expected str, bytes or os.PathLike object, not tuple --> self = <mimetypes.MimeTypes object at 0x7f2f08345b20>, url = ('Journal', 'Journal'), strict = True
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('resource_name', "Database Name"),
                ('publisher', "Publisher"),
                ('platform', "Platform"),
            ),
            'resource_name_filter': "eric",
            'publisher_filter': None,
            'platform_filter': None,
            'data_type_filter': (
                forms.data_type_values['Database'],
                forms.data_type_values['Journal'],
            ),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Searches_Regular'],
                forms.metric_type_values['No_License'],
                forms.metric_type_values['Limit_Exceeded'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publisher, platform, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (resource_name='ERIC' OR resource_name='Historical Abstracts' OR resource_name='Periodicals Archive Online->Periodicals Archive Online Foundation Collection 3' OR resource_name='Periodicals Archive Online->Periodicals Archive Online Foundation Collection 2' OR resource_name='Periodicals Archive Online->Periodicals Archive Online Foundation Collection' OR resource_name='Periodicals Archive Online Foundation Collection 2' OR resource_name='Periodicals Archive Online Foundation Collection 3' OR resource_name='01 Periodicals Archive Online Foundation Collection 1' OR resource_name='Social Science Premium Collection->Education Collection->ERIC')
                AND (data_type='Database' OR data_type='Journal')
                AND (metric_type='Searches_Regular' OR metric_type='Regular Searches' OR metric_type='No_License' OR metric_type='Access denied: content item not licensed' OR metric_type='Limit_Exceeded' OR metric_type='Access denied: concurrent/simultaneous user license limit exceeded' OR metric_type='Access denied: concurrent/simultaneous user license exceeded. (Currently N/A to all platforms).')
            GROUP BY usage_count, publisher, platform, access_method, metric_type;
        """  # Resource names based off of values returned in test data
        yield (form_input, query)
    elif request.param == "Filter by publisher name":  #TEST: TypeError: expected str, bytes or os.PathLike object, not tuple --> self = <mimetypes.MimeTypes object at 0x7f2f08345b20>, url = ('Database', 'Database'), strict = True
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('resource_name', "Database Name"),
                ('publisher', "Publisher"),
                ('platform', "Platform"),
            ),
            'resource_name_filter': None,
            'publisher_filter': "proq",
            'platform_filter': None,
            'data_type_filter':(
                forms.data_type_values['Book'],
                forms.data_type_values['Database'],
            ),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Searches_Regular'],
                forms.metric_type_values['Limit_Exceeded'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publisher, platform, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (publisher='ProQuest')
                AND (data_type='Book' OR data_type='Database')
                AND (metric_type='Searches_Regular' OR metric_type='Regular Searches' OR metric_type='Limit_Exceeded' OR metric_type='Access denied: concurrent/simultaneous user license limit exceeded' OR metric_type='Access denied: concurrent/simultaneous user license exceeded. (Currently N/A to all platforms).')
            GROUP BY usage_count, resource_name, platform, access_method, metric_type;
        """  # Publisher name based off of values returned in test data
        yield (form_input, query)


def test_construct_DR_query_with_wizard(engine, client, header_value, DR_parameters, COUNTER_download_CSV, caplog):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.construct_DR_query_with_wizard()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`

    form_input, query = DR_parameters
    log.debug(f"The form input is type {type(form_input)} and the query is type {type(query)}.")
    POST_response = client.post(  #TEST: Errors raised here
        '/view_usage/query-wizard/DR',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    log.debug(check_if_file_exists_statement(COUNTER_download_CSV))
    CSV_df = pd.read_csv(
        COUNTER_download_CSV,
        index=False,
        parse_dates=['usage_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    CSV_df = CSV_df.astype(COUNTERData.state_data_types())
    database_df = query_database(
        query=query,
        engine=engine,
        index='COUNTER_data_ID',
    )
    if isinstance(database_df, str):
        pytest.skip(database_function_skip_statements(database_df))
    database_df = database_df.astype(COUNTERData.state_data_types())

    assert POST_response.status == "200 OK"
    assert COUNTER_download_CSV.is_file()
    assert_frame_equal(CSV_df, database_df)
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


@pytest.fixture(params=[
    "Filter by fixed vocabulary fields",
    #"Filter by resource name with apostrophe and non-ASCII character",
    #"Filter by ISBN",
    #"Filter by ISSN",
    #"Filter by ISSN and platform",
    #"Filter by year of publication",
])
def TR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    The `werkzeug.test.EnvironBuilder` class creates a WSGI environment for testing Flask applications without actually starting a server, which makes it useful for testing; the `data` attribute accepts a dict with the values of form data. If the form data values are collections, the `add_file()` method is called, meaning the values for SelectMultipleFields CANNOT contain multiple selections.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    if request.param == "Filter by fixed vocabulary fields":
        form_input = {
            'begin_date': date.fromisoformat('2019-07-01'),
            'end_date': date.fromisoformat('2020-06-30'),
            'display_fields': 'resource_name',
            'resource_name_filter': "",
            'publisher_filter': "",
            'platform_filter': "",
            'ISBN_filter': "",
            'ISSN_filter': "",
            'data_type_filter': forms.data_type_values['Book'][0],
            'section_type_filter': 'Book',
            'YOP_start_filter': "",
            'YOP_end_filter': "",
            'access_type_filter': 'Controlled',
            'access_method_filter': 'Regular',
            'metric_type_filter': forms.metric_type_values['Total_Item_Investigations'][0],
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='2019-07-01' AND usage_date<='2020-06-30'
                AND (data_type='Book')
                AND (section_type='Book' OR section_type IS NULL)
                AND (access_type='Controlled' OR access_type IS NULL)
                AND (access_method='Regular' OR access_method IS NULL)
                AND (metric_type='Total_Item_Investigations')
            GROUP BY usage_count;
        """
        yield (form_input, query)
    elif request.param == "Filter by resource name with apostrophe and non-ASCII character":  #TEST: `ValueError: TR_parameters did not yield a value` with stack trace that doesn't include any NoLCAT code
        form_input = {
            'begin_date': date.fromisoformat('2019-07-01'),
            'end_date': date.fromisoformat('2020-06-30'),
            'display_fields': (
                ('resource_name', "Title Name"),
                ('publisher', "Publisher"),
                ('platform', "Platform"),
                ('DOI', "DOI"),
            ),
            'resource_name_filter': "Pikachu's Global Adventure: The Rise and Fall of Pokémon",
            'publisher_filter': None,
            'platform_filter': None,
            'ISBN_filter': None,
            'ISSN_filter': None,
            'data_type_filter': (
                forms.data_type_values['Book'],
                forms.data_type_values['Other'],
            ),
            'section_type_filter': (
                ('Book', "Book"),
                ('Chapter', "Chapter"),
                ('Other', "Other"),
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Unique_Item_Investigations'],
                forms.metric_type_values['Unique_Title_Investigations'],
                forms.metric_type_values['Unique_Title_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publisher, platform, DOI, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='2019-07-01' AND usage_date<='2020-06-30'
                AND (resource_name='Pikachu\'s Global Adventure<subtitle>The Rise and Fall of Pokémon</subtitle>')
                AND (data_type='Book' OR data_type='Other')
                AND (section_type='Book' OR section_type='Chapter' OR section_type='Other')
                AND (metric_type='Total_Item_Investigations' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests' OR metric_type='Successful Title Requests')
            GROUP BY usage_count, publisher, platform, DOI;
        """  # Resource name based off of value returned in test data
        yield (form_input, query)
    elif request.param == "Filter by ISBN":
        form_input = {
            'begin_date': date.fromisoformat('2017-07-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (  #TEST: TypeError: add_file() takes from 3 to 5 positional arguments but 6 were given --> self = <flask.testing.EnvironBuilder object at 0x7f2f052c9490>, key = 'display_fields', value = (('resource_name', 'Title Name'), ('ISBN', 'ISBN'), ('data_type', 'Data Type'), ('section_type', 'Section Type'))
                ('resource_name', "Title Name"),
                ('ISBN', "ISBN"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'ISBN_filter': "978-0-0286-6072-1",
            'ISSN_filter': None,
            'data_type_filter': (
                forms.data_type_values['Book'],
                forms.data_type_values['Other'],
            ),
            'section_type_filter': (
                ('Book', "Book"),
                ('Chapter', "Chapter"),
                ('Other', "Other"),
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Unique_Title_Investigations'],
                forms.metric_type_values['Unique_Title_Requests'],
                forms.metric_type_values['No_License'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, ISBN, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='2017-07-01' AND usage_date<='2019-12-31'
                AND (ISBN='978-0-0286-6072-1')
                AND (data_type='Book' OR data_type='Other')
                AND (section_type='Book' OR section_type='Chapter' OR section_type='Other')
                AND (metric_type='Unique_Title_Investigations' OR metric_type='Unique_Title_Requests' OR metric_type='Successful Title Requests' OR metric_type='No_License' OR metric_type='Access denied: content item not licensed')
            GROUP BY usage_count, resource_name;
        """
        yield (form_input, query)
    elif request.param == "Filter by ISSN":  #TEST: TypeError: expected str, bytes or os.PathLike object, not tuple --> self = <mimetypes.MimeTypes object at 0x7f2f08345b20>, url = ('TDM', 'TDM'), strict = True
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('resource_name', "Title Name"),
                ('print_ISSN', "Print ISSN"),
                ('online_ISSN', "Online ISSN"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'ISBN_filter': None,
            'ISSN_filter': "0363-0277",
            'data_type_filter': (
                forms.data_type_values['Journal'],
                forms.data_type_values['Newspaper_or_Newsletter'],
                forms.data_type_values['Other'],
            ),
            'section_type_filter': (
                ('Article', "Article"),
                ('Other', "Other"),
                ('Section', "Section"),
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Unique_Item_Investigations'],
                forms.metric_type_values['Unique_Item_Requests'],
                forms.metric_type_values['Limit_Exceeded'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, print_ISSN, online_ISSN, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (print_ISSN='0363-0277' OR online_ISSN='0363-0277')
                AND (data_type='Journal' OR data_type='Newspaper_or_Newsletter' OR data_type='Other')
                AND (section_type='Article' OR section_type='Other' OR section_type='Section')
                AND (metric_type='Total_Item_Investigations' OR metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='Limit_Exceeded' OR metric_type='Access denied: concurrent/simultaneous user license limit exceeded' OR metric_type='Access denied: concurrent/simultaneous user license exceeded. (Currently N/A to all platforms).')
            GROUP BY usage_count, resource_name;
        """
        yield (form_input, query)
    elif request.param == "Filter by ISSN and platform":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (  #TEST: TypeError: add_file() takes from 3 to 5 positional arguments but 6 were given --> self = <flask.testing.EnvironBuilder object at 0x7f2f0535a6d0>, key = 'display_fields' value = (('resource_name', 'Title Name'), ('platform', 'Platform'), ('print_ISSN', 'Print ISSN'), ('online_ISSN', 'Online ISSN'))
                ('platform', "Platform"),
                ('print_ISSN', "Print ISSN"),
                ('online_ISSN', "Online ISSN"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': "EBSCO",
            'ISBN_filter': None,
            'ISSN_filter': "0363-0277",
            'data_type_filter': (
                forms.data_type_values['Journal'],
                forms.data_type_values['Newspaper_or_Newsletter'],
                forms.data_type_values['Other'],
            ),
            'section_type_filter': (
                ('Article', "Article"),
                ('Other', "Other"),
                ('Section', "Section"),
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Total_Item_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, print_ISSN, online_ISSN, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (platform='EBSCOhost')
                AND (print_ISSN='0363-0277' OR online_ISSN='0363-0277')
                AND (data_type='Journal' OR data_type='Newspaper_or_Newsletter' OR data_type='Other')
                AND (section_type='Article' OR section_type='Other' OR section_type='Section')
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Successful Full-text Article Requests' OR metric_type='Successful Title Requests' OR metric_type='Successful Section Requests' OR metric_type='Successful Content Unit Requests')
            GROUP BY usage_count;
        """  # Platform name based off of value returned in test data
        yield (form_input, query)
    elif request.param == "Filter by year of publication":  #TEST: TypeError: expected str, bytes or os.PathLike object, not tuple --> self = <mimetypes.MimeTypes object at 0x7f2f08345b20>, url = ('TDM', 'TDM'), strict = True
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('resource_name', "Title Name"),
                ('DOI', "DOI"),
                ('YOP', "Year of Publication"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'ISBN_filter': None,
            'ISSN_filter': None,
            'data_type_filter': (
                forms.data_type_values['Journal'],
                forms.data_type_values['Newspaper_or_Newsletter'],
                forms.data_type_values['Other'],
            ),
            'section_type_filter': (
                ('Article', "Article"),
                ('Other', "Other"),
                ('Section', "Section"),
            ),
            'YOP_start_filter': 1995,
            'YOP_end_filter': 2005,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Unique_Item_Investigations'],
                forms.metric_type_values['Unique_Item_Requests'],
                forms.metric_type_values['No_License'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, DOI, YOP, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='TR' OR report_type='BR1' OR report_type='BR2' OR report_type='BR3' OR report_type='BR5' OR report_type='JR1' OR report_type='JR2' OR report_type='MR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (data_type='Journal' OR data_type='Newspaper_or_Newsletter' OR data_type='Other')
                AND (section_type='Article' OR section_type='Other' OR section_type='Section')
                AND YOP>=1995 AND YOP<=2005
                AND (metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests' OR metric_type='No_License' OR metric_type='Access denied: content item not licensed')
            GROUP BY usage_count, resource_name, DOI;
        """
        yield (form_input, query)


def test_construct_TR_query_with_wizard(engine, client, header_value, TR_parameters, COUNTER_download_CSV, caplog):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.construct_TR_query_with_wizard()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`

    form_input, query = TR_parameters
    log.debug(f"The form input is type {type(form_input)} and the query is type {type(query)}.")
    POST_response = client.post(  #TEST: Errors raised here
        '/view_usage/query-wizard/TR',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    log.debug(check_if_file_exists_statement(COUNTER_download_CSV))
    CSV_df = pd.read_csv(
        COUNTER_download_CSV,
        index=False,
        parse_dates=['usage_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    CSV_df = CSV_df.astype(COUNTERData.state_data_types())
    database_df = query_database(
        query=query,
        engine=engine,
        index='COUNTER_data_ID',
    )
    if isinstance(database_df, str):
        pytest.skip(database_function_skip_statements(database_df))
    database_df = database_df.astype(COUNTERData.state_data_types())

    assert POST_response.status == "200 OK"
    assert COUNTER_download_CSV.is_file()
    assert_frame_equal(CSV_df, database_df)
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


@pytest.fixture(params=[
    "Filter by fixed vocabulary fields",
    #"Filter by publication date",
    #"Filter by parent title",
    #"Filter by parent ISBN",
    #"Filter by parent ISSN",
])
def IR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    The `werkzeug.test.EnvironBuilder` class creates a WSGI environment for testing Flask applications without actually starting a server, which makes it useful for testing; the `data` attribute accepts a dict with the values of form data. If the form data values are collections, the `add_file()` method is called, meaning the values for SelectMultipleFields CANNOT contain multiple selections.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    if request.param == "Filter by fixed vocabulary fields":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': 'resource_name',
            'resource_name_filter': "",
            'publisher_filter': "",
            'platform_filter': "",
            'publication_date_start_filter': "",
            'publication_date_end_filter': "",
            'ISBN_filter': "",
            'ISSN_filter': "",
            'parent_title_filter': "",
            'parent_ISBN_filter': "",
            'parent_ISSN_filter': "",
            'data_type_filter': forms.data_type_values['Article'][0],
            'YOP_start_filter': "",
            'YOP_end_filter': "",
            'access_type_filter': 'Controlled',
            'access_method_filter': 'Regular',
            'metric_type_filter': forms.metric_type_values['Total_Item_Investigations'][0],
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                report_type='IR'
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (data_type='Article')
                AND (access_type='Controlled' OR access_type IS NULL)
                AND (access_method='Regular' OR access_method IS NULL)
                AND (metric_type='Total_Item_Investigations')
            GROUP BY usage_count, resource_name;
        """
        yield (form_input, query)
    elif request.param == "Filter by publication date":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (  #TEST: TypeError: add_file() takes from 3 to 5 positional arguments but 6 were given --> self = <flask.testing.EnvironBuilder object at 0x7f2f05067040>, key = 'display_fields' value = (('resource_name', 'Item Name'), ('publication_date', 'Publication Date'), ('DOI', 'DOI'), ('YOP', 'Year of Publication'))
                ('resource_name', "Item Name"),
                ('publication_date', "Publication Date"),
                ('YOP', "Year of Publication"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'publication_date_start_filter': date.fromisoformat('2018-01-01'),
            'publication_date_end_filter': date.fromisoformat('2018-12-31'),
            'ISBN_filter': None,
            'ISSN_filter': None,
            'parent_title_filter': None,
            'parent_ISBN_filter': None,
            'parent_ISSN_filter': None,
            'data_type_filter': (
                forms.data_type_values['Article'], 
                forms.data_type_values['Book_Segment'], 
                forms.data_type_values['Other'],
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Total_Item_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publication_date, YOP, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                report_type='IR'
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND publication_date>='2018-01-01' AND publication_date<='2018-12-31'
                AND (data_type='Article' OR data_type='Book_Segment' OR data_type='Other')
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Successful Full-text Article Requests' Or metric_type='Successful Title Requests' OR metric_type='Successful Section Requests' OR metric_type='Successful Content Unit Requests')
            GROUP BY usage_count, resource_name, YOP;
        """
        yield (form_input, query)
    elif request.param == "Filter by parent title":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (  #TEST: TypeError: add_file() takes from 3 to 5 positional arguments but 6 were given --> self = <flask.testing.EnvironBuilder object at 0x7f2f05251490>, key = 'display_fields', value = (('resource_name', 'Item Name'), ('DOI', 'DOI'), ('parent_title', 'Parent Title'), ('parent_DOI', 'Parent DOI'))
                ('resource_name', "Item Name"),
                ('parent_title', "Parent Title"),
                ('parent_DOI', "Parent DOI"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'publication_date_start_filter': None,
            'publication_date_end_filter': None,
            'ISBN_filter': None,
            'ISSN_filter': None,
            'parent_title_filter': "glq",
            'parent_ISBN_filter': None,
            'parent_ISSN_filter': None,
            'data_type_filter': (
                forms.data_type_values['Article'],
                forms.data_type_values['Database_Full_Item'],
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['No_License'],
                forms.metric_type_values['Limit_Exceeded'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, parent_title, parent_DOI, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                report_type='IR'
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (parent_title='GLQ: A Journal of Lesbian and Gay Studies')
                AND (data_type='Article' OR data_type='Database' OR data_type='Database_Full_Item')
                AND (metric_type='Total_Item_Investigations' OR metric_type='No_License' OR metric_type='Access denied: content item not licensed' OR metric_type='Limit_Exceeded' OR metric_type='Access denied: concurrent/simultaneous user license limit exceeded' OR metric_type='Access denied: concurrent/simultaneous user license exceeded. (Currently N/A to all platforms).')
            GROUP BY usage_count, resource_name, parent_DOI;
        """  # Parent title based off of value returned in test data
        yield (form_input, query)
    elif request.param == "Filter by parent ISBN":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (  #TEST: TypeError: add_file() takes from 3 to 5 positional arguments but 6 were given --> self = <flask.testing.EnvironBuilder object at 0x7f2f05763f40>, key = 'display_fields' value = (('resource_name', 'Item Name'), ('ISBN', 'ISBN'), ('parent_title', 'Parent Title'), ('parent_ISBN', 'Parent ISBN'))
                ('resource_name', "Item Name"),
                ('ISBN', "ISBN"),
                ('parent_ISBN', "Parent ISBN"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'publication_date_start_filter': None,
            'publication_date_end_filter': None,
            'ISBN_filter': None,
            'ISSN_filter': None,
            'parent_title_filter': None,
            'parent_ISBN_filter': "978-0-8223-8491-5",
            'parent_ISSN_filter': None,
            'data_type_filter': (
                forms.data_type_values['Book_Segment'],
                forms.data_type_values['Other'],
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Total_Item_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, ISBN, parent_ISBN, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                report_type='IR'
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (ISBN='978-0-8223-8491-5')
                AND (data_type='Book_Segment' OR data_type='Other')
                AND (metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Successful Full-text Article Requests' Or metric_type='Successful Title Requests' OR metric_type='Successful Section Requests' OR metric_type='Successful Content Unit Requests')
            GROUP BY usage_count, resource_name;
        """
        yield (form_input, query)
    elif request.param == "Filter by parent ISSN":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (  #TEST: TypeError: add_file() takes from 3 to 5 positional arguments but 6 were given --> self = <flask.testing.EnvironBuilder object at 0x7f2f051da4c0>, key = 'display_fields' value = (('resource_name', 'Item Name'), ('parent_title', 'Parent Title'), ('parent_print_ISSN', 'Parent Print ISSN'), ('parent_online_ISSN', 'Parent Online ISSN'))
                ('parent_title', "Parent Title"),
                ('parent_print_ISSN', "Parent Print ISSN"),
                ('parent_online_ISSN', "Parent Online ISSN"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'publication_date_start_filter': None,
            'publication_date_end_filter': None,
            'ISBN_filter': None,
            'ISSN_filter': None,
            'parent_title_filter': None,
            'parent_ISBN_filter': None,
            'parent_ISSN_filter': "0270-5346",
            'data_type_filter': (
                forms.data_type_values['Article'],
                forms.data_type_values['Other'],
            ),
            'YOP_start_filter': None,
            'YOP_end_filter': None,
            'access_type_filter': tuple(forms.access_type_values),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Unique_Item_Investigations'],
                forms.metric_type_values['Unique_Item_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT parent_title, parent_print_ISSN, parent_online_ISSN, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                report_type='IR'
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (parent_print_ISSN='0270-5346' OR parent_online_ISSN='0270-5346')
                AND (data_type='Article' OR data_type='Other')
                AND (metric_type='Unique_Item_Investigations' OR metric_type='Unique_Item_Requests')
            GROUP BY usage_count, parent_title;
        """
        yield (form_input, query)


def test_construct_IR_query_with_wizard(engine, client, header_value, IR_parameters, COUNTER_download_CSV, caplog):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.construct_IR_query_with_wizard()`
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`

    form_input, query = IR_parameters
    log.debug(f"The form input is type {type(form_input)} and the query is type {type(query)}.")
    POST_response = client.post(  #TEST: Errors raised here
        '/view_usage/query-wizard/IR',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?

    log.debug(check_if_file_exists_statement(COUNTER_download_CSV))
    CSV_df = pd.read_csv(  #TEST: FileNotFoundError: [Errno 2] No such file or directory: '/nolcat/nolcat/view_usage/downloads/NoLCAT_download.csv'
        COUNTER_download_CSV,
        index=False,
        parse_dates=['usage_date'],
        date_parser=date_parser,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    CSV_df = CSV_df.astype(COUNTERData.state_data_types())
    database_df = query_database(
        query=query,
        engine=engine,
        index='COUNTER_data_ID',
    )
    if isinstance(database_df, str):
        pytest.skip(database_function_skip_statements(database_df))
    database_df = database_df.astype(COUNTERData.state_data_types())

    assert POST_response.status == "200 OK"
    assert COUNTER_download_CSV.is_file()
    assert_frame_equal(CSV_df, database_df)
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


def construct_PR_query_with_wizard_without_string_match(client, header_value, caplog):
    """Tests using the PR query wizard with a string that won't return any matches."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.construct_PR_query_with_wizard()`

    form_input = {
        'begin_date': date.fromisoformat('2019-01-01'),
        'end_date': date.fromisoformat('2019-12-31'),
        'display_fields': (
            ('platform', "Platform"),
            ('data_type', "Data Type"),
            ('access_method', "Access Method"),
        ),
        'platform_filter': "not going to match",
        'data_type_filter': (forms.data_type_values['Platform']),
        'access_method_filter': tuple(forms.access_method_values),
        'metric_type_filter': (
            forms.metric_type_values['Searches_Platform'],
            forms.metric_type_values['Total_Item_Investigations'],
            forms.metric_type_values['Unique_Item_Investigations'],
            forms.metric_type_values['Unique_Title_Investigations'],
            forms.metric_type_values['Total_Item_Requests'],
            forms.metric_type_values['Unique_Item_Requests'],
            forms.metric_type_values['Unique_Title_Requests'],
        ),
        'open_in_Excel': False,
    }

    POST_response = client.post(
        '/view_usage/query-wizard/PR',
        #timeout=90,  # `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    assert POST_response.status == "200 OK"
    assert "No platforms in the database were matched to the value not going to match." in prepare_HTML_page_for_comparison(POST_response.data)


def test_GET_request_for_download_non_COUNTER_usage(engine, client, caplog):
    """Tests that the page for downloading non-COUNTER compliant files can be successfully GET requested and that the response properly populates with the requested data."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `create_AUCT_SelectField_options()` and `query_database()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.download_non_COUNTER_usage()`
 
    page = client.get('/view_usage/non-COUNTER-downloads')
    GET_soup = BeautifulSoup(page.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1
    GET_select_field_options = []
    log.info(f"`GET_soup`:\n{GET_soup}")  #temp
    log.info(f"`GET_soup.find(name='select', id='AUCT_of_file_download')` (type {type(GET_soup.find(name='select', id='AUCT_of_file_download'))}):\n{GET_soup.find(name='select', id='AUCT_of_file_download')}")  #temp
    for child in GET_soup.find(name='select', id='AUCT_of_file_download').children:
        tuple_content = re.search(r"\((\d*),\s(\d*)\)", child['value'])
        GET_select_field_options.append((
            tuple([int(i) for i in tuple_content.group(1, 2)]),
            str(child.string),
        ))
    
    with open(TOP_NOLCAT_DIRECTORY / 'nolcat' / 'view_usage' / 'templates' / 'view_usage' / 'download-non-COUNTER-usage.html', 'br') as HTML_file:
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1
    db_select_field_options = query_database(
        query="""
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
        engine=engine,
    )
    if isinstance(db_select_field_options, str):
        pytest.skip(database_function_skip_statements(db_select_field_options))
    db_select_field_options = create_AUCT_SelectField_options(db_select_field_options)

    assert page.status == "200 OK"
    assert HTML_file_title == GET_response_title
    assert HTML_file_page_title == GET_response_page_title
    assert GET_select_field_options == db_select_field_options


def test_download_non_COUNTER_usage(client, header_value, non_COUNTER_AUCT_object_after_upload, non_COUNTER_file_to_download_from_S3, caplog):  # `non_COUNTER_file_to_download_from_S3()` not called but used to create file in S3 and instance and remove file from S3 for tests
    """Tests downloading the file at the path selected in the `view_usage.ChooseNonCOUNTERDownloadForm` form."""
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `view_usage.views.download_non_COUNTER_usage()`
    
    form_input = {
        'AUCT_of_file_download': f"({non_COUNTER_AUCT_object_after_upload.AUCT_statistics_source}, {non_COUNTER_AUCT_object_after_upload.AUCT_fiscal_year})",  # The string of a tuple is what gets returned by the actual form submission in Flask; trial and error determined that for tests to pass, that was also the value that needed to be passed to the POST method
    }
    POST_response = client.post(
        '/view_usage/non-COUNTER-downloads',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        follow_redirects=True,
        headers=header_value,
        data=form_input,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    file_path = views.create_downloads_folder() / f'{non_COUNTER_AUCT_object_after_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_after_upload.AUCT_fiscal_year}.{non_COUNTER_AUCT_object_after_upload.usage_file_path.split(".")[-1]}'
    #ToDo: Read file at file_path
    
    log.info(f"Location of downloaded file: {file_path.is_file()}")  #TEST: confirm assert
    #ToDo: Confirm contents of file at `file_path` and file at `non_COUNTER_AUCT_object_after_upload.usage_file_path` are the same
    assert POST_response.status == "200 OK"
    # Currently unable to interact with files on host machine, so unable to confirm downloaded file is a file on the host machine