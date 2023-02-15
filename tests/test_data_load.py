"""This module consists exclusively of a fixture for loading the test data for the relations into the relational database. Its purpose is to quickly add the test data to the database; since the data rollback functionality has not yet been established, data loaded into the database via this module will persist past the completion of the pytest session and must be deleted manually."""

import pytest
import sys
import pyinputplus as pyip
import pandas as pd
from sqlalchemy import exc

# `conftest.py` fixtures are imported automatically
from data import relations


@pytest.fixture(scope='module')
def load_test_data_into_database(engine):
    """Loads the test data into the relation chosen by the user."""
    relation_name = pyip.inputMenu(
        prompt="Enter the number of the relation that should have test data loaded into it.\n",
        choices=[
            "fiscalYears",
            "vendors",
            "vendorNotes",
            "statisticsSources",
            "statisticsSourceNotes",
            "resourceSources",
            "resourceSourceNotes",
            "statisticsResourceSources",
            "annualUsageCollectionTracking",
            "COUNTERData",
        ],
        numbered=True,
    )
    
    check_for_data = pd.read_sql(
        sql=f"SELECT COUNT(*) FROM {relation_name};",
        con=engine,
    )
    if not check_for_data.empty or not check_for_data.isnull().all().all():
        return f"The `{relation_name}` relation already has data in it, so there will either be an error when attempting to load the test data or data in other relations won't be appropriately matched. To prevent either of those problems, the program is quitting now without loading any data into the selected relation; please use the MySQL command line or the `db-actions` script's truncate function, both in the instance, to remove all data from the relation before trying again."
    
    if relation_name == "fiscalYears":
        relation_data = relations.fiscalYears_relation()
    elif relation_name == "vendors":
        relation_data = relations.vendors_relation()
    elif relation_name == "vendorNotes":
        relation_data = relations.vendorNotes_relation()
    elif relation_name == "statisticsSources":
        relation_data = relations.statisticsSources_relation()
    elif relation_name == "statisticsSourceNotes":
        relation_data = relations.statisticsSourceNotes_relation()
    elif relation_name == "resourceSources":
        relation_data = relations.resourceSources_relation()
    elif relation_name == "resourceSourceNotes":
        relation_data = relations.resourceSourceNotes_relation()
    elif relation_name == "statisticsResourceSources":
        relation_data = relations.statisticsResourceSources_relation()
    elif relation_name == "annualUsageCollectionTracking":
        relation_data = relations.annualUsageCollectionTracking_relation()
    elif relation_name == "COUNTERData":
        relation_data = relations.COUNTERData_relation()
    
    try:
        relation_data.to_sql(
            relation_name,
            con=engine,
            if_exists='append',
        )
    except exc.IntegrityError as error:
        return f"The `to_sql` method raised an IntegrityError: {error.orig.args}"
    except Exception as error:
            return f"The `to_sql` method raised an exception: {error.orig.args}"

    return f"The test data was loaded into {relation_name}."


def test_data_load_function(load_test_data_into_database):
    """The pytest function that runs the `load_test_data_into_database` fixture."""
    print(load_test_data_into_database)
    assert load_test_data_into_database.startswith("The test data was loaded into ")  # String method returns Boolean true if the load is successful, so the test's pass or fail will match the success of the load 