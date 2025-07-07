"""This module contains the tests for the functions in `nolcat\\nolcat_glue_job.py`."""
########## Passing ??? ##########

import pytest
from datetime import datetime
from pandas.testing import assert_series_equal

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


def test_return_string_of_dataframe_info():
    """Tests returning a string version of `DataFrame.info()` for logging statements."""
    one = pd.DataFrame(
        [
            [1, 2],
            [3, 4],
            [5, 6],
        ],
        columns=["a", "b"],
    )
    assert return_string_of_dataframe_info(one) == "<class 'pandas.core.frame.DataFrame'>\nRangeIndex: 3 entries, 0 to 2\nData columns (total 2 columns):\n #   Column  Non-Null Count  Dtype\n---  ------  --------------  -----\n 0   a       3 non-null      int64\n 1   b       3 non-null      int64\ndtypes: int64(2)\nmemory usage: 180.0 bytes\n"
    two = pd.DataFrame(
        [
            [10, "a", True],
            [100, "b", None],
            [1000, "c", False],
        ],
        columns=["int", "string", "Bool"],
    )
    two.index.name = "index"
    two = two.astype({
        "int": 'int',
        "string": 'string',
        "Bool": 'boolean',
    })
    assert return_string_of_dataframe_info(two) == "<class 'pandas.core.frame.DataFrame'>\nRangeIndex: 3 entries, 0 to 2\nData columns (total 3 columns):\n #   Column  Non-Null Count  Dtype  \n---  ------  --------------  -----  \n 0   int     3 non-null      int64  \n 1   string  3 non-null      string \n 2   Bool    2 non-null      boolean\ndtypes: boolean(1), int64(1), string(1)\nmemory usage: 186.0 bytes\n"

def test_format_list_for_stdout_with_list():
    """Test pretty printing a list by adding a line break between each item."""
    assert format_list_for_stdout(['a', 'b', 'c']) == "a\nb\nc"


def test_format_list_for_stdout_with_generator(create_COUNTERData_workbook_iterdir_list):
    """Test pretty printing a list created by a generator object by adding a line break between each item.
    
    The assert statements, which look for every file that should be in the created string and then check that there are only that many items in the string, is used to compensate for `iterdir()` not outputting the files in an exact order.
    """
    result = format_list_for_stdout(create_COUNTERData_workbook_iterdir_list)
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2017.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2018.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/0_2020.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2017.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2018.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/1_2020.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2017.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2018.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/2_2020.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/3_2019.xlsx" in result
    assert "/nolcat/tests/bin/COUNTER_workbooks_for_tests/3_2020.xlsx" in result
    assert len(result.split('\n')) == 14


def test_remove_IDE_spacing_from_statement():
    """Test removing newlines and indentations from SQL statements."""
    statement = """
        SELECT
            a,
            b,
            c
        FROM relation
            JOIN anotherRelation ON relation.a=anotherRelation.a
        WHERE
            a > 10 AND
            (
                b='spam' OR
                b='eggs'
            );
    """
    assert remove_IDE_spacing_from_statement(statement) == "SELECT a, b, c FROM relation JOIN anotherRelation ON relation.a=anotherRelation.a WHERE a > 10 AND ( b='spam' OR b='eggs' );"


def test_truncate_longer_lines():
    """Tests truncating aly string longer than 50 characters to just 50 characters including the ellipsis at the end."""
    assert truncate_longer_lines("This is shorter than 50 characters.") == "This is shorter than 50 characters."
    assert truncate_longer_lines("This is muuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuch longer than 50 characters.") == "This is muuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuch lon..."


#SECTION: Dataframe Adjustment Tests
def test_change_single_field_dataframe_into_series():
    """Tests the transformation of a dataframe with a single field into a series."""
    mx = pd.MultiIndex.from_frame(
        pd.DataFrame(
            [
                [0, "a"],
                [0, "b"],
                [1, "a"],
                [1, "c"],
            ],
            columns=["numbers", "letters"],
        )
    )
    df = pd.DataFrame(
        [[1], [2], [3], [4]],
        index=mx,
        dtype='int64',
        columns=["test"],
    )
    s = pd.Series(
        [1, 2, 3, 4],
        index=mx,
        dtype='int64',
        name="test",
    )
    assert_series_equal(change_single_field_dataframe_into_series(df), s)


def test_restore_boolean_values_to_boolean_field():
    """Tests the replacement of MySQL's single-bit int data type with pandas's `boolean` data type."""
    tinyint_s = pd.Series(
        [1, 0, pd.NA, 1],
        dtype='Int8',  # pandas' single-bit int data type is used because it allows nulls; using the Python data type raises an error
        name="boolean_values",
    )
    boolean_s = pd.Series(
        [True, False, pd.NA, True],
        dtype='boolean',
        name="boolean_values",
    )
    assert_series_equal(restore_boolean_values_to_boolean_field(tinyint_s), boolean_s)


def test_create_AUCT_SelectField_options():
    """Tests the transformation of a dataframe with four fields into a list for the `SelectField.choices` attribute with the characteristics described in the docstring of the function being tested."""
    df = pd.DataFrame(
        [
            [1, 1, "First Statistics Source", "2017"],
            [2, 1, "Second Statistics Source", "2017"],
            [1, 2, "First Statistics Source", "2018"],
            [3, 2, "Third Statistics Source", "2018"],
        ],
        columns=["AUCT_statistics_source", "AUCT_fiscal_year", "statistics_source_name", "fiscal_year"],
    )
    result_list = [
        (
            (1, 1),
            "First Statistics Source--FY 2017",
        ),
        (
            (2, 1),
            "Second Statistics Source--FY 2017",
        ),
        (
            (1, 2),
            "First Statistics Source--FY 2018",
        ),
        (
            (3, 2),
            "Third Statistics Source--FY 2018",
        ),
    ]
    assert create_AUCT_SelectField_options(df) == result_list


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