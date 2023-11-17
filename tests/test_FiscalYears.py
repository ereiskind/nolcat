"""Tests the methods in FiscalYears."""
########## Passing 2023-09-08 ##########

import pytest
import logging
from datetime import date
import pandas as pd
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from nolcat.app import *
from nolcat.models import *
from nolcat.statements import *

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def FiscalYears_object_and_record():
    """Creates a FiscalYears object and an empty record for the fiscalYears relation.

    Yields:
        tuple: a FiscalYears object; a single-record dataframe for the fiscalYears relation
    """
    primary_key_value = 6
    fiscal_year_value = "2023"
    start_date_value = date.fromisoformat('2022-07-01')
    end_date_value = date.fromisoformat('2023-06-30')

    FY_instance = FiscalYears(
        fiscal_year_ID = primary_key_value,
        fiscal_year = fiscal_year_value,
        start_date = start_date_value,
        end_date = end_date_value,
        depreciated_ACRL_60b = None,
        depreciated_ACRL_63 = None,
        ACRL_61a = None,
        ACRL_61b = None,
        ARL_18 = None,
        ARL_19 = None,
        ARL_20 = None,
        notes_on_statisticsSources_used = None,
        notes_on_corrections_after_submission = None,
    )
    FY_df = pd.DataFrame(
        [[fiscal_year_value, start_date_value, end_date_value, None, None, None, None, None, None, None, None, None]],
        index=[primary_key_value],
        columns=["fiscal_year", "start_date", "end_date", "depreciated_ACRL_60b", "depreciated_ACRL_63","ACRL_61a", "ACRL_61b",  "ARL_18", "ARL_19", "ARL_20", "notes_on_statisticsSources_used", "notes_on_corrections_after_submission"],
    )
    FY_df.index.name = "fiscal_year_ID"
    yield (FY_instance, FY_df)


def test_calculate_depreciated_ACRL_60b():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_depreciated_ACRL_63():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ACRL_61a():
    """Create a test for the function."""
    #ToDo: Write test and docstring
    pass


def test_calculate_ACRL_61b():
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


@pytest.fixture
def load_new_records_into_fiscalYears(engine, FiscalYears_object_and_record, caplog):
    """Since the test data AUCT relation includes all of the years in the fiscal years relation, to avoid primary key duplication, a new record is added to the `fiscalYears` relation for the `test_create_usage_tracking_records_for_fiscal_year()` test function.

    Args:
        engine (sqlalchemy.engine.Engine): a SQLAlchemy engine
        FiscalYears_object_and_record (tuple): a FiscalYears object; a single-record dataframe for the fiscalYears relation corresponding to that object
        caplog (pytest.logging.caplog): changes the logging capture level of individual test modules during test runtime
    
    Yields:
        None
    """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `load_data_into_database()`
    method_result = load_data_into_database(
        df=FiscalYears_object_and_record[1],
        relation='fiscalYears',
        engine=engine,
        index_field_name='fiscal_year_ID',
    )
    if not load_data_into_database_success_regex().fullmatch(method_result):
        pytest.skip(database_function_skip_statements(method_result, False))
    yield None


def test_create_usage_tracking_records_for_fiscal_year(engine, client, load_new_records_into_fiscalYears, FiscalYears_object_and_record, caplog):  # `load_new_records_into_fiscalYears()` not called but used to load record needed for test
    """Tests creating a record in the `annualUsageCollectionTracking` relation for the given fiscal year for each current statistics source."""
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `query_database()`

    #Section: Call Method
    with client:
        method_result = FiscalYears_object_and_record[0].create_usage_tracking_records_for_fiscal_year()
    if not load_data_into_database_success_regex().fullmatch(method_result):
        assert False  # If the code comes here, the method call being tested failed; by failing and thus ending the test here, error handling isn't needed in the remainder of the test function
    
    #Section: Create and Compare Dataframes
    retrieved_data = query_database(
        query="SELECT * FROM annualUsageCollectionTracking;",
        engine=engine,
        index=["AUCT_statistics_source", "AUCT_fiscal_year"],
    )
    if isinstance(retrieved_data, str):
        pytest.skip(database_function_skip_statements(retrieved_data))
    retrieved_data = retrieved_data.astype({
        "collection_status": AnnualUsageCollectionTracking.state_data_types()["collection_status"],
        "usage_file_path": AnnualUsageCollectionTracking.state_data_types()["usage_file_path"],
        "notes": AnnualUsageCollectionTracking.state_data_types()["notes"],
    })
    retrieved_data['usage_is_being_collected'] = restore_boolean_values_to_boolean_field(retrieved_data['usage_is_being_collected'])
    retrieved_data['manual_collection_required'] = restore_boolean_values_to_boolean_field(retrieved_data['manual_collection_required'])
    retrieved_data['collection_via_email'] = restore_boolean_values_to_boolean_field(retrieved_data['collection_via_email'])
    retrieved_data['is_COUNTER_compliant'] = restore_boolean_values_to_boolean_field(retrieved_data['is_COUNTER_compliant'])
    
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
            [True, True, False, False, "Collection complete", "11_2.csv", "This is the first FY with usage statistics"],
            [True, True, False, False, "Collection complete", "11_3.csv", None],
            [True, True, False, False, "Collection complete", "11_4.csv", None],
            [True, True, False, False, "Collection not started", None, None],
            [None, None, None, None, None, None, None],
        ],
        index=multiindex,
        columns=["usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"],
    )
    expected_output_data = expected_output_data.astype(AnnualUsageCollectionTracking.state_data_types())
    
    regex_match_object = load_data_into_database_success_regex().fullmatch(method_result)
    assert regex_match_object is not None
    assert int(regex_match_object.group(1)) == 10
    assert regex_match_object.group(2) == "annualUsageCollectionTracking"
    log.info(f"Comparison:\n{retrieved_data.compare(expected_output_data)}")  #TEST:: temp
    assert_frame_equal(retrieved_data, expected_output_data, check_index_type=False)  # `check_index_type` argument allows test to pass if indexes are different dtypes


def test_collect_fiscal_year_usage_statistics(caplog):
    """Create a test calling the `StatisticsSources._harvest_R5_SUSHI()` method with the `FiscalYears.start_date` and `FiscalYears.end_date` as the arguments. """
    caplog.set_level(logging.INFO, logger='nolcat.app')  # For `first_new_PK_value()`
    caplog.set_level(logging.INFO, logger='nolcat.SUSHI_call_and_response')  # For `make_SUSHI_call()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.INFO, logger='nolcat.convert_JSON_dict_to_dataframe')  # For `create_dataframe()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`
    caplog.set_level(logging.WARNING, logger='sqlalchemy.engine')  # For database I/O called in `self._check_if_data_in_database()` called in `self._harvest_single_report()` called in `self._harvest_R5_SUSHI()`

    #ToDo: This method makes a SUSHI call for every AnnualUsageCollectionTracking record for the given FY where `AnnualUsageCollectionTracking.usage_is_being_collected` is `True` and `AnnualUsageCollectionTracking.manual_collection_required` is `False`. Right now, no record in the test data meets those criteria.
    # logging_statement, flash_messages = FiscalYears.collect_fiscal_year_usage_statistics()
    # assert load_data_into_database_success_regex().match(logging_statement)
    # assert update_database_success_regex().search(logging_statement)
    # assert isinstance(flash_messages, list)
    pass