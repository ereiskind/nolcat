"""This module contains the tests for the functions in `nolcat\\nolcat_glue_job.py`."""
########## Passing ??? ##########

import pytest
from datetime import datetime

# `conftest.py` fixtures are imported automatically
from nolcat.logging_config import *
from nolcat.nolcat_glue_job import *
#from nolcat.app import *
#from nolcat.statements import *
#from nolcat.annual_stats import *
#from nolcat.<blueprint> import *
#from nolcat.<class file name> import <class name>

log = logging.getLogger(__name__)


#SECTION: Basic Helper Function Tests
def test_last_day_of_month():
    """Tests returning the last day of the given month."""
    assert last_day_of_month(date(2022, 1, 2)) == date(2022, 1, 31)
    assert last_day_of_month(date(2020, 2, 1)) == date(2020, 2, 29)
    assert last_day_of_month(date(2021, 2, 1)) == date(2021, 2, 28)


def test_ISSN_regex():
    """Tests matching the regex object to ISSN strings."""
    assert ISSN_regex().fullmatch("1234-5678") is not None
    assert ISSN_regex().fullmatch("1123-000x") is not None
    assert ISSN_regex().fullmatch("0987-6543 ") is not None


def test_ISBN_regex():
    """Tests matching the regex object to ISBN strings."""
    assert ISBN_regex().fullmatch("978-1-56619-909-4") is not None
    assert ISBN_regex().fullmatch("1-56619-909-3") is not None
    assert ISBN_regex().fullmatch("1257561035") is not None
    assert ISBN_regex().fullmatch("9781566199094") is not None
    assert ISBN_regex().fullmatch("1-56619-909-3 ") is not None


def test_AWS_timestamp_format():
    """Tests formatting a datetime value with the given format code."""
    assert datetime(2022, 1, 12, 23, 59, 59).strftime(AWS_timestamp_format()) == "2022-01-12T23-59-59"
    assert datetime(2024, 7, 4, 2, 45, 8).strftime(AWS_timestamp_format()) == "2024-07-04T02-45-08"
    assert datetime(1999, 11, 27, 13, 18, 27).strftime(AWS_timestamp_format()) == "1999-11-27T13-18-27"


def test_non_COUNTER_file_name_regex():
    """Tests matching the regex object to file names."""
    assert non_COUNTER_file_name_regex().fullmatch("1_2020.csv") is not None
    assert non_COUNTER_file_name_regex().fullmatch("100_2021.xlsx") is not None
    assert non_COUNTER_file_name_regex().fullmatch("55_2016.pdf") is not None
    assert non_COUNTER_file_name_regex().fullmatch("99999_2030.json") is not None


def test_empty_string_regex():
    """Tests matching the regex object to empty and whitespace-only strings."""
    assert empty_string_regex().fullmatch("") is not None
    assert empty_string_regex().fullmatch(" ") is not None
    assert empty_string_regex().fullmatch("\n") is not None


#ToDo: Create test for `nolcat.app.return_string_of_dataframe_info`


# test_statements.test_format_list_for_stdout_with_list


# test_statements.test_format_list_for_stdout_with_generator


# test_statements.test_remove_IDE_spacing_from_statement


# test_app.test_truncate_longer_lines


#SECTION: Dataframe Adjustment Tests
# test_app.test_change_single_field_dataframe_into_series


# test_app.test_restore_boolean_values_to_boolean_field


# test_app.test_create_AUCT_SelectField_options


# test_app.test_extract_value_from_single_value_df


#SECTION: MySQL Interaction Tests
# test_app.test_SQLAlchemy_engine_creation


# test_app.test_load_data_into_database


# test_app.test_loading_connected_data_into_other_relation


# test_app.test_query_database


# test_app.test_first_new_PK_value


# Testing of `nolcat.app.check_if_data_already_in_COUNTERData()` in `tests.test_StatisticsSources.test_check_if_data_already_in_COUNTERData()`


# test_app.vendors_relation_after_test_update_database


# test_app.test_update_database


# test_app.vendors_relation_after_test_update_database_with_insert_statement


# test_app.test_update_database_with_insert_statement


#SECTION: S3 Interaction Tests
# test_app.test_upload_file_to_S3_bucket


# test_app.file_name_stem_and_data


# test_app.test_save_unconverted_data_via_upload