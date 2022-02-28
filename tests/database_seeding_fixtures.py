"""These fixtures add content to any blank relations in the NoLCAT database so all tables have data that can be used in running tests."""

import pytest
import pandas as pd

@pytest.fixture
def fiscalYears_relation():
    """Creates a dataframe that can be loaded into the `fiscalYears` relation."""
    df = pd.DataFrame(
        [
            ["2017", "2016-07-01", "2017-06-30", None, None, None, None, None, None, None],
            ["2018", "2017-07-01", "2018-06-30", None, None, None, None, None, None, None],
            ["2019", "2018-07-01", "2019-06-30", None, None, None, None, None, None, None],
            ["2020", "2019-07-01", "2020-06-30", None, None, None, None, None, None, None],
            ["2021", "2021-07-01", "2022-06-30", None, None, None, None, None, None, None],
        ],
        index=[1, 2, 3, 4, 5],
        columns=["Year", "Start_Date", "End_Date", "ACRL_60b", "ACRL_63", "ARL_18", "ARL_19", "ARL_20", "Notes_on_statisticsSources_Used", "Notes_on_Corrections_After_Submission"]
    )
    df.index.name = "Fiscal_Year_ID"
    yield df


@pytest.fixture
def vendors_relation():
    """Creates a dataframe that can be loaded into the `vendors` relation."""
    df = pd.DataFrame(
        [
            ["ProQuest", None],
            ["EBSCO", None],
            ["Gale", None],
            ["iG Publishing/BEP", None],
            ["Ebook Library", None],
            ["Ebrary", None],
            ["MyiLibrary", None],
        ],
        index=[1, 2, 3, 4, 5, 6, 7],
        columns=["Vendor_Name", "Alma_Vendor_Code"]
    )
    df.index.name = "Vendor_ID"
    yield df


#ToDo: Create fixture for vendorNotes


@pytest.fixture
def statisticsSources_relation():
    """Creates a dataframe that can be loaded into the `statisticsSources` relation."""
    df = pd.DataFrame(
        [
            ["ProQuest", None, 1],
            ["EBSCOhost", None, 2],
            ["Gale Cengage Learning", None, 3],
            ["iG Library/Business Expert Press (BEP)", None, 4],
            ["DemographicsNow", None, 3],
            ["Ebook Central", None, 1],
            ["Peterson's Career Prep", None, 3],
            ["Peterson's Test Prep", None, 3],
            ["Peterson's Prep", None, 3],
            ["Pivot", None, 1],
            ["Ulrichsweb", None, 1],
        ],
        index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        columns=["Statistics_Source_Name", "Statistics_Source_Retrieval_Code", "Vendor_ID"]
    )
    df.index.name = "Statistics_Source_ID"
    yield df


#toDo: Create fixture for statisticsSourceNotes


#ToDo: Create fixture for statisticsResourceSources


@pytest.fixture
def resourceSources_relation():
    """Creates a dataframe that can be loaded into the `resourceSources` relation."""
    df = pd.DataFrame(
        [
            ["ProQuest Congressional", True, None, 1],
            ["ProQuest Databases", True, None, 1],
            ["ProQuest History Vault", True, None, 1],
            ["ProQuest Statistical Insight", True, None, 1],
            ["ProQuest U.K. Parliamentary Papers", True, None, 1],
            ["Statistical Abstract of the US", True, None, 1],
            ["Ulrichsweb", True, None, 1],
            ["Peterson's Career Prep", True, None, 3],
            ["Peterson's Test Prep", True, None, 3],
            ["Pivot", True, None, 1],
            ["DemographicsNow", True, None, 3],
            ["Ebook Central", True, None, 1],
            ["Ebook Library", False, "2019-06-30", 5],
            ["Ebrary", False, "2017-12-31", 6],
            ["EBSCOhost", True, None, 2],
            ["Gale Cengage Learning", True, None, 3],
            ["iG Library/Business Expert Press (BEP)", True, None, 4],
            ["MyiLibrary", False, "2019-06-30", 7],
            
        ],
        index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        columns=["Resource_Source_Name", "Source_in_Use", "Use_Stop_Date", "Vendor_ID"]
    )
    df.index.name = "Resource_Source_ID"
    yield df


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