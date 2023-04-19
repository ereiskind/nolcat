"""Tests the routes in the `initialization` blueprint."""

import pytest
from pathlib import Path
import os
from bs4 import BeautifulSoup
import pandas as pd
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pandas.testing import assert_frame_equal, assert_series_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import date_parser
from nolcat.initialization import *


#Section: Fixtures
@pytest.fixture
def create_fiscalYears_CSV_file(tmp_path, fiscalYears_relation):
    """Create a CSV file with the test data for the `fiscalYears` relation, then removes the file at the end of the test."""
    yield fiscalYears_relation.to_csv(
        tmp_path / 'fiscalYears_relation.csv',
        index_label="fiscal_year_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'fiscalYears_relation.csv')


@pytest.fixture
def create_vendors_CSV_file(tmp_path, vendors_relation):
    """Create a CSV file with the test data for the `vendors` relation, then removes the file at the end of the test."""
    yield vendors_relation.to_csv(
        tmp_path / 'vendors_relation.csv',
        index_label="vendor_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'vendors_relation.csv')


@pytest.fixture
def create_vendorNotes_CSV_file(tmp_path, vendorNotes_relation):
    """Create a CSV file with the test data for the `vendorNotes_relation` relation, then removes the file at the end of the test."""
    yield vendorNotes_relation.to_csv(
        tmp_path / 'vendorNotes_relation.csv',
        index_label="vendor_notes_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'vendorNotes_relation.csv')


@pytest.fixture
def create_statisticsSources_CSV_file(tmp_path, statisticsSources_relation):
    """Create a CSV file with the test data for the `statisticsSources_relation` relation, then removes the file at the end of the test."""
    yield statisticsSources_relation.to_csv(
        tmp_path / 'statisticsSources_relation.csv',
        index_label="statistics_source_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'statisticsSources_relation.csv')


@pytest.fixture
def create_statisticsSourceNotes_CSV_file(tmp_path, statisticsSourceNotes_relation):
    """Create a CSV file with the test data for the `statisticsSourceNotes_relation` relation, then removes the file at the end of the test."""
    yield statisticsSourceNotes_relation.to_csv(
        tmp_path / 'statisticsSourceNotes_relation.csv',
        index_label="statistics_source_notes_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'statisticsSourceNotes_relation.csv')


@pytest.fixture
def create_resourceSources_CSV_file(tmp_path, resourceSources_relation):
    """Create a CSV file with the test data for the `resourceSources_relation` relation, then removes the file at the end of the test."""
    yield resourceSources_relation.to_csv(
        tmp_path / 'resourceSources_relation.csv',
        index_label="resource_source_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'resourceSources_relation.csv')


@pytest.fixture
def create_resourceSourceNotes_CSV_file(tmp_path, resourceSourceNotes_relation):
    """Create a CSV file with the test data for the `resourceSourceNotes_relation` relation, then removes the file at the end of the test."""
    yield resourceSourceNotes_relation.to_csv(
        tmp_path / 'resourceSourceNotes_relation.csv',
        index_label="resource_source_notes_ID",
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'resourceSourceNotes_relation.csv')


@pytest.fixture
def create_statisticsResourceSources_CSV_file(tmp_path, statisticsResourceSources_relation):
    """Create a CSV file with the test data for the `statisticsResourceSources_relation` relation, then removes the file at the end of the test."""
    yield statisticsResourceSources_relation.to_csv(
        tmp_path / 'statisticsResourceSources_relation.csv',
        index_label=["SRS_statistics_source", "SRS_resource_source"],
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'statisticsResourceSources_relation.csv')


@pytest.fixture
def create_blank_annualUsageCollectionTracking_CSV_file(tmp_path):
    """Create a CSV file with the test data resulting from the Cartesian join creating the AUCT template, then removes the file at the end of the test.
    
    The `annualUsageCollectionTracking_relation` fixture represents the aforementioned relation when completely filled out with data. Since this fixture is used to test the CSV created from the Cartesian join in the `collect_AUCT_and_historical_COUNTER_data()` route function, which contains fields for the fiscal year and statistics source name and no values in any other fields, a new dataframe meeting those criteria needed to be created for conversion to the CSV.
    """
    multiindex = pd.DataFrame(
        [
            [0, 0],
            [1, 0],
            [2, 0],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
            [7, 0],
            [9, 0],
            [10, 0],
            [11, 0],
            [0, 1],
            [1, 1],
            [2, 1],
            [3, 1],
            [4, 1],
            [5, 1],
            [6, 1],
            [7, 1],
            [9, 1],
            [10, 1],
            [11, 1],
            [0, 2],
            [1, 2],
            [2, 2],
            [3, 2],
            [4, 2],
            [5, 2],
            [6, 2],
            [7, 2],
            [9, 2],
            [10, 2],
            [11, 2],
            [0, 3],
            [1, 3],
            [2, 3],
            [3, 3],
            [4, 3],
            [5, 3],
            [8, 3],
            [9, 3],
            [10, 3],
            [11, 3],
            [0, 4],
            [1, 4],
            [2, 4],
            [3, 4],
            [4, 4],
            [5, 4],
            [8, 4],
            [9, 4],
            [10, 4],
            [11, 4],
            [0, 5],
            [1, 5],
            [2, 5],
            [3, 5],
            [4, 5],
            [5, 5],
            [8, 5],
            [9, 5],
            [10, 5],
            [11, 5],
        ],
        columns=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    multiindex = pd.MultiIndex.from_frame(multiindex)
    df = pd.DataFrame(
        [
            ["ProQuest", "2017", None, None, None, None, None, None, None],
            ["EBSCOhost", "2017", None, None, None, None, None, None, None],
            ["Gale Cengage Learning", "2017", None, None, None, None, None, None, None],
            ["Duke UP", "2017", None, None, None, None, None, None, None],
            ["iG Library/Business Expert Press (BEP)", "2017", None, None, None, None, None, None, None],
            ["DemographicsNow", "2017", None, None, None, None, None, None, None],
            ["Ebook Central", "2017", None, None, None, None, None, None, None],
            ["Peterson's Career Prep", "2017", None, None, None, None, None, None, None],
            ["Peterson's Prep", "2017", None, None, None, None, None, None, None],
            ["Pivot", "2017", None, None, None, None, None, None, None],
            ["Ulrichsweb", "2017", None, None, None, None, None, None, None],
            ["ProQuest", "2018", None, None, None, None, None, None, None],
            ["EBSCOhost", "2018", None, None, None, None, None, None, None],
            ["Gale Cengage Learning", "2018", None, None, None, None, None, None, None],
            ["Duke UP", "2018", None, None, None, None, None, None, None],
            ["iG Library/Business Expert Press (BEP)", "2018", None, None, None, None, None, None, None],
            ["DemographicsNow", "2018", None, None, None, None, None, None, None],
            ["Ebook Central", "2018", None, None, None, None, None, None, None],
            ["Peterson's Career Prep", "2018", None, None, None, None, None, None, None],
            ["Peterson's Prep", "2018", None, None, None, None, None, None, None],
            ["Pivot", "2018", None, None, None, None, None, None, None],
            ["Ulrichsweb", "2018", None, None, None, None, None, None, None],
            ["ProQuest", "2019", None, None, None, None, None, None, None],
            ["EBSCOhost", "2019", None, None, None, None, None, None, None],
            ["Gale Cengage Learning", "2019", None, None, None, None, None, None, None],
            ["Duke UP", "2019", None, None, None, None, None, None, None],
            ["iG Library/Business Expert Press (BEP)", "2019", None, None, None, None, None, None, None],
            ["DemographicsNow", "2019", None, None, None, None, None, None, None],
            ["Ebook Central", "2019", None, None, None, None, None, None, None],
            ["Peterson's Career Prep", "2019", None, None, None, None, None, None, None],
            ["Peterson's Prep", "2019", None, None, None, None, None, None, None],
            ["Pivot", "2019", None, None, None, None, None, None, None],
            ["Ulrichsweb", "2019", None, None, None, None, None, None, None],
            ["ProQuest", "2020", None, None, None, None, None, None, None],
            ["EBSCOhost", "2020", None, None, None, None, None, None, None],
            ["Gale Cengage Learning", "2020", None, None, None, None, None, None, None],
            ["Duke UP", "2020", None, None, None, None, None, None, None],
            ["iG Library/Business Expert Press (BEP)", "2020", None, None, None, None, None, None, None],
            ["DemographicsNow", "2020", None, None, None, None, None, None, None],
            ["Peterson's Test Prep", "2020", None, None, None, None, None, None, None],
            ["Peterson's Prep", "2020", None, None, None, None, None, None, None],
            ["Pivot", "2020", None, None, None, None, None, None, None],
            ["Ulrichsweb", "2020", None, None, None, None, None, None, None],
            ["ProQuest", "2021", None, None, None, None, None, None, None],
            ["EBSCOhost", "2021", None, None, None, None, None, None, None],
            ["Gale Cengage Learning", "2021", None, None, None, None, None, None, None],
            ["Duke UP", "2021", None, None, None, None, None, None, None],
            ["iG Library/Business Expert Press (BEP)", "2021", None, None, None, None, None, None, None],
            ["DemographicsNow", "2021", None, None, None, None, None, None, None],
            ["Peterson's Test Prep", "2021", None, None, None, None, None, None, None],
            ["Peterson's Prep", "2021", None, None, None, None, None, None, None],
            ["Pivot", "2021", None, None, None, None, None, None, None],
            ["Ulrichsweb", "2021", None, None, None, None, None, None, None],
            ["ProQuest", "2022", None, None, None, None, None, None, None],
            ["EBSCOhost", "2022", None, None, None, None, None, None, None],
            ["Gale Cengage Learning", "2022", None, None, None, None, None, None, None],
            ["Duke UP", "2022", None, None, None, None, None, None, None],
            ["iG Library/Business Expert Press (BEP)", "2022", None, None, None, None, None, None, None],
            ["DemographicsNow", "2022", None, None, None, None, None, None, None],
            ["Peterson's Test Prep", "2022", None, None, None, None, None, None, None],
            ["Peterson's Prep", "2022", None, None, None, None, None, None, None],
            ["Pivot", "2022", None, None, None, None, None, None, None],
            ["Ulrichsweb", "2022", None, None, None, None, None, None, None],
        ],
        index=multiindex,
        columns=["Statistics Source", "Fiscal Year", "usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"],
    )
    df = df.astype({
        "Statistics Source": 'string',
        "Fiscal Year": 'string',
        "usage_is_being_collected": 'bool',
        "manual_collection_required": 'bool',
        "collection_via_email": 'bool',
        "is_COUNTER_compliant": 'bool',
        "collection_status": 'string',
        "usage_file_path": 'string',
        "notes": 'string',
    })
    yield df.to_csv(
        tmp_path / 'annualUsageCollectionTracking_relation.csv',
        index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'annualUsageCollectionTracking_relation.csv')


@pytest.fixture
def create_annualUsageCollectionTracking_CSV_file(tmp_path, annualUsageCollectionTracking_relation):
    """Create a CSV file with the test data for the `annualUsageCollectionTracking_relation` relation, then removes the file at the end of the test."""
    yield annualUsageCollectionTracking_relation.to_csv(
        tmp_path / 'annualUsageCollectionTracking_relation.csv',
        index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
        encoding='utf-8',
        errors='backslashreplace',
    )
    os.remove(tmp_path / 'annualUsageCollectionTracking_relation.csv')


@pytest.fixture
def create_COUNTERData_CSV_file(tmp_path, COUNTERData_relation):
    """Create a CSV file with the test data for the `COUNTERData_relation` relation, then removes the file at the end of the test."""
    yield COUNTERData_relation.to_csv(
        tmp_path / 'COUNTERData_relation.csv',
        index_label="COUNTER_data_ID",
        encoding='utf-8',
        errors='backslashreplace',  
    )
    os.remove(tmp_path / 'COUNTERData_relation.csv')


#Section: Tests
def test_download_file():
    """Tests the route enabling file downloads."""
    #ToDo: How can this route be tested?
    pass


def test_GET_request_for_collect_FY_and_vendor_data(client):
    """Tests that the homepage can be successfully GET requested and that the response matches the file being used."""
    #Section: Get Data from `GET` Requested Page
    homepage = client.get('/initialization/')
    GET_soup = BeautifulSoup(homepage.data, 'lxml')
    GET_response_title = GET_soup.head.title
    GET_response_page_title = GET_soup.body.h1

    #Section: Get Data from HTML File
    with open(Path(os.getcwd(), 'nolcat', 'initialization', 'templates', 'initialization', 'index.html'), 'br') as HTML_file:  # CWD is where the tests are being run (root for this suite)
        file_soup = BeautifulSoup(HTML_file, 'lxml')
        HTML_file_title = file_soup.head.title
        HTML_file_page_title = file_soup.body.h1

    assert homepage.status == "200 OK" and HTML_file_title == GET_response_title and HTML_file_page_title == GET_response_page_title


@pytest.mark.dependency()
def test_collect_FY_and_vendor_data(tmp_path, create_fiscalYears_CSV_file, create_vendors_CSV_file, create_vendorNotes_CSV_file, header_value, client):  # Fixture names aren't invoked, but without them, the files yielded by those fixtures aren't available in the test function
    """Tests uploading CSVs with data in the `fiscalYears`, `vendors`, and `vendorNotes` relations and loading that data into the database."""
    CSV_files = MultipartEncoder({
        'fiscalYears_CSV': ('fiscalYears_relation.csv', open(tmp_path / 'fiscalYears_relation.csv', 'rb')),
        'vendors_CSV': ('vendors_relation.csv', open(tmp_path / 'vendors_relation.csv', 'rb')),
        'vendorNotes_CSV': ('vendorNotes_relation.csv', open(tmp_path / 'vendorNotes_relation.csv', 'rb')),
    })
    header_value['Content-Type'] = CSV_files.content_type
    POST_request = client.post(
        '/initialization/',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        headers=header_value,
        data=CSV_files,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    print(f"`POST_request.history` (type {type(POST_request.history)}): {POST_request.history}")
    print(f"`POST_request.status_code` (type {type(POST_request.status_code)}): {POST_request.status_code}")
    print(f"`POST_request.data` (type {type(POST_request.data)}): {POST_request.data}")
    assert True


@pytest.mark.dependency(depends=['test_collect_FY_and_vendor_data'])
def test_fiscalYears_relation_to_database(engine, fiscalYears_relation):
    """Tests that the `fiscalYears` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_FY_and_vendor_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    fiscalYears_relation_data = pd.read_sql(
        sql="SELECT * FROM fiscalYears;",
        con=engine,
        index_col='fiscal_year_ID',
    )
    fiscalYears_relation_data = fiscalYears_relation_data.astype({
        "fiscal_year": 'string',
        "ACRL_60b": 'Int64',  # Using the pandas data type here because it allows null values
        "ACRL_63": 'Int64',  # Using the pandas data type here because it allows null values
        "ARL_18": 'Int64',  # Using the pandas data type here because it allows null values
        "ARL_19": 'Int64',  # Using the pandas data type here because it allows null values
        "ARL_20": 'Int64',  # Using the pandas data type here because it allows null values
        "notes_on_statisticsSources_used": 'string',  # For `text` data type
        "notes_on_corrections_after_submission": 'string',  # For `text` data type
    })
    fiscalYears_relation_data["start_date"] = pd.to_datetime(fiscalYears_relation_data["start_date"])
    fiscalYears_relation_data["end_date"] = pd.to_datetime(fiscalYears_relation_data["end_date"])
    assert_frame_equal(fiscalYears_relation_data, fiscalYears_relation)


@pytest.mark.dependency(depends=['test_collect_FY_and_vendor_data'])
def test_vendors_relation_to_database(engine, vendors_relation):
    """Tests that the `vendors` relation was was successfully loaded into the database.
    
    This test is separate from the `test_collect_FY_and_vendor_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    vendors_relation_data = pd.read_sql(
        sql="SELECT * FROM vendors;",
        con=engine,
        index_col='vendor_ID',
    )
    vendors_relation_data = vendors_relation_data.astype({
        "vendor_name": 'string',
        "alma_vendor_code": 'string',
    })
    assert_frame_equal(vendors_relation_data, vendors_relation)


@pytest.mark.dependency(depends=['test_collect_FY_and_vendor_data'])
def test_vendorNotes_relation_to_database(engine, vendorNotes_relation):
    """Tests that the `vendorNotes` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_FY_and_vendor_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    vendorNotes_relation_data = pd.read_sql(
        sql="SELECT * FROM vendorNotes;",
        con=engine,
        index_col='vendor_notes_ID',
    )
    vendorNotes_relation_data = vendorNotes_relation_data.astype({
        "note": 'string',  # For `text` data type
        "written_by": 'string',
        "vendor_ID": 'int',
    })
    vendorNotes_relation_data["date_written"] = pd.to_datetime(vendorNotes_relation_data["date_written"])
    assert_frame_equal(vendorNotes_relation_data, vendorNotes_relation)


@pytest.mark.dependency()
def test_collect_sources_data(tmp_path, create_statisticsSources_CSV_file, create_statisticsSourceNotes_CSV_file, create_resourceSources_CSV_file, create_resourceSourceNotes_CSV_file, create_statisticsResourceSources_CSV_file, header_value, client):  # Fixture names aren't invoked, but without them, the files yielded by those fixtures aren't available in the test function
    """Tests uploading CSVs with data in the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relations and loading that data into the database."""
    CSV_files = MultipartEncoder({
        'statisticsSources_CSV': ('statisticsSources_relation.csv', open(tmp_path / 'statisticsSources_relation.csv', 'rb')),
        'statisticsSourceNotes_CSV': ('statisticsSourceNotes_relation.csv', open(tmp_path / 'statisticsSourceNotes_relation.csv', 'rb')),
        'resourceSources_CSV': ('resourceSources_relation.csv', open(tmp_path / 'resourceSources_relation.csv', 'rb')),
        'resourceSourceNotes_CSV': ('resourceSourceNotes_relation.csv', open(tmp_path / 'resourceSourceNotes_relation.csv', 'rb')),
        'statisticsResourceSources_CSV': ('statisticsResourceSources_relation.csv', open(tmp_path / 'statisticsResourceSources_relation.csv', 'rb')),
    })
    header_value['Content-Type'] = CSV_files.content_type
    POST_request = client.post(
        '/initialization/',
        #timeout=90,  #ALERT: `TypeError: __init__() got an unexpected keyword argument 'timeout'` despite the `timeout` keyword at https://requests.readthedocs.io/en/latest/api/#requests.request and its successful use in the SUSHI API call class
        headers=header_value,
        data=CSV_files,
    )  #ToDo: Is a try-except block that retries with a 299 timeout needed?
    pass


@pytest.mark.dependency(depends=['test_collect_sources_data'])
def test_statisticsSources_relation_to_database(engine, statisticsSources_relation):
    """Tests that the `statisticsSources` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_sources_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    statisticsSources_relation_data = pd.read_sql(
        sql="SELECT * FROM statisticsSources;",
        con=engine,
        index_col='statistics_source_ID',
    )
    statisticsSources_relation_data = statisticsSources_relation_data.astype({
        "statistics_source_name": 'string',
        "statistics_source_retrieval_code": 'string',
        "vendor_ID": 'int',
    })
    assert_frame_equal(statisticsSources_relation_data, statisticsSources_relation)


@pytest.mark.dependency(depends=['test_collect_sources_data'])
def test_statisticsSourceNotes_relation_to_database(engine, statisticsSourceNotes_relation):
    """Tests that the `statisticsSourceNotes` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_sources_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    statisticsSourceNotes_relation_data = pd.read_sql(
        sql="SELECT * FROM statisticsSourceNotes;",
        con=engine,
        index_col='statistics_source_notes_ID',
    )
    statisticsSourceNotes_relation_data = statisticsSourceNotes_relation_data.astype({
        "note": 'string',  # For `text` data type
        "written_by": 'string',
        "statistics_source_ID": 'int',
    })
    statisticsSourceNotes_relation_data["date_written"] = pd.to_datetime(statisticsSourceNotes_relation_data["date_written"])
    assert_frame_equal(statisticsSourceNotes_relation_data, statisticsSourceNotes_relation)


@pytest.mark.dependency(depends=['test_collect_sources_data'])
def test_resourceSources_relation_to_database(engine, resourceSources_relation):
    """Tests that the `resourceSources` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_sources_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    resourceSources_relation_data = pd.read_sql(
        sql="SELECT * FROM resourceSources;",
        con=engine,
        index_col='resource_source_ID',
    )
    resourceSources_relation_data = resourceSources_relation_data.astype({
        "resource_source_name": 'string',
        "source_in_use": 'bool',
        "vendor_ID": 'int',
    })
    resourceSources_relation_data["use_stop_date"] = pd.to_datetime(resourceSources_relation_data["use_stop_date"])
    assert_frame_equal(resourceSources_relation_data, resourceSources_relation)


@pytest.mark.dependency(depends=['test_collect_sources_data'])
def test_resourceSourceNotes_relation_to_database(engine, resourceSourceNotes_relation):
    """Tests that the `resourceSourceNotes` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_sources_data()` test function because a single test function can't support multiple `assert_frame_equal` comparisons.
    """
    resourceSourceNotes_relation_data = pd.read_sql(
        sql="SELECT * FROM resourceSourceNotes;",
        con=engine,
        index_col='resource_source_notes_ID',
    )
    resourceSourceNotes_relation_data = resourceSourceNotes_relation_data.astype({
        "note": 'string',  # For `text` data type
        "written_by": 'string',
        "resource_source_ID": 'int',
    })
    resourceSourceNotes_relation_data["date_written"] = pd.to_datetime(resourceSourceNotes_relation_data["date_written"])
    assert_frame_equal(resourceSourceNotes_relation_data, resourceSourceNotes_relation)


@pytest.mark.dependency(depends=['test_collect_sources_data'])
def test_statisticsResourceSources_relation_to_database(engine, statisticsResourceSources_relation):
    """Tests that the `statisticsResourceSources` relation was successfully loaded into the database.
    
    This test is separate from the `test_collect_sources_data()` test function because a single test function can't support multiple `assert_frame_equal` (or, in this case, `assert_series_equal`) comparisons.
    """
    statisticsResourceSources_relation_data = pd.read_sql(
        sql="SELECT * FROM statisticsResourceSources;",
        con=engine,
        index_col=['SRS_statistics_source', 'SRS_resource_source'],
    )
    print(f"`statisticsResourceSources_relation_data`:\n{statisticsResourceSources_relation_data}")  # <class 'pandas.core.frame.DataFrame'>
    print(f"`statisticsResourceSources_relation`:\n{statisticsResourceSources_relation}")  # <class 'pandas.core.series.Series'>
    statisticsResourceSources_relation_data = statisticsResourceSources_relation_data.astype({
        "current_statistics_source": 'bool',
    })
    assert_series_equal(statisticsResourceSources_relation_data, statisticsResourceSources_relation)


@pytest.mark.dependency(depends=['test_collect_sources_data'])
def test_GET_request_for_collect_AUCT_and_historical_COUNTER_data(client, create_blank_annualUsageCollectionTracking_CSV_file):
    """Test creating the AUCT relation template CSV."""
    page = client.get('/initialization/initialization-page-3')
    df_dtypes = {  # Initialized here for reusability
        "Statistics Source": 'string',
        "Fiscal Year": 'string',
        "usage_is_being_collected": 'bool',
        "manual_collection_required": 'bool',
        "collection_via_email": 'bool',
        "is_COUNTER_compliant": 'bool',
        "collection_status": 'string',
        "usage_file_path": 'string',
        "notes": 'string',
    }
    path_to_template = Path(os.getcwd(), 'nolcat', 'initialization', 'initialize_annualUsageCollectionTracking.csv')  # CWD is where the tests are being run (root for this suite)
    AUCT_template_df = pd.read_csv(
        path_to_template,  #ToDo: When download functionality is set up, download CSV and read it into dataframe
        index_col=["AUCT_statistics_source", "AUCT_fiscal_year"],
        dtype=df_dtypes,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    AUCT_fixture_df = pd.read_csv(
        create_blank_annualUsageCollectionTracking_CSV_file,
        index_col=["AUCT_statistics_source", "AUCT_fiscal_year"],
        dtype=df_dtypes,
        encoding='utf-8',
        encoding_errors='backslashreplace',
    )
    assert_frame_equal(AUCT_template_df, AUCT_fixture_df)  #ToDo: Does this work in lieu of a direct comparison between the text file contents?


@pytest.mark.dependency(depends=['test_GET_request_for_collect_AUCT_and_historical_COUNTER_data'])
def test_collect_AUCT_and_historical_COUNTER_data():
    """Tests uploading the AUCT relation CSV and historical tabular COUNTER reports and loading that data into the database."""
    #ToDo: Get the fixture representing the AUCT relation in `conftest.py` to serve as CSVs being uploaded into the rendered form
    #ToDo: Get other files to serve as temp tabular COUNTER report files
    #ToDo: Submit the files to the appropriate forms on the page
    #ToDo: At or after function return statement/redirect, query database for `annualUsageCollectionTracking` and `COUNTERData` relations and ensure results match files used for submitting data and/or `conftest.py`
    pass


@pytest.mark.dependency(depends=['test_GET_request_for_collect_AUCT_and_historical_COUNTER_data'])
def test_GET_request_for_upload_historical_non_COUNTER_usage():
    """Tests creating a form with the option to upload a file for each statistics source and fiscal year combination that's not COUNTER-compliant."""
    #ToDo: Render the page
    #ToDo: Compare the fields in the form on the page to a static list of the test data values that meet the requirements
    pass


@pytest.mark.dependency(depends=['test_GET_request_for_upload_historical_non_COUNTER_usage'])
def test_upload_historical_non_COUNTER_usage():
    """Tests uploading the files with non-COUNTER usage statistics."""
    #ToDo: Get the file paths out of the AUCT relation
    #ToDo: For each file path, get the file at that path and compare its contents to the test data file used to create it
    pass


def test_data_load_complete():
    """Tests calling the route and subsequently rendering the page."""
    #ToDo: Write test once this route contains content for displaying the newly uploaded data in the browser
    pass