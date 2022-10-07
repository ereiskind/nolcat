"""Tests the methods in StatisticsSources."""

import json
from random import sample
import datetime
import pytest
import pandas as pd
from pandas._testing import assert_frame_equal
from dateutil import relativedelta  # dateutil is a pandas dependency, so it doesn't need to be in requirements.txt
from sqlalchemy.orm import sessionmaker

from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE


@pytest.fixture(autouse=True, scope='function')
def CREDENTIALS_FILE_PATH():
    """This will skip the rest of the tests in this module if the nolcat.models.PATH_TO_CREDENTAILS_FILE function doesn't return a string."""
    #ALERT: This is untested
    if str(type(PATH_TO_CREDENTIALS_FILE())) == "<class 'str'>":
        yield PATH_TO_CREDENTIALS_FILE()
    pytest.skip("Credentials file path not available.")


@pytest.fixture(scope='module')
def engine():
    """Creates a SQLAlchemy engine object by calling the `create_engine` function with the appropriate variables."""
    #ToDo: Adjust test to basic "check that program can connect to database" test using Flask-SQLAlchemy
    yield _engine()


@pytest.fixture(scope='module')
def session(engine):
    """Creates a SQLAlchemy session object so all tests in this module run within a transaction that will be rolled back once the tests are complete."""
    #ToDo: Determine if or how a engine creation test works with Flask-SQLAlchemy
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


#ALERT: Couldn't figure out which fixture to retain, so saving both here
@pytest.fixture(scope='session')
def StatisticsSources_fixture_old():
    """A fixture mocking up a StatisticsSources object based on the R5 SUSHI credentials JSON."""
    #ToDo: The fixture currently counts the number of StatisticsSources in the R5 SUSHI credentials JSON and currently chooses a number in that range for the fixture's StatisticsSources.statistics_source_retrieval_code value; all the other attributes are placeholders with static values. Should the randomly selected number be used to retrieve actual values for a StatisticsSources object instead?
    number_of_StatisticsSources = 0
    with open(PATH_TO_CREDENTIALS_FILE) as JSON_file:
        SUSHI_data_file = json.load(JSON_file)
        for vendor in SUSHI_data_file:
            for stats_source in vendor:
                if stats_source['interface_id']:
                    number_of_StatisticsSources += 1
    
    random_StatisticsSources_value = str(randint(1, number_of_StatisticsSources))
    fixture_value = StatisticsSources(
        1,  # StatisticsSources.statistics_source_id
        "StatisticsSources.statistics_source_name",
        random_StatisticsSources_value,
        1,  # StatisticsSources.vendor_id
    )
    return fixture_value


@pytest.fixture
def statisticsSources_fixture_new(CREDENTIALS_FILE_PATH):
    """Creates a dataframe for loading into the statisticsSources relation with data for creating StatisticsSources objects.
    
    This fixture modifies the `statisticsSources_relation` fixture from the  `database_seeding_fixtures` helper module by replacing the values in `statisticsSources_relation['Statistics_Source_Retrieval_Code']` with retrieval code values found in "R5_SUSHI_credentials.json" so any SUSHI API calls will work. Because the `_harvest_R5_SUSHI` method includes a check preventing SUSHI calls to stats source/date combos already in the database, stats sources current with the available usage statistics cannot be used.
    #ALERT: Using just the data from the  `database_seeding_fixtures` helper module, the above described problem will never become an issue, but when running tests on the program in production, which will include more recent data, the above will need to be handled. A plan for removing `statisticsSources` records with usage data from `most_recent_month_with_usage` in the database is outlined in the second section of this function. When the change is made, the `engine` and `most_recent_month_with_usage` fixtures will need to be added as arguments to this test. The piece that needs to be determined is how this function will know if the `usageData` relation has production data.
    """
    #Section: Get List of StatisticsSources.statistics_source_retrieval_code Values
    retrieval_codes_as_interface_IDs = []
    with open(CREDENTIALS_FILE_PATH) as JSON_file:  #Alert: Use of fixture instead of function directly untested
        SUSHI_data_file = json.load(JSON_file)
        for vendor in SUSHI_data_file:
            for stats_source in vendor['interface']:
                if "interface_id" in list(stats_source.keys()):
                        retrieval_codes_as_interface_IDs.append(stats_source['interface_id'])
    
    #Section: Remove Values for Ineligible Statistics Sources
    retrieval_codes = []
    for interface in retrieval_codes_as_interface_IDs:
        retrieval_codes.append(interface)  #ToDo: When rewriting this function per the alert in the docstring, this line will be removed in favor of the identical one below marked as a "ToDo"
        #ToDo: Run query below against database
            # SELECT COUNT(*)
            # FROM usageData
            # JOIN resourcePlatforms ON resourcePlatforms.Resource_Platform_ID=usageData.Resource_Platform_ID
            # JOIN statisticsSources ON statisticsSources.Statistics_Source_ID=resourcePlatforms.Interface
            # WHERE statisticsSources.Statistics_Source_Retrieval_Code = {code}
            # AND WHERE usageData.Usage_Date = {str(most_recent_month_with_usage)};
        #ToDo: if the above returns an empty set:
            #ToDo: retrieval_codes.append(interface)
    
    #Section: Create Dataframe
    df = statisticsSources_relation
    number_of_records = len(df.index)
    retrieval_code_series = sample(retrieval_codes, number_of_records)
    df['Statistics_Source_Retrieval_Code'] = retrieval_code_series
    yield df


def test_loading_into_relation(engine, vendors_relation, statisticsSources_fixture):  #ALERT: Unsure if this should be retained
    """Test using the engine to load and query data.  #ToDo: Change to use Flask-SQLAlchemy connection
    
    This is a basic integration test, determining if dataframes can be loaded into the database and if data can be queried out of the database, not a StatisticsSources method test. All of those method tests, however, require the database I/O to be working and the existence of data in the `statisticsSources` and `vendors` relations; this test checks the former and ensures the latter.
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


def test_fetch_SUSHI_credentials_for_API(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a StatisticsSources.statistics_source_retrieval_code value and returning a value suitable for use in a API call."""
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: credentials = stats.source.fetch_SUSHI_credentials()
    #ToDo: assert credentials == dict and credentials['URL'] matches regex /https?:\/\/.*\//
    pass


def test_fetch_SUSHI_credentials_for_display(StatisticsSources_fixture):
    """Test collecting SUSHI credentials based on a StatisticsSources.statistics_source_retrieval_code value and returning the credentials for user display."""
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: credentials = stats.source.fetch_SUSHI_credentials(False)
    #ToDo: assert `credentials` is displaying credentials to the user
    pass


def test_harvest_R5_SUSHI(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests collecting all available R5 reports for a StatisticsSources.statistics_source_retrieval_code value and combining them into a single dataframe."""
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: last_day = the last day of the month represented by most_recent_month_with_usage
    #ToDo: SUSHI_data = stats_source._harvest_R5_SUSHI(most_recent_month_with_usage, last_day)
    #ToDo: assert `SUSHI_data` is a dataframe; what else can be checked to confirm the right data was returned?
    pass


def test_collect_usage_statistics(StatisticsSources_fixture, most_recent_month_with_usage):
    """Tests the method making the StatisticsSources._harvest_R5_SUSHI result a RawCOUNTERReport object."""
    #ToDo: stats_source = StatisticsSources_fixture
    #ToDo: wrapped_data = stats_source.collect_usage_statistics(most_recent_month_with_usage, last_day)
    #ToDo: assert wrapped_data is a RawCOUNTERReport
    pass


def test_upload_R4_report(StatisticsSources_fixture):
    """Tests the uploading and ingesting of a transformed R4 report."""
    #ToDo: Develop this test alongside the method its testing
    pass


def test_upload_R5_report(StatisticsSources_fixture):
    """Tests the uploading and ingesting of a R5 report."""
    #ToDo: Develop this test alongside the method its testing
    pass