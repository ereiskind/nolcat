"""This module contains the tests for the functions in `nolcat\\nolcat_glue_job.py`."""
########## Passing ??? ##########

import pytest

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

# test_app.test_ISSN_regex

# test_app.test_ISBN_regex

# test_app.test_AWS_timestamp_format

# test_app.test_non_COUNTER_file_name_regex

# test_app.test_empty_string_regex

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