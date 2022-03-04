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


@pytest.fixture
def resources_relation():
    """Creates a dataframe that can be loaded into the `resources` relation."""
    df = pd.DataFrame(
        [
            [None, None, None, None, "Database", None],
            [None, None, None, None, "Database", None],
            [None, None, None, None, "Database", None],
            [None, None, "0262-4079", "1356-1766", "Journal", "Article"],
            [None, None, None, None, "Database", None],
            [None, None, "8755-4550", None, "Journal", "Article"],
            [None, None, None, None, "Database", None],
            [None, None, "2223-2095", "2310-3698", "Journal", "Article"],
            [None, None, None, None, "Database", None],
            [None, None, "1002-0829", None, "Journal", "Article"],
            [None, None, "0044-0094", "1939-8611", "Journal", "Article"],
            [None, None, "1097-5322", None, "Journal", "Article"],
            [None, None, "1348-8406", "1349-6174", "Journal", "Article"],
            [None, None, "0363-0277", None, "Journal", "Article"],
            [None, None, None, None, "Book", "Book_Segment"],
            [None, None, None, "1092-7735", "Book", "Book_Segment"],
            [None, None, None, None, "Database", None],
            [None, None, None, None, "Database", None],
            [None, None, None, None, "Journal", "Article"],
            [None, "978-0-226-75021-7", None, None, "Book", "Book"],
            [None, "978-1-77651-048-1", None, None, "Book", "Book"],
            [None, "978-0-309-28658-9", None, None, "Book", "Book"],
            [None, None, None, None, "Multimedia", None],
            [None, "978-1-935259-35-0", None, None, "Book", "Book"],
            [None, None, None, None, "Book", "Book_Segment"],
            [None, "978-0-0286-6072-1", None, None, "Book", "Book_Segment"],
            [None, "978-3-319-05113-0", None, None, "Book", "Book"],
            [None, None, None, None, "Book", "Book_Segment"],
            [None, "978-1-59947-552-3", None, None, "Book", "Book"],
            [None, "978-1-68403-034-7", None, None, "Book", "Book"],
            [None, "978-0-19-507386-7", None, None, "Book", "Book"],
            [None, "978-0-227-67931-9", None, None, "Book", "Book_Segment"],
            [None, None, "0008-6495", "2470-6302", "Journal", "Article"],
            [None, "978-1-282-46575-6", None, None, "Book", "Book"],
            [None, None, None, None, "Database", None],
            [None, "978-1-61499-139-7", None, None, "Book", "Book"],
            [None, "978-0-309-30492-4", None, None, "Book", "Book"],
            [None, None, "1791-1362", "2241-1666", "Journal", "Article"],
            [None, "978-1-56592-893-0", None, None, "Book", "Book"],
            [None, "978-1-4008-1096-3", None, None, "Book", "Book"],
            [None, "978-0-309-31046-8", None, None, "Book", "Book"],
            [None, "978-0-309-31343-8", None, None, "Book", "Book"],
            [None, "978-87-7684-266-6", None, None, "Book", "Book"],
            [None, None, "0254-8038", None, "Journal", "Article"],
            [None, None, "1229-1285", None, "Journal", "Article"],
            [None, None, None, None, "Journal", "Article"],
            [None, None, None, None, "Database", None],
            [None, None, "0874-5498", None, "Journal", "Article"],
            [None, None, None, None, "Database", None],
            [None, "978-1-61499-696-5", None, None, "Book", "Book"],
            [None, "978-1-904456-41-4", None, None, "Book", "Book_Segment"],
            [None, "978-1-4144-3750-7", None, "1084-4473", "Book", "Book_Segment"],
            [None, "978-1-84150-679-1", None, None, "Book", "Book"],
            [None, "978-90-04-22241-0", None, None, "Book", "Book"],
            [None, "978-1-4384-2411-8", None, None, "Book", "Book"],
            [None, "978-1-4426-7037-2", None, None, "Book", "Book"],
            [None, "978-1-60750-643-0", None, None, "Book", "Book"],
            [None, "978-1-4144-6161-8", None, "1084-4473", "Book", "Book_Segment"],
            [None, None, None, "1048-7972", "Book", "Book_Segment"],
            [None, "978-1-78216-185-1", None, None, "Book", "Book"],
            [None, "978-1-4144-2823-9", None, "1092-7735", "Book", "Book_Segment"],
            [None, "978-1-4422-3212-9", None, None, "Book", "Book"],
            [None, "978-0-8135-8754-7", None, None, "Book", "Book"],
            [None, "978-0-585-03362-4", None, None, "Book", "Book"],
            [None, "978-1-78320-340-6", None, None, "Book", "Book"],
            [None, "978-1-84150-678-4", None, None, "Book", "Book"],
            [None, "978-1-78320-107-5", None, None, "Book", "Book"],
            [None, "978-1-84150-677-7", None, None, "Book", "Book"],
            [None, "978-1-84150-680-7", None, None, "Book", "Book"],
            [None, "978-1-84150-592-3", None, None, "Book", "Book"],
            [None, "978-1-78320-172-3", None, None, "Book", "Book"],
            [None, "978-1-84150-736-1", None, None, "Book", "Book"],
            [None, None, None, None, "Book", "Book_Segment"],
            [None, "978-0-0286-6072-1", None, None, "Book", "Book_Segment"],
            [None, None, None, None, "Platform", None],
        ],
        # Index: 0-74
        columns=["DOI", "ISBN", "Print_ISSN", "Online_ISSN", "Data_Type", "Section_Type"]
    )
    df.index.name = "Resource_ID"
    yield df


#ToDo: Create fixture for resourceTitles


#ToDo: Create fixture for resourcePlatforms


#ToDo: Create fixture for usageData