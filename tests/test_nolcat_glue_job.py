"""This module contains the tests for the functions in `nolcat\\nolcat_glue_job.py`."""
########## Passing ??? ##########

import pytest
from datetime import datetime
from filecmp import cmp
from random import choice
from pandas.testing import assert_series_equal
from pandas.testing import assert_frame_equal

# `conftest.py` fixtures are imported automatically
from conftest import prepare_HTML_page_for_comparison
from nolcat.nolcat_glue_job import *
from nolcat.models import *

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


def test_prepare_HTML_page_for_comparison():
    """Tests creating an Unicode string from HTML page data.
    
    The function being tested here is in the "tests/conftest.py" file; as it's the only function from that file with a test, it was placed here with other helper function tests.
    """
    assert prepare_HTML_page_for_comparison(b'<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Ingest Usage</title>\n</head>\n<body>\n    <h1>Ingest Usage Homepage</h1>\n\n    \n        \n            <p>[{&#39;DR&#39;: [], &#39;IR&#39;: [], &#39;PR&#39;: [], &#39;reports&#39;: [], &#39;status&#39;: []}]</p>\n        \n    \n\n    <ul>\n        <li>To upload a tabular COUNTER report, <a href="/ingest_usage/upload-COUNTER">click here</a>.</li>\n        <li>To make a SUSHI call, <a href="/ingest_usage/harvest">click here</a>.</li>\n        <li>To save a non-COUNTER usage file, <a href="/ingest_usage/upload-non-COUNTER">click here</a>.</li>\n    </ul>\n\n    <p>To return to the homepage, <a href="/">click here</a>.</p>\n</body>\n</html>') == '<!DOCTYPE html>\\n<html lang="en">\\n<head>\\n    <meta charset="UTF-8">\\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\\n    <title>Ingest Usage</title>\\n</head>\\n<body>\\n    <h1>Ingest Usage Homepage</h1>\\n\\n    \\n        \\n            <p>[{\'DR\': [], \'IR\': [], \'PR\': [], \'reports\': [], \'status\': []}]</p>\\n        \\n    \\n\\n    <ul>\\n        <li>To upload a tabular COUNTER report, <a href="/ingest_usage/upload-COUNTER">click here</a>.</li>\\n        <li>To make a SUSHI call, <a href="/ingest_usage/harvest">click here</a>.</li>\\n        <li>To save a non-COUNTER usage file, <a href="/ingest_usage/upload-non-COUNTER">click here</a>.</li>\\n    </ul>\\n\\n    <p>To return to the homepage, <a href="/">click here</a>.</p>\\n</body>\\n</html>'


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


def test_extract_value_from_single_value_df():
    """Tests extracting the value from a dataframe containing a single value."""
    assert extract_value_from_single_value_df(pd.DataFrame([[10]])) == 10
    assert extract_value_from_single_value_df(pd.DataFrame([["hi"]])) == "hi"
    assert extract_value_from_single_value_df(pd.DataFrame([[10.0]])) == 10
    assert extract_value_from_single_value_df(pd.DataFrame([[None]])) == 0


#SECTION: MySQL Interaction Tests
@pytest.mark.dependency()
def test_load_data_into_database(engine, vendors_relation):
    """Tests loading data into a relation.

    Testing the helper function for loading data into the database also confirms that the database and program are connected.
    """
    result = load_data_into_database(
        df=vendors_relation,
        relation='vendors',
        engine=engine,
        index_field_name='vendor_ID',
    )
    regex_match_object = load_data_into_database_success_regex().fullmatch(result)
    assert regex_match_object is not None
    assert int(regex_match_object.group(1)) == 8
    assert regex_match_object.group(2) == "vendors"


@pytest.mark.dependency(depends=['test_query_database'])
def test_loading_connected_data_into_other_relation(engine, statisticsSources_relation):
    """Tests loading data into a second relation connected with foreign keys and performing a joined query.

    This test uses second dataframe to load data into a relation that has a foreign key field that corresponds to the primary keys of the relation loaded with data in `test_load_data_into_database`, then tests that the data load and the primary key-foreign key connection worked by performing a `JOIN` query and comparing it to a manually constructed dataframe containing that same data.
    """
    df_dtypes = {
        "statistics_source_name": StatisticsSources.state_data_types()['statistics_source_name'],
        "statistics_source_retrieval_code": StatisticsSources.state_data_types()['statistics_source_retrieval_code'],
        "vendor_name": Vendors.state_data_types()['vendor_name'],
        "alma_vendor_code": Vendors.state_data_types()['alma_vendor_code'],
    }

    check = load_data_into_database(
        df=statisticsSources_relation,
        relation='statisticsSources',
        engine=engine,
        index_field_name='statistics_source_ID',
    )
    if not load_data_into_database_success_regex().fullmatch(check):
        pytest.skip(database_function_skip_statements(check))
    retrieved_data = query_database(
        query="""
            SELECT
                statisticsSources.statistics_source_ID,
                statisticsSources.statistics_source_name,
                statisticsSources.statistics_source_retrieval_code,
                vendors.vendor_name,
                vendors.alma_vendor_code
            FROM statisticsSources
            JOIN vendors ON statisticsSources.vendor_ID=vendors.vendor_ID
            ORDER BY statisticsSources.statistics_source_ID;
        """,
        engine=engine,
        index='statistics_source_ID'
        # Each stats source appears only once, so the PKs can still be used--remember that pandas doesn't have a problem with duplication in the index
    )
    if isinstance(retrieved_data, str):
        pytest.skip(database_function_skip_statements(retrieved_data))
    retrieved_data = retrieved_data.astype(df_dtypes)

    expected_output_data = pd.DataFrame(
        [
            ["ProQuest", "1", "ProQuest", None],
            ["EBSCOhost", "2", "EBSCO", None],
            ["Gale Cengage Learning", None, "Gale", None],
            ["Duke UP", "3", "Duke UP", None],
            ["iG Library/Business Expert Press (BEP)", None, "iG Publishing/BEP", None],
            ["DemographicsNow", None, "Gale", None],
            ["Ebook Central", None, "ProQuest", None],
            ["Peterson's Career Prep", None, "Gale", None],
            ["Peterson's Test Prep", None, "Gale", None],
            ["Peterson's Prep", None, "Gale", None],
            ["Pivot", None, "ProQuest", None],
            ["Ulrichsweb", None, "ProQuest", None],
        ],
        columns=["statistics_source_name", "statistics_source_retrieval_code", "vendor_name", "alma_vendor_code"],
    )
    expected_output_data.index.name = "statistics_source_ID"
    expected_output_data = expected_output_data.astype(df_dtypes)
    assert_frame_equal(retrieved_data, expected_output_data)
'''
Makes calls for data IO
    test_loading_connected_data_into_other_relation -> load_data_into_database
    test_loading_connected_data_into_other_relation -> query_database -> remove_IDE_spacing_from_statement
Makes call to for match purposes
    test_loading_connected_data_into_other_relation -> load_data_into_database_success_regex
'''


@pytest.mark.dependency(depends=['test_load_data_into_database'])
def test_query_database(engine, vendors_relation):
    """Tests getting data from the database through a SQL query.

    This test performs a `SELECT *` query on the relation that had data loaded into it in the previous test, confirming that the function works and that the database and program are connected to allow CRUD operations.
    """
    retrieved_vendors_data = query_database(
        query="SELECT * FROM vendors;",
        engine=engine,
        index='vendor_ID',
    )
    retrieved_vendors_data = retrieved_vendors_data.astype(Vendors.state_data_types())
    assert_frame_equal(vendors_relation, retrieved_vendors_data)


@pytest.mark.dependency(depends=['test_load_data_into_database'])
def test_first_new_PK_value(client):
    """Tests the retrieval of a relation's next primary key value."""
    with client:
        assert first_new_PK_value('vendors') == 8


# Testing of `nolcat.nolcat_glue_job.check_if_data_already_in_COUNTERData()` and its related fixtures are in `tests.test_StatisticsSources` because the test requires the test data to be loaded into the `COUNTERData` relation while every other test function in this module relies upon the test suite starting with an empty database.


@pytest.fixture
def vendors_relation_after_test_update_database():
    """The test data for the `vendors` relation featuring the change to be made in the `test_update_database()` test.

    Yields:
        dataframe: data matching the updated `vendors` relation
    """
    df = pd.DataFrame(
        [
            ["ProQuest", None],
            ["EBSCO", None],
            ["Gale", "CODE"],
            ["iG Publishing/BEP", None],
            ["Ebook Library", None],
            ["Ebrary", None],
            ["MyiLibrary", None],
            ["Duke UP", None],
        ],
        columns=["vendor_name", "alma_vendor_code"],
    )
    df.index.name = "vendor_ID"
    df = df.astype(Vendors.state_data_types())
    yield df


@pytest.mark.dependency(depends=['test_load_data_into_database'])
def test_update_database(engine, client, vendors_relation_after_test_update_database):
    """Tests updating data in the database through a SQL update statement."""
    with client:
        update_result = update_database(
            update_statement=f"UPDATE vendors SET alma_vendor_code='CODE' WHERE vendor_ID=2;",
            engine=engine,
        )
    retrieved_updated_vendors_data = query_database(
        query="SELECT * FROM vendors;",
        engine=engine,
        index='vendor_ID',
    )
    if isinstance(retrieved_updated_vendors_data, str):
        pytest.skip(database_function_skip_statements(retrieved_updated_vendors_data))
    retrieved_updated_vendors_data = retrieved_updated_vendors_data.astype(Vendors.state_data_types())
    assert update_database_success_regex().fullmatch(update_result).group(0) == update_result
    assert_frame_equal(vendors_relation_after_test_update_database, retrieved_updated_vendors_data)


@pytest.fixture
def vendors_relation_after_test_update_database_with_insert_statement():
    """The test data for the `vendors` relation featuring the changes to be made in the `test_update_database_with_insert_statement()` test.

    Yields:
        dataframe: data matching the updated `vendors` relation
    """
    df = pd.DataFrame(
        [
            ["ProQuest", None],
            ["EBSCO", None],
            ["Gale", "CODE"],
            ["iG Publishing/BEP", None],
            ["Ebook Library", None],
            ["Ebrary", None],
            ["MyiLibrary", None],
            ["Duke UP", None],
            ["A Vendor", None],
            ["Another Vendor", "1"],
        ],
        columns=["vendor_name", "alma_vendor_code"],
    )
    df.index.name = "vendor_ID"
    df = df.astype(Vendors.state_data_types())
    yield df


@pytest.mark.dependency(depends=['test_load_data_into_database'])
def test_update_database_with_insert_statement(engine, client, vendors_relation_after_test_update_database_with_insert_statement):
    """Tests adding records to the database through a SQL insert statement."""
    with client:
        update_result = update_database(
            update_statement=f"INSERT INTO vendors VALUES (8, 'A Vendor', NULL), (9, 'Another Vendor', '1');",
            engine=engine,
        )
    retrieved_updated_vendors_data = query_database(
        query="SELECT * FROM vendors;",
        engine=engine,
        index='vendor_ID',
    )
    if isinstance(retrieved_updated_vendors_data, str):
        pytest.skip(database_function_skip_statements(retrieved_updated_vendors_data))
    retrieved_updated_vendors_data = retrieved_updated_vendors_data.astype(Vendors.state_data_types())
    assert update_database_success_regex().fullmatch(update_result).group(0) == update_result
    assert_frame_equal(vendors_relation_after_test_update_database_with_insert_statement, retrieved_updated_vendors_data)


#SECTION: S3 Interaction Tests
def test_upload_file_to_S3_bucket(tmp_path, path_to_sample_file, remove_file_from_S3):  # `remove_file_from_S3()` not called but used to remove file loaded during test
    """Tests uploading files to a S3 bucket."""
    logging_message = upload_file_to_S3_bucket(
        path_to_sample_file,
        path_to_sample_file.name,
        bucket_path=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    log.debug(logging_message)
    if not upload_file_to_S3_bucket_success_regex().fullmatch(logging_message):
        assert False  # Entering this block means the function that's being tested raised an error, so continuing with the test won't provide anything meaningful
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    log.debug(f"Raw contents of `{BUCKET_NAME}/{PATH_WITHIN_BUCKET_FOR_TESTS}` (type {type(list_objects_response)}):\n{format_list_for_stdout(list_objects_response)}.")
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(f"{PATH_WITHIN_BUCKET_FOR_TESTS}", "") for file_name in bucket_contents]
    assert path_to_sample_file.name in bucket_contents
    download_location = tmp_path / path_to_sample_file.name
    s3_client.download_file(
        Bucket=BUCKET_NAME,
        Key=PATH_WITHIN_BUCKET_FOR_TESTS + path_to_sample_file.name,
        Filename=download_location,
    )
    assert cmp(path_to_sample_file, download_location)


@pytest.fixture(params=[
    {'Report_Header': {'Created': '2023-10-17T21:13:26Z','Created_By': 'ProQuest','Customer_ID': '0000','Report_ID': 'PR','Release': '5','Report_Name': 'Platform Master Report','Institution_Name': 'FLORIDA STATE UNIVERSITY','Institution_ID': [{'Type': 'Proprietary','Value': 'ProQuest:0000'}],'Report_Filters': [{'Name': 'Platform','Value': 'ProQuest'},{'Name': 'Begin_Date','Value': '2022-07-01'},{'Name': 'End_Date','Value': '2023-08-31'},{'Name': 'Data_Type','Value': 'Book|Journal'}],'Report_Attributes': [{'Name': 'Attributes_To_Show','Value': 'Data_Type|Access_Method'}]},'Report_Items': [{'Platform': 'ProQuest','Data_Type': 'Book','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 8},{'Metric_Type': 'Total_Item_Requests','Count': 9}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 2},{'Metric_Type': 'Total_Item_Requests','Count': 12}]}]},{'Platform': 'ProQuest','Data_Type': 'Journal','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 53},{'Metric_Type': 'Total_Item_Requests','Count': 89}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 77},{'Metric_Type': 'Total_Item_Requests','Count': 92}]}]}]},
    "{'Report_Header': {'Created': '2023-10-17T21:13:26Z','Created_By': 'ProQuest','Customer_ID': '0000','Report_ID': 'PR','Release': '5','Report_Name': 'Platform Master Report','Institution_Name': 'FLORIDA STATE UNIVERSITY','Institution_ID': [{'Type': 'Proprietary','Value': 'ProQuest:0000'}],'Report_Filters': [{'Name': 'Platform','Value': 'ProQuest'},{'Name': 'Begin_Date','Value': '2022-07-01'},{'Name': 'End_Date','Value': '2023-08-31'},{'Name': 'Data_Type','Value': 'Book|Journal'}],'Report_Attributes': [{'Name': 'Attributes_To_Show','Value': 'Data_Type|Access_Method'}]},'Report_Items': [{'Platform': 'ProQuest','Data_Type': 'Book','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 8},{'Metric_Type': 'Total_Item_Requests','Count': 9}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 2},{'Metric_Type': 'Total_Item_Requests','Count': 12}]}]},{'Platform': 'ProQuest','Data_Type': 'Journal','Access_Method': 'Regular','Performance': [{'Period': {'Begin_Date': '2022-07-01','End_Date': '2022-07-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 53},{'Metric_Type': 'Total_Item_Requests','Count': 89}]},{'Period': {'Begin_Date': '2022-08-01','End_Date': '2022-08-31'},'Instance': [{'Metric_Type': 'Total_Item_Investigations','Count': 77},{'Metric_Type': 'Total_Item_Requests','Count': 92}]}]}]}",
])
def file_name_stem_and_data(request, most_recent_month_with_usage):
    """Provides the contents and name stem for the file in `test_save_unconverted_data_via_upload()`, then removes that file from S3 after the test runs.

    Args:
        request (dict or str): the contents of the file that will be saved to S3

    Yields:
        tuple: the stem of the name under which the file will be saved in S3 (str); the data that will be in the file saved to S3 (dict or str)
    """
    data = request.param
    log.debug(f"In `remove_file_from_S3_with_yield()`, the `data` is {data}.")
    file_name_stem = f"{choice(('P', 'D', 'T', 'I'))}R_{most_recent_month_with_usage[0].strftime('%Y-%m')}_{most_recent_month_with_usage[1].strftime('%Y-%m')}_{datetime.now().strftime(AWS_timestamp_format())}"  # This is the format used for usage reports, which are the most frequently type of saved report
    log.info(f"In `remove_file_from_S3_with_yield()`, the `file_name_stem` is {file_name_stem}.")
    yield (file_name_stem, data)
    if isinstance(data, dict):
        file_name = file_name_stem + '.json'
    else:
        file_name = file_name_stem + '.txt'
    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=PATH_WITHIN_BUCKET_FOR_TESTS + file_name
        )
    except botocore.exceptions as error:
        log.error(f"Trying to remove file `{file_name}` from the S3 bucket raised {error}.")


def test_save_unconverted_data_via_upload(file_name_stem_and_data):
    """Tests saving data that can't be transformed for loading into the database to a file in S3."""
    file_name_stem, data = file_name_stem_and_data
    logging_message = save_unconverted_data_via_upload(
        data=data,
        file_name_stem=file_name_stem,
        bucket_path=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    if not upload_file_to_S3_bucket_success_regex().fullmatch(logging_message):
        assert False  # Entering this block means the function that's being tested raised an error, so continuing with the test won't provide anything meaningful
    list_objects_response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=PATH_WITHIN_BUCKET_FOR_TESTS,
    )
    bucket_contents = []
    for contents_dict in list_objects_response['Contents']:
        bucket_contents.append(contents_dict['Key'])
    bucket_contents = [file_name.replace(PATH_WITHIN_BUCKET_FOR_TESTS, "") for file_name in bucket_contents]
    if isinstance(data, dict):
        assert f"{file_name_stem}.json" in bucket_contents
    else:
        assert f"{file_name_stem}.txt" in bucket_contents