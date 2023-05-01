"""Tests the methods in FiscalYears."""

import pytest
from datetime import date
import pandas as pd
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import change_multiindex_single_field_dataframe_into_series, return_string_of_dataframe_info, restore_Boolean_values_to_Boolean_field
from nolcat.models import FiscalYears


@pytest.mark.dependency()
def test_data_loaded_successfully(engine, fiscalYears_relation, vendors_relation, vendorNotes_relation, statisticsSources_relation, statisticsSourceNotes_relation, resourceSources_relation, resourceSourceNotes_relation, statisticsResourceSources_relation, annualUsageCollectionTracking_relation, COUNTERData_relation):
    """This test loads data into all the relations and confirms the data ingest was successful.
    
    All of the methods being tested in this module require there to be data in the database, so the database needs to be filled with the test data if any of the tests are going to pass. Placing the `to_sql` statements in a fixture scoped for the module didn't load them successfully, so both the methods to load them and the checks to ensure they were loaded are contained in this test function.
    """
    fiscalYears_relation.to_sql(
        'fiscalYears',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='fiscal_year_ID',
    )
    vendors_relation.to_sql(
        'vendors',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='vendor_ID',
    )
    vendorNotes_relation.to_sql(
        'vendorNotes',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='vendor_notes_ID',
    )
    statisticsSources_relation.to_sql(
        'statisticsSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='statistics_source_ID',
    )
    statisticsSourceNotes_relation.to_sql(
        'statisticsSourceNotes',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='statistics_source_notes_ID',
    )
    resourceSources_relation.to_sql(
        'resourceSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='resource_source_ID',
    )
    resourceSourceNotes_relation.to_sql(
        'resourceSourceNotes',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='resource_source_notes_ID',
    )
    statisticsResourceSources_relation.to_sql(
        'statisticsResourceSources',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label=['SRS_statistics_source', 'SRS_resource_source'],
    )
    annualUsageCollectionTracking_relation.to_sql(
        'annualUsageCollectionTracking',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label=['AUCT_statistics_source', 'AUCT_fiscal_year'],
    )
    COUNTERData_relation.to_sql(
        'COUNTERData',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index_label='COUNTER_data_ID',
    )

    fiscalYears_relation_data = pd.read_sql(
        sql="SELECT * FROM fiscalYears;",
        con=engine,
        index_col='fiscal_year_ID',
    )
    fiscalYears_relation_data = fiscalYears_relation_data.astype({
        "fiscal_year": 'string',
        "ACRL_60b": 'Int64',  # Using the pandas data type here because it allows null values
        "ACRL_63": 'Int64',  # Using the pandas data type here because it allows null values
        "ARL_18": 'Int64',  # Using the pandas data type here because it allows null values
        "ARL_19": 'Int64',  # Using the pandas data type here because it allows null values
        "ARL_20": 'Int64',  # Using the pandas data type here because it allows null values
        "notes_on_statisticsSources_used": 'string',  # For `text` data type
        "notes_on_corrections_after_submission": 'string',  # For `text` data type
    })
    fiscalYears_relation_data["start_date"] = pd.to_datetime(fiscalYears_relation_data["start_date"])
    fiscalYears_relation_data["end_date"] = pd.to_datetime(fiscalYears_relation_data["end_date"])

    vendors_relation_data = pd.read_sql(
        sql="SELECT * FROM vendors;",
        con=engine,
        index_col='vendor_ID',
    )
    vendors_relation_data = vendors_relation_data.astype({
        "vendor_name": 'string',
        "alma_vendor_code": 'string',
    })

    vendorNotes_relation_data = pd.read_sql(
        sql="SELECT * FROM vendorNotes;",
        con=engine,
        index_col='vendor_notes_ID',
    )
    vendorNotes_relation_data = vendorNotes_relation_data.astype({
        "note": 'string',  # For `text` data type
        "written_by": 'string',
        "vendor_ID": 'int',
    })
    vendorNotes_relation_data["date_written"] = pd.to_datetime(vendorNotes_relation_data["date_written"])

    statisticsSources_relation_data = pd.read_sql(
        sql="SELECT * FROM statisticsSources;",
        con=engine,
        index_col='statistics_source_ID',
    )
    statisticsSources_relation_data = statisticsSources_relation_data.astype({
        "statistics_source_name": 'string',
        "statistics_source_retrieval_code": 'string',
        "vendor_ID": 'int',
    })

    statisticsSourceNotes_relation_data = pd.read_sql(
        sql="SELECT * FROM statisticsSourceNotes;",
        con=engine,
        index_col='statistics_source_notes_ID',
    )
    statisticsSourceNotes_relation_data = statisticsSourceNotes_relation_data.astype({
        "note": 'string',  # For `text` data type
        "written_by": 'string',
        "statistics_source_ID": 'int',
    })
    statisticsSourceNotes_relation_data["date_written"] = pd.to_datetime(statisticsSourceNotes_relation_data["date_written"])

    resourceSources_relation_data = pd.read_sql(
        sql="SELECT * FROM resourceSources;",
        con=engine,
        index_col='resource_source_ID',
    )
    resourceSources_relation_data = resourceSources_relation_data.astype({
        "resource_source_name": 'string',
        "source_in_use": 'boolean',
        "vendor_ID": 'int',
    })
    resourceSources_relation_data["use_stop_date"] = pd.to_datetime(resourceSources_relation_data["use_stop_date"])

    resourceSourceNotes_relation_data = pd.read_sql(
        sql="SELECT * FROM resourceSourceNotes;",
        con=engine,
        index_col='resource_source_notes_ID',
    )
    resourceSourceNotes_relation_data = resourceSourceNotes_relation_data.astype({
        "note": 'string',  # For `text` data type
        "written_by": 'string',
        "resource_source_ID": 'int',
    })
    resourceSourceNotes_relation_data["date_written"] = pd.to_datetime(resourceSourceNotes_relation_data["date_written"])

    statisticsResourceSources_relation_data = pd.read_sql(  # This creates a dataframe with a multiindex and a single field, requiring the conversion below
        sql="SELECT * FROM statisticsResourceSources;",
        con=engine,
        index_col=['SRS_statistics_source', 'SRS_resource_source'],
    )
    statisticsResourceSources_relation_data = change_multiindex_single_field_dataframe_into_series(statisticsResourceSources_relation_data)
    statisticsResourceSources_relation_data = statisticsResourceSources_relation_data.astype({
        "current_statistics_source": 'boolean',
    })

    annualUsageCollectionTracking_relation_data = pd.read_sql(
        sql="SELECT * FROM annualUsageCollectionTracking;",
        con=engine,
        index_col=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    annualUsageCollectionTracking_relation_data = annualUsageCollectionTracking_relation_data.astype({
        "usage_is_being_collected": 'boolean',
        "manual_collection_required": 'boolean',
        "collection_via_email": 'boolean',
        "is_COUNTER_compliant": 'boolean',
        "collection_status": 'string',  # For `enum` data type
        "usage_file_path": 'string',
        "notes": 'string',  # For `text` data type
    })

    COUNTERData_relation_data = pd.read_sql(
        sql="SELECT * FROM COUNTERData;",
        con=engine,
        index_col="COUNTER_data_ID",
    )
    COUNTERData_relation_data = COUNTERData_relation_data.astype({
        "statistics_source_ID": 'int',
        "report_type": 'string',
        "resource_name": 'string',
        "publisher": 'string',
        "publisher_ID": 'string',
        "platform": 'string',
        "authors": 'string',
        "article_version": 'string',
        "DOI": 'string',
        "proprietary_ID": 'string',
        "ISBN": 'string',
        "print_ISSN": 'string',
        "online_ISSN": 'string',
        "URI": 'string',
        "data_type": 'string',
        "section_type": 'string',
        "YOP": 'Int64',  # Using the pandas data type here because it allows null values
        "access_type": 'string',
        "access_method": 'string',
        "parent_title": 'string',
        "parent_authors": 'string',
        "parent_article_version": 'string',
        "parent_data_type": 'string',
        "parent_DOI": 'string',
        "parent_proprietary_ID": 'string',
        "parent_ISBN": 'string',
        "parent_print_ISSN": 'string',
        "parent_online_ISSN": 'string',
        "parent_URI": 'string',
        "metric_type": 'string',
    })
    COUNTERData_relation_data["publication_date"] = pd.to_datetime(COUNTERData_relation_data["publication_date"])
    COUNTERData_relation_data["parent_publication_date"] = pd.to_datetime(COUNTERData_relation_data["parent_publication_date"])
    COUNTERData_relation_data["usage_date"] = pd.to_datetime(COUNTERData_relation_data["usage_date"])
    COUNTERData_relation_data["report_creation_date"] = pd.to_datetime(COUNTERData_relation_data["report_creation_date"])

    assert_frame_equal(fiscalYears_relation_data, fiscalYears_relation)
    assert_frame_equal(vendors_relation_data, vendors_relation)
    assert_frame_equal(vendorNotes_relation_data, vendorNotes_relation)
    assert_frame_equal(statisticsSources_relation_data, statisticsSources_relation)
    assert_frame_equal(statisticsSourceNotes_relation_data, statisticsSourceNotes_relation)
    assert_frame_equal(resourceSources_relation_data, resourceSources_relation)
    assert_frame_equal(resourceSourceNotes_relation_data, resourceSourceNotes_relation)
    assert_series_equal(statisticsResourceSources_relation_data, statisticsResourceSources_relation)
    assert_frame_equal(annualUsageCollectionTracking_relation_data, annualUsageCollectionTracking_relation)
    assert_frame_equal(COUNTERData_relation_data, COUNTERData_relation)


def test_calculate_ACRL_60b():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ACRL_63():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ARL_18():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ARL_19():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ARL_20():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_create_usage_tracking_records_for_fiscal_year(engine, client):
    """Tests creating a record in the `annualUsageCollectionTracking` relation for the given fiscal year for each current statistics source.
    
    The test data AUCT relation includes all of the years in the fiscal years relation, so to avoid primary key duplication, a new record needs to be added to the `fiscalYears` relation and used for the method.
    """
    #Section: Create `FiscalYears` Object and `fiscalYears` Record
    primary_key_value = 6
    fiscal_year_value = "2023"
    start_date_value = date.fromisoformat('2022-07-01')
    end_date_value = date.fromisoformat('2023-06-30')

    FY_instance = FiscalYears(
        fiscal_year_ID = primary_key_value,
        fiscal_year = fiscal_year_value,
        start_date = start_date_value,
        end_date = end_date_value,
        ACRL_60b = None,
        ACRL_63 = None,
        ARL_18 = None,
        ARL_19 = None,
        ARL_20 = None,
        notes_on_statisticsSources_used = None,
        notes_on_corrections_after_submission = None,
    )
    FY_df = pd.DataFrame(
        [[fiscal_year_value, start_date_value, end_date_value, None, None, None, None, None, None, None]],
        index=[primary_key_value],
        columns=["fiscal_year", "start_date", "end_date", "ACRL_60b", "ACRL_63", "ARL_18", "ARL_19", "ARL_20", "notes_on_statisticsSources_used", "notes_on_corrections_after_submission"],
    )
    FY_df.index.name = "fiscal_year_ID"

    #Section: Update Relation and Run Method
    FY_df.to_sql(
        name='fiscalYears',
        con=engine,
        if_exists='append',
        chunksize=1000,
        index=True,
        index_label='fiscal_year_ID',
    )
    with client:  # `client` fixture results from `test_client()` method, without which, the error `RuntimeError: No application found.` is raised; using the test client as a solution for this error comes from https://stackoverflow.com/a/67314104
        method_result = FY_instance.create_usage_tracking_records_for_fiscal_year()
    if "error" in method_result:  # If this is true,  pass
        assert False  # If the code comes here, the new AUCT records weren't successfully loaded into the relation; failing the test here means not needing add handling for this error to the database I/O later in the test
    
    #Section: Create and Compare Dataframes
    retrieved_data = pd.read_sql(
        sql="SELECT * FROM annualUsageCollectionTracking;",
        con=engine,
        index_col=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    retrieved_data['usage_is_being_collected'] = restore_Boolean_values_to_Boolean_field(retrieved_data['usage_is_being_collected'])
    retrieved_data['manual_collection_required'] = restore_Boolean_values_to_Boolean_field(retrieved_data['manual_collection_required'])
    retrieved_data['collection_via_email'] = restore_Boolean_values_to_Boolean_field(retrieved_data['collection_via_email'])
    retrieved_data['is_COUNTER_compliant'] = restore_Boolean_values_to_Boolean_field(retrieved_data['is_COUNTER_compliant'])
    print(f"Info on `retrieved_data` dataframe;\n{return_string_of_dataframe_info(retrieved_data)}")
    
    multiindex = pd.MultiIndex.from_tuples(  # MySQL returns results sorted by index; the order of the dataframe elements below copies that order
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
            (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
            (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
            (7, 0), (7, 1), (7, 2),
            (8, 0), (8, 1), (8, 2),
            (9, 3), (9, 4), (9, 5), (9, 6),
            (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6),
            (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6),
        ],
        names=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    expected_output_data = pd.DataFrame(
        [
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Simulating a resource that's become COUNTER compliant"],
            [True, True, False, True, "No usage to report", None, None],
            [True, True, False, True, "Collection complete", None, None],
            [True, True, False, True, "Collection complete", None, "Ended subscription, only Med has content now"],
            [False, False, False, False, "N/A: Paid by Med", None, "Still have access to content through Med"],
            [None, None, None, None, None, None, None],

            [True, True, True, False, "Collection complete", None, "Simulating a resource with usage requested by sending an email"],
            [True, True, True, False, "Collection in process (see notes)", None, "When sending the email, note the date sent and who it was sent to"],
            [True, True, True, False, "Collection in process (see notes)", None, "Having the note about sending the email lets you know if you're in the response window, if you need to follow up, or if too much time has passed for a response to be expected"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [True, True, True, False, "Collection in process (see notes)", None, "Email info"],
            [True, True, True, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [True, True, False, True, "Collection complete", None, "Simulating a resource that becomes OA at the start of a calendar year"],
            [True, True, False, True, "Collection complete", None, "Resource became OA at start of calendar year 2018"],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [None, None, None, None, None, None, None],

            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],

            [True, True, True, False, "Collection not started", None, None],
            [True, True, True, False, "Collection complete", None, None],
            [True, True, True, False, "Collection complete", None, None],

            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],

            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [False, False, False, False, "N/A: Open access", None, None],
            [None, None, None, None, None, None, None],

            [True, True, True, False, "Usage not provided", None, "Simulating a resource that starts offering usage statistics"],
            [True, True, True, False, "Usage not provided", None, None],
            [True, True, False, False, "Collection complete", None, "This is the first FY with usage statistics"],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection complete", None, None],
            [True, True, False, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],
        ],
        index=multiindex,
        columns=["usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"],
    )
    expected_output_data = expected_output_data.astype({
        "usage_is_being_collected": 'boolean',
        "manual_collection_required": 'boolean',
        "collection_via_email": 'boolean',
        "is_COUNTER_compliant": 'boolean',
        "collection_status": 'string',  # For `enum` data type
        "usage_file_path": 'string',
        "notes": 'string',  # For `text` data type
    })
    
    assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes


def test_collect_fiscal_year_usage_statistics():
    """Create a test calling the StatisticsSources._harvest_R5_SUSHI method with the FiscalYears.start_date and FiscalYears.end_date as the arguments."""
    #ToDo: With each year's results changing, and with each API call having the date and time of the call in it, how can matching be done?
    pass