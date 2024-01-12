"""Tests the routes in the `view_usage` blueprint."""
########## Passing 2024-01-11 ##########

import pytest
import logging
from pathlib import Path
import os
from random import choice
import re
from bs4 import BeautifulSoup
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *
from nolcat.statements import *
from nolcat.view_usage import *

log = logging.getLogger(__name__)


@pytest.fixture
def remove_COUNTER_download_CSV():
    """Removes a CSV download of COUNTER usage data.

    This fixture exists purely for cleanup--the file is created by the function being tested. Since fixtures only accept other fixtures as arguments, this cannot be used for files of various names.

    Yields:
        None
    """
    file_path = TOP_NOLCAT_DIRECTORY / 'nolcat' / 'view_usage' / 'NoLCAT_download.csv'
    yield None
    try:
        file_path.unlink()
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


def test_run_custom_SQL_query(client, header_value, remove_COUNTER_download_CSV, caplog):  # `remove_COUNTER_download_CSV()` not called but used to remove file loaded during test
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
    assert Path(TOP_NOLCAT_DIRECTORY, 'nolcat', 'view_usage', 'NoLCAT_download.csv').is_file()
    #ToDo: Should the presence of the above file in the host computer's file system be checked?


def test_use_predefined_SQL_query(engine, client, header_value, remove_COUNTER_download_CSV, caplog):  # `remove_COUNTER_download_CSV()` not called but used to remove file loaded during test
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
        TOP_NOLCAT_DIRECTORY / 'nolcat' / 'view_usage' / 'NoLCAT_download.csv',
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
    assert Path(TOP_NOLCAT_DIRECTORY, 'nolcat', 'view_usage', 'NoLCAT_download.csv').is_file()
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
    "Filter by metric type and limit fields in results",
    "Filter by platform name",
    "Filter by data type with field not in results"
    "Filter by access method",
])
def PR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    PR_display_fields = (
        ('platform', "Platform"),
        ('data_type', "Data Type"),
        ('access_method', "Access Method"),
    )
    PR_data_types = (
        forms.data_type_values['Article'],
        forms.data_type_values['Audiovisual'],
        forms.data_type_values['Book'],
        forms.data_type_values['Book_Segment'],
        forms.data_type_values['Conference'],
        forms.data_type_values['Conference_Item'],
        forms.data_type_values['Database_Full_Item'],
        forms.data_type_values['Dataset'],
        forms.data_type_values['Image'],
        forms.data_type_values['Interactive_Resource'],
        forms.data_type_values['Journal'],
        forms.data_type_values['Multimedia'],
        forms.data_type_values['News_Item'],
        forms.data_type_values['Newspaper_or_Newsletter'],
        forms.data_type_values['Other'],
        forms.data_type_values['Patent'],
        forms.data_type_values['Platform'],
        forms.data_type_values['Reference_Item'],
        forms.data_type_values['Reference_Work'],
        forms.data_type_values['Report'],
        forms.data_type_values['Repository_Item'],
        forms.data_type_values['Software'],
        forms.data_type_values['Sound'],
        forms.data_type_values['Standard'],
        forms.data_type_values['Thesis_or_Dissertation'],
        forms.data_type_values['Unspecified'],
    )
    PR_metric_types = (
        forms.metric_type_values['Searches_Platform'],
        forms.metric_type_values['Total_Item_Investigations'],
        forms.metric_type_values['Unique_Item_Investigations'],
        forms.metric_type_values['Unique_Title_Investigations'],
        forms.metric_type_values['Total_Item_Requests'],
        forms.metric_type_values['Unique_Item_Requests'],
        forms.metric_type_values['Unique_Title_Requests'],
    )

    if request.param == "Filter by metric type and limit fields in results":
        form_input = {
            'begin_date': date.fromisoformat('2016-07-01'),
            'end_date': date.fromisoformat('2017-06-30'),
            'display_fields': (
                ('platform', "Platform"),
                ('access_method', "Access Method"),
            ),
            'platform_filter': None,
            'data_type_filter': PR_data_types,
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Searches_Platform'],
                forms.metric_type_values['Total_Item_Investigations'],
                forms.metric_type_values['Total_Item_Requests'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='2016-07-01' AND usage_date<='2017-06-30'
                AND (metric_type='Searches_Platform' OR metric_type='Regular Searches' OR metric_type='Total_Item_Investigations' OR metric_type='Total_Item_Requests' OR metric_type='Successful Full-text Article Requests' OR metric_type='Successful Title Requests' OR metric_type='Successful Section Requests' OR metric_type='Successful Content Unit Requests')
            GROUP BY usage_count, platform, access_method;
        """
        yield (form_input, query)
    elif request.param == "Filter by platform name":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': PR_display_fields,
            'platform_filter': "EBSCO",
            'data_type_filter': PR_data_types,
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': PR_metric_types,
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, data_type, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND platform LIKE 'EBSCOhost'
            GROUP BY usage_count, data_type, access_method, metric_type, usage_date;
        """  # With the test data, the only fuzzy match to `EBSCO` will be `EBSCOhost`
        yield (form_input, query)
    elif request.params == "Filter by data type with field not in results":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('platform', "Platform"),
                ('access_method', "Access Method"),
            ),
            'platform_filter': None,
            'data_type_filter': (forms.data_type_values['Platform']),
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': PR_metric_types,
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (data_type='Platform')
            GROUP BY usage_count, platform, access_method, metric_type;
        """
        yield (form_input, query)
    elif request.params == "Filter by access method":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': PR_display_fields,
            'platform_filter': None,
            'data_type_filter': PR_data_types,
            'access_method_filter': (('Regular', "Regular")),
            'metric_type_filter': PR_metric_types,
            'open_in_Excel': False,
        }
        query = """
            SELECT platform, data_type, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='PR' OR report_type='PR1')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (access_method='Regular')
            GROUP BY usage_count, platform, data_type, metric_type;
        """
        yield (form_input, query)



def test_construct_PR_query_with_wizard(PR_parameters):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    pass


@pytest.fixture(params=[
    "Filter by metric types and limit fields in results",
    "Filter by resource name",
    "Filter by publisher name",
])
def DR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    DR_display_fields = (
        ('resource_name', "Database Name"),
        ('publisher', "Publisher"),
        ('platform', "Platform"),
        ('data_type', "Data Type"),
        ('access_method', "Access Method"),
    )
    DR_data_types = (
        forms.data_type_values['Audiovisual'],
        forms.data_type_values['Book'],
        forms.data_type_values['Conference'],
        forms.data_type_values['Database_Aggregated'],
        forms.data_type_values['Database_AI'],
        forms.data_type_values['Database_Full'],
        forms.data_type_values['Database'],
        forms.data_type_values['Database_Full_Item'],
        forms.data_type_values['Image'],
        forms.data_type_values['Interactive_Resource'],
        forms.data_type_values['Journal'],
        forms.data_type_values['Multimedia'],
        forms.data_type_values['Newspaper_or_Newsletter'],
        forms.data_type_values['Other'],
        forms.data_type_values['Patent'],
        forms.data_type_values['Reference_Work'],
        forms.data_type_values['Report'],
        forms.data_type_values['Sound'],
        forms.data_type_values['Standard'],
        forms.data_type_values['Thesis_or_Dissertation'],
        forms.data_type_values['Unspecified'],
    )
    DR_metric_types = (
        forms.metric_type_values['Searches_Regular'],
        forms.metric_type_values['Searches_Automated'],
        forms.metric_type_values['Searches_Federated'],
        forms.metric_type_values['Total_Item_Investigations'],
        forms.metric_type_values['Unique_Item_Investigations'],
        forms.metric_type_values['Unique_Title_Investigations'],
        forms.metric_type_values['Total_Item_Requests'],
        forms.metric_type_values['Unique_Item_Requests'],
        forms.metric_type_values['Unique_Title_Requests'],
        forms.metric_type_values['No_License'],
        forms.metric_type_values['Limit_Exceeded'],
    )

    if request.param == "Filter by metric types and limit fields in results":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': (
                ('resource_name', "Database Name"),
                ('publisher', "Publisher"),
                ('platform', "Platform"),
            ),
            'resource_name_filter': None,
            'publisher_filter': None,
            'platform_filter': None,
            'data_type_filter': DR_data_types,
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': (
                forms.metric_type_values['Searches_Regular'],
                forms.metric_type_values['Searches_Automated'],
                forms.metric_type_values['Searches_Federated'],
                forms.metric_type_values['No_License'],
                forms.metric_type_values['Limit_Exceeded'],
            ),
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publisher, platform, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (metric_type='Searches_Regular' OR metric_type='Regular Searches' OR metric_type='Searches_Automated' OR metric_type='Searches-federated and automated' OR metric_type='Searches: federated and automated' OR metric_type='Searches_Federated' OR metric_type='Searches-federated and automated' OR metric_type='Searches: federated and automated' OR metric_type='No_License' OR metric_type='Access denied: content item not licensed' OR metric_type='Limit_Exceeded' OR metric_type='Access denied: concurrent/simultaneous user license limit exceeded' OR metric_type='Access denied: concurrent/simultaneous user license exceeded. (Currently N/A to all platforms).')
            GROUP BY usage_count, resource_name, publisher, platform;
        """
        yield (form_input, query)
    elif request.param == "Filter by resource name":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': DR_display_fields,
            'resource_name_filter': "eric",
            'publisher_filter': None,
            'platform_filter': None,
            'data_type_filter': DR_data_types,
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': DR_metric_types,
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publisher, platform, data_type, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (resource_name='ERIC' OR resource_name='Historical Abstracts' OR resource_name='Periodicals Archive Online->Periodicals Archive Online Foundation Collection 3' OR resource_name='Periodicals Archive Online->Periodicals Archive Online Foundation Collection 2' OR resource_name='Periodicals Archive Online->Periodicals Archive Online Foundation Collection' OR resource_name='Periodicals Archive Online Foundation Collection 2' OR resource_name='Periodicals Archive Online Foundation Collection 3' OR resource_name='01 Periodicals Archive Online Foundation Collection 1' OR resource_name='Social Science Premium Collection->Education Collection->ERIC')
            GROUP BY usage_count, publisher, platform, data_type, access_method, metric_type;
        """  # Resource names based off of values returned in test data
        yield (form_input, query)
    elif request.param == "Filter by publisher name":
        form_input = {
            'begin_date': date.fromisoformat('2019-01-01'),
            'end_date': date.fromisoformat('2019-12-31'),
            'display_fields': DR_display_fields,
            'resource_name_filter': None,
            'publisher_filter': "proq",
            'platform_filter': None,
            'data_type_filter': DR_data_types,
            'access_method_filter': tuple(forms.access_method_values),
            'metric_type_filter': DR_metric_types,
            'open_in_Excel': False,
        }
        query = """
            SELECT resource_name, publisher, platform, data_type, access_method, metric_type, usage_date, SUM(usage_count)
            FROM COUNTERData
            WHERE
                (report_type='DR' OR report_type='DB1' OR report_type='DB2')
                AND usage_date>='2019-01-01' AND usage_date<='2019-12-31'
                AND (publisher='ProQuest')
            GROUP BY usage_count, resource_name, platform, data_type, access_method, metric_type;
        """  # Publisher name based off of values returned in test data
        yield (form_input, query)


def test_construct_DR_query_with_wizard(DR_parameters):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    pass


@pytest.fixture(params=[
    "Filter by resource name with apostrophe and non-ASCII character",
    "Filter by ISBN",
    "Filter by ISSN",
    "Filter by section type",
    "Filter by year of publication",
    "Filter by access type",
])
def TR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    if request.param == "Filter by resource name with apostrophe and non-ASCII character":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by ISBN":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by ISSN":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by section type":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by year of publication":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by access type":
        #ToDo: Create form input and SQL query


def test_construct_TR_query_with_wizard(TR_parameters):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    pass


@pytest.fixture(params=[
    "Filter by publication date",
    "Filter by parent title",
    "Filter by parent ISBN",
    "Filter by parent ISSN",
])
def IR_parameters(request):
    """A parameterized fixture function for simulating multiple custom query constructions.

    Args:
        request (str): description of the use case

    Yields:
        tuple: the `form_input` argument of the test's `post()` method (dict); the SQL query the wizard should construct (str)
    """
    if request.param == "Filter by publication date":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by parent title":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by parent ISBN":
        #ToDo: Create form input and SQL query
    elif request.param == "Filter by parent ISSN":
        #ToDo: Create form input and SQL query


def test_construct_IR_query_with_wizard(IR_parameters):
    """Tests downloading the results of a query for platform usage data constructed with a form."""
    pass


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


def test_download_non_COUNTER_usage(client, header_value, non_COUNTER_AUCT_object_after_upload, non_COUNTER_file_to_download_from_S3, caplog):  # `non_COUNTER_file_to_download_from_S3()` not called but used to create and remove file from S3 and instance for tests
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
    log.info(f"`POST_response.history` (type {type(POST_response.history)}) is\n{POST_response.history}")  #TEST: temp
    log.info(f"`POST_response.data` (type {type(POST_response.data)}) is very long")  #TEST: temp
    log.info(f"`POST_response.status` (type {type(POST_response.status)}) is\n{POST_response.status}")  #assert POST_response.status == "200 OK"  #TEST: confirm assert
    log.info(f"Location of downloaded file:\n{format_list_for_stdout(Path(TOP_NOLCAT_DIRECTORY, 'nolcat', 'view_usage').iterdir())}")  #assert Path(TOP_NOLCAT_DIRECTORY, 'nolcat', 'view_usage', f'{non_COUNTER_AUCT_object_after_upload.AUCT_statistics_source}_{non_COUNTER_AUCT_object_after_upload.AUCT_fiscal_year}.csv').is_file()  #TEST: confirm assert
    # Currently unable to interact with files on host machine, so unable to confirm downloaded file is a file on the host machine
    pass