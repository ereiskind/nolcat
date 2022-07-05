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
        data=[  # No notes, but need PK values of 0-86, so 87 `None` items
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None,
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
            ["Resource_Name", "Performing Arts Periodicals Database", True, 0],
            ["Resource_Name", "Small Business Collection", True, 1],
            ["Resource_Name", "Periodicals Archive Online->Periodicals Archive Online Foundation Collection", True, 4],
            ["Resource_Name", "Вестник Балтийского федерального университета им. И. Канта", True, 7],
            ["Print_ISSN", "2223-2095", True, 7],
            ["Online_ISSN", "2310-3698", True, 7],
            ["Resource_Name", "ProQuest Social Sciences Premium Collection->ERIC", False, 2],
            ["Resource_Name", "Social Science Premium Collection->Education Collection->ERIC", False, 2],
            ["Resource_Name", "ERIC", True, 2],
            ["Resource_Name", "New Scientist", True, 3],
            ["Online_ISSN", "0262-4079", False, 3],
            ["Print_ISSN", "0262-4079", True, 3],
            ["Online_ISSN", "1356-1766", False, 3],
            ["Online_ISSN", "2059-5387", True, 3],
            ["Resource_Name", "Women and Language", True, 5],
            ["Print_ISSN", "8755-4550", True, 5],
            ["Resource_Name", "Small Business Resource Center", True, 6],
            ["Resource_Name", "Caribbean Quarterly", True, 32],
            ["Print_ISSN", "0254-8038", False, 32],
            ["Print_ISSN", "0008-6495", True, 32],
            ["Online_ISSN", "2470-6302", True, 32],
            ["Resource_Name", "Learning Python", True, 38],
            ["ISBN", "978-1-56592-893-0", True, 38],
            ["Resource_Name", "“Pouring Jewish Water into Fascist Wine\": Untold Stories of (Catholic) Jews From the Archive of Mussolini's Jesuit Pietro Tacchi Venturi", True, 53],
            ["ISBN", "978-90-04-22241-0", True, 53],
            ["Resource_Name", "Periodicals Archive Online->Periodicals Archive Online Foundation Collection 3", True, 8],
            ["Resource_Name", "上海精神医学 = Shanghai Archives of Psychiatry", True, 9],
            ["Print_ISSN", "1002-0829", True, 9],
            ["Resource_Name", "Yale Law Journal", True, 10],
            ["Print_ISSN", "0044-0094", True, 10],
            ["Online_ISSN", "0044-0094", False, 10],
            ["Online_ISSN", "1939-8611", True, 10],
            ["Resource_Name", "Whole Dog Journal", True, 11],
            ["Print_ISSN", "1097-5322", True, 11],
            ["Online_ISSN", "1097-5322", True, 11],
            ["Resource_Name", "パーソナリティ研究 = The Japanese journal of personality", True, 12],
            ["Print_ISSN", "1348-8406", True, 12],
            ["Online_ISSN", "1349-6174", True, 12],
            ["Resource_Name", "Library Journal", True, 13],
            ["Print_ISSN", "0363-0277", True, 13],
            ["Online_ISSN", "0363-0277", True, 13],
            ["Resource_Name", "Illumina Biological Content - unstructured", True, 14],
            ["Resource_Name", "Short Stories for Students", True, 15],
            ["Resource_Name", "Periodicals Archive Online->Periodicals Archive Online Foundation Collection 2", True, 16],
            ["Resource_Name", "Historical Abstracts", True, 17],
            ["Resource_Name", "Washington Post ï¿¢ï¾€ï¾“ Blogs", True, 18],
            ["Online_ISSN", "1092-7735", True, 15],
            ["Resource_Name", "The Scientific Revolution", True, 19],
            ["ISBN", "978-0-226-75021-7", True, 19],
            ["ISBN", "978-1-281-43040-3", False, 19],
            ["ISBN", "978-1-77651-048-1", True, 20],
            ["ISBN", "978-0-585-15016-1", False, 20],
            ["Resource_Name", "The yellow wallpaper", True, 20],
            ["Resource_Name", "Yellow Wallpaper", False, 20],
            ["ISBN", "978-0-227-67931-9", True, 31],
            ["Resource_Name", "Encyclopedia of the Middle Ages", True, 31],
            ["Resource_Name", "Beauty", True, 33],
            ["ISBN", "978-1-282-46575-6", True, 33],
            ["Resource_Name", "Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States", True, 21],
            ["Resource_Name", "The Washington Post", True, 22],
            ["Resource_Name", "The Supergirls: Feminism, Fantasy, and the History of Comic Book Heroines (Revised and Updated)", True, 23],
            ["Resource_Name", "Salem Press Encyclopedia of Literature", True, 24],
            ["Resource_Name", "Encyclopedia of Philosophy 2nd ed. vol. 1", True, 25],
            ["Resource_Name", "The Yale Swallow Protocol", True, 26],
            ["Resource_Name", "Superhero Ethics: 10 Comic Book Heroes; 10 Ways to Save the World; Which One Do We Need Most Now?", True, 28],
            ["Resource_Name", "Superhero Therapy: Mindfulness Skills to Help Teens and Young Adults Deal with Anxiety, Depression, and Trauma", True, 29],
            ["Resource_Name", "Feminist Methods in Social Research", True, 30],
            ["Resource_Name", "Early European Books->Collection 1", True, 34],
            ["Resource_Name", "Artificial Intelligence Research and Development: Proceedings of the 15th International Conference of the Catalan Association for Artificial Intelligence (Frontiers in Artificial Intelligence and Appl", True, 35],
            ["Resource_Name", "Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States: A Guide for Providers of Victim and Support Services", True, 36],
            ["Resource_Name", "ΕΠΙΣΤΗΜΟΝΙΚΑ ΧΡΟΝΙΚΑ", True, 37],
            ["Resource_Name", "New Stoicism", True, 39],
            ["Resource_Name", "Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States: A Guide for the Health Care Sector", True, 40],
            ["Resource_Name", "Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States: A Guide for the Legal Sector", True, 41],
            ["Resource_Name", "Learning Bodies", True, 42],
            ["Resource_Name", "한국호스피스완화의료학회지=The Korean Journal of Hospice and Palliative Care", True, 44],
            ["Resource_Name", "PARLIAMENTARY PAPER", True, 45],
            ["Resource_Name", "Early European Books->Collection 10", True, 46],
            ["Resource_Name", "Ágora: Estudos Clássicos em Debate", True, 47],
            ["Resource_Name", "MLA International Bibliography (Module)", True, 48],
            ["Resource_Name", "Artificial Intelligence Research and Development: Proceedings of the 19th International Conference of the Catalan Association for Artificial Intelligence, Barcelona, Catalonia, Spain, October 19-21, 2", True, 49],
            ["Resource_Name", "The No-Nonsense Guide to Climate Change", True, 50],
            ["Resource_Name", "Business Plans Handbook v14 2008", True, 51],
            ["Resource_Name", "World Film Locations : Mumbai", True, 52],
            ["Resource_Name", "The ÁAbbåasid Revolution (SUNY Series in Near Eastern Studies)", True, 54],
            ["Resource_Name", "A History of Ukraine", True, 55],
            ["Resource_Name", "Artificial Intelligence Research and Development: Proceedings of the 13th International Conference of the Catalan Association for Artificial Intelligence (Frontiers in artificial intelligence and appl", True, 56],
            ["Resource_Name", "Business Plans Handbook vol. 18", True, 57],
            ["Resource_Name", "Gale Directory of Publications and Broadcast Media 151st ed.", True, 58],
            ["Resource_Name", "Learning Bootstrap", True, 59],
            ["Resource_Name", "Short Stories for Students vol. 12", True, 60],
            ["Resource_Name", "Superhero Synergies: Comic Book Characters Go Digital", True, 61],
            ["Resource_Name", "Superman: The Persistence of an American Icon", True, 62],
            ["Resource_Name", "Women and Language Debate: A Sourcebook", True, 63],
            ["Resource_Name", "World Film Locations : Buenos Aires", True, 64],
            ["Resource_Name", "World Film Locations:  Melbourne", True, 65],
            ["Resource_Name", "World Film Locations: Barcelona", True, 66],
            ["Resource_Name", "World Film Locations: Beijing", True, 67],
            ["Resource_Name", "World Film Locations: Berlin", True, 68],
            ["Resource_Name", "World Film Locations: Dublin", True, 69],
            ["Resource_Name", "World Film Locations: Marseilles", True, 70],
            ["Resource_Name", "World Film Locations: Vienna", True, 71],
            ["Resource_Name", "Salem Press Encyclopedia of Science", True, 72],
            ["Resource_Name", "Encyclopedia of Philosophy 2nd ed. vol. 2", True, 73],
            ["ISBN", "978-0-309-28658-9", True, 21],
            ["ISBN", "978-1-935259-35-0", True, 23],
            ["ISBN", "978-0-0286-6072-1", True, 25],
            ["ISBN", "978-3-319-05113-0", True, 26],
            ["ISBN", "978-1-59947-552-3", True, 28],
            ["ISBN", "978-1-68403-034-7", True, 29],
            ["ISBN", "978-0-19-507386-7", True, 30],
            ["ISBN", "978-1-61499-139-7", True, 35],
            ["ISBN", "978-0-309-30492-4", True, 36],
            ["Print_ISSN", "1791-1362", True, 37],
            ["Online_ISSN", "2241-1666", True, 37],
            ["ISBN", "978-1-4008-1096-3", True, 39],
            ["ISBN", "978-0-309-31046-8", True, 40],
            ["ISBN", "978-0-309-31343-8", True, 41],
            ["ISBN", "978-87-7684-266-6", True, 42],
            ["Print_ISSN", "1229-1285", True, 44],
            ["Print_ISSN", "0874-5498", True, 47],
            ["ISBN", "978-1-61499-696-5", True, 49],
            ["ISBN", "978-1-904456-41-4", True, 50],
            ["Online_ISSN", "1084-4473", True, 51],
            ["ISBN", "978-1-4144-3750-7", True, 51],
            ["ISBN", "978-1-84150-679-1", True, 52],
            ["ISBN", "978-1-4384-2411-8", True, 54],
            ["ISBN", "978-1-4426-7037-2", True, 55],
            ["ISBN", "978-1-60750-643-0", True, 56],
            ["Online_ISSN", "1084-4473", True, 57],
            ["ISBN", "978-1-4144-6161-8", True, 57],
            ["Online_ISSN", "1048-7972", True, 58],
            ["ISBN", "978-1-78216-185-1", True, 59],
            ["Online_ISSN", "1092-7735", True, 60],
            ["ISBN", "978-1-4144-2823-9", True, 60],
            ["ISBN", "978-1-4422-3212-9", True, 61],
            ["ISBN", "978-0-8135-8754-7", True, 62],
            ["ISBN", "978-0-585-03362-4", True, 63],
            ["ISBN", "978-1-78320-340-6", True, 64],
            ["ISBN", "978-1-84150-678-4", True, 65],
            ["ISBN", "978-1-78320-107-5", True, 66],
            ["ISBN", "978-1-84150-677-7", True, 67],
            ["ISBN", "978-1-84150-680-7", True, 68],
            ["ISBN", "978-1-84150-592-3", True, 69],
            ["ISBN", "978-1-78320-172-3", True, 70],
            ["ISBN", "978-1-84150-736-1", True, 71],
            ["ISBN", "978-0-0286-6072-1", True, 73],
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