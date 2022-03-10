"""Tests the methods in StatisticsSources."""

import json
from random import sample
import datetime
import pytest
import pandas as pd
from pandas._testing import assert_frame_equal
from dateutil import relativedelta  # dateutil is a pandas dependency, so it doesn't need to be in requirements.txt
from sqlalchemy.orm import sessionmaker

from nolcat.SQLAlchemy_engine import engine as _engine
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE
from database_seeding_fixtures import vendors_relation
from database_seeding_fixtures import statisticsSources_relation


@pytest.fixture(scope="module")
def engine():
    """Creates a SQLAlchemy engine object by calling the `create_engine` function with the appropriate variables."""
    yield _engine()


@pytest.fixture(scope='module')
def session(engine):
    """Creates a SQLAlchemy session object so all tests in this module run within a transaction that will be rolled back once the tests are complete."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)
    yield session
    connection.close()
    session.close()
    transaction.rollback()


@pytest.fixture
def most_recent_month_with_usage():
    """Creates the value that will be used for the `begin_date` SUSHI parameter and for database queries in other locations in the testing module."""
    current_date = datetime.date.today()
    if current_date.day < 10:
        begin_month = current_date + relativedelta(months=-2)
        yield begin_month.replace(day=1)
    else:
        begin_month = current_date + relativedelta(months=-1)
        yield begin_month.replace(day=1)


@pytest.fixture
def statisticsSources_fixture(most_recent_month_with_usage):
    """Creates a dataframe for loading into the statisticsSources relation with data for creating StatisticsSources objects.
    
    This fixture modifies the `statisticsSources_relation` fixture from the  `database_seeding_fixtures` helper module by replacing the values in `statisticsSources_relation['Statistics_Source_Retrieval_Code']` with retrieval code values found in "R5_SUSHI_credentials.json" so any SUSHI API calls will work. Because the `_harvest_R5_SUSHI` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics cannot be used.
    """
    #Section: Get List of StatisticsSources.statistics_source_retrieval_code Values
    retrieval_codes_as_interface_IDs = []
    with open(PATH_TO_CREDENTIALS_FILE()) as JSON_file:
        SUSHI_data_file = json.load(JSON_file)
        for vendor in SUSHI_data_file:
            for stats_source in vendor['interface']:
                if "interface_id" in list(stats_source.keys()):
                        retrieval_codes_as_interface_IDs.append(stats_source['interface_id'])
    
    #Section: Remove Values for Ineligible Statistics Sources
    #ToDo: retrieval_codes = []
    #ToDo: for interface in list_of_interface_IDs:
        #ToDo: query database: for interface, find the StatisticsSources.statistics_source_id, then find any usage data from that stats source from month most_recent_month_with_usage
        #ToDo: if the above returns an empty set:
            #ToDo: retrieval_codes.append(interface)
    
    #Section: Create Dataframe
    #ToDo: df = statisticsSources_relation
    #ToDo: number_of_records = number of records in df
    #ToDo: retrieval_code_series = sample(retrieval_codes, number_of_records)
    #ToDo: Replace series `df['Statistics_Source_Retrieval_Code']` with retrieval_code_series
    #ToDo: yield df
    pass


def test_engine_creation(engine_fixture):
    """Test that a SQLAlchemy engine is created."""
    assert repr(type(engine_fixture)) == "<class 'sqlalchemy.engine.base.Engine'>"


def test_loading_into_relation(engine, vendors_relation, statisticsSources_fixture):
    """Test using the engine to load and query data.
    
    This is a basic integration test, determining if dataframes cna be loaded into the database and if data can be queried out of the database, not a StatisticsSources method test. All of those method tests, however, require the database I/O to be working and the existence of data in the `statisticsSources` and `vendors` relations; this test checks the former and ensures the latter.
    """
    ###ToDo: Confirm that the imported fixture can be used as an argument directly
    #ToDo: vendors_relation.to_sql(
        # name='vendors',
        # con=engine,
        # if_exists='replace',  # This removes the existing data and replaces it with the data from the fixture, ensuring that PK duplication and PK-FK matching problems don't arise; the rollback at the end of the test restores the original data
        # chunksize=1000,
        # index=True,
        # index_label='Vendor_ID',
    #ToDo: )
    #ToDo: statisticsSources_fixture.to_sql(
        # name='statisticsSources',
        # con=engine,
        # if_exists='replace',
        # chunksize=1000,
        # index=True,
        # index_label='Statistics_Source_ID',
    #ToDo: )

    #ToDo: retrieved_vendors_data = pd.read_sql(
        # sql="SELECT * FROM vendors;",
        # con=engine,
        # index_col='Vendor_ID',
    #ToDo: )
    #ToDo: retrieved_statisticsSources_data = pd.read_sql(
        # sql="SELECT * FROM statisticsSources;",
        # con=engine,
        # index_col='Statistics_Source_ID',
    #ToDo: )

    #ToDo: assert_frame_equal(vendors_relation, retrieved_vendors_data) and assert_frame_equal(statisticsSources_fixture, retrieved_statisticsSources_data)
    pass


def test_fetch_SUSHI_information_for_API():
    """Test collecting SUSHI credentials based on a StatisticsSources.statistics_source_retrieval_code value and returning a value suitable for use in a API call."""
    #ToDo: Query database to get data for a StatisticsSources object
    #ToDo: stats_source = StatisticsSources object based on above data
    #ToDo: credentials = stats_source.fetch_SUSHI_information()
    #ToDo: assert credentials['customer_id'] exists and credentials['URL'] matches regex /https?:\/\/.*\//
    pass


def test_fetch_SUSHI_information_for_display():
    """Test collecting SUSHI credentials based on a StatisticsSources.statistics_source_retrieval_code value and returning the credentials for user display."""
    #ToDo: Query database to get data for a StatisticsSources object
    #ToDo: stats_source = StatisticsSources object based on above data
    #ToDo: credentials = stats_source.fetch_SUSHI_information(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


def test_harvest_R5_SUSHI(most_recent_month_with_usage):
    """Tests collecting all available R5 reports for a StatisticsSources.statistics_source_retrieval_code value and combining them into a single dataframe."""
    #ToDo: Query database to get data for a StatisticsSources object
    #ToDo: stats_source = StatisticsSources object based on above data
    #ToDo: last_day = the last day of the month represented by most_recent_month_with_usage
    #ToDo: SUSHI_data = stats_source._harvest_R5_SUSHI(most_recent_month_with_usage, last_day)
    #ToDo: assert SUSHI_data is a dataframe; what else can be checked to confirm the right data was returned?
    pass


def test_collect_usage_statistics(most_recent_month_with_usage):
    """Tests wrapping SUSHI usage data in a RawCOUNTERReport object."""
    #ToDo: Query database to get data for a StatisticsSources object
    #ToDo: stats_source = StatisticsSources object based on above data
    #ToDo: last_day = the last day of the month represented by most_recent_month_with_usage
    #ToDo: wrapped_data = stats_source.collect_usage_statistics(most_recent_month_with_usage, last_day)
    #ToDo: assert wrapped_data is a RawCOUNTERReport
    pass


def test_upload_R4_report():
    #ToDo: Outline a test when outlining the method
    pass


def test_upload_R5_report():
    #ToDo: Outline a test when outlining the method
    pass