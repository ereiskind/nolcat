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
        # Index: 0-4
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
        # Index: 0-6
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
            ["ProQuest", None, 0],
            ["EBSCOhost", None, 1],
            ["Gale Cengage Learning", None, 2],
            ["iG Library/Business Expert Press (BEP)", None, 3],
            ["DemographicsNow", None, 2],
            ["Ebook Central", None, 0],
            ["Peterson's Career Prep", None, 2],
            ["Peterson's Test Prep", None, 2],
            ["Peterson's Prep", None, 2],
            ["Pivot", None, 0],
            ["Ulrichsweb", None, 0],
        ],
        # Index: 0-10
        columns=["Statistics_Source_Name", "Statistics_Source_Retrieval_Code", "Vendor_ID"]
    )
    df.index.name = "Statistics_Source_ID"
    yield df


#toDo: Create fixture for statisticsSourceNotes


@pytest.fixture
def statisticsResourceSources_relation():
    """Creates a dataframe that can be loaded into the `statisticsResourceSources` relation.
    
    Because this relation has only three fields, two of which are a composite primary key, this is a pandas series object with a multiindex rather than a dataframe.
    """
    multiindex = pd.DataFrame(
        [
            [0, 0],
            [0, 1],
            [0, 2],
            [0, 3],
            [0, 4],
            [0, 5],
            [10, 6],
            [6, 7],
            [8, 7],
            [7, 8],
            [8, 8],
            [9, 9],
            [4, 10],
            [5, 11],
            [5, 12],
            [5, 13],
            [1, 14],
            [2, 15],
            [3, 16],
            [5, 17],
        ],
        columns=["SRS_Statistics_Source", "SRS_Resource_Source"]
    )
    multiindex = pd.MultiIndex.from_frame(multiindex)
    series = pd.Series(
        data=[
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
            False,
        ],
        index=multiindex,
        name="Current_Statistics_Source"
    )
    yield series


@pytest.fixture
def resourceSources_relation():
    """Creates a dataframe that can be loaded into the `resourceSources` relation."""
    df = pd.DataFrame(
        [
            ["ProQuest Congressional", True, None, 0],
            ["ProQuest Databases", True, None, 0],
            ["ProQuest History Vault", True, None, 0],
            ["ProQuest Statistical Insight", True, None, 0],
            ["ProQuest U.K. Parliamentary Papers", True, None, 0],
            ["Statistical Abstract of the US", True, None, 0],
            ["Ulrichsweb", True, None, 0],
            ["Peterson's Career Prep", True, None, 2],
            ["Peterson's Test Prep", True, None, 2],
            ["Pivot", True, None, 0],
            ["DemographicsNow", True, None, 2],
            ["Ebook Central", True, None, 0],
            ["Ebook Library", False, "2019-06-30", 4],
            ["Ebrary", False, "2017-12-31", 5],
            ["EBSCOhost", True, None, 1],
            ["Gale Cengage Learning", True, None, 2],
            ["iG Library/Business Expert Press (BEP)", True, None, 3],
            ["MyiLibrary", False, "2019-06-30", 6],
            
        ],
        # Index: 0-17
        columns=["Resource_Source_Name", "Source_in_Use", "Use_Stop_Date", "Vendor_ID"]
    )
    df.index.name = "Resource_Source_ID"
    yield df


#ToDo: Create fixture for resourceSourceNotes


@pytest.fixture
def annualUsageCollectionTracking_relation():
    """Creates a dataframe that can be loaded into the `annualUsageCollectionTracking` relation."""
    #ToDo: Add FY 2019-2020, 2020-2021 to the relation
    multiindex = pd.DataFrame(
        [
            [0, 0],
            [2, 0],
            [1, 0],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
            [7, 0],
            [9, 0],
            [10, 0],
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
            # [0, 3],
            # [1, 3],
            # [2, 3],
            # [3, 3],
            # [4, 3],
            # [5, 3],
            # [8, 3],
            # [9, 3],
            # [10, 3],
            # [0, 4],
            # [1, 4],
            # [2, 4],
            # [3, 4],
            # [4, 4],
            # [5, 4],
            # [8, 4],
            # [9, 4],
            # [10, 4],
        ],
        columns=["AUCT_Statistics_Source", "AUCT_Fiscal_Year"]
    )
    multiindex = pd.MultiIndex.from_frame(multiindex)
    df = pd.DataFrame(
        [
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, "Simulating a resource with usage requested by sending an email"],
            [True, True, False, True, "Collection complete", None, "Simulating a resource that becomes OA at the start of a calendar year"],
            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection not started", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, True, False, "Usage not provided", None, "Simulating a resource that starts offering usage statistics"],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Simulating a resource that's become COUNTER compliant"],
            [True, True, True, False, "Collection in process (see notes)", None, "When sending the email, note the date sent and who it was sent to"],
            [True, True, False, True, "Collection complete", None, "Resource became OA at start of calendar year 2018"],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, True, False, "Usage not provided", None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "No usage to report", None, None],
            [True, True, True, False, "Collection in process (see notes)", None, "Having the note about sending the email lets you know if you're in the response window, if you need to follow up, or if too much time has passed for a response to be expected"],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection not started", None, "This is the first FY with usage statistics"],

            # ProQuest FY 2019-2020
            # EBSCOhost FY 2019-2020
            # Gale Cengage Learning FY 2019-2020
            # iG Library/Business Expert Press (BEP) FY 2019-2020
            # DemographicsNow FY 2019-2020
            # Ebook Central FY 2019-2020  [False, False, False, False, "N/A: Open access", None, None],
            # Peterson's Prep FY 2019-2020  [True, True, False, False, "Collection complete", None, None],
            # Pivot FY 2019-2020  [False, False, False, False, "N/A: Open access", None, None],
            # Ulrichsweb FY 2019-2020

            # ProQuest FY 2020-2021
            # EBSCOhost FY 2020-2021
            # Gale Cengage Learning FY 2020-2021
            # iG Library/Business Expert Press (BEP) FY 2020-2021
            # DemographicsNow FY 2020-2021
            # Ebook Central FY 2020-2021  [False, False, False, False, "N/A: Open access", None, None],
            # Peterson's Prep FY 2020-2021  [True, True, False, False, "Collection complete", None, None],
            # Pivot FY 2020-2021  [False, False, False, False, "N/A: Open access", None, None],
            # Ulrichsweb FY 2020-2021
        ],
        index=multiindex,
        columns=["Usage_Is_Being_Collected", "Manual_Collection_Required", "Collection_Via_Email", "Is_COUNTER_Compliant", "Collection_Status", "Usage_File_Path", "Notes"]
    )
    yield df


#Section: Data for Resources (from samples based on ProQuest, EBSCOhost, Gale Cengage Learning reports)
@pytest.fixture
def resources_relation():
    """Creates a series that can be loaded into the `resources` relation.
    
    Because this relation has only two fields, one of which is the primary key, this is a pandas series object rather than a dataframe.
    """
    series = pd.Series(
        data=[
            #ToDo: Add data
        ],
        name="note"
    )
    series.index.name = "resource_ID"
    yield series


@pytest.fixture
def resourceMetadata_relation():
    """Creates a dataframe that can be loaded into the `resourceMetadata` relation."""
    df = pd.DataFrame(
        [
            #ToDo: Add data
        ],
        columns=["metadata_field", "metadata_value", "default", "resource_ID"]
    )
    df.index.name = "resource_metadata_ID"
    yield df


@pytest.fixture
def resourcePlatforms_relation():
    """Creates a dataframe that can be loaded into the `resourcePlatforms` relation."""
    df = pd.DataFrame(
        [
            #ToDo: Add data
        ],
        columns=["publisher", "publisher_ID", "platform", "proprietary_ID", "URI", "interface", "resource_ID"]
    )
    df.index.name = "resource_platform_ID"
    yield df


@pytest.fixture
def usageData_relation():
    """Creates a dataframe that can be loaded into the `usageData` relation."""
    df = pd.DataFrame(
        [
            #ToDo: Add data
        ],
        columns=["resource_platform_ID", "metric_type", "usage_date", "usage_count", "YOP", "access_type", "access_method", "data_type", "section_type", "report_creation_date"]
    )
    df.index.name = "usage_data_ID"
    yield df