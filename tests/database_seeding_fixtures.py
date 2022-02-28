"""These fixtures add content to any blank relations in the NoLCAT database so all tables have data that can be used in running tests."""

import pytest
import pandas as pd

#ToDo: Create fixture for fiscalYears


#ToDo: Create fixture for vendors


#ToDo: Create fixture for vendorNotes


#ToDo: Create fixture for statisticsSources


#toDo: Create fixture for statisticsSourceNotes


#ToDo: Create fixture for statisticsResourceSources


#ToDo: Create fixture for resourceSources


#ToDo: Create fixture for resourceSourceNotes


#ToDo: Create fixture for annualUsageCollectionTracking


@pytest.fixture
def resources_relation():
    """Creates a dataframe that can be loaded into the `resources` relation."""
    df = pd.DataFrame(
        [
            [None, None, "8755-4550", None, "Serial", None],
            [None, "978-0-585-03362-4", None, None, "Book", None],
        ],
        index=[1, 2],
        columns=["DOI", "ISBN", "Print_ISSN", "Online_ISSN", "Data_Type", "Section_Type"]
    )
    df.index.name = "Resource_ID"
    yield df


#ToDo: Create fixture for resourceTitles


#ToDo: Create fixture for resourcePlatforms


#ToDo: Create fixture for usageData