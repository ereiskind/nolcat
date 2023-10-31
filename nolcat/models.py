"""These classes represent the relations in the database."""

import logging
from pathlib import Path
import sys
import json
import re
from datetime import date
from datetime import datetime
import calendar
from sqlalchemy.ext.hybrid import hybrid_method  # Initial example at https://pynash.org/2013/03/01/Hybrid-Properties-in-SQLAlchemy/
import pandas as pd
from dateutil.rrule import rrule
from dateutil.rrule import MONTHLY

from .app import *
from .statements import *
from .SUSHI_call_and_response import SUSHICallAndResponse
from .convert_JSON_dict_to_dataframe import ConvertJSONDictToDataframe

log = logging.getLogger(__name__)


# Using field length constants ensures the lengths being checked for in `ConvertJSONDictToDataframe` are the lengths used in the database
RESOURCE_NAME_LENGTH = ConvertJSONDictToDataframe.RESOURCE_NAME_LENGTH
PUBLISHER_LENGTH = ConvertJSONDictToDataframe.PUBLISHER_LENGTH
PUBLISHER_ID_LENGTH = ConvertJSONDictToDataframe.PUBLISHER_ID_LENGTH
PLATFORM_LENGTH = ConvertJSONDictToDataframe.PLATFORM_LENGTH
AUTHORS_LENGTH = ConvertJSONDictToDataframe.AUTHORS_LENGTH
DOI_LENGTH = ConvertJSONDictToDataframe.DOI_LENGTH
PROPRIETARY_ID_LENGTH = ConvertJSONDictToDataframe.PROPRIETARY_ID_LENGTH
URI_LENGTH = ConvertJSONDictToDataframe.URI_LENGTH


def PATH_TO_CREDENTIALS_FILE():
    """Provides the file path to the SUSHI credentials file as a string.
    
    The SUSHI credentials are stored in a JSON file with a fixed location set by the Dockerfile that builds the `nolcat` container in the AWS image; the function's name is capitalized to reflect its nature as a constant. It's placed within a function for error handling--if the file can't be found, the program being run will exit cleanly.
    
    Returns:
        str: the absolute path to the R5 SUSHI credentials file
    """
    file_path = Path('/nolcat/nolcat/R5_SUSHI_credentials.json')
    if file_path.exists():
        log.debug(check_if_folder_exists_statement(file_path))
        return str(file_path)
    log.critical("The R5 SUSHI credentials file could not be located. The program is ending.")
    sys.exit()


class FiscalYears(db.Model):
    """The class representation of the `fiscalYears` relation, which contains a list of the fiscal years with data in the database as well as information about the national reporting aggregate statistics for the given fiscal year.
    
    Attributes:
        self.fiscal_year_ID (int): the primary key
        self.fiscal_year (string): the fiscal year in "yyyy" format; the ending year of the range is used
        self.start_date (datetime64[ns]): the first day of the fiscal year
        self.end_date (datetime64[ns]) the last day of the fiscal year
        self.depreciated_ACRL_60b (Int64): the reported value for depreciated ACRL 60b
        self.depreciated_ACRL_63 (Int64): the reported value for depreciated ACRL 63
        self.ACRL_61a (Int64): the reported value for ACRL 61a
        self.ACRL_61b (Int64): the reported value for 61b
        self.ARL_18 (Int64): the reported value for ARL 18
        self.ARL_19 (Int64): the reported value for ARL 19
        self.ARL_20 (Int64): the reported value for ARL 20
        self.notes_on_statisticsSources_used (text): notes on data sources used to collect ARL and ACRL/IPEDS numbers
        self.notes_on_corrections_after_submission (text): information on any corrections to usage data done by vendors after initial harvest, especially if later corrected numbers were used in national reporting statistics

    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
        calculate_depreciated_ACRL_60b: This method calculates the value of depreciated ACRL question 60b for the given fiscal year.
        calculate_depreciated_ACRL_63: This method calculates the value of depreciated ACRL question 63 for the given fiscal year.
        calculate_ACRL_61a: This method calculates the value of ACRL question 61a for the given fiscal year.
        calculate_ACRL_61b: This method calculates the value of ACRL question 61b for the given fiscal year.
        calculate_ARL_18: This method calculates the value of ARL question 18 for the given fiscal year.
        calculate_ARL_19: This method calculates the value of ARL question 19 for the given fiscal year.
        calculate_ARL_20: This method calculates the value of ARL question 20 for the given fiscal year.
        create_usage_tracking_records_for_fiscal_year: Create the records for the given fiscal year in the `annualUsageCollectionTracking` relation.
        collect_fiscal_year_usage_statistics: A method invoking the `_harvest_R5_SUSHI()` method for all of a fiscal year's usage.
    """
    __tablename__ = 'fiscalYears'

    fiscal_year_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    fiscal_year = db.Column(db.String(4), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    depreciated_ACRL_60b = db.Column(db.Integer)
    depreciated_ACRL_63 = db.Column(db.Integer)
    ACRL_61a = db.Column(db.Integer)
    ACRL_61b = db.Column(db.Integer)
    ARL_18 = db.Column(db.Integer)
    ARL_19 = db.Column(db.Integer)
    ARL_20 = db.Column(db.Integer)
    notes_on_statisticsSources_used = db.Column(db.Text)
    notes_on_corrections_after_submission = db.Column(db.Text)

    FK_in_AUCT = db.relationship('AnnualUsageCollectionTracking', backref='fiscalYears')


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "fiscal_year": 'string',
            "start_date": 'datetime64[ns]',
            "end_date": 'datetime64[ns]',
            "depreciated_ACRL_60b": 'Int64',
            "depreciated_ACRL_63": 'Int64',
            "ACRL_61a": 'Int64',
            "ACRL_61b": 'Int64',
            "ARL_18": 'Int64',
            "ARL_19": 'Int64',
            "ARL_20": 'Int64',
            "notes_on_statisticsSources_used": 'string',
            "notes_on_corrections_after_submission": 'string',
        }


    @hybrid_method
    def calculate_depreciated_ACRL_60b(self):
        """This method calculates the value of depreciated ACRL question 60b for the given fiscal year.

        ACRL 60b, which was last asked on the 2022 survey, was the sum of "usage of digital/electronic titles whether viewed, downloaded, or streamed. Include usage for e-books, e-serials, and e-media titles even if they were purchased as part of a collection or database."

        Returns:
            int: the answer to ACRL 60b
            str: the error message if a query fails
        """
        log.info(f"Starting `FiscalYears.calculate_depreciated_ACRL_60b()` for {self.fiscal_year}.")
        TR_B1_df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Title_Requests' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            """,
            engine=db.engine,
        )
        if isinstance(TR_B1_df, str):
            message = f"Unable to return requested sum because it relied on {TR_B1_df[0].lower()}{TR_B1_df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        else:
            TR_B1_sum = TR_B1_df.iloc[0][0]
            log.debug(return_value_from_query_statement(TR_B1_sum, "TR_B1"))

        IR_M1_df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Total_Item_Requests' AND data_type='Multimedia' AND access_method='Regular' AND report_type='IR';
            """,
            engine=db.engine,
        )
        if isinstance(IR_M1_df, str):
            message = f"Unable to return requested sum because it relied on {IR_M1_df[0].lower()}{IR_M1_df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        else:
            IR_M1_sum = IR_M1_df.iloc[0][0]
            log.debug(return_value_from_query_statement(IR_M1_sum, "IR_M1"))

        TR_J1_df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            """,
            engine=db.engine,
        )
        if isinstance(TR_J1_df, str):
            message = f"Unable to return requested sum because it relied on {TR_J1_df[0].lower()}{TR_J1_df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        else:
            TR_J1_sum = TR_J1_df.iloc[0][0]
            log.debug(return_value_from_query_statement(TR_J1_sum, "TR_J1"))
        
        return TR_B1_sum + IR_M1_sum + TR_J1_sum


    @hybrid_method
    def calculate_depreciated_ACRL_63(self):
        """This method calculates the value of depreciated ACRL question 63 for the given fiscal year.

        ACRL 60b, which was last asked on the 2022 survey, was the sum of "usage of e-serial titles whether viewed, downloaded, or streamed. Include usage for e-serial titles only, even if the title was purchased as part of a database."

        Returns:
            int: the answer to ACRL 63
            str: the error message if the query fails
        """
        log.info(f"Starting `FiscalYears.calculate_depreciated_ACRL_63()` for {self.fiscal_year}.")
        df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            """,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = f"Unable to return requested sum because it relied on {df[0].lower()}{df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        ACRL_63 = df.iloc[0][0]
        log.debug(return_value_from_query_statement(ACRL_63))
        return ACRL_63
    

    @hybrid_method
    def calculate_ACRL_61a(self):
        """This method calculates the value of ACRL question 61a for the given fiscal year.

        ACRL 61a is the sum of "usage of digital/electronic titles whether viewed, downloaded, or streamed.  Do not include institutional repository documents.Include usage for e-books and e-media titles only, even if the title was purchased as part of a database."

        Returns:
            int: the answer to ACRL 61a
            str: the error message if a query fails
        """
        log.info(f"Starting `FiscalYears.calculate_ACRL_61a()` for {self.fiscal_year}.")
        TR_B1_df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Title_Requests' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            """,
            engine=db.engine,
        )
        if isinstance(TR_B1_df, str):
            message = f"Unable to return requested sum because it relied on {TR_B1_df[0].lower()}{TR_B1_df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        else:
            TR_B1_sum = TR_B1_df.iloc[0][0]
            log.debug(return_value_from_query_statement(TR_B1_sum, "TR_B1"))

        IR_M1_df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Total_Item_Requests' AND data_type='Multimedia' AND access_method='Regular' AND report_type='IR';
            """,
            engine=db.engine,
        )
        if isinstance(IR_M1_df, str):
            message = f"Unable to return requested sum because it relied on {IR_M1_df[0].lower()}{IR_M1_df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        else:
            IR_M1_sum = IR_M1_df.iloc[0][0]
            log.debug(return_value_from_query_statement(IR_M1_sum, "IR_M1"))

        return TR_B1_sum + IR_M1_sum


    @hybrid_method
    def calculate_ACRL_61b(self):
        """This method calculates the value of ACRL question 61b for the given fiscal year.

        ACRL 61b is the sum of "usage of e-serial titles whether viewed, downloaded, or streamed. Include usage for e-serial titles only, even if the title was purchased as part of a database." This calculation includes open access usage.

        Returns:
            int: the answer to ACRL 61b, OA included
            str: the error message if a query fails
        """
        log.info(f"Starting `FiscalYears.calculate_ACRL_61b()` for {self.fiscal_year}.")
        df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_method='Regular' AND report_type='TR';
            """,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = f"Unable to return requested sum because it relied on {df[0].lower()}{df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        ACRL_61b = df.iloc[0][0]
        log.debug(return_value_from_query_statement(ACRL_61b))
        return ACRL_61b


    @hybrid_method
    def calculate_ARL_18(self):
        """This method calculates the value of ARL question 18 for the given fiscal year.

        ARL 18 is the "Number of successful full-text article requests (journals)."

        Returns:
            int: the answer to ARL 18
            str: the error message if the query fails
        """
        log.info(f"Starting `FiscalYears.calculate_ARL_18()` for {self.fiscal_year}.")
        df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_method='Regular' AND report_type='TR';
            """,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = f"Unable to return requested sum because it relied on {df[0].lower()}{df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        ARL_18= df.iloc[0][0]
        log.debug(return_value_from_query_statement(ARL_18))
        return ARL_18

    
    @hybrid_method
    def calculate_ARL_19(self):
        """This method calculates the value of ARL question 19 for the given fiscal year.

        ARL 19 is the "Number of regular searches (databases)."

        Returns:
            int: the answer to ARL 19
            str: the error message if the query fails
        """
        log.info(f"Starting `FiscalYears.calculate_ARL_19()` for {self.fiscal_year}.")
        df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Searches_Regular' AND access_method='Regular' AND report_type='DR';
            """,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = f"Unable to return requested sum because it relied on {df[0].lower()}{df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        ARL_19= df.iloc[0][0]
        log.debug(return_value_from_query_statement(ARL_19))
        return ARL_19


    @hybrid_method
    def calculate_ARL_20(self):
        """This method calculates the value of ARL question 20 for the given fiscal year.

        ARL 20 is the "Number of federated searches (databases)."

        Returns:
            int: the answer to ARL 20
            str: the error message if the query fails
        """
        log.info(f"Starting `FiscalYears.calculate_ARL_20()` for {self.fiscal_year}.")
        df = query_database(
            query=f"""
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Searches_Federated' AND access_method='Regular' AND report_type='DR';
            """,
            engine=db.engine,
        )
        if isinstance(df, str):
            message = f"Unable to return requested sum because it relied on {df[0].lower()}{df[1:]}"  ##database_query_fail_statement()
            log.warning(message)
            return message
        ARL_20= df.iloc[0][0]
        log.debug(return_value_from_query_statement(ARL_20))
        return ARL_20


    @hybrid_method
    def create_usage_tracking_records_for_fiscal_year(self):
        """Create the records for the given fiscal year in the `annualUsageCollectionTracking` relation.

        Scheduling a function to run within Python requires a module that calls that function to be running, making programmatically adding new records at the start of each fiscal year an aspirational iteration. For the `fiscalYears` relation, only one record needs to be added each year, so manually adding the record isn't problematic. For `annualUsageCollectionTracking`, which requires hundreds of new records which are identified through a field in the `statisticsResourceSources` relation, a method to create the new records is necessary.

        Returns:
            str: the logging statement to indicate if calling and loading the data succeeded or failed
        """
        log.info(f"Starting `FiscalYears.create_usage_tracking_records_for_fiscal_year()` for {self.fiscal_year}.")
        #Section: Get PKs of the Fiscal Year's Statistics Sources
        current_statistics_sources = query_database(
            query=f"SELECT SRS_statistics_source FROM statisticsResourceSources WHERE current_statistics_source=true;",  # In MySQL, `field=true` is faster when the field is indexed and all values are either `1` or `0` (MySQL's Boolean field actually stores a one-bit integer) (see https://stackoverflow.com/q/24800881 and https://stackoverflow.com/a/34149077)
            engine=db.engine,
        )
        if isinstance(current_statistics_sources, str):
            return current_statistics_sources  ##database_query_fail_statement()
        log.debug(return_database_from_query_statement("current statistics sources PKs", current_statistics_sources))
        current_statistics_sources_PKs = [(PK, self.fiscal_year_ID) for PK in current_statistics_sources['SRS_statistics_source'].unique().tolist()]  # `uniques()` method returns a numpy array, so numpy's `tolist()` method is used

        #Section: Create Dataframe to Load into Relation
        multiindex = pd.MultiIndex.from_tuples(
            current_statistics_sources_PKs,
            names=["AUCT_statistics_source", "AUCT_fiscal_year"],
        )
        all_records = []
        for i in range(len(multiindex)):
            all_records.append([None, None, None, None, None, None, None])  # All seven of the non-PK fields in the relation should contain null values at creation
        df = pd.DataFrame(
            all_records,
            index=multiindex,
            columns=["usage_is_being_collected", "manual_collection_required", "collection_via_email", "is_COUNTER_compliant", "collection_status", "usage_file_path", "notes"],
        )
        df = df.astype(AnnualUsageCollectionTracking.state_data_types())
        log.info(f"Records being loaded into `annualUsageCollectionTracking`:\n{df.index}")
        log.debug(f"And a summary of the dataframe the above records are in:\n{return_string_of_dataframe_info(df)}")

        #Section: Load Data into `annualUsageCollectionTracking` Relation
        load_result = load_data_into_database(
            df=df,
            relation='annualUsageCollectionTracking',
            engine=db.engine,
            index_field_name=["AUCT_statistics_source", "AUCT_fiscal_year"],
        )
        return load_result


    @hybrid_method
    def collect_fiscal_year_usage_statistics(self):
        """A method invoking the `_harvest_R5_SUSHI()` method for all of a fiscal year's usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Returns:
            tuple: the logging statement to indicate if calling and loading the data succeeded or failed (str); a dictionary of harvested reports and the list of the statements that should be flashed returned by those reports (dict, key: str, value: list of str)
        """
        log.info(f"Starting `FiscalYears.collect_fiscal_year_usage_statistics()` for {self.fiscal_year}.")
        #Section: Get AUCT Records for Statistics Sources to be Pulled
        AUCT_objects_to_collect_df = query_database(
            query=f"""
                SELECT
                    annualUsageCollectionTracking.AUCT_statistics_source,
                    annualUsageCollectionTracking.AUCT_fiscal_year,
                    annualUsageCollectionTracking.usage_is_being_collected,
                    annualUsageCollectionTracking.manual_collection_required,
                    annualUsageCollectionTracking.collection_via_email,
                    annualUsageCollectionTracking.is_COUNTER_compliant,
                    annualUsageCollectionTracking.collection_status,
                    annualUsageCollectionTracking.usage_file_path,
                    annualUsageCollectionTracking.notes
                FROM annualUsageCollectionTracking
                    JOIN statisticsSources ON statisticsSources.statistics_source_ID=annualUsageCollectionTracking.AUCT_statistics_source
                    JOIN fiscalYears ON fiscalYears.fiscal_year_ID=annualUsageCollectionTracking.AUCT_fiscal_year
                WHERE annualUsageCollectionTracking.AUCT_fiscal_year={self.fiscal_year_ID} AND
                annualUsageCollectionTracking.usage_is_being_collected=true AND
                annualUsageCollectionTracking.manual_collection_required=false;
            """,  #ToDo: Is a check that `annualUsageCollectionTracking.collection_status` isn't "Collection complete" needed?
            engine=db.engine,
        )
        if isinstance(AUCT_objects_to_collect_df, str):
            return (AUCT_objects_to_collect_df, [AUCT_objects_to_collect_df])  ##database_query_fail_statement()
        log.debug(f"The dataframe of the AUCT records of the statistics sources that need their usage collected for FY {self.fiscal_year}:\n{AUCT_objects_to_collect_df}")
        AUCT_objects_to_collect = [
            AnnualUsageCollectionTracking(
                AUCT_statistics_source=record_tuple[0],
                AUCT_fiscal_year=record_tuple[1],
                usage_is_being_collected=record_tuple[2],
                manual_collection_required=record_tuple[3],
                collection_via_email=record_tuple[4],
                is_COUNTER_compliant=record_tuple[5],
                collection_status=record_tuple[6],
                usage_file_path=record_tuple[7],
                notes=record_tuple[8],
            ) for record_tuple in AUCT_objects_to_collect_df.itertuples(name=None)
        ]
        log.info(f"The AUCT records of the statistics sources that need their usage collected for FY {self.fiscal_year}:\n{format_list_for_stdout(AUCT_objects_to_collect)}")

        #Section: Collect Usage from Each Statistics Source
        dfs = []
        where_statements = []
        all_flash_statements = []
        for AUCT_object in AUCT_objects_to_collect:
            statistics_source = query_database(
                query=f"""
                    SELECT
                        statisticsSources.statistics_source_ID,
                        statisticsSources.statistics_source_name,
                        statisticsSources.statistics_source_retrieval_code,
                        statisticsSources.vendor_ID
                    FROM statisticsSources
                    WHERE statisticsSources.statistics_source_ID={AUCT_object.AUCT_statistics_source};
                """,
                engine=db.engine,
            )
            if isinstance(statistics_source, str):
                all_flash_statements.append(f"Unable to collect usage statistics for the statistics source with primary key {AUCT_object.AUCT_statistics_source} because it relied on {statistics_source[0].lower()}{statistics_source[1:].replace(' raised', ', which raised')}")  ##database_query_fail_statement()
                continue
            df, flash_statements = statistics_source._harvest_R5_SUSHI(self.start_date, self.end_date)
            for statement in flash_statements:
                all_flash_statements.append(f"{statement} [statistics source {statistics_source.statistics_source_name}; FY {self.fiscal_year}]")
            if isinstance(df, str):
                continue
            dfs.append(df)
            where_statements.append(f"(AUCT_statistics_source={AUCT_object.AUCT_statistics_source} AND AUCT_fiscal_year={AUCT_object.AUCT_fiscal_year})")
            log.debug(f"The SUSHI harvest for statistics source {statistics_source.statistics_source_name} for FY {self.fiscal_year} successfully found {df.shape[1]} records. Those records and the `annualUsageCollectionTracking` relation composite primary key value have been saved for loaded into the database.")  ##_harvest_R5_SUSHI_success_statement()
        
        #Section: Update Data in Database
        df = pd.concat(dfs)
        try:
            df.index += first_new_PK_value('COUNTERData')
        except Exception as error:
            message = unable_to_get_updated_primary_key_values_statement("COUNTERData", error)
            log.warning(message)
            all_flash_statements.append(message)
            return (message, all_flash_statements)
        load_result = load_data_into_database(
            df=df,
            relation='COUNTERData',
            engine=db.engine,
            index_field_name='COUNTER_data_ID',
        )
        if load_result.startswith("Loading data into the COUNTERData relation raised the error"):  ##CheckStatement
            return (load_result, all_flash_statements)
        update_statement = f"""
            UPDATE annualUsageCollectionTracking
            SET collection_status='Collection complete'
            WHERE {" OR ".join(where_statements)};
        """
        update_result = update_database(
            update_statement=update_statement,
            engine=db.engine,
        )
        if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
            message = f"Updating the `annualUsageCollectionTracking` relation automatically failed, so the SQL update statement needs to be submitted via the SQL command line:\n{update_statement}"  ##add_data_success_and_update_database_fail_statement()
            log.warning(message)
            all_flash_statements.append(message)
            return (f"{load_result[:-1]}, but {message[0].lower()}{message[1:]}", all_flash_statements)
        return (f"{load_result[:-1]} and {update_result[13:]}", all_flash_statements)  ##add_data_and_update_database_success_statement()


class Vendors(db.Model):
    """The class representation of the `vendors` relation, which contains a list of entities that provide access to either electronic resources or usage statistics.
    
    Attributes:
        self.vendor_ID (int): the primary key
        self.vendor_name (string): the name of the vendor= db.Column(db.String(80))
        self.alma_vendor_code (string): the code used to identify vendors in the Alma API return value

    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
        get_statisticsSources_records: Shows the records for all the statistics sources associated with the vendor.
        get_resourceSources_records: Shows the records for all the resource sources associated with the vendor.
        add_note: #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'vendors'

    vendor_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    vendor_name = db.Column(db.String(80), nullable=False)
    alma_vendor_code = db.Column(db.String(10))

    FK_in_VendorNotes = db.relationship('VendorNotes', backref='vendors')
    FK_in_StatisticsSources = db.relationship('StatisticsSources', backref='vendors')
    FK_in_ResourceSources = db.relationship('ResourceSources', backref='vendors')


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "vendor_name": 'string',
            "alma_vendor_code": 'string',
        }


    @hybrid_method
    def get_statisticsSources_records(self):
        """Shows the records for all the statistics sources associated with the vendor.

        Returns:
            dataframe: a filtered copy of the `statisticsSources` relation
        """
        log.info(f"Starting `Vendors.get_statisticsSources_records()` for {self.vendor_name}.")
        # vendor_PK = the int value that serves as the primary key for the vendor
        # df = query_database(
        #     query=f"""
        #         SELECT
        #             statistics_source_ID,
        #             statistics_source_name,
        #             statistics_source_retrieval_code
        #         FROM statisticsSources
        #         WHERE vendor_ID={vendor_PK};
        #     """,
        #     engine=db.engine,
        #     index='statistics_source_ID',
        # )
        # if isinstance(df, str):
        #     ##database_query_fail_statement()
        # log.debug(return_database_from_query_statement(f"a list of statistics sources associated with {self.vendor_name}", df))
        # return df
        pass


    @hybrid_method
    def get_resourceSources_records(self):
        """Shows the records for all the resource sources associated with the vendor.

        Returns:
            dataframe: a filtered copy of the `resourceSources` relation
        """
        log.info(f"Starting `Vendors.get_resourceSources_records()` for {self.vendor_name}.")
        # vendor_PK = the int value that serves as the primary key for the vendor
        # df = query_database(
        #     query=f"""
        #         SELECT
        #             resource_source_ID,
        #             resource_source_name,
        #             source_in_use,
        #             access_stop_date
        #         FROM resourceSources
        #         WHERE vendor_ID={vendor_PK};
        #     """,
        #     engine=db.engine,
        #     index='resource_source_ID',
        # )
        # if isinstance(df, str):
        #     ##database_query_fail_statement()
        # log.debug(return_database_from_query_statement(f"a list of resource sources associated with {self.vendor_name}", df))
        # return df
        pass


    @hybrid_method
    def add_note(self):
        log.info(f"Starting `Vendors.add_note()` for {self.vendor_name}.")
        #ToDo: Create a method for adding notes
        pass


class VendorNotes(db.Model):
    """The class representation of the `vendorNotes` relation, which contains notes about the vendors in `vendors`.
    
    Attributes:
        self.vendor_notes_ID (int): the primary key
        self.note (text): the content of the note
        self.written_by (string): the note author
        self.date_written (datetime64[ns]): the day the note was last edited
        self.vendor_ID (int): the foreign key for `vendors`
    
    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
    """
    __tablename__ = 'vendorNotes'

    vendor_notes_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    note = db.Column(db.Text)
    written_by = db.Column(db.String(100))
    date_written = db.Column(db.Date)
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'), nullable=False)


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "note": 'string',
            "written_by": 'string',
            "date_written": 'datetime64[ns]',
            "vendor_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        }


class StatisticsSources(db.Model):
    """The class representation of the `statisticsSources` relation, which contains a list of all the possible sources of usage statistics.
    
    Attributes:
        self.statistics_source_ID (int): the primary key
        self.statistics_source_name (string): the name of the statistics source
        self.statistics_source_retrieval_code (string): the ID used to uniquely identify each set of SUSHI credentials in the SUSHI credentials JSON
        self.vendor_ID (int): the foreign key for `vendors`
    
    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
        fetch_SUSHI_information: A method for fetching the information required to make a SUSHI API call for the statistics source.
        _harvest_R5_SUSHI: Collects the specified COUNTER R5 reports for the given statistics source and converts them into a single dataframe.
        _harvest_single_report: Makes a single API call for a customizable report with all possible attributes.
        _check_if_data_in_database: Checks if any usage report for the given date and statistics source combination is already in the database.
        collect_usage_statistics: A method invoking the `_harvest_R5_SUSHI()` method for usage in the specified time range.
        add_note: #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'statisticsSources'

    statistics_source_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    statistics_source_name = db.Column(db.String(100), nullable=False)
    statistics_source_retrieval_code = db.Column(db.String(30))
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'), nullable=False)

    FK_in_StatisticsSourceNotes = db.relationship('StatisticsSourceNotes', backref='statisticsSources')
    FK_in_StatisticsResourceSources = db.relationship('StatisticsResourceSources', backref='statisticsSources')
    FK_in_AUCT = db.relationship('AnnualUsageCollectionTracking', backref='statisticsSources')
    FK_in_COUNTERData = db.relationship('COUNTERData', backref='statisticsSources')


    def __repr__(self):
        """The printable representation of a `StatisticsSources` instance."""
        return f"<'statistics_source_ID': '{self.statistics_source_ID}', 'statistics_source_name': '{self.statistics_source_name}', 'statistics_source_retrieval_code': '{self.statistics_source_retrieval_code}', 'vendor_ID': '{self.vendor_ID}'>"
    

    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "statistics_source_name": 'string',
            "statistics_source_retrieval_code": 'string',
            "vendor_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        }


    @hybrid_method
    def fetch_SUSHI_information(self, for_API_call=True):
        """A method for fetching the information required to make a SUSHI API call for the statistics source.

        This method fetches the information for making a SUSHI API call and, depending on the optional argument value, returns them for use in an API call or for display to the user.

        Args:
            for_API_call (bool, optional): a Boolean indicating if the return value should be formatted for use in an API call, which is the default; the other option is formatting the return value for display to the user
        
        Returns:
            dict: the SUSHI API parameters as a dictionary with the API call URL added as a value with the key `URL`
            TBD: a data type that can be passed into Flask for display to the user
        """
        log.info(f"Starting `StatisticsSources.fetch_SUSHI_information()` for {self.statistics_source_name} with retrieval code {self.statistics_source_retrieval_code} (type {repr(type(self.statistics_source_retrieval_code))}).")
        #Section: Retrieve Data
        #Subsection: Retrieve Data from JSON
        with open(PATH_TO_CREDENTIALS_FILE()) as JSON_file:
            SUSHI_data_file = json.load(JSON_file)
            log.debug("JSON with SUSHI credentials loaded.")
            for vendor in SUSHI_data_file:  # No index operator needed--outermost structure is a list
                for statistics_source_dict in vendor['interface']:  # `interface` is a key within the `vendor` dictionary, and its value, a list, is the only info needed, so the index operator is used to reference the specific key
                    if statistics_source_dict['interface_id'] == self.statistics_source_retrieval_code:
                        log.debug(f"Saving credentials for {self.statistics_source_name} ({self.statistics_source_retrieval_code}) to dictionary.")
                        credentials = dict(
                            URL = statistics_source_dict['statistics']['online_location'],
                            customer_id = statistics_source_dict['statistics']['user_id']
                        )

                        try:
                            credentials['requestor_id'] = statistics_source_dict['statistics']['user_password']
                        except:
                            pass

                        try:
                            credentials['api_key'] = statistics_source_dict['statistics']['user_pass_note']
                        except:
                            pass

                        try:
                            credentials['platform'] = statistics_source_dict['statistics']['delivery_address']
                        except:
                            pass

        #Subsection: Retrieve Data from Alma
        #ToDo: When credentials are in Alma, create this functionality


        #Section: Return Data in Requested Format
        if for_API_call:
            log.info(f"Returning the credentials {credentials} for a SUSHI API call.")
            return credentials
        else:
            #ToDo: Pass credentials as formatted string back to route function; where is this version of the method being called?
            return f"ToDo: Display {credentials} in Flask."


    @hybrid_method
    def _harvest_R5_SUSHI(self, usage_start_date, usage_end_date, report_to_harvest=None):
        """Collects the specified COUNTER R5 reports for the given statistics source and converts them into a single dataframe.

        For a given statistics source and date range, this method uses SUSHI to harvest the specified COUNTER R5 report(s) at their most granular level, then combines all gathered report(s) in a single dataframe. This is a private method where the calling method provides the parameters and loads the results into the `COUNTERData` relation.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
            report_to_harvest (str, optional): the report ID for the customizable report to harvest; defaults to `None`, which harvests all available custom reports
        
        Returns:
            tuple: all the SUSHI data per the specified arguments (dataframe) or an error message (str); a dictionary of harvested reports and the list of the statements that should be flashed returned by those reports (dict, key: str, value: list of str)
        """
        #Section: Get API Call URL and Parameters
        log.info(f"Starting `StatisticsSources._harvest_R5_SUSHI()` for {self.statistics_source_name} for {usage_start_date.strftime('%Y-%m-%d')} to {usage_end_date.strftime('%Y-%m-%d')}.")
        if usage_start_date > usage_end_date:
            message = attempted_SUSHI_call_with_invalid_dates_statement(usage_end_date, usage_start_date)
            log.error(message)
            return (message, {'dates': [message]})
        SUSHI_info = self.fetch_SUSHI_information()
        log.debug(f"`StatisticsSources.fetch_SUSHI_information()` method returned the credentials {SUSHI_info} for a SUSHI API call.")  # This is nearly identical to the logging statement just before the method return statement and is for checking that the program does return to this method
        SUSHI_parameters = {key: value for key, value in SUSHI_info.items() if key != "URL"}
        all_flashed_statements = {}
        log.info(f"Making SUSHI calls for {self.statistics_source_name}.")  ##about_to_statement()


        #Section: Confirm SUSHI API Functionality
        SUSHI_status_response, flash_message_list = SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "status", SUSHI_parameters).make_SUSHI_call()
        all_flashed_statements['status'] = flash_message_list
        if isinstance(SUSHI_info['URL'], str) and re.match(r'https?://.*mathscinet.*\.\w{3}/', SUSHI_info['URL']):  # MathSciNet `status` endpoint returns HTTP status code 400, which will cause an error here, but all the other reports are viable; this specifically bypasses the error checking for the SUSHI call to the `status` endpoint to the domain starting with `mathscinet` via `re.match()`
            log.info(successful_SUSHI_call_statement("status", self.statistics_source_name))
            pass
        #ToDo: Is there a way to bypass `HTTPSConnectionPool` errors caused by `SSLError(CertificateError`?
        elif isinstance(SUSHI_status_response, str) or isinstance(SUSHI_status_response, Exception):
            message = f"The call to the `status` endpoint for {self.statistics_source_name} raised the error {SUSHI_status_response}."  ##failed_SUSHI_call_statement_statement()
            log.warning(message)
            return (message, all_flashed_statements)
        else:
            log.info(successful_SUSHI_call_statement("status", self.statistics_source_name))
            pass


        #Section: Harvest Individual Report if Specified
        if isinstance(report_to_harvest, str):
            log.debug(f"Harvesting just a {report_to_harvest} report.")
            if report_to_harvest == "PR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
            elif report_to_harvest == "DR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
            elif report_to_harvest == "TR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
            elif report_to_harvest == "IR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Authors|Publication_Date|Article_Version"
                SUSHI_parameters["include_parent_details"] = "True"
            else:
                message = "An invalid value was received from a fixed text field."
                log.critical(message)
                all_flashed_statements['CRITICAL'] = message
                return (message, all_flashed_statements)
            SUSHI_data_response, flash_message_list = self._harvest_single_report(
                report_to_harvest,
                SUSHI_info['URL'],
                SUSHI_parameters,
                usage_start_date,
                usage_end_date,
            )
            all_flashed_statements[report_to_harvest] = flash_message_list
            if isinstance(SUSHI_data_response, str):
                log.error(SUSHI_data_response)
            return (SUSHI_data_response, all_flashed_statements)
        
        else:  # Default; `else` not needed for handling invalid input because input option is a fixed text field
            #Section: Get List of Resources
            #Subsection: Make API Call
            log.debug(f"Making a call for the `reports` endpoint.")
            SUSHI_reports_response, flash_message_list = SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "reports", SUSHI_parameters).make_SUSHI_call()
            all_flashed_statements['reports'] = flash_message_list
            if len(SUSHI_reports_response) == 1 and list(SUSHI_reports_response.keys())[0] == "reports":  # The `reports` route should return a list; to make it match all the other routes, the `make_SUSHI_call()` method makes it the value in a one-item dict with the key `reports`
                log.info(successful_SUSHI_call_statement("reports", self.statistics_source_name))
                all_available_reports = []
                for report_call_response in SUSHI_reports_response.values():  # The dict only has one value, so there will only be one iteration
                    for report_details_dict in report_call_response:
                        for report_detail_keys, report_detail_values in report_details_dict.items():
                            if isinstance(report_detail_keys, str) and re.fullmatch(r'[Rr]eport_[Ii][Dd]', report_detail_keys):
                                all_available_reports.append(report_detail_values)
                log.debug(f"All reports provided by {self.statistics_source_name}: {all_available_reports}.")
            elif isinstance(SUSHI_reports_response, str):
                log.warning(SUSHI_reports_response)
                return (SUSHI_reports_response, all_flashed_statements)
            else:
                message = f"The SUSHI call for a list of reports returned the following invalid value; investigation into the response  is required:\n{SUSHI_reports_response}"
                log.error(message)
                return (message, all_flashed_statements)

            #Subsection: Get List of Available Customizable Reports
            available_reports = [report for report in all_available_reports if re.search(r'\w{2}(_\w\d)?', report)]
            available_custom_reports = [custom_report for custom_report in available_reports if "_" not in custom_report]
            log.info(f"Customizable reports provided by {self.statistics_source_name}: {available_custom_reports}.")

            #Subsection: Add Any Standard Reports Not Corresponding to a Customizable Report
            represented_by_custom_report = set()
            for custom_report in available_custom_reports:
                for report in available_reports:
                    if report[0:2] == custom_report:
                        represented_by_custom_report.add(report)
            not_represented_by_custom_report = [report for report in available_reports if report not in represented_by_custom_report]
            if len(not_represented_by_custom_report) > 0:  # Logging statement only appears if it would include content
                log.debug(f"Standard reports lacking corresponding customizable reports provided by {self.statistics_source_name}: {not_represented_by_custom_report}.")


            #Section: Make Customizable Report SUSHI Calls
            #Subsection: Set Up Loop Through Customizable Reports
            custom_report_dataframes = []
            complete_flash_message_list = []
            no_usage_returned_count = 0
            for custom_report in available_custom_reports:
                report_name = custom_report.upper()
                log.info(f"Starting SUSHI calls to {self.statistics_source_name} for report {report_name}.")  ##about_to_statement()

                #Subsection: Add Parameters for Customizable Report Type
                if "include_parent_details" in list(SUSHI_parameters.keys()):  # When included in reports other than IR, this parameter often causes an error message to appear
                    del SUSHI_parameters["include_parent_details"]
                
                if report_name == "PR":
                    SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
                elif report_name == "DR":
                    SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
                elif report_name == "TR":
                    SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
                elif report_name == "IR":
                    SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Authors|Publication_Date|Article_Version"
                    SUSHI_parameters["include_parent_details"] = "True"
                else:
                    #ToDo: Allow for standard reports not matching an available customizable report to be pulled
                    log.warning(f"The {report_name} report for {self.statistics_source_name} isn't recognized as a customizable report. Without knowing the appropriate parameters to add to the SUSHI call, this report wasn't pulled.")
                    continue  # A `return` statement here would keep any other valid reports from being pulled and processed

                #Subsection: Make API Call(s)
                SUSHI_data_response, flash_message_list = self._harvest_single_report(
                    report_name,
                    SUSHI_info['URL'],
                    SUSHI_parameters,
                    usage_start_date,
                    usage_end_date,
                )
                all_flashed_statements[report_name] = flash_message_list
                for item in flash_message_list:
                    complete_flash_message_list.append(item)
                if isinstance(SUSHI_data_response, str) and re.fullmatch(r'The call to the .* endpoint for .* raised the SUSHI error.*API calls to .* have stopped and no other calls will be made\.', SUSHI_data_response):  ##CheckStatement
                    log.error(SUSHI_data_response)
                    return (SUSHI_data_response, all_flashed_statements)
                elif isinstance(SUSHI_data_response, str) and re.search(r'returned no( usage)? data', SUSHI_data_response):  ##CheckStatement
                    log.debug("The `no_usage_returned_count` counter in `StatisticsSources._harvest_R5_SUSHI()` is being increased.")
                    no_usage_returned_count += 1
                    continue  # A `return` statement here would keep any other valid reports from being pulled and processed
                custom_report_dataframes.append(SUSHI_data_response)
            if len(custom_report_dataframes) == no_usage_returned_count:
                message = f"All of the calls to {self.statistics_source_name} returned no usage data."
                log.warning(message)
                return (message, all_flashed_statements)


            #Section: Return a Single Dataframe
            try:
                return (pd.concat(custom_report_dataframes, ignore_index=True), all_flashed_statements)  # Without `ignore_index=True`, the autonumbering from the creation of each individual dataframe is retained, causing a primary key error when attempting to load the dataframe into the database
            except ValueError as error:
                message = f"The harvested reports couldn't be combined because of the error {error}."
                log.error(message)
                return (message, all_flashed_statements)


    @hybrid_method
    def _harvest_single_report(self, report, SUSHI_URL, SUSHI_parameters, start_date, end_date):
        """Makes a single API call for a customizable report with all possible attributes.

        Args:
            report (str): the two-letter abbreviation for the report being called
            SUSHI_URL (str): the root URL for the SUSHI API call
            SUSHI_parameters (str): the parameter values for the API call
            start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month
            end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month

        Returns:
            tuple: SUSHI data from the API call (dataframe) or an error message (str); a list of the statements that should be flashed (list of str)
        """
        log.info(f"Starting `StatisticsSources._harvest_single_report()` for {report} from {self.statistics_source_name} for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
        subset_of_months_to_harvest = self._check_if_data_in_database(report, start_date, end_date)
        if isinstance(subset_of_months_to_harvest, str) and re.fullmatch(r'Running the query `.*` raised the error .*\.', subset_of_months_to_harvest, flags=re.DOTALL):  ##CheckStatement
            message = f"When attempting to check if the data was already in the database, {subset_of_months_to_harvest[0].lower()}{subset_of_months_to_harvest[1:]}"
            return (message, [message])
        elif subset_of_months_to_harvest:
            log.info(f"Calling `reports/{report.lower()}` endpoint for {self.statistics_source_name} for individual months to avoid adding duplicate data in the database.")  ##about_to_statement()
            individual_month_dfs = []
            complete_flash_message_list = []
            no_usage_returned_count = 0
            for month_to_harvest in subset_of_months_to_harvest:
                SUSHI_parameters['begin_date'] = month_to_harvest
                SUSHI_parameters['end_date'] = date(
                    month_to_harvest.year,
                    month_to_harvest.month,
                    calendar.monthrange(month_to_harvest.year, month_to_harvest.month)[1],
                )
                SUSHI_data_response, flash_message_list = SUSHICallAndResponse(self.statistics_source_name, SUSHI_URL, f"reports/{report.lower()}", SUSHI_parameters).make_SUSHI_call()
                for item in flash_message_list:
                    complete_flash_message_list.append(item)
                if isinstance(SUSHI_data_response, str) and re.fullmatch(r'The call to the `.*` endpoint for .* raised the SUSHI errors?[\n\s].*[\n\s]API calls to .* have stopped and no other calls will be made\.', SUSHI_data_response):  ##CheckStatement
                    message = f"Data collected from the call to the `reports/{report.lower()}` endpoint for {self.statistics_source_name} before this point won't be loaded into the database."
                    log.warning(SUSHI_data_response + " " + message)
                    complete_flash_message_list.append(message)
                    return (SUSHI_data_response, complete_flash_message_list)
                elif isinstance(SUSHI_data_response, str) and re.fullmatch(r'The call to the `.*` endpoint for .* returned no( usage)? data.*', SUSHI_data_response):  ##CheckStatement
                    log.debug("The `no_usage_returned_count` counter in `StatisticsSources._harvest_single_report()` is being increased.")
                    no_usage_returned_count += 1
                    log.warning(SUSHI_data_response)
                    continue  # A `return` statement here would keep any other valid reports from being pulled and processed
                elif isinstance(SUSHI_data_response, str):
                    log.warning(SUSHI_data_response)
                    continue  # A `return` statement here would keep any other valid reports from being pulled and processed
                
                if len(subset_of_months_to_harvest) == no_usage_returned_count:
                    message = f"The calls to the `reports/{report.lower()}` endpoint for {self.statistics_source_name} returned no usage data."
                    log.warning(message)
                    return (message, complete_flash_message_list)
                df = ConvertJSONDictToDataframe(SUSHI_data_response).create_dataframe()
                if isinstance(df, str):
                    message = unable_to_convert_SUSHI_data_to_dataframe_statement(df, report, self.statistics_source_name)
                    log.warning(message)
                    temp_file_path = Path(__file__).parent / 'temp.json'
                    with open(temp_file_path, 'xb') as JSON_file:  # The JSON-like dict is being saved to a file because `upload_file_to_S3_bucket()` takes file-like objects or path-like objects that lead to file-like objects
                        json.dump(SUSHI_data_response, JSON_file)
                    file_name = f"{self.statistics_source_ID}_reports-{report.lower()}_{SUSHI_parameters['begin_date'].strftime('%Y-%m')}_{SUSHI_parameters['end_date'].strftime('%Y-%m')}_{datetime.now().isoformat()}.json"
                    log.debug(file_IO_statement(file_name, f"temporary file location {temp_file_path.resolve()}", f"S3 bucket {BUCKET_NAME}"))
                    logging_message = upload_file_to_S3_bucket(
                        temp_file_path,
                        file_name,
                    )
                    if isinstance(logging_message, str) and re.fullmatch(r'Running the function `.*\(\)` on .* \(type .*\) raised the error .*\.', logging_message):  ##CheckStatement
                        message = message + " " + failed_upload_to_S3_statement(file_name, logging_message)
                        log.critical(message)
                    else:
                        message = message + " " + logging_message
                        log.debug(message)
                    temp_file_path.unlink()
                    complete_flash_message_list.append(message)
                    continue  # A `return` statement here would keep any other reports from being pulled and processed
                df['statistics_source_ID'] = self.statistics_source_ID
                df['report_type'] = report
                df['report_type'] = df['report_type'].astype(COUNTERData.state_data_types()['report_type'])
                log.debug(f"Dataframe for SUSHI call for {report} report from {self.statistics_source_name} for {month_to_harvest.strftime('%Y-%m')}:\n{df}")
                log.info(f"Dataframe info for SUSHI call for {report} report from {self.statistics_source_name} for {month_to_harvest.strftime('%Y-%m')}:\n{return_string_of_dataframe_info(df)}")
                individual_month_dfs.append(df)
                log.info(f"Combining {len(individual_month_dfs)} single-month dataframes to load into the database.")  ##about_to_statement()
                return (pd.concat(individual_month_dfs, ignore_index=True), complete_flash_message_list)  # Without `ignore_index=True`, the autonumbering from the creation of each individual dataframe is retained, causing a primary key error when attempting to load the dataframe into the database
        else:
            SUSHI_parameters['begin_date'] = start_date
            SUSHI_parameters['end_date'] = end_date
            SUSHI_data_response, flash_message_list = SUSHICallAndResponse(self.statistics_source_name, SUSHI_URL, f"reports/{report.lower()}", SUSHI_parameters).make_SUSHI_call()
            if isinstance(SUSHI_data_response, str):
                log.warning(SUSHI_data_response)
                return (SUSHI_data_response, flash_message_list)
            df = ConvertJSONDictToDataframe(SUSHI_data_response).create_dataframe()
            if isinstance(df, str):
                message = unable_to_convert_SUSHI_data_to_dataframe_statement(df, report, self.statistics_source_name)
                log.warning(message)
                temp_file_path = Path(__file__).parent / 'temp.json'
                with open(temp_file_path, 'xb') as JSON_file:  # The JSON-like dict is being saved to a file because `upload_file_to_S3_bucket()` takes file-like objects or path-like objects that lead to file-like objects
                    json.dump(SUSHI_data_response, JSON_file)
                file_name = f"{self.statistics_source_ID}_reports-{report.lower()}_{SUSHI_parameters['begin_date'].strftime('%Y-%m')}_{SUSHI_parameters['end_date'].strftime('%Y-%m')}_{datetime.now().isoformat()}.json"
                log.debug(file_IO_statement(file_name, f"temporary file location {temp_file_path.resolve()}", f"S3 bucket {BUCKET_NAME}"))
                logging_message = upload_file_to_S3_bucket(
                    temp_file_path,
                    file_name,
                )
                if isinstance(logging_message, str) and re.fullmatch(r'Running the function `.*\(\)` on .* \(type .*\) raised the error .*\.', logging_message):  ##CheckStatement
                    message = message + " " + failed_upload_to_S3_statement(file_name, logging_message)
                    log.critical(message)
                else:
                    message = message + " " + logging_message
                    log.debug(message)
                temp_file_path.unlink()
                flash_message_list.append(message)
                return (message, flash_message_list)
            df['statistics_source_ID'] = self.statistics_source_ID
            df['report_type'] = report
            df['report_type'] = df['report_type'].astype(COUNTERData.state_data_types()['report_type'])
            log.debug(f"Dataframe for SUSHI call for {report} report from {self.statistics_source_name}:\n{df}")
            log.info(f"Dataframe info for SUSHI call for {report} report from {self.statistics_source_name}:\n{return_string_of_dataframe_info(df)}")
            return (df, flash_message_list)


    @hybrid_method
    def _check_if_data_in_database(self, report, start_date, end_date):
        """Checks if any usage report for the given date and statistics source combination is already in the database.

        Args:
            report_code (str): the two-letter abbreviation for the report being called
            start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month
            end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month

        Returns:
            list: the dates that should be harvested; a null value means the full range should be harvested
            str: the error message from `query_database()` being passed through
        """
        log.info(f"Starting `StatisticsSources._check_if_data_in_database()` for {report} from {self.statistics_source_name} for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
        months_in_date_range = [d.date() for d in list(rrule(MONTHLY, dtstart=start_date, until=end_date))]  # Creates a list of date objects representing the first day of the month of every month in the date range (rrule alone creates datetime objects)
        log.debug(f"The months in the date range are {months_in_date_range}.")
        months_to_harvest = []
        
        for month_being_checked in months_in_date_range:
            number_of_records = query_database(
                query=f"SELECT COUNT(*) FROM COUNTERData WHERE statistics_source_ID={self.statistics_source_ID} AND report_type='{report}' AND usage_date='{month_being_checked.strftime('%Y-%m-%d')}';",
                engine=db.engine,
            )
            if isinstance(number_of_records, str):
                return number_of_records  ##database_query_fail_statement()
            number_of_records = number_of_records.iloc[0][0]
            log.debug(return_value_from_query_statement(number_of_records, f"records for {self.statistics_source_name} in {month_being_checked.strftime('%Y-%m')}"))
            if number_of_records == 0:
                months_to_harvest.append(month_being_checked)
            else:
                log.warning(f"There were records for {self.statistics_source_name} in {month_being_checked.strftime('%Y-%m')} already loaded in the database; {month_being_checked.strftime('%Y-%m')} won't be included in the harvested date range.")
        
        log.debug(f"The months to harvest are {months_to_harvest}.")
        if months_in_date_range == months_to_harvest:
            return None  # Indicating the complete date range should be harvested
        else:
            return months_to_harvest
    
    
    @hybrid_method
    def collect_usage_statistics(self, usage_start_date, usage_end_date, report_to_harvest=None):
        """A method invoking the `_harvest_R5_SUSHI()` method for usage in the specified time range.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
            report_to_harvest (str, optional): the report ID for the customizable report to harvest; defaults to `None`, which harvests all available custom reports
        
        Returns:
            tuple: the logging statement to indicate if calling and loading the data succeeded or failed (str); a dictionary of harvested reports and the list of the statements that should be flashed returned by those reports (dict, key: str, value: list of str)
        """
        log.info(f"Starting `StatisticsSources.collect_usage_statistics()` for {self.statistics_source_name} for {usage_start_date.strftime('%Y-%m-%d')} to {usage_end_date.strftime('%Y-%m-%d')}.")
        df, flash_statements = self._harvest_R5_SUSHI(usage_start_date, usage_end_date, report_to_harvest)
        if isinstance(df, str):
            log.warning(df)
            return (df, flash_statements)
        else:
            log.debug(f"The SUSHI harvest for statistics source {self.statistics_source_name} successfully found {df.shape[1]} records.")  ##_harvest_R5_SUSHI_success_statement()
        try:
            df.index += first_new_PK_value('COUNTERData')
        except Exception as error:
            message = unable_to_get_updated_primary_key_values_statement("COUNTERData", error)
            log.warning(message)
            flash_statements.append(message)
            return (message, flash_statements)
        log.debug(f"The dataframe after adjusting the index:\n{df}")
        load_result = load_data_into_database(
            df=df,
            relation='COUNTERData',
            engine=db.engine,
            index_field_name='COUNTER_data_ID',
        )
        return (load_result, flash_statements)


    @hybrid_method
    def add_note(self):
        log.info(f"Starting `StatisticsSources.add_note()` for {self.statistics_source_name}.")
        #ToDo: Create a method for adding notes
        pass


class StatisticsSourceNotes(db.Model):
    """The class representation of the `statisticsSourceNotes` relation, which contains notes about the statistics sources in `statisticsSources`.
    
    Attributes:
        self.statistics_source_notes_ID (int): the primary key
        self.note (text): the content of the note
        self.written_by (string): the note author
        self.date_written (datetime64[ns]): the day the note was last edited
        self.statistics_source_ID (int): the foreign key for `statisticsSources`

    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
    """
    __tablename__ = 'statisticsSourceNotes'

    statistics_source_notes_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    note = db.Column(db.Text)
    written_by = db.Column(db.String(100))
    date_written = db.Column(db.Date)
    statistics_source_ID = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), nullable=False)
    

    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "note": 'string',
            "written_by": 'string',
            "date_written": 'datetime64[ns]',
            "statistics_source_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        }


class ResourceSources(db.Model):
    """The class representation of the `resourceSources` relation, which contains a list of the places where e-resources are available.

    Resource sources are often called platforms; Alma calls them interfaces. Resource sources are often declared distinct by virtue of having different HTTP domains.
    
    Attributes:
        self.resource_source_ID (int): the primary key
        self.resource_source_name (string): the resource source name
        self.source_in_use (bool): indicates if we currently have access to resources at the resource source
        self.access_stop_date (datetime64[ns]): if we don't have access to resources at this source, the last date we had access
        self.vendor_ID (int): the foreign key for `vendors`
    
    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
        add_access_stop_date: Indicate that a resource is no longer in use by adding a date to `access_stop_date` and changing the `source_in_use` value to `False`.
        remove_access_stop_date:  Indicate that a resource is in use again by removing the date from `access_stop_date` and changing the `source_in_use` value to `True`.
        change_StatisticsSource: Change the current statistics source for the resource source.
        add_note:  #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'resourceSources'

    resource_source_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    resource_source_name = db.Column(db.String(100), nullable=False)
    source_in_use = db.Column(db.Boolean, nullable=False)
    access_stop_date = db.Column(db.Date)
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'), nullable=False)

    FK_in_ResourceSourceNotes = db.relationship('ResourceSourceNotes', backref='resourceSources')
    FK_in_StatisticsResourceSources = db.relationship('StatisticsResourceSources', backref='resourceSources')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "resource_source_name": 'string',
            "source_in_use": 'bool',  # Python's `bool` is used to reinforce that this is a non-null field
            "access_stop_date": 'datetime64[ns]',
            "vendor_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        }


    @hybrid_method
    def add_access_stop_date(self, access_stop_date=date.today()):
        """Indicate that a resource is no longer in use by adding a date to `access_stop_date` and changing the `source_in_use` value to `False`.

        Args:
            access_stop_date (datetime.date, optional): the date when the access to the content on the platform ended; defaults to `date.today()`
        
        Returns:
            _type_: _description_  #ToDo: Update on completion of method
        """
        log.info(f"Starting `ResourceSources.add_access_stop_date()` for {self.resource_source_name}.")
        update_result = update_database(
            update_statement=f"""
                UPDATE resourceSources
                SET access_stop_date='{access_stop_date}' AND source_in_use=false
                WHERE resource_source_ID={self.resource_source_ID};
            """,
            engine=db.engine,
        )
        if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
            #ToDo: log.warning()
            pass  ##database_update_fail_statement()
        return update_result


    @hybrid_method
    def remove_access_stop_date(self):
        """Indicate that a resource is in use again by removing the date from `access_stop_date` and changing the `source_in_use` value to `True`.

        Returns:
            _type_: _description_  #ToDo: Update on completion of method
        """
        log.info(f"Starting `ResourceSources.remove_access_stop_date()` for {self.resource_source_name}.")
        update_result = update_database(
            update_statement=f"""
                UPDATE resourceSources
                SET access_stop_date IS NONE AND source_in_use=true
                WHERE resource_source_ID={self.resource_source_ID};
            """,
            engine=db.engine,
        )
        if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
            #ToDo: log.warning()
            pass  ##database_update_fail_statement()
        return update_result


    @hybrid_method
    def change_StatisticsSource(self, statistics_source_PK):
        """Change the current statistics source for the resource source.

        This method changes the `True` value in the `StatisticsResourceSources` record for the given resource source to `False`, then adds a new record creating a connection between the given statistics source and resource source.

        Args:
            statistics_source_PK (int): the primary key from the `statisticsSources` record for the statistics source now used by the given resource source
        
        Returns:
            str: a message indicating success or including the error raised by the attempt to update the data
        """
        log.info(f"Starting `ResourceSources.change_StatisticsSource()` for {self.resource_source_name}.")
        update_result = update_database(
            update_statement=f"""
                UPDATE statisticsResourceSources
                SET current_statistics_source=false
                WHERE SRS_resource_source={self.resource_source_ID};
            """,
            engine=db.engine,
        )
        if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
            #ToDo: log.warning()
            pass  ##database_update_fail_statement()
        
        check_for_existing_record = query_database(
            query=f"SELECT * FROM statisticsResourceSources WHERE SRS_statistics_source={statistics_source_PK} AND SRS_resource_source={self.resource_source_ID};",
            engine=db.engine,
        )
        if isinstance(check_for_existing_record, str):
            pass  ##database_query_fail_statement()
        
        if check_for_existing_record.empty:
            log.debug("Adding a new record to the `statisticsResourceSources` relation.")
            multiindex = pd.DataFrame(
                [
                    [statistics_source_PK, self.resource_source_ID]
                ],
                columns=["SRS_statistics_source", "SRS_resource_source"],
            )
            multiindex = pd.MultiIndex.from_frame(multiindex)
            series = pd.Series(
                data=[
                    True
                ],
                index=multiindex,
                name="current_statistics_source",
            )
            series = series.astype(StatisticsResourceSources.state_data_types())

            load_result = load_data_into_database(
                df=series,
                relation='statisticsResourceSources',
                engine=db.engine,
            )
            return load_result

        else:
            log.debug("Updating an existing record in the `statisticsResourceSources` relation.")
            update_result = update_database(
                update_statement=f"""
                    UPDATE statisticsResourceSources
                    SET current_statistics_source=true
                    WHERE SRS_statistics_source={statistics_source_PK} AND SRS_resource_source={self.resource_source_ID};
                """,
                engine=db.engine,
            )
            if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
                #ToDo: log.warning()
                pass  ##database_update_fail_statement()
            return update_result


    @hybrid_method
    def add_note(self):
        log.info(f"Starting `ResourceSources.add_note()` for {self.resource_source_name}.")
        #ToDo: Create a method for adding notes
        pass


class ResourceSourceNotes(db.Model):
    """The class representation of the `resourceSourceNotes` relation, which contains notes about the resource sources in `resourceSources`.
    
    Attributes:
        self.resource_source_notes_ID (int): the primary key
        self.note (text): the content of the note
        self.written_by (string): the note author
        self.date_written (datetime64[ns]): the day the note was last edited
        self.resource_source_ID (int): the foreign key for `resourceSources`

    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
    """
    __tablename__ = 'resourceSourceNotes'

    resource_source_notes_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    note = db.Column(db.Text)
    written_by = db.Column(db.String(100))
    date_written = db.Column(db.Date)
    resource_source_ID = db.Column(db.Integer, db.ForeignKey('resourceSources.resource_source_ID'), nullable=False)
    

    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "note": 'string',
            "written_by": 'string',
            "date_written": 'datetime64[ns]',
            "resource_source_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        }


class StatisticsResourceSources(db.Model):
    """The class representation of the `statisticsResourceSources` relation, which functions as the junction table between `statisticsSources` and `resourceSources`.

    The relationship between resource sources and statistics sources can be complex. A single vendor can have multiple platforms, each with their own statistics source (e.g. Taylor & Francis); a single statistics source can provide usage for multiple separate platforms/domains from a single vendor (e.g. historical Oxford) or from different vendors (e.g. HighWire); statistics sources can be combined (e.g. Peterson's Prep) or split apart (e.g. UN/OECD iLibrary); changes in publisher (e.g. Nature) or platform hosting service (e.g. Company of Biologists) can change where to get the usage for a given resource. This complexity creates a many-to-many relationship between resource sources and statistics sources, which relational databases implement through a junction table such as this one. The third field in this relation, `current_statistics_source`, indicates if the given statistics source is the current source of usage for the resource source.
    
    Attributes:
        self.SRS_statistics_source (int): part of the composite primary key; the foreign key for `statisticsSources`
        self.SRS_resource_source (int): part of the composite primary key; the foreign key for `resourceSources`
        self.current_statistics_source (bool): indicates if the statistics source currently provides the usage for the resource source

    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
    """
    __tablename__ = 'statisticsResourceSources'

    SRS_statistics_source = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), primary_key=True, autoincrement=False)
    SRS_resource_source = db.Column(db.Integer, db.ForeignKey('resourceSources.resource_source_ID'), primary_key=True, autoincrement=False)
    current_statistics_source = db.Column(db.Boolean, nullable=False)


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "current_statistics_source": 'bool',  # Python's `bool` is used to reinforce that this is a non-null field
        }


class AnnualUsageCollectionTracking(db.Model):
    """The class representation of the `annualUsageCollectionTracking` relation, which tracks the collecting of usage statistics by containing a record for each fiscal year and statistics source.
    
    Attributes:
        self.AUCT_statistics_source (int): part of the composite primary key; the foreign key for `statisticsSources`
        self.AUCT_fiscal_year (int): part of the composite primary key; the foreign key for `fiscalYears`
        self.usage_is_being_collected (boolean): indicates if usage needs to be collected
        self.manual_collection_required (boolean): indicates if usage needs to be collected manually
        self.collection_via_email (boolean): indicates if usage needs to be requested by sending an email
        self.is_COUNTER_compliant (boolean): indicates if usage is COUNTER R4 or R5 compliant
        self.collection_status (enum): the status of the usage statistics collection
        self.usage_file_path (string): the name of the file containing the non-COUNTER usage statistics, not including the `PATH_WITHIN_BUCKET` section (see note)
        self.notes (text): notes about collecting usage statistics for the particular statistics source and fiscal year
    
    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
        collect_annual_usage_statistics: A method invoking the `_harvest_R5_SUSHI()` method for the given resource's fiscal year usage.
        upload_nonstandard_usage_file: A method uploading a file with usage statistics for a statistics source for a given fiscal year to S3 and updating the `annualUsageCollectionTracking.usage_file_path` field so the file can be downloaded in the future.
        download_nonstandard_usage_file: A method for downloading a file with usage statistics for a statistics source for a given fiscal year from S3.
    
    Note:
        Strictly speaking, S3 doesn't use folders, just file names with segments that can be separated by slashes, but the segmentation of the file names allows a file-like structure to be created and used for the S3 GUI. The `PATH_WITHIN_BUCKET` constant is a shared beginning to all usage statistics files loaded into S3 by NoLCAT.
    """
    __tablename__ = 'annualUsageCollectionTracking'

    AUCT_statistics_source = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), primary_key=True, autoincrement=False)
    AUCT_fiscal_year = db.Column(db.Integer, db.ForeignKey('fiscalYears.fiscal_year_ID'), primary_key=True, autoincrement=False)
    usage_is_being_collected = db.Column(db.Boolean)
    manual_collection_required = db.Column(db.Boolean)
    collection_via_email = db.Column(db.Boolean)
    is_COUNTER_compliant = db.Column(db.Boolean)
    collection_status = db.Column(db.Enum(
        'N/A: Paid by Law',
        'N/A: Paid by Med',
        'N/A: Paid by Music',
        'N/A: Open access',
        'N/A: Other (see notes)',
        'Collection not started',
        'Collection in process (see notes)',
        'Collection issues requiring resolution',
        'Collection complete',
        'Usage not provided',
        'No usage to report'
    ))
    usage_file_path = db.Column(db.String(150))
    notes = db.Column(db.Text)


    def __repr__(self):
        """The printable representation of the record."""
        return f"<'AUCT_statistics_source': '{self.AUCT_statistics_source}', 'AUCT_fiscal_year': '{self.AUCT_fiscal_year}', 'usage_is_being_collected': '{self.usage_is_being_collected}', 'manual_collection_required': '{self.manual_collection_required}', 'collection_via_email': '{self.collection_via_email}', 'is_COUNTER_compliant': '{self.is_COUNTER_compliant}', 'collection_status': '{self.collection_status}', 'usage_file_path': '{self.usage_file_path}', 'notes': '{self.notes}'>"


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "usage_is_being_collected": 'boolean',
            "manual_collection_required": 'boolean',
            "collection_via_email": 'boolean',
            "is_COUNTER_compliant": 'boolean',
            "collection_status": 'string',  # Using Python's `enum` standard library would add complexity
            "usage_file_path": 'string',
            "notes": 'string',
        }


    @hybrid_method
    def collect_annual_usage_statistics(self):
        """A method invoking the `_harvest_R5_SUSHI()` method for the given resource's fiscal year usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Returns:
            tuple: the logging statement to indicate if calling and loading the data succeeded or failed (str); a dictionary of harvested reports and the list of the statements that should be flashed returned by those reports (dict, key: str, value: list of str)
        """
        log.info(f"Starting `AnnualUsageCollectionTracking.collect_annual_usage_statistics()`.")
        #Section: Get Data from Relations Corresponding to Composite Key
        #Subsection: Get Data from `fiscalYears`
        fiscal_year_data = query_database(
            query=f"SELECT fiscal_year, start_date, end_date FROM fiscalYears WHERE fiscal_year_ID={self.AUCT_fiscal_year};",
            engine=db.engine,
        )
        if isinstance(fiscal_year_data, str):
            return (fiscal_year_data, [fiscal_year_data])  ##database_query_fail_statement()
        start_date = fiscal_year_data['start_date'][0]
        end_date = fiscal_year_data['end_date'][0]
        fiscal_year = fiscal_year_data['fiscal_year'][0]
        log.debug(return_value_from_query_statement((start_date, end_date, fiscal_year), f"start date, end date, and fiscal year"))  #ToDo: Confirm that the variables are `datetime.date` objects, and if not, change them to that type
        
        #Subsection: Get Data from `statisticsSources`
        # Using SQLAlchemy to pull a record object doesn't work because the `StatisticsSources` class isn't recognized
        statistics_source_data = query_database(
            query=f"SELECT statistics_source_name, statistics_source_retrieval_code, vendor_ID FROM statisticsSources WHERE statistics_source_ID={self.AUCT_statistics_source};",
            engine=db.engine,
        )
        if isinstance(statistics_source_data, str):
            return (statistics_source_data, [statistics_source_data])  ##database_query_fail_statement()
        statistics_source = StatisticsSources(
            statistics_source_ID = self.AUCT_statistics_source,
            statistics_source_name = str(statistics_source_data['statistics_source_name'][0]),
            statistics_source_retrieval_code = str(statistics_source_data['statistics_source_retrieval_code'][0]).split(".")[0],  # String created is of a float (aka `n.0`), so the decimal and everything after it need to be removed
            vendor_ID = int(statistics_source_data['vendor_ID'][0]),
        )
        log.debug(initialize_relation_class_object_statement("StatisticsSources", statistics_source))

        #Section: Collect and Load SUSHI Data
        df, flash_statements = statistics_source._harvest_R5_SUSHI(start_date, end_date)
        if isinstance(df, str):
            log.warning(df)
            return (df, flash_statements)
        log.debug(f"The SUSHI harvest for statistics source {statistics_source.statistics_source_name} for FY {fiscal_year} successfully found {df.shape[1]} records.")  ##_harvest_R5_SUSHI_success_statement()
        try:
            df.index += first_new_PK_value('COUNTERData')
        except Exception as error:
            message = unable_to_get_updated_primary_key_values_statement("COUNTERData", error)
            log.warning(message)
            flash_statements.append(message)
            return (message, flash_statements)
        load_result = load_data_into_database(
            df=df,
            relation='COUNTERData',
            engine=db.engine,
            index_field_name='COUNTER_data_ID',
        )
        if load_result.startswith("Loading data into the COUNTERData relation raised the error"):  ##CheckStatement
            return (load_result, flash_statements)
        update_statement = update_statement=f"""
            UPDATE annualUsageCollectionTracking
            SET collection_status='Collection complete'
            WHERE AUCT_statistics_source={self.AUCT_statistics_source} AND AUCT_fiscal_year={self.AUCT_fiscal_year};
        """
        update_result = update_database(  # This updates the field in the relation to confirm that the data has been collected and is in NoLCAT
            update_statement=update_statement,
            engine=db.engine,
        )
        if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
            message = f"Updating the `annualUsageCollectionTracking` relation automatically failed, so the SQL update statement needs to be submitted via the SQL command line:\n{update_statement}"  ##add_data_success_and_update_database_fail_statement()
            log.warning(message)
            flash_statements.append(message)
            return (f"{load_result[:-1]}, but {message[0].lower()}{message[1:]}", flash_statements)
        return (f"{load_result[:-1]} and {update_result[13:]}", flash_statements)  ##add_data_and_update_database_success_statement()


    @hybrid_method
    def upload_nonstandard_usage_file(self, file, bucket=BUCKET_NAME, bucket_path=PATH_WITHIN_BUCKET):
        """A method uploading a file with usage statistics for a statistics source for a given fiscal year to S3 and updating the `annualUsageCollectionTracking.usage_file_path` field so the file can be downloaded in the future.

        Args:
            file (werkzeug.datastructures.FileStorage): a file loaded through a WTForms FileField field
            bucket (str, optional): the name of the S3 bucket; default is constant derived from `nolcat_secrets.py`
            bucket_path (str, optional): the path within the bucket where the files will be saved; default is constant initialized at the beginning of this module

        Returns:
            str: the logging statement to indicate if uploading the data and updating the database succeeded or failed
        """
        log.info(f"Starting `AnnualUsageCollectionTracking.upload_nonstandard_usage_file()`.")
        file_path = Path(file)
        file_extension = file_path.suffix
        if file_extension not in file_extensions_and_mimetypes().keys():
            message = f"The file extension of {file_path} is invalid. Please convert the file to use one of the following extensions and try again:\n{list(file_extensions_and_mimetypes().keys())}"
            log.error(message)
            return message
        
        file_name = f"{self.AUCT_statistics_source}_{self.AUCT_fiscal_year}{file_extension}"  # `file_extension` is a `Path.suffix` attribute, which means it begins with a period
        log.debug(file_IO_statement(file_name, f"WTForms FileField field {file_path.resolve()}", f"S3 bucket {BUCKET_NAME}"))
        logging_message = upload_file_to_S3_bucket(
            file,
            file_name,
        )
        if isinstance(logging_message, str) and re.fullmatch(r'Running the function `.*\(\)` on .* \(type .*\) raised the error .*\.', logging_message):  ##CheckStatement
            message = failed_upload_to_S3_statement(file_name, logging_message)
            log.critical(message)
            return message
        log.debug(logging_message)
        
        update_statement = f"""
            UPDATE annualUsageCollectionTracking
            SET usage_file_path='{file_name}'
            AND collection_status='Collection complete'
            WHERE AUCT_statistics_source={self.AUCT_statistics_source} AND AUCT_fiscal_year={self.AUCT_fiscal_year};
        """
        update_result = update_database(  # This updates the fields in the relation so the uploaded file can be downloaded later
            update_statement=update_statement,
            engine=db.engine,
        )
        if isinstance(update_result, str) and re.fullmatch(r'Running the update statement `.*` raised the error .*\.', update_result, flags=re.DOTALL):  ##CheckStatement
            message = f"Updating the `annualUsageCollectionTracking` relation failed, so the SQL update statement needs to be submitted via the SQL command line:\n{update_statement}"  ##add_data_success_and_update_database_fail_statement()
            log.warning(message)
            return f"{logging_message[:-1]}, but {message[0].lower()}{message[1:]}"
        message = f"{logging_message[:-1]} and {update_result[0].lower()}{update_result[1:]}"  ##add_data_and_update_database_success_statement()
        log.debug(message)
        return message
    

    @hybrid_method
    def download_nonstandard_usage_file(self, web_app_download_folder, client=s3_client, bucket=BUCKET_NAME, bucket_path=PATH_WITHIN_BUCKET):
        """A method for downloading a file with usage statistics for a statistics source for a given fiscal year from S3.

        Args:
            web_app_download_folder (pathlib.Path): the absolute path for the folder to which the web app will download the file
            client (S3.Client, optional): the client for connecting to an S3 bucket; default is `S3_client` initialized in `nolcat.app` module
            bucket (str, optional): the name of the S3 bucket; default is constant derived from `nolcat_secrets.py`
            bucket_path (str, optional): the path within the bucket where the files will be saved; default is constant initialized at the beginning of this module
        
        Returns:
            pathlib.Path: the absolute file path to the downloaded file
        """
        log.info(f"Starting `AnnualUsageCollectionTracking.download_nonstandard_usage_file()`.")
        file_download_path = web_app_download_folder / self.usage_file_path
        log.debug(file_IO_statement(self.usage_file_path, f"S3 bucket {BUCKET_NAME}", f"top repo folder {TOP_NOLCAT_DIRECTORY.resolve()}", False))
        client.download_file(
            Bucket=bucket,
            Key=bucket_path + self.usage_file_path,
            Filename=self.usage_file_path,
        )
        if self.usage_file_path in [str(p.name) for p in TOP_NOLCAT_DIRECTORY.iterdir()]:
            temp_usage_file_path = TOP_NOLCAT_DIRECTORY / self.usage_file_path  # Temp variable used because the `rename()` method used below just executes on the string that should be the final component of the path
            temp_usage_file_path.rename(file_download_path)
            log.info(f"Successfully downloaded {self.usage_file_path} to the top-level repo folder {TOP_NOLCAT_DIRECTORY}.")
            return file_download_path
        else:
            log.error(f"The file {self.usage_file_path} wasn't downloaded because it couldn't be found in {TOP_NOLCAT_DIRECTORY}.")
            return False


class COUNTERData(db.Model):
    """The class representation of the `COUNTERData` relation, which contains all the data from the ingested COUNTER reports.

    The attributes of this class represent the general and parent data fields found in R4 and R5 COUNTER reports, which are loaded into this relation with no processing beyond those necessary for aligning data types. Some of the variable string lengths are set with constants, which allow both the string length in the created database and the confirmations that the strings will fit in the database in `ConvertJSONDictToDataframe` to be updated at the same time.

    Attributes:
        self.COUNTER_data_ID (int): the primary key
        self.statistics_source_ID (int): the foreign key for `statisticsSources`
        self.report_type (string): the type of COUNTER report, represented by the official report abbreviation
        self.resource_name (string): the name of the resource
        self.publisher (string): the name of the publisher
        self.publisher_ID (string): the statistics source's ID for the publisher
        self.platform (string): the name of the resource's platform in the COUNTER report
        self.authors (string): the authors of the resource
        self.publication_date (datetime64[ns]): the resource publication date in the COUNTER IR
        self.article_version (string): version of article within the publication life cycle from the COUNTER IR
        self.DOI (string): the DOI for the resource
        self.proprietary_ID (string): the statistics source's ID for the resource
        self.ISBN (string): the ISBN for the resource
        self.print_ISSN (string): the print ISSN for the resource
        self.online_ISSN (string): the online ISSN for the resource
        self.URI (string): the statistics source's permalink to the resource
        self.data_type (string): the COUNTER data type
        self.section_type (string): the COUNTER section type
        self.YOP (Int16): the year the resource used was published, where an unknown year is represented with `0001` and articles in press are assigned `9999`
        self.access_type (string): the COUNTER access type
        self.access_method (string): the COUNTER access method
        self.parent_title (string): the name of the resource's host
        self.parent_authors (string): the authors of the resource's host
        self.parent_publication_date (datetime64[ns]): the resource's host's publication date in the COUNTER IR
        self.parent_article_version (string): version of article's host within the publication life cycle from the COUNTER IR
        self.parent_data_type (string): the COUNTER data type for the resource's host
        self.parent_DOI (string): the DOI for the resource's host
        self.parent_proprietary_ID (string): the statistics source's ID for the resource's host
        self.parent_ISBN (string): the ISBN for the resource's host
        self.parent_print_ISSN (string): the print ISSN for the resource's host
        self.parent_online_ISSN (string): the online ISSN for the resource's host
        self.parent_URI (string): the statistics source's permalink to the resource's host
        self.metric_type (string): the COUNTER metric type
        self.usage_date (datetime64[ns]): the month when the use occurred, represented by the first day of that month
        self.usage_count (int): the number of uses
        self.report_creation_date (datetime64[ns]): the date and time when the SUSHI call for the COUNTER report which provided the data was downloaded

    Methods:
        state_data_types: This method provides a dictionary of the attributes and their data types.
    """
    __tablename__ = 'COUNTERData'

    COUNTER_data_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    statistics_source_ID = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), nullable=False)
    report_type = db.Column(db.String(5))
    resource_name = db.Column(db.String(RESOURCE_NAME_LENGTH))
    publisher = db.Column(db.String(PUBLISHER_LENGTH))
    publisher_ID = db.Column(db.String(PUBLISHER_ID_LENGTH))
    platform = db.Column(db.String(PLATFORM_LENGTH))
    authors = db.Column(db.String(AUTHORS_LENGTH))
    publication_date = db.Column(db.DateTime)
    article_version = db.Column(db.String(50))
    DOI = db.Column(db.String(DOI_LENGTH))
    proprietary_ID = db.Column(db.String(PROPRIETARY_ID_LENGTH))
    ISBN = db.Column(db.String(20))
    print_ISSN = db.Column(db.String(10))
    online_ISSN = db.Column(db.String(20))  # Some R4 book reports put another ISBN in the report's ISSN field, the contents of which go into this field, so the field must be large enough to store ISBNs
    URI = db.Column(db.String(URI_LENGTH))
    data_type = db.Column(db.String(25))
    section_type = db.Column(db.String(25))
    YOP = db.Column(db.SmallInteger)
    access_type = db.Column(db.String(20))
    access_method = db.Column(db.String(10))
    parent_title = db.Column(db.String(RESOURCE_NAME_LENGTH))
    parent_authors = db.Column(db.String(AUTHORS_LENGTH))
    parent_publication_date = db.Column(db.DateTime)
    parent_article_version = db.Column(db.String(50))
    parent_data_type = db.Column(db.String(25))
    parent_DOI = db.Column(db.String(DOI_LENGTH))
    parent_proprietary_ID = db.Column(db.String(PROPRIETARY_ID_LENGTH))
    parent_ISBN = db.Column(db.String(20))
    parent_print_ISSN = db.Column(db.String(10))
    parent_online_ISSN = db.Column(db.String(10))
    parent_URI = db.Column(db.String(URI_LENGTH))
    metric_type = db.Column(db.String(75), nullable=False)
    usage_date = db.Column(db.Date, nullable=False)
    usage_count = db.Column(db.Integer, nullable=False)
    report_creation_date = db.Column(db.DateTime)


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    @classmethod
    def state_data_types(self):
        """This method provides a dictionary of the attributes and their data types."""
        return {
            "statistics_source_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
            "report_type": 'string',
            "resource_name": 'string',
            "publisher": 'string',
            "publisher_ID": 'string',
            "platform": 'string',
            "authors": 'string',
            "publication_date": 'datetime64[ns]',
            "article_version": 'string',
            "DOI": 'string',
            "proprietary_ID": 'string',
            "ISBN": 'string',
            "print_ISSN": 'string',
            "online_ISSN": 'string',
            "URI": 'string',
            "data_type": 'string',
            "section_type": 'string',
            "YOP": 'Int16',  # Relation uses two-byte integer type, so code uses two-byte integer data type from pandas, which allows nulls
            "access_type": 'string',
            "access_method": 'string',
            "parent_title": 'string',
            "parent_authors": 'string',
            "parent_publication_date": 'datetime64[ns]',
            "parent_article_version": 'string',
            "parent_data_type": 'string',
            "parent_DOI": 'string',
            "parent_proprietary_ID": 'string',
            "parent_ISBN": 'string',
            "parent_print_ISSN": 'string',
            "parent_online_ISSN": 'string',
            "parent_URI": 'string',
            "metric_type": 'string',
            "usage_date": 'datetime64[ns]',
            "usage_count": 'int',  # Python's `int` is used to reinforce that this is a non-null field
            "report_creation_date": 'datetime64[ns]',
        }
