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


@pytest.fixture
def resourceTitles_relation():
    """Creates a dataframe that can be loaded into the `resourceTitles` relation."""
    df = pd.DataFrame(
        [
            ["Performing Arts Periodicals Database", 0],
            ["Small Business Collection", 1],
            ["ERIC", 2],
            ["ProQuest Social Sciences Premium Collection->ERIC", 2],
            ["Social Science Premium Collection->Education Collection->ERIC", 2],
            ["New Scientist", 3],
            ["Periodicals Archive Online->Periodicals Archive Online Foundation Collection", 4],
            ["Women and Language", 5],
            ["Small Business Resource Center", 6],
            ["Вестник Балтийского федерального университета им. И. Канта", 7],
            ["Periodicals Archive Online->Periodicals Archive Online Foundation Collection 3", 8],
            ["上海精神医学 = Shanghai Archives of Psychiatry", 9],
            ["Yale Law Journal", 10],
            ["Whole Dog Journal", 11],
            ["パーソナリティ研究 = The Japanese journal of personality", 12],
            ["Library Journal", 13],
            ["Illumina Biological Content - unstructured", 14],
            ["Short Stories for Students", 15],
            ["Periodicals Archive Online->Periodicals Archive Online Foundation Collection 2", 16],
            ["Historical Abstracts", 17],
            ["Washington Post ï¿¢ï¾€ï¾“ Blogs", 18],
            ["The Scientific Revolution", 19],
            ["Yellow Wallpaper", 20],
            ["Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States", 21],
            ["The Washington Post", 22],
            ["The Supergirls: Feminism, Fantasy, and the History of Comic Book Heroines (Revised and Updated)", 23],
            ["Salem Press Encyclopedia of Literature", 24],
            ["Encyclopedia of Philosophy 2nd ed. vol. 1", 25],
            ["The Yale Swallow Protocol", 26],
            ["Small Business Resource Center", 27],
            ["Superhero Ethics: 10 Comic Book Heroes; 10 Ways to Save the World; Which One Do We Need Most Now?", 28],
            ["Superhero Therapy: Mindfulness Skills to Help Teens and Young Adults Deal with Anxiety, Depression, and Trauma", 29],
            ["Feminist Methods in Social Research", 30],
            ["Encyclopedia of the Middle Ages", 31],
            ["Caribbean Quarterly", 32],
            ["Beauty", 33],
            ["Early European Books->Collection 1", 34],
            ["Artificial Intelligence Research and Development: Proceedings of the 15th International Conference of the Catalan Association for Artificial Intelligence (Frontiers in Artificial Intelligence and Appl", 35],
            ["Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States: A Guide for Providers of Victim and Support Services", 36],
            ["ΕΠΙΣΤΗΜΟΝΙΚΑ ΧΡΟΝΙΚΑ", 37],
            ["Learning Python", 38],
            ["New Stoicism", 39],
            ["Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States: A Guide for the Health Care Sector", 40],
            ["Confronting Commercial Sexual Exploitation and Sex Trafficking of Minors in the United States: A Guide for the Legal Sector", 41],
            ["Learning Bodies", 42],
            ["Caribbean Quarterly", 43],
            ["한국호스피스완화의료학회지=The Korean Journal of Hospice and Palliative Care", 44],
            ["PARLIAMENTARY PAPER", 45],
            ["Early European Books->Collection 10", 46],
            ["Ágora: Estudos Clássicos em Debate", 47],
            ["MLA International Bibliography (Module)", 48],
            ["Artificial Intelligence Research and Development: Proceedings of the 19th International Conference of the Catalan Association for Artificial Intelligence, Barcelona, Catalonia, Spain, October 19-21, 2", 49],
            ["The No-Nonsense Guide to Climate Change", 50],
            ["Business Plans Handbook v14 2008", 51],
            ["World Film Locations : Mumbai", 52],
            ["“Pouring Jewish Water into Fascist Wine\": Untold Stories of (Catholic) Jews From the Archive of Mussolini's Jesuit Pietro Tacchi Venturi", 53],
            ["The ÁAbbåasid Revolution (SUNY Series in Near Eastern Studies)", 54],
            ["A History of Ukraine", 55],
            ["Artificial Intelligence Research and Development: Proceedings of the 13th International Conference of the Catalan Association for Artificial Intelligence (Frontiers in artificial intelligence and appl", 56],
            ["Business Plans Handbook vol. 18", 57],
            ["Gale Directory of Publications and Broadcast Media 151st ed.", 58],
            ["Learning Bootstrap", 59],
            ["Short Stories for Students vol. 12", 60],
            ["Superhero Synergies: Comic Book Characters Go Digital", 61],
            ["Superman: The Persistence of an American Icon", 62],
            ["Women and Language Debate: A Sourcebook", 63],
            ["World Film Locations : Buenos Aires", 64],
            ["World Film Locations:  Melbourne", 65],
            ["World Film Locations: Barcelona", 66],
            ["World Film Locations: Beijing", 67],
            ["World Film Locations: Berlin", 68],
            ["World Film Locations: Dublin", 69],
            ["World Film Locations: Marseilles", 70],
            ["World Film Locations: Vienna", 71],
            ["Salem Press Encyclopedia of Science", 72],
            ["Encyclopedia of Philosophy 2nd ed. vol. 2", 73],
        ],
        # Index: 0-75
        columns=["Resource_Title", "Resource_ID"]
    )
    df.index.name = "Resource_Title_ID"
    yield df


@pytest.fixture
def resourcePlatforms_relation():
    """Creates a dataframe that can be loaded into the `resourcePlatforms` relation."""
    df = pd.DataFrame(
        [
            ["ProQuest", None, "ProQuest", None, None, 1, 0],
            ["Gale Cengage Learning", None, "GOLD", None, None, 3, 1],
            ["ProQuest", None, "ProQuest", None, None, 1, 2],
            ["EBSCO", None, "EBSCOhost", None, None, 2, 2],
            ["Reed Business Information Ltd", None, "EBSCOhost", "51838", None, 2, 3],
            ["Reed Business Information Limited", None, "ProQuest", None, None, 1, 3],
            ["New Scientist", None, "ProQuest", None, None, 1, 3],
            ["New Scientist Ltd.", None, "EBSCOhost", "16190823", None, 2, 3],
            ["New Scientist Ltd.", None, "GOLD", None, None, 3, 3],
            ["ProQuest", None, "ProQuest", None, None, 1, 4],
            ["Organization for the Study of Communication Language and Gender", None, "ProQuest", None, None, 1, 5],
            ["Michigan Technological University", None, "EBSCOhost", "69983", None, 2, 5],
            ["George Mason University", None, "GOLD", None, None, 3, 5],
            ["EBSCO", None, "EBSCOhost", None, None, 2, 6],
            ["Gale Cengage Learning", None, "GOLD", None, None, 3, 6],
            ["??????????? ??????????????? ?????????? ??????????????? ?????????? ??????? ????????????????? ????????", None, "EBSCOhost", "970011", None, 2, 7],
            ["ProQuest", None, "ProQuest", None, None, 1, 8],
            ["?????????", None, "EBSCOhost", "279947", None, 2, 9],
            ["Yale Law Journal", None, "EBSCOhost", "70693", None, 2, 10],
            ["Yale University School of Law", None, "GOLD", None, None, 3, 10],
            ["Belvoir Publications Incorporated", None, "EBSCOhost", "214024", None, 2, 11],
            ["Belvoir Media Group LLC", None, "GOLD", None, None, 3, 11],
            ["?????????????", None, "EBSCOhost", "144395", None, 2, 12],
            ["Library Journals, LLC", None, "EBSCOhost", "45875", None, 2, 13],
            ["Media Source  Inc.", None, "ProQuest", None, None, 1, 13],
            ["Library Journals LLC", None, "GOLD", None, None, 3, 13],
            ["CSA Title Bucket", None, "ProQuest", None, None, 1, 14],
            ["Gale", None, "GOLD", "Collection", None, 3, 15],
            ["ProQuest", None, "ProQuest", None, None, 1, 16],
            ["EBSCO", None, "EBSCOhost", None, None, 2, 17],
            ["WP Company LLC d/b/a The Washington Post", None, "ProQuest", None, None, 1, 18],
            ["University of Chicago Press", None, "EBSCOhost", "590320", None, 2, 19],
            ["The Floating Press", None, "EBSCOhost", "1122716", None, 2, 20],
            ["Project Gutenberg Literary Archive Foundation", None, "EBSCOhost", "387764", None, 2, 20],
            ["National Academies Press", None, "EBSCOhost", "2269134", None, 2, 21],
            ["ProQuest", None, "ProQuest", None, None, 1, 22],
            ["Exterminating Angel Press", None, "EBSCOhost", "12362699", None, 2, 23],
            [None, None, "EBSCOhost", None, None, 2, 24],
            ["Gale", None, "GOLD", "Encyclopedia", None, 3, 25],
            ["Springer International Publishing", None, "EBSCOhost", "2866183", None, 2, 26],
            ["Gale", None, "GOLD", "Collection", None, 3, 27],
            ["Templeton Press", None, "EBSCOhost", "17602328", None, 2, 28],
            ["Instant Help", None, "EBSCOhost", "14313227", None, 2, 29],
            ["Oxford University Press", None, "EBSCOhost", "993517", None, 2, 30],
            [None, None, "EBSCOhost", None, None, 2, 31],
            ["James Clarke & Co.", None, "EBSCOhost", "188368", None, 2, 31],
            ["Taylor & Francis Ltd", None, "ProQuest", None, None, 1, 32],
            ["Oxford University Press", None, "EBSCOhost", "661533", None, 2, 33],
            ["Alexander Street Press", None, "EBSCOhost", "661533", None, 2, 33],
            ["ProQuest", None, "ProQuest", None, None, 1, 34],
            ["IOS Press", None, "EBSCOhost", "1838181", None, 2, 35],
            ["National Academies Press", None, "EBSCOhost", "3060374", None, 2, 36],
            ["Scientific Council of the General Hospital of Piraeus \"Tzaneion\"", None, "EBSCOhost", "10152036", None, 2, 37],
            ["Springer eBooks", None, "EBSCOhost", "167776", None, 2, 38],
            ["O'Reilly Media, Inc.", None, "EBSCOhost", "167776", None, 2, 38],
            ["Princeton University Press", None, "EBSCOhost", "1007639", None, 2, 39],
            ["National Academies Press", None, "EBSCOhost", "3212862", None, 2, 40],
            ["National Academies Press", None, "EBSCOhost", "4061558", None, 2, 41],
            ["Aarhus University Press", None, "EBSCOhost", "947950", None, 2, 42],
            ["University of the West Indies", None, "ProQuest", None, None, 1, 43],
            ["????????????", None, "EBSCOhost", "418223", None, 2, 44],
            [None, None, "ProQuest", None, None, 1, 45],
            ["ProQuest", None, "ProQuest", None, None, 1, 46],
            ["Universidade de Aveiro", None, "EBSCOhost", "1598020", None, 2, 47],
            ["ProQuest", None, "ProQuest", None, None, 1, 48],
            ["IOS Press", None, "EBSCOhost", "11996100", None, 2, 49],
            ["New Internationalist Publications Ltd", None, "ProQuest", None, None, 1, 50],
            ["Gale a Cengage Company", None, "GOLD", "Handbook", None, 3, 51],
            ["Intellect", None, "EBSCOhost", "2262490", None, 2, 52],
            ["Martinus Nijhoff", None, "EBSCOhost", "1195825", None, 2, 53],
            ["Brill Academic Publishers", None, "EBSCOhost", "1195825", None, 2, 53],
            ["State University of New York Press", None, "EBSCOhost", "967718", None, 2, 54],
            ["University of Toronto Press", None, "EBSCOhost", "1439259", None, 2, 55],
            ["IOS Press", None, "EBSCOhost", "1129080", None, 2, 56],
            ["Gale a Cengage Company", None, "GOLD", "Handbook", None, 3, 57],
            ["Gale a Cengage Company", None, "GOLD", "Directory", None, 3, 58],
            ["Packt Publishing", None, "EBSCOhost", "4183662", None, 2, 59],
            ["Gale", None, "GOLD", "Collection", None, 3, 60],
            ["Rowman & Littlefield Publishers", None, "EBSCOhost", "2748458", None, 2, 61],
            ["Rutgers University Press", None, "EBSCOhost", "12323310", None, 2, 62],
            ["Rutgers University Press", None, "EBSCOhost", "961298", None, 2, 63],
            ["Intellect", None, "EBSCOhost", "7196045", None, 2, 64],
            ["Intellect", None, "EBSCOhost", "2262643", None, 2, 65],
            ["Intellect", None, "EBSCOhost", "2098507", None, 2, 66],
            ["Intellect", None, "EBSCOhost", "1726098", None, 2, 67],
            ["Intellect", None, "EBSCOhost", "1720493", None, 2, 68],
            ["Intellect", None, "EBSCOhost", "1726075", None, 2, 69],
            ["Intellect", None, "EBSCOhost", "16021877", None, 2, 70],
            ["Intellect", None, "EBSCOhost", "1738834", None, 2, 71],
            [None, None, "EBSCOhost", None, None, 2, 72],
            ["Gale", None, "GOLD", "Encyclopedia", None, 3, 73],
            ["ProQuest", None, "ProQuest", None, None, 1, 74],
            ["EBSCO", None, "EBSCOhost", None, None, 2, 74],
        ],
        # Index: 0-92
        columns=["Publisher", "Publisher_ID", "Platform", "Proprietary_ID", "URI", "Interface", "Resource_ID"]
    )
    df.index.name = "Resource_Platform_ID"
    yield df


#ToDo: Create fixture for usageData