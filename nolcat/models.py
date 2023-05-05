"""These classes represent the relations in the database."""

import logging
from pathlib import Path
import sys
import json
import re
import datetime
from sqlalchemy.ext.hybrid import hybrid_method  # Initial example at https://pynash.org/2013/03/01/Hybrid-Properties-in-SQLAlchemy/
import pandas as pd
from numpy import ndarray
from dateutil.rrule import rrule, MONTHLY

from .app import db
from .app import return_string_of_dataframe_info, first_new_PK_value
from .SUSHI_call_and_response import SUSHICallAndResponse
from .convert_JSON_dict_to_dataframe import ConvertJSONDictToDataframe


logging.basicConfig(level=logging.DEBUG, format="DB models - - [%(asctime)s] %(message)s")  # This formats logging messages like Flask's logging messages, but with the class name where Flask put the server info


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
        logging.debug(f"The R5 SUSHI credentials file was found at at `{file_path}`.")
        return str(file_path)
    logging.critical("The R5 SUSHI credentials file could not be located. The program is ending.")
    sys.exit()


class FiscalYears(db.Model):
    """The class representation of the `fiscalYears` relation, which contains a list of the fiscal years with data in the database as well as information about the national reporting aggregate statistics for the given fiscal year.
    
    Attributes:
        self.fiscal_year_ID (int): the primary key
        self.fiscal_year (str): the fiscal year in "yyyy" format; the ending year of the range is used
        self.start_date (date): the first day of the fiscal year
        self.end_date (date) the last day of the fiscal year
        self.ACRL_60b (smallInt): the reported value for ACRL 60b
        self.ACRL_63 (smallInt): the reported value for ACRL 63
        self.ARL_18 (smallInt): the reported value for ARL 18
        self.ARL_19 (smallInt): the reported value for ARL 19
        self.ARL_20 (smallInt): the reported value for ARL 20
        self.notes_on_statisticsSources_used (text): notes on data sources used to collect ARL and ACRL/IPEDS numbers
        self.notes_on_corrections_after_submission (text): information on any corrections to usage data done by vendors after initial harvest, especially if later corrected numbers were used in national reporting statistics

    Methods:
        calculate_ACRL_60b: This method calculates the value of ACRL question 60b for the given fiscal year.
        calculate_ACRL_63: This method calculates the value of ACRL question 63 for the given fiscal year.
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
    ACRL_60b = db.Column(db.SmallInteger)
    ACRL_63 = db.Column(db.SmallInteger)
    ARL_18 = db.Column(db.SmallInteger)
    ARL_19 = db.Column(db.SmallInteger)
    ARL_20 = db.Column(db.SmallInteger)
    notes_on_statisticsSources_used = db.Column(db.Text)
    notes_on_corrections_after_submission = db.Column(db.Text)

    FK_in_AUCT = db.relationship('AnnualUsageCollectionTracking', backref='fiscalYears')


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def calculate_ACRL_60b(self):
        """This method calculates the value of ACRL question 60b for the given fiscal year.

        ACRL 60b is the sum of "usage of digital/electronic titles whether viewed, downloaded, or streamed. Include usage for e-books, e-serials, and e-media titles even if they were purchased as part of a collection or database."

        Returns:
            int: the answer to ACRL 60b
        """
        TR_B1_df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Title_Requests' AND data_type='Book' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            ''',
            con=db.engine,
        )
        TR_B1_sum = TR_B1_df.iloc[0][0]
        logging.debug(f"The e-book sum query returned\n{TR_B1_df}\nfrom which {TR_B1_sum} ({type(TR_B1_sum)}) was extracted.")

        IR_M1_df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Total_Item_Requests' AND data_type='Multimedia' AND access_method='Regular' AND report_type='IR';
            ''',
            con=db.engine,
        )
        IR_M1_sum = IR_M1_df.iloc[0][0]
        logging.debug(f"The e-media sum query returned\n{IR_M1_df}\nfrom which {IR_M1_sum} ({type(IR_M1_sum)}) was extracted.")

        TR_J1_df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            ''',
            con=db.engine,
        )
        TR_J1_sum = TR_J1_df.iloc[0][0]
        logging.debug(f"The e-serials sum query returned\n{TR_J1_df}\nfrom which {TR_J1_sum} ({type(TR_J1_sum)}) was extracted.")
        
        return TR_B1_sum + IR_M1_sum + TR_J1_sum


    @hybrid_method
    def calculate_ACRL_63(self):
        """This method calculates the value of ACRL question 63 for the given fiscal year.

        ACRL 60b is the sum of "usage of e-serial titles whether viewed, downloaded, or streamed. Include usage for e-serial titles only, even if the title was purchased as part of a database."

        Returns:
            int: the answer to ACRL 63
        """
        df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_type='Controlled' AND access_method='Regular' AND report_type='TR';
            ''',
            con=db.engine,
        )
        logging.debug(f"The sum query returned (type {type(df)}):\n{df}")
        return df.iloc[0][0]


    @hybrid_method
    def calculate_ARL_18(self):
        """This method calculates the value of ARL question 18 for the given fiscal year.

        ARL 18 is the "Number of successful full-text article requests (journals)."

        Returns:
            int: the answer to ARL 18
        """
        df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Unique_Item_Requests' AND data_type='Journal' AND access_method='Regular' AND report_type='TR';
            ''',
            con=db.engine,
        )
        logging.debug(f"The sum query returned (type {type(df)}):\n{df}")
        return df.iloc[0][0]

    
    @hybrid_method
    def calculate_ARL_19(self):
        """This method calculates the value of ARL question 19 for the given fiscal year.

        ARL 19 is the "Number of regular searches (databases)."

        Returns:
            int: the answer to ARL 19
        """
        df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Searches_Regular' AND access_method='Regular' AND report_type='DR';
            ''',
            con=db.engine,
        )
        logging.debug(f"The sum query returned (type {type(df)}):\n{df}")
        return df.iloc[0][0]


    @hybrid_method
    def calculate_ARL_20(self):
        """This method calculates the value of ARL question 20 for the given fiscal year.

        ARL 20 is the "Number of federated searches (databases)."

        Returns:
            int: the answer to ARL 20
        """
        df = pd.read_sql(
            sql=f'''
                SELECT SUM(usage_count) FROM COUNTERData
                WHERE usage_date>='{self.start_date.strftime('%Y-%m-%d')}' AND usage_date<='{self.end_date.strftime('%Y-%m-%d')}'
                AND metric_type='Searches_Federated' AND access_method='Regular' AND report_type='DR';
            ''',
            con=db.engine,
        )
        logging.debug(f"The sum query returned (type {type(df)}):\n{df}")
        return df.iloc[0][0]


    @hybrid_method
    def create_usage_tracking_records_for_fiscal_year(self):
        """Create the records for the given fiscal year in the `annualUsageCollectionTracking` relation.

        Scheduling a function to run within Python requires a module that calls that function to be running, making programmatically adding new records at the start of each fiscal year an aspirational iteration. For the `fiscalYears` relation, only one record needs to be added each year, so manually adding the record isn't problematic. For `annualUsageCollectionTracking`, which requires hundreds of new records which are identified through a field in the `statisticsResourceSources` relation, a method to create the new records is necessary.

        Returns:
            str: the logging statement to indicate if calling and loading the data succeeded or failed
        """
        #Section: Get PKs of the Fiscal Year's Statistics Sources
        current_statistics_sources = pd.read_sql(
            sql=f"SELECT SRS_statistics_source FROM statisticsResourceSources WHERE current_statistics_source = true;",  # In MySQL, `field = true` is faster when the field is indexed and all values are either `1` or `0` (MySQL's Boolean field actually stores a one-bit integer) (see https://stackoverflow.com/q/24800881 and https://stackoverflow.com/a/34149077)
            con=db.engine,
        )
        logging.debug(f"Result of query for current statistics sources PKs:\n{current_statistics_sources}")
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
        df = df.astype({
            "usage_is_being_collected": 'boolean',
            "manual_collection_required": 'boolean',
            "collection_via_email": 'boolean',
            "is_COUNTER_compliant": 'boolean',
            "collection_status": 'string',  # For `enum` data type
            "usage_file_path": 'string',
            "notes": 'string',  # For `text` data type
        })
        logging.info(f"Records being loaded into `annualUsageCollectionTracking`:\n{df}\nAnd a summary of the dataframe:\n{return_string_of_dataframe_info(df)}")

        #Section: Load Data into `annualUsageCollectionTracking` Relation
        try:
            df.to_sql(
                'annualUsageCollectionTracking',
                con=db.engine,
                if_exists='append',
                index_label=["AUCT_statistics_source", "AUCT_fiscal_year"],
            )
            logging.info(f"The AUCT records load for FY {self.fiscal_year} was a success.")
            return f"The AUCT records load for FY {self.fiscal_year} was a success."
        except Exception as error:
            logging.warning(f"The AUCT records load for FY {self.fiscal_year} had an error: {format(error)}")
            return f"The AUCT records load for FY {self.fiscal_year} had an error: {format(error)}"


    @hybrid_method
    def collect_fiscal_year_usage_statistics(self):
        """A method invoking the `_harvest_R5_SUSHI()` method for all of a fiscal year's usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Returns:
            str: the logging statement to indicate if calling and loading the data succeeded or failed
        """
        #ToDo: dfs = []
        #ToDo: For every AnnualUsageCollectionTracking object with the given FY where usage_is_being_collected=True and manual_collection_required=False
            #ToDo: statistics_source = Get the matching StatisticsSources object
            #ToDo: df = statistics_source._harvest_R5_SUSHI(self.start_date, self.end_date)
            #ToDo: if repr(type(df)) == "<class 'str'>":
                #ToDo: return f"SUSHI harvesting returned the following error: {df}"
            #ToDo: else:
                #ToDo: logging.debug("The SUSHI harvest was a success")
            #ToDo: dfs.append(df)
            #ToDo: Update AUCT table; see https://www.geeksforgeeks.org/how-to-execute-raw-sql-in-flask-sqlalchemy-app/ for executing SQL update statements
        #ToDo: df = pd.concat(dfs)
        #ToDo: df.index += first_new_PK_value('COUNTERData')
        #ToDo: try:
            #ToDo: df.to_sql(
            #ToDo:     'COUNTERData',
            #ToDo:     con=db.engine,
            #ToDo:     if_exists='append',
            #ToDo: )
            #ToDo: logging.info(f"The load for FY {self.fiscal_year} was a success.")
            #ToDo: return f"The load for FY {self.fiscal_year} was a success."
        #ToDo: except Exception as e:
            #ToDo: logging.warning(f"The load for FY {self.fiscal_year} had an error: {format(error)}")
            #ToDo: return f"The load for FY {self.fiscal_year} had an error: {format(error)}"
        pass


class Vendors(db.Model):
    """The class representation of the `vendors` relation, which contains a list of entities that provide access to either electronic resources or usage statistics.
    
    Attributes:
        self. vendor_ID (int): the primary key
        self.vendor_name (str): the name of the vendor= db.Column(db.String(80))
        self.alma_vendor_code (str): the code used to identify vendors in the Alma API return value

    Methods:
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
    def get_statisticsSources_records(self):
        """Shows the records for all the statistics sources associated with the vendor.

        Returns:
            dataframe: a filtered copy of the `statisticsSources` relation
        """
        #ToDo: vendor_PK = the int value that serves as the primary key for the vendor
        #ToDo: df = pd.read_sql(
        #ToDo:     sql=f'''
        #ToDo:         SELECT
        #ToDo:             statistics_source_ID,
        #ToDo:             statistics_source_name,
        #ToDo:             statistics_source_retrieval_code
        #ToDo:         FROM statisticsSources
        #ToDo:         WHERE vendor_ID = {vendor_PK};
        #ToDo:     ''',
        #ToDo:     con=db.engine,
        #ToDo:     index_col='statistics_source_ID',
        #ToDo: )
        #ToDo: return df
        pass


    @hybrid_method
    def get_resourceSources_records(self):
        """Shows the records for all the resource sources associated with the vendor.

        Returns:
            dataframe: a filtered copy of the `resourceSources` relation
        """
        #ToDo: vendor_PK = the int value that serves as the primary key for the vendor
        #ToDo: df = pd.read_sql(
        #ToDo:     sql=f'''
        #ToDo:         SELECT
        #ToDo:             resource_source_ID,
        #ToDo:             resource_source_name,
        #ToDo:             source_in_use,
        #ToDo:             use_stop_date
        #ToDo:         FROM resourceSources
        #ToDo:         WHERE vendor_ID = {vendor_PK};
        #ToDo:     ''',
        #ToDo:     con=db.engine,
        #ToDo:     index_col='resource_source_ID',
        #ToDo: )
        #ToDo: return df
        pass


    @hybrid_method
    def add_note(self):
        #ToDo: Create a method for adding notes
        pass


class VendorNotes(db.Model):
    """The class representation of the `vendorNotes` relation, which contains notes about the vendors in `vendors`.
    
    Attributes:
        self.vendor_notes_ID (int): the primary key
        self.note (text): the content of the note
        self.written_by (str): the note author
        self.date_written (date): the day the note was last edited
        self.vendor_ID (int): the foreign key for `vendors`
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


class StatisticsSources(db.Model):
    """The class representation of the `statisticsSources` relation, which contains a list of all the possible sources of usage statistics.
    
    Attributes:
        self.statistics_source_ID (int): the primary key
        self.statistics_source_name (str): the name of the statistics source
        self.statistics_source_retrieval_code (str): the ID used to uniquely identify each set of SUSHI credentials in the SUSHI credentials JSON
        self.vendor_ID (int): the foreign key for `vendors`
    
    Methods:
        fetch_SUSHI_information: A method for fetching the information required to make a SUSHI API call for the statistics source.
        _harvest_R5_SUSHI: Collects the COUNTER R5 reports for the given statistics source and converts them into a single dataframe.
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
    def fetch_SUSHI_information(self, for_API_call=True):
        """A method for fetching the information required to make a SUSHI API call for the statistics source.

        This method fetches the information for making a SUSHI API call and, depending on the optional argument value, returns them for use in an API call or for display to the user.

        Args:
            for_API_call (bool, optional): a Boolean indicating if the return value should be formatted for use in an API call, which is the default; the other option is formatting the return value for display to the user
        
        Returns:
            dict: the SUSHI API parameters as a dictionary with the API call URL added as a value with the key `URL` 
            TBD: a data type that can be passed into Flask for display to the user
        """
        logging.debug("Starting the `StatisticsSources.fetch_SUSHI_information()` method.")
        #Section: Retrieve Data
        #Subsection: Retrieve Data from JSON
        with open(PATH_TO_CREDENTIALS_FILE()) as JSON_file:
            SUSHI_data_file = json.load(JSON_file)
            logging.debug("JSON with SUSHI credentials loaded.")
            for vendor in SUSHI_data_file:  # No index operator needed--outermost structure is a list
                for stats_source in vendor['interface']:  # `interface` is a key within the `vendor` dictionary, and its value, a list, is the only info needed, so the index operator is used to reference the specific key
                    if stats_source['interface_id'] == self.statistics_source_retrieval_code:
                        logging.info(f"Saving credentials for {self.statistics_source_name} ({self.statistics_source_retrieval_code}) to dictionary.")
                        credentials = dict(
                            URL = stats_source['statistics']['online_location'],
                            customer_id = stats_source['statistics']['user_id']
                        )

                        try:
                            credentials['requestor_id'] = stats_source['statistics']['user_password']
                        except:
                            pass

                        try:
                            credentials['api_key'] = stats_source['statistics']['user_pass_note']
                        except:
                            pass

                        try:
                            credentials['platform'] = stats_source['statistics']['delivery_address']
                        except:
                            pass

        #Subsection: Retrieve Data from Alma
        #ToDo: When credentials are in Alma, create this functionality


        #Section: Return Data in Requested Format
        if for_API_call:
            logging.debug(f"Returning the credentials {credentials} for a SUSHI API call.")
            return credentials
        else:
            return f"ToDo: Display {credentials} in Flask"  #ToDo: Change to a way to display the `credentials` values to the user via Flask


    @hybrid_method
    def _harvest_R5_SUSHI(self, usage_start_date, usage_end_date):
        """Collects the COUNTER R5 reports for the given statistics source and converts them into a single dataframe.

        For a given statistics source and date range, this method uses SUSHI to harvest all available COUNTER R5 reports at their most granular level, then combines them in a single dataframe. This is a private method where the calling method provides the parameters and loads the results into the `COUNTERData` relation.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month 
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
        
        Returns:
            dataframe: a dataframe containing all of the R5 COUNTER data
        """
        #Section: Get API Call URL and Parameters
        logging.debug("Starting the `StatisticsSources._harvest_R5_SUSHI()` method.")
        SUSHI_info = self.fetch_SUSHI_information()
        logging.debug(f"`StatisticsSources.fetch_SUSHI_information()` method returned the credentials {SUSHI_info} for a SUSHI API call.")  # This is nearly identical to the logging statement just before the method return statement and is for checking that the program does return to this method
        SUSHI_parameters = {key: value for key, value in SUSHI_info.items() if key != "URL"}
        logging.info(f"Making SUSHI calls for {self.statistics_source_name}.")


        #Section: Confirm SUSHI API Functionality
        SUSHI_status_response = SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "status", SUSHI_parameters).make_SUSHI_call()
        if re.match(r'^https?://.*mathscinet.*\.\w{3}/', SUSHI_info['URL']):  # MathSciNet `status` endpoint returns HTTP status code 400, which will cause an error here, but all the other reports are viable; this specifically bypasses the error checking for the SUSHI call to the `status` endpoint to the domain containing `mathscinet`
            logging.info(f"Call to `status` endpoint for {self.statistics_source_name} successful.")
            pass
        #ToDo: Allen Press raises error `HTTPSConnectionPool(host='pinnacle-secure.allenpress.com', port=443): Max retries exceeded with url: /status?customer_id=786-26-602&requestor_id=lib-eresources%40fsu.edu&begin_date=2023-01&end_date=2023-01 (Caused by SSLError(CertificateError("hostname 'pinnacle-secure.allenpress.com' doesn't match either of '*.literatumonline.com', 'literatumonline.com'")))`; can requests ignore the specific error?
        elif len(SUSHI_status_response) == 1 and list(SUSHI_status_response.keys())[0] == "ERROR":
            logging.error(f"The call to the `status` endpoint for {self.statistics_source_name} returned the error {SUSHI_status_response}.")
            return f"The call to the `status` endpoint for {self.statistics_source_name} returned the error {SUSHI_status_response}."
        else:
            logging.info(f"Call to `status` endpoint for {self.statistics_source_name} successful.")  # These are status endpoints that checked out
            pass

        #Section: Get List of Resources
        #Subsection: Make API Call
        SUSHI_reports_response = SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "reports", SUSHI_parameters).make_SUSHI_call()
        if len(SUSHI_reports_response) == 1 and list(SUSHI_reports_response.keys())[0] == "reports":  # The `reports` route should return a list; to make it match all the other routes, the `make_SUSHI_call()` method makes it the value in a one-item dict with the key `reports`
            logging.info(f"Call to `reports` endpoint for {self.statistics_source_name} successful.")
            all_available_reports = []
            for report_call_response in SUSHI_reports_response.values():  # The dict only has one value, so there will only be one iteration
                for report_details_dict in report_call_response:
                    for report_detail_keys, report_detail_values in report_details_dict.items():
                        logging.debug(f"Report detail key-value pair: {report_detail_keys} | {report_detail_values}")
                        if re.match(r'^[Rr]eport_[(ID)|(id)|(Id)]', report_detail_keys):
                            logging.debug(f"{report_detail_keys} is a match to the regex for `Report_ID`")
                            all_available_reports.append(report_detail_values)
            logging.debug(f"All reports provided by {self.statistics_source_name}: {all_available_reports}")
        elif len(SUSHI_reports_response) == 1 and list(SUSHI_reports_response.keys())[0] == "ERROR":
            logging.error(f"The call to the `reports` endpoint for {self.statistics_source_name} returned the error {SUSHI_reports_response}.")
            return f"The call to the `reports` endpoint for {self.statistics_source_name} returned the error {SUSHI_reports_response}."
        else:
            logging.error(f"A `reports` SUSHI call was made to {self.statistics_source_name}, but the data returned was neither handled as a should have been in `SUSHICallAndResponse.make_SUSHI_call()` nor raised an error. Investigation into the response {SUSHI_reports_response} is required.")
            return f"A `reports` SUSHI call was made to {self.statistics_source_name}, but the data returned was neither handled as a should have been in `SUSHICallAndResponse.make_SUSHI_call()` nor raised an error. Investigation into the response {SUSHI_reports_response} is required."

        #Subsection: Get List of Master Reports
        available_reports = [report for report in all_available_reports if re.search(r'\w{2}(_\w\d)?', report)]
        available_master_reports = [master_report for master_report in available_reports if "_" not in master_report]
        logging.debug(f"Master reports provided by {self.statistics_source_name}: {available_master_reports}")

        #Subsection: Add Any Standard Reports Not Corresponding to a Master Report
        represented_by_master_report = set()
        for master_report in available_master_reports:
            for report in available_reports:
                if report[0:2] == master_report:
                    represented_by_master_report.add(report)
        not_represented_by_master_report = [report for report in available_reports if report not in represented_by_master_report]
        if len(not_represented_by_master_report) > 0:  # Logging statement only appears if it would include content
            logging.debug(f"Standard reports lacking corresponding master reports provided by {self.statistics_source_name}: {not_represented_by_master_report}")


        #Section: Make Master Report SUSHI Calls
        #Subsection: Add Date Parameters
        SUSHI_parameters['begin_date'] = usage_start_date
        SUSHI_parameters['end_date'] = usage_end_date

        #Subsection: Set Up Loop Through Master Reports
        master_report_dataframes = []
        for master_report in available_master_reports:
            master_report_name = master_report.upper()
            logging.info(f"Making SUSHI calls for {self.statistics_source_name} for report {master_report_name}.")

            #Subsection: Check if Usage Is Already in Database
            #ToDo: months_to_exclude_from_harvest = []
            #for month_being_checked in list(rrule(MONTHLY, dtstart=SUSHI_parameters['begin_date'], until=SUSHI_parameters['end_date'])):  # rrule generates a object that can be unpacked into a list of datetime objects representing dates and/or times occurring on a recurring schedule
            #    date_for_query = datetime.date(month_being_checked.year, month_being_checked.month, 1)
            #    number_of_records = pd.read_sql(
            #        sql=f'''
            #            SELECT COUNT(*) FROM COUNTERData
            #            WHERE statistics_source_ID={self.statistics_source_ID} AND report_type='{master_report_name}' AND usage_date='{date_for_query.strftime('%Y-%m-%d')}';
            #        ''',
            #        con=db.engine,  #ALERT: In testing, causing `RuntimeError: No application found. Either work inside a view function or push an application context. See http://flask-sqlalchemy.pocoo.org/contexts/.`
            #    )
            #    logging.debug(f"There were {number_of_records.iloc[0][0]} records for {self.statistics_source_name} in {date_for_query.strftime('%Y-%m')} already loaded in the database.")
            #    if number_of_records.iloc[0][0] > 0:
            #        logging.warning(f"There were records for {self.statistics_source_name} in {date_for_query.strftime('%Y-%m')} already loaded in the database. Since {date_for_query.strftime('%Y-%m')} is in the requested time interval, the usage wasn't requested to avoid duplication.")
            #        return f"There were records for {self.statistics_source_name} in {date_for_query.strftime('%Y-%m')} already loaded in the database. Since {date_for_query.strftime('%Y-%m')} is in the requested time interval, the usage wasn't requested to avoid duplication."
                    #ToDo: Use Flask to ask if data should be loaded, and if not, `months_to_exclude_from_harvest.append(month_being_checked)`
            #ToDo: if len(months_to_exclude_from_harvest) > 0:
                #ToDo: Use position of items in `months_to_exclude_from_harvest` within `list(rrule(MONTHLY, dtstart=SUSHI_parameters['begin_date'], until=SUSHI_parameters['end_date']))` to come up with the range or ranges that need to be checked
                #ToDo: If it's multiple ranges, how will that iteration be initiated from here?

            #Subsection: Add Parameters for Master Report Type
            if "include_parent_details" in list(SUSHI_parameters.keys()):  # When included in reports other than IR, this parameter often causes an error message to appear
                del SUSHI_parameters["include_parent_details"]
            
            if master_report_name == "PR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
            elif master_report_name == "DR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
            elif master_report_name == "TR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
            elif master_report_name == "IR":
                SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Authors|Publication_Date|Article_Version"
                SUSHI_parameters["include_parent_details"] = "True"
            else:
                logging.error(f"This placeholder for potentially calling non-master reports caught a {master_report_name} report for {self.statistics_source_name}. Without knowing the appropriate parameters to add to the SUSHI call, this report wasn't pulled.")  #ToDo: Change so this also displays in Flask without overwriting any other similar messages
                continue  # A `return` statement here would keep any other valid reports from being pulled and processed
            logging.debug(f"Making SUSHI calls for {master_report_name} report from {self.statistics_source_name}.")
            
            #Subsection: Make Master Report API Call
            SUSHI_data_response = SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], f"reports/{master_report_name.lower()}", SUSHI_parameters).make_SUSHI_call()
            if len(SUSHI_data_response) == 1 and list(SUSHI_data_response.keys())[0] == "ERROR":
                logging.error(f"The call to the `reports/{master_report_name.lower()}` endpoint for {self.statistics_source_name} returned the error {SUSHI_data_response}.")  #ToDo: Change so this also displays in Flask without overwriting any other similar messages
                continue  # A `return` statement here would keep any other valid reports from being pulled and processed
            logging.info(f"Call to `reports/{master_report_name.lower()}` endpoint for {self.statistics_source_name} successful.")
            df = ConvertJSONDictToDataframe(SUSHI_data_response).create_dataframe()
            if df.empty:
                continue  # The method above returns an empty dataframe if the dataframe created couldn't be successfully loaded into the database; a `return` statement here would keep any other valid reports from being pulled and processed
            df['statistics_source_ID'] = self.statistics_source_ID
            df['report_type'] = master_report_name
            master_report_dataframes.append(df)
        

        #Section: Return a Single Dataframe
        return pd.concat(master_report_dataframes)


    @hybrid_method
    def collect_usage_statistics(self, usage_start_date, usage_end_date):
        """A method invoking the `_harvest_R5_SUSHI()` method for usage in the specified time range.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month 
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
        
        Returns:
            str: the logging statement to indicate if calling and loading the data succeeded or failed
        """
        logging.debug(f"Starting `StatisticsSources.collect_usage_statistics()` for {self.statistics_source_name}")
        df = self._harvest_R5_SUSHI(usage_start_date, usage_end_date)
        if repr(type(df)) == "<class 'str'>":
            return f"SUSHI harvesting returned the following error: {df}"
        else:
            logging.debug("The SUSHI harvest was a success")
        df.index += first_new_PK_value('COUNTERData')
        try:
            df.to_sql(
                'COUNTERData',
                con=db.engine,
                if_exists='append',
            )
            logging.info("The load was a success.")
            return "The load was a success."
        except Exception as error:
            logging.warning(f"The load had an error: {format(error)}")
            return f"The load had an error: {format(error)}"


    @hybrid_method
    def add_note(self):
        #ToDo: Create a method for adding notes
        pass


class StatisticsSourceNotes(db.Model):
    """The class representation of the `statisticsSourceNotes` relation, which contains notes about the statistics sources in `statisticsSources`.
    
    Attributes:
        self.statistics_source_notes_ID (int): the primary key
        self.note (text): the content of the note
        self.written_by (str): the note author
        self.date_written (date): the day the note was last edited
        self.statistics_source_ID (int): the foreign key for `statisticsSources`
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


class ResourceSources(db.Model):
    """The class representation of the `resourceSources` relation, which contains a list of the places where e-resources are available.

    Resource sources are often called platforms; Alma calls them interfaces. Resource sources are often declared distinct by virtue of having different HTTP domains. 
    
    Attributes:
        self.resource_source_ID (int): the primary key
        self.resource_source_name (str): the resource source name
        self.source_in_use (boolean): indicates if we currently have access to resources at the resource source; uses the pandas Boolean dtype, which allows null values, but null values disallowed through field restraint
        self.use_stop_date (date): if we don't have access to resources at this source, the last date we had access
        self.vendor_ID (int): the foreign key for `vendors`
    
    Methods:
        add_access_stop_date: #ToDo: Copy first line of docstring here
        remove_access_stop_date:  #ToDo: Copy first line of docstring here
        change_StatisticsSource: Change the current statistics source for the resource source.
        add_note:  #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'resourceSources'

    resource_source_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    resource_source_name = db.Column(db.String(100), nullable=False)
    source_in_use = db.Column(db.Boolean, nullable=False)
    use_stop_date = db.Column(db.Date)
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'), nullable=False)

    FK_in_ResourceSourceNotes = db.relationship('ResourceSourceNotes', backref='resourceSources')
    FK_in_StatisticsResourceSources = db.relationship('StatisticsResourceSources', backref='resourceSources')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def add_access_stop_date(self):
        #ToDo: Put value in access_stop_date when current_access goes from True to False
        pass


    @hybrid_method
    def remove_access_stop_date(self):
        #ToDo: Null value in access_stop_date when current_access goes from False to True
        pass


    @hybrid_method
    def change_StatisticsSource(self, statistics_source_PK):
        """Change the current statistics source for the resource source.

        This method changes the `True` value in the `StatisticsResourceSources` record for the given resource source to `False`, then adds a new record creating a connection between the given statistics source and resource source.

        Args:
            statistics_source_PK (int): the primary key from the `statisticsSources` record for the statistics source now used by the given resource source
        
        Returns:
            None: no return value is needed, so the default `None` is used
        """
        #ToDo: SQL_query = f'''
        #ToDo:     UPDATE 
        #ToDo:     SET current_statistics_source = false
        #ToDo:     WHERE SRS_resource_source = {self.resource_source_ID};
        #ToDo: '''
        #ToDo: Apply above query to database
        #ToDo: Inset record into `statisticsResourceSources` relation with values `statistics_source_PK`, `self.resource_source_ID`, and "true"
        pass


    @hybrid_method
    def add_note(self):
        #ToDo: Create a method for adding notes
        pass


class ResourceSourceNotes(db.Model):
    """The class representation of the `resourceSourceNotes` relation, which contains notes about the resource sources in `resourceSources`.
    
    Attributes:
        self.resource_source_notes_ID (int): the primary key
        self.note (text): the content of the note
        self.written_by (str): the note author
        self.date_written (date): the day the note was last edited
        self.resource_source_ID (int): the foreign key for `resourceSources`
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


class StatisticsResourceSources(db.Model):
    """The class representation of the `statisticsResourceSources` relation, which functions as the junction table between `statisticsSources` and `resourceSources`.

    The relationship between resource sources and statistics sources can be complex. A single vendor can have multiple platforms, each with their own statistics source (e.g. Taylor & Francis); a single statistics source can provide usage for multiple separate platforms/domains from a single vendor (e.g. Oxford) or from different vendors (e.g. HighWire); statistics sources can be combined (e.g. Peterson's Prep) or split apart (e.g. UN/OECD iLibrary); changes in publisher (e.g. Nature) or platform hosting service (e.g. Company of Biologists) can change where to get the usage for a given resource. This complexity creates a many-to-many relationship between resource sources and statistics sources, which relational databases implement through a junction table such as this one. The third field in this relation, `Current_Statistics_Source`, indicates if the given statistics source is the current source of usage for the resource source.
    
    Attributes:
        self.SRS_statistics_source (int): part of the composite primary key; the foreign key for `statisticsSources`
        self.SRS_resource_source (int): part of the composite primary key; the foreign key for `resourceSources`
        self.current_statistics_source (boolean): indicates if the statistics source currently provides the usage for the resource source; uses the pandas Boolean dtype, which allows null values, but null values disallowed through field restraint
    """
    __tablename__ = 'statisticsResourceSources'

    SRS_statistics_source = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), primary_key=True, autoincrement=False)
    SRS_resource_source = db.Column(db.Integer, db.ForeignKey('resourceSources.resource_source_ID'), primary_key=True, autoincrement=False)
    current_statistics_source = db.Column(db.Boolean, nullable=False)


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class AnnualUsageCollectionTracking(db.Model):
    """The class representation of the `annualUsageCollectionTracking` relation, which tracks the collecting of usage statistics by containing a record for each fiscal year and statistics source.
    
    Attributes:
        self.AUCT_statistics_source (int): part of the composite primary key; the foreign key for `statisticsSources`
        self.AUCT_fiscal_year (int): part of the composite primary key; the foreign key for `fiscalYears`
        self.usage_is_being_collected (boolean): indicates if usage needs to be collected; uses the pandas Boolean dtype, which allows null values
        self.manual_collection_required (boolean): indicates if usage needs to be collected manually; uses the pandas Boolean dtype, which allows null values
        self.collection_via_email (boolean): indicates if usage needs to be requested by sending an email; uses the pandas Boolean dtype, which allows null values
        self.is_COUNTER_compliant (boolean): indicates if usage is COUNTER R4 or R5 compliant; uses the pandas Boolean dtype, which allows null values
        self.collection_status (enum): the status of the usage statistics collection
        self.usage_file_path (str): the path to the file containing the non-COUNTER usage statistics
        self.notes (test): notes about collecting usage statistics for the particular statistics source and fiscal year
    
    Methods:
        collect_annual_usage_statistics: A method invoking the `_harvest_R5_SUSHI()` method for the given resource's fiscal year usage.
        upload_nonstandard_usage_file: #ToDo: Copy first line of docstring here
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
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def collect_annual_usage_statistics(self):
        """A method invoking the `_harvest_R5_SUSHI()` method for the given resource's fiscal year usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Returns:
            str: the logging statement to indicate if calling and loading the data succeeded or failed
        """
        #Section: Get Data from Relations Corresponding to Composite Key
        #Subsection: Get Data from `fiscalYears`
        fiscal_year_data = pd.read_sql(
            sql=f'SELECT fiscal_year, start_date, end_date FROM fiscalYears WHERE fiscal_year_ID={self.AUCT_fiscal_year};',
            con=db.engine,  #ALERT: This method has no test; running it from command line raises `RuntimeError: No application found. Either work inside a view function or push an application context. See http://flask-sqlalchemy.pocoo.org/contexts/.` which seems to be common to all hybrid methods run from the command line
        )
        start_date = fiscal_year_data['start_date'][0]
        end_date = fiscal_year_data['end_date'][0]
        fiscal_year = fiscal_year_data['fiscal_year'][0]
        logging.debug(f"The fiscal year start and end dates are {start_date} (type {type(start_date)})and {end_date} (type {type(end_date)})")  #ToDo: Confirm that the variables are `datetime.date` objects, and if not, change them to that type
        
        #Subsection: Get Data from `statisticsSources`
        # Using SQLAlchemy to pull a record object doesn't work because the `StatisticsSources` class isn't recognized
        statistics_source_data = pd.read_sql(
            sql=f'SELECT statistics_source_name, statistics_source_retrieval_code, vendor_ID FROM statisticsSources WHERE statistics_source_ID={self.AUCT_statistics_source}',
            con=db.engine,
        )
        statistics_source = StatisticsSources(
            statistics_source_ID = self.AUCT_statistics_source,
            statistics_source_name = statistics_source_data['statistics_source_name'][0],
            statistics_source_retrieval_code = statistics_source_data['statistics_source_retrieval_code'][0],
            vendor_ID = statistics_source_data['vendor_ID'][0],
        )
        logging.debug(f"The `StatisticsSources` object is {statistics_source}")

        #Section: Collect and Load SUSHI Data
        df = statistics_source._harvest_R5_SUSHI(start_date, end_date)
        if repr(type(df)) == "<class 'str'>":
            return f"SUSHI harvesting returned the following error: {df}"
        else:
            logging.debug("The SUSHI harvest was a success")
        df.index += first_new_PK_value('COUNTERData')
        try:
            df.to_sql(
                'COUNTERData',
                con=db.engine,
                if_exists='append',
            )
            logging.info(f"The load for {statistics_source.statistics_source_name} for FY {fiscal_year} was a success.")
            self.collection_status = "Collection complete"  # This updates the field in the relation to confirm that the data has been collected and is in NoLCAT
            return f"The load for {statistics_source.statistics_source_name} for FY {fiscal_year} was a success."
        except Exception as error:
            logging.warning(f"The load for {statistics_source.statistics_source_name} for FY {fiscal_year} had an error: {format(error)}")
            return f"The load for {statistics_source.statistics_source_name} for FY {fiscal_year} had an error: {format(error)}"


    @hybrid_method
    def upload_nonstandard_usage_file(self):
        pass


class COUNTERData(db.Model):
    """The class representation of the `COUNTERData` relation, which contains all the data from the ingested COUNTER reports.

    The attributes of this class represent the general and parent data fields found in R4 and R5 COUNTER reports, which are loaded into this relation with no processing beyond those necessary for aligning data types. Some of the variable string lengths are set with constants, which allow both the string length in the created database and the confirmations that the strings will fit in the database in `ConvertJSONDictToDataframe` to be updated at the same time.

    Attributes:
        self.COUNTER_data_ID (int): the primary key
        self.statistics_source_ID (int): the foreign key for `statisticsSources`
        self.report_type (str): the type of COUNTER report, represented by the official report abbreviation
        self.resource_name (str): the name of the resource
        self.publisher (str): the name of the publisher
        self.publisher_ID (str): the statistics source's ID for the publisher
        self.platform (str): the name of the resource's platform in the COUNTER report
        self.authors (str): the authors of the resource
        self.publication_date (datetime): the resource publication date in the COUNTER IR
        self.article_version (str): version of article within the publication life cycle from the COUNTER IR
        self.DOI (str): the DOI for the resource
        self.proprietary_ID (str): the statistics source's ID for the resource
        self.ISBN (str): the ISBN for the resource
        self.print_ISSN (str): the print ISSN for the resource
        self.online_ISSN (str): the online ISSN for the resource
        self.URI (str): the statistics source's permalink to the resource
        self.data_type (str): the COUNTER data type
        self.section_type (str): the COUNTER section type
        self.YOP (smallInt): the year the resource used was published, where an unknown year is represented with `0001` and articles in press are assigned `9999`
        self.access_type (str): the COUNTER access type
        self.access_method (str): the COUNTER access method
        self.parent_title (str): the name of the resource's host
        self.parent_authors (str): the authors of the resource's host
        self.parent_publication_date (datetime): the resource's host's publication date in the COUNTER IR
        self.parent_article_version (str): version of article's host within the publication life cycle from the COUNTER IR
        self.parent_data_type (str): the COUNTER data type for the resource's host
        self.parent_DOI (str): the DOI for the resource's host
        self.parent_proprietary_ID (str): the statistics source's ID for the resource's host
        self.parent_ISBN (str): the ISBN for the resource's host
        self.parent_print_ISSN (str): the print ISSN for the resource's host
        self.parent_online_ISSN (str): the online ISSN for the resource's host
        self.parent_URI (str): the statistics source's permalink to the resource's host
        self.metric_type (str): the COUNTER metric type
        self.usage_date (date): the month when the use occurred, represented by the first day of that month
        self.usage_count (int): the number of uses
        self.report_creation_date (datetime): the date and time when the SUSHI call for the COUNTER report which provided the data was downloaded
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