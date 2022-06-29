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
            ["2021", "2020-07-01", "2021-06-30", None, None, None, None, None, None, None],
            ["2022", "2021-07-01", "2022-06-30", None, None, None, None, None, None, None],
        ],
        columns=["fiscal_year", "start_date", "end_date", "ACRL_60b", "ACRL_63", "ARL_18", "ARL_19", "ARL_20", "notes_on_statisticsSources_used", "notes_on_corrections_after_submission"]
    )
    df.index = df.index + 1  # To make a one-based index
    df.index.name = "fiscal_year_ID"
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
        columns=["vendor_name", "alma_vendor_code"]
    )
    df.index = df.index + 1
    df.index.name = "vendor_ID"
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
        columns=["statistics_source_name", "statistics_source_retrieval_code", "vendor_ID"]
    )
    df.index = df.index + 1
    df.index.name = "statistics_source_ID"
    yield df


#toDo: Create fixture for statisticsSourceNotes


@pytest.fixture
def statisticsResourceSources_relation():
    """Creates a dataframe that can be loaded into the `statisticsResourceSources` relation.
    
    Because this relation has only three fields, two of which are a composite primary key, this is a pandas series object with a multiindex rather than a dataframe.
    """
    multiindex = pd.DataFrame(
        [
            [1, 1],
            [1, 2],
            [1, 3],
            [1, 4],
            [1, 5],
            [1, 6],
            [2, 15],
            [3, 16],
            [4, 17],
            [5, 11],
            [6, 12],
            [6, 13],
            [6, 14],
            [6, 18],
            [7, 8],
            [8, 9],
            [9, 8],
            [9, 9],
            [10, 10],
            [11, 7],
        ],
        columns=["SRS_statistics_source", "SRS_resource_source"]
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
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            True,
            True,
        ],
        index=multiindex,
        name="current_statistics_source"
    )
    yield series


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
        columns=["resource_source_name", "source_in_use", "use_stop_date", "vendor_ID"]
    )
    df.index = df.index + 1
    df.index.name = "resource_source_ID"
    yield df


#ToDo: Create fixture for resourceSourceNotes


@pytest.fixture
def annualUsageCollectionTracking_relation():
    """Creates a dataframe that can be loaded into the `annualUsageCollectionTracking` relation."""
    multiindex = pd.DataFrame(
        [
            [1, 1],
            [2, 1],
            [3, 1],
            [4, 1],
            [5, 1],
            [6, 1],
            [7, 1],
            [8, 1],
            [10, 1],
            [11, 1],
            [1, 2],
            [2, 2],
            [3, 2],
            [4, 2],
            [5, 2],
            [6, 2],
            [7, 2],
            [8, 2],
            [10, 2],
            [11, 2],
            [1, 3],
            [2, 3],
            [3, 3],
            [4, 3],
            [5, 3],
            [6, 3],
            [7, 3],
            [8, 3],
            [10, 3],
            [11, 3],
            [1, 4],
            [2, 4],
            [3, 4],
            [4, 4],
            [5, 4],
            [6, 4],
            [9, 4],
            [10, 4],
            [11, 4],
            [1, 5],
            [2, 5],
            [3, 5],
            [4, 5],
            [5, 5],
            [6, 5],
            [9, 5],
            [10, 5],
            [11, 5],
            [1, 6],
            [2, 6],
            [3, 6],
            [4, 6],
            [5, 6],
            [6, 6],
            [9, 6],
            [10, 6],
            [11, 6],
        ],
        columns=["AUCT_statistics_source", "AUCT_fiscal_year"]
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
            [True, True, False, False, "Collection complete", None, "This is the first FY with usage statistics"],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection complete", None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Ended subscription, only Med has content now"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection complete", None, None],

            [True, True, False, True, "Collection not started", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [False, False, False, False, "N/A: Paid by Med", None, "Still have access to content through Med"],
            [True, True, True, False, "Collection not started", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection not started", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [True, True, False, False, "Collection not started", None, None],
        ],
        index=multiindex,
        columns=["usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"]
    )
    yield df


@pytest.fixture
def resources_relation():
    """Creates a dataframe that can be loaded into the `resources` relation."""
    df = pd.DataFrame(
        [
            #ToDo: Data types and section types proved inconsistent even within the sample data; having an ID for the resource and a space for its notes but putting all other data in the metadata relation may be the better solution
        ],
        columns=["data_type", "section_type", "note"]
    )
    df.index = df.index + 1
    df.index.name = "resource_ID"
    yield df


@pytest.fixture
def resourceMetadata_relation():
    """Creates a dataframe that can be loaded into the `resourceMetadata` relation."""
    df = pd.DataFrame(
        [
            #ToDo: Add data
        ],
        columns=["metadata_field", "metadata_value", "default", "resource_ID"]
    )
    df.index = df.index + 1
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
    df.index = df.index + 1
    df.index.name = "resource_platform_ID"
    yield df


@pytest.fixture
def usageData_relation():
    """Creates a dataframe that can be loaded into the `usageData` relation."""
    df = pd.DataFrame(
        [
            #ToDo: Add data
        ],
        columns=["resource_platform_ID", "metric_type", "usage_date", "usage_count", "YOP", "access_type", "access_method", "report_creation_date"]
    )
    df.index = df.index + 1
    df.index.name = "usage_data_ID"
    yield df