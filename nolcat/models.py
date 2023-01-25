"""These classes represent the relations in the database."""

import logging
from pathlib import Path
import os
import sys
import json
from sqlalchemy import Column
from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, SmallInteger, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method  # Initial example at https://pynash.org/2013/03/01/Hybrid-Properties-in-SQLAlchemy/
import pandas as pd

from .app import db


logging.basicConfig(level=logging.DEBUG, format="DB models - - [%(asctime)s] %(message)s")  # This formats logging messages like Flask's logging messages, but with the class name where Flask put the server info


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
        calculate_ARL_19: #ToDo: Copy first line of docstring here
        calculate_ARL_20: #ToDo: Copy first line of docstring here
        create_usage_tracking_records_for_fiscal_year: #ToDo: Copy first line of docstring here
        collect_fiscal_year_usage_statistics: A method invoking the `_harvest_R5_SUSHI()` method for all of a fiscal year's usage.
    """
    #ToDo: On July 1 every year, a new record needs to be added to fiscalYears; how can that be set to happen automatically?
    __tablename__ = 'fiscalYears'

    fiscal_year_ID = db.Column(db.Integer, primary_key=True)
    fiscal_year = db.Column(db.String(4))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    ACRL_60b = db.Column(db.SmallInteger)
    ACRL_63 = db.Column(db.SmallInteger)
    ARL_18 = db.Column(db.SmallInteger)
    ARL_19 = db.Column(db.SmallInteger)
    ARL_20 = db.Column(db.SmallInteger)
    notes_on_statisticsSources_used = db.Column(db.Text)
    notes_on_corrections_after_submission = db.Column(db.Text)

    fiscal_years_FK = db.relationship('ChildRelation', backref='FiscalYearsFK')


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
        pass


    @hybrid_method
    def calculate_ARL_20(self):
        pass


    @hybrid_method
    def create_usage_tracking_records_for_fiscal_year(self):
        #ToDo: For every record in statisticsSources
            #ToDo: For all of its statisticsResourceSources records
                #ToDo: If statisticsResourceSources.Current_Statistics_Source for any of those records is `True`, create a record in annualUsageCollectionTracking where annualUsageCollectionTracking.AUCT_Statistics_Source is the statisticsSources.Statistics_Source_ID for the statisticsSource record for this iteration and annualUsageCollectionTracking.AUCT_Fiscal_Year is the FiscalYears.fiscal_year_ID of the instance this method is being run on
        pass


    @hybrid_method
    def collect_fiscal_year_usage_statistics(self):
        """A method invoking the `_harvest_R5_SUSHI()` method for all of a fiscal year's usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Returns:
            None: no return value is needed, so the default `None` is used
        """
        #ToDo: dfs = []
        #ToDo: For every AnnualUsageCollectionTracking object with the given FY where usage_is_being_collected=True and manual_collection_required=False
            #ToDo: statistics_source = Get the matching StatisticsSources object
            #ToDo: df = statistics_source._harvest_R5_SUSHI(self.start_date, self.end_date)
            #ToDo: dfs.append(df)
            #ToDo: Update AUCT table; see https://www.geeksforgeeks.org/how-to-execute-raw-sql-in-flask-sqlalchemy-app/ for executing SQL update statements
        #ToDo: df = pd.concat(dfs)
        #ToDo: df.to_sql(
        #ToDo:     'COUNTERData',
        #ToDo:     con=db.engine,
        #ToDo:     if_exists='append',
        #ToDo: )
        #ToDo: add logging statement
        pass


class Vendors(db.Model):
    """The class representation of the `vendors` relation, which contains a list of entities that provide access to either electronic resources or usage statistics.
    
    Attributes:
        self. vendor_ID (int): the primary key
        self.vendor_name (str): the name of the vendor= db.Column(db.String(80))
        self.alma_vendor_code (str): the code used to identify vendors in the Alma API return value

    Methods:
        get_statisticsSources: Shows all the statistics sources associated with the vendor.
        get_resourceSources: Shows all the resource sources associated with the vendor.
        add_note: #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'vendors'

    vendor_ID = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(80))
    alma_vendor_code = db.Column(db.String(10))

    vendors_FK = db.relationship('ChildRelation', backref='VendorsFK')


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def get_statisticsSources(self):
        """Shows all the statistics sources associated with the vendor.

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
    def get_resourceSources(self):
        """Shows all the resource sources associated with the vendor.

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

    vendor_notes_ID = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    written_by = db.Column(db.String(100))
    date_written = db.Column(db.Date)
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'))


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

    statistics_source_ID = db.Column(db.Integer, primary_key=True)
    statistics_source_name = db.Column(db.String(100))
    statistics_source_retrieval_code = db.Column(db.String(30))
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'))

    statistics_sources_FK = db.relationship('ChildRelation', backref='StatisticsSourcesFK')


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Should the name of the vendor be returned instead of or in addition to the ID?
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
        #ToDo: Determine if info for API calls is coming from the Alma API or a JSON file saved in a secure location
        #Section: Retrieve Data
        #Subsection: Retrieve Data from JSON
        with open(PATH_TO_CREDENTIALS_FILE()) as JSON_file:
            SUSHI_data_file = json.load(JSON_file)
            logging.debug("JSON with SUSHI credentials loaded.")
            for vendor in SUSHI_data_file:
                for stats_source in vendor:
                    if stats_source['interface_id'] == self.statistics_source_retrieval_code:
                        logging.info(f"Saving credentials for {self.statistics_source_name} ({self.statistics_source_retrieval_code}) to dictionary.")
                        credentials = dict(
                            URL = stats_source['online_location'],
                            customer_id = stats_source['user_id']
                        )

                        try:
                            credentials['requestor_id'] = stats_source['user_password']
                        except:
                            pass

                        try:
                            credentials['api_key'] = stats_source['user_pass_note']
                        except:
                            pass

                        try:
                            credentials['platform'] = stats_source['delivery_address']
                        except:
                            pass

        #Subsection: Retrieve Data from Alma
        #ToDo: When credentials are in Alma, create this functionality


        #Section: Return Data in Requested Format
        if for_API_call:
            logging.debug(f"Returning the credentials {credentials} for a SUSHI API call.")
            return credentials
        else:
            return None  #ToDo: Change to a way to display the `credentials` values to the user via Flask


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
        #ToDo: SUSHI_info = self.statistics_source_retrieval_code.fetch_SUSHI_information()
        #ToDo: SUSHI_parameters = {key: value for key, value in SUSHI_info.items() if key != "URL"}


        #Section: Confirm SUSHI API Functionality
        #ToDo: SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "status", SUSHI_parameters).make_SUSHI_call()
        #ToDo: If a single-item dict with the key `ERROR` is returned, there was a problem--exit the function, providing information about the problem
        #Alert: MathSciNet `status` endpoint returns HTTP status code 400, which will cause an error here, but all the other reports are viable--how should this be handled so that it can pass through?


        #Section: Get List of Resources
        #Subsection: Make API Call
        #ToDo: SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "reports", SUSHI_parameters).make_SUSHI_call()
        #ToDo: If a single-item dict with the key `ERROR` is returned, there was a problem--exit the function, providing information about the problem
        #ToDo: If a single-item dict with the key "reports" is returned, iterate through the list so the ultimate result is all_available_reports = a list of all available reports

        #Subsection: Get List of Master Reports
        #ToDo: available_reports = [report for report in all_available_reports if report not matching regex /\w{2}_\w{2}/]
        #ToDo: available_master_reports = [master_report for master_report in available_reports if "_" not in master_report]

        #Subsection: Add Any Standard Reports Not Corresponding to a Master Report
        #ToDo: represented_by_master_report = set()
        #ToDo: for master_report in available_master_reports:
            #ToDo: for report in available_reports:
                #ToDo: if report[0:2] == master_report:
                    #ToDo: Add report to represented_by_master_report
        #ToDo: not_represented_by_master_report = [report for report in available_reports if report not in represented_by_master_report]
        #ToDo: Figure out inspecting to see if pulling usage from reports in not_represented_by_master_report is appropriate


        #Section: Make Master Report SUSHI Calls
        #Subsection: Add Date Parameters
        #ToDo: SUSHI_parameters['begin_date'] = usage_start_date
        #toDo: SUSHI_parameters['end_date'] = usage_end_date

        #Subsection: Set Up Loop Through Master Reports
        #ToDo: master_report_dataframes = []
        #ToDo: for master_report in available_master_reports:
            #ToDo: master_report_name = master_report short name in uppercase letters

            #Subsection: Check if Usage Is Already in Database
            #ToDo: for month in <the range of months the usage time span represents>
                #ToDo: Get number of records in usage data relation with self.statistics_source_ID, the month, and master_report
                #ToDo: If the above returns data
                    #ToDo: Ask if data should be loaded
            #ToDo: If any months shouldn't be loaded, check if the date range is still contiguous; if not, figure out a way to make call as many times as necessary to call for all dates that need to be pulled

            #Subsection: Add Parameters for Master Report Type
            #ToDo: if master_report_name == "PR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
                #ToDo: try:
                    #ToDo: del SUSHI_parameters["include_parent_details"]
            #ToDo: if master_report_name == "DR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
                    #ToDo: try:
                        #ToDo: del SUSHI_parameters["include_parent_details"]
            #ToDo: if master_report_name == "TR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
                #ToDo: try:
                    #ToDo: del SUSHI_parameters["include_parent_details"]
            #ToDo: if master_report_name == "IR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type"
                #ToDo: SUSHI_parameters["include_parent_details"] = "True"
            
            #Subsection: Make Master Report API Call
            #ToDo: SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], f"reports/{master_report_name.lower()}", SUSHI_parameters).make_SUSHI_call()
            #ToDo: If a single-item dict with the key `ERROR` is returned, there was a problem--exit the function, providing information about the problem
            #ToDo: If a JSON-like dictionary is returned, convert it into a dataframe, making the field labels lowercase
            #ToDo: df['report_type'] = master_report_name
            #ToDo: master_report_dataframes.append(dataframe created from JSON-like dictionary)
        

        #Section: Return a Single Dataframe
        #ToDo: return pd.concat(master_report_dataframes)
        pass


    @hybrid_method
    def collect_usage_statistics(self, usage_start_date, usage_end_date):
        """A method invoking the `_harvest_R5_SUSHI()` method for usage in the specified time range.

        A helper method encapsulating `_harvest_R5_SUSHI` to load its result into the `COUNTERData` relation.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month 
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
        
        Returns:
            None: no return value is needed, so the default `None` is used
        """
        #ToDo: df = self._harvest_R5_SUSHI(usage_start_date, usage_end_date)
        #ToDo: df.to_sql(
        #ToDo:     'COUNTERData',
        #ToDo:     con=db.engine,
        #ToDo:     if_exists='append',
        #ToDo: )
        #ToDo: add logging statement
        pass


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

    statistics_source_notes_ID = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    written_by = db.Column(db.String(100))
    date_written = db.Column(db.Date)
    statistics_source_ID = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'))
    

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
        self.source_in_use (bool): indicates if we currently have access to resources at the resource source
        self.use_stop_date (date): if we don't have access to resources at this source, the last date we had access
        self.vendor_ID (int): the foreign key for `vendors`
    
    Methods:
        add_access_stop_date: #ToDo: Copy first line of docstring here
        remove_access_stop_date:  #ToDo: Copy first line of docstring here
        change_StatisticsSource: Change the current statistics source for the resource source.
        add_note:  #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'resourceSources'

    resource_source_ID = db.Column(db.Integer, primary_key=True)
    resource_source_name = db.Column(db.String(100))
    source_in_use = db.Column(db.Boolean)
    use_stop_date = db.Column(db.Date)
    vendor_ID = db.Column(db.Integer, db.ForeignKey('vendors.vendor_ID'))

    resource_sources_FK = db.relationship('ChildRelation', backref='ResourceSourcesFK')


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

    resource_source_notes_ID = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    written_by = db.Column(db.String(100))
    date_written = db.Column(db.Date)
    resource_source_ID = db.Column(db.Integer, db.ForeignKey('resourceSources.resource_source_ID'))
    

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
        self.current_statistics_source (bool): indicates if the statistics source currently provides the usage for the resource source
    """
    __tablename__ = 'statisticsResourceSources'

    SRS_statistics_source = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), primary_key=True)
    SRS_resource_source = db.Column(db.Integer, db.ForeignKey('resourceSources.resource_source_ID'), primary_key=True)
    current_statistics_source = db.Column(db.Boolean)


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class AnnualUsageCollectionTracking(db.Model):
    """The class representation of the `annualUsageCollectionTracking` relation, which tracks the collecting of usage statistics by containing a record for each fiscal year and statistics source.
    
    Attributes:
        self.AUCT_statistics_source (int): part of the composite primary key; the foreign key for `statisticsSources`
        self.AUCT_fiscal_year (int): part of the composite primary key; the foreign key for `fiscalYears`
        self.usage_is_being_collected (bool): indicates if usage needs to be collected
        self.manual_collection_required (bool): indicates if usage needs to be collected manually
        self.collection_via_email (bool): indicates if usage needs to be requested by sending an email
        self.is_COUNTER_compliant (bool): indicates if usage is COUNTER R4 or R5 compliant
        self.collection_status (enum): the status of the usage statistics collection
        self.usage_file_path (str): the path to the file containing the non-COUNTER usage statistics
        self.notes (test): notes about collecting usage statistics for the particular statistics source and fiscal year
    
    Methods:
        collect_annual_usage_statistics: A method invoking the `_harvest_R5_SUSHI()` method for the given resource's fiscal year usage.
        upload_nonstandard_usage_file: #ToDo: Copy first line of docstring here
    """
    __tablename__ = 'annualUsageCollectionTracking'

    AUCT_statistics_source = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'), primary_key=True)
    AUCT_fiscal_year = db.Column(db.Integer, db.ForeignKey('fiscalYears.fiscal_year_ID'), primary_key=True)
    usage_is_being_collected = db.Column(db.Boolean)
    manual_collection_required = db.Column(db.Boolean)
    collection_via_email = db.Column(db.Boolean)
    is_COUNTER_compliant = db.Column(db.Boolean)
    #ToDo: Check how to do enums in Flask-SQLAlchemy
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
            None: no return value is needed, so the default `None` is used
        """
        #ToDo: start_date = start date for FY
        #ToDo: end_date = end date for FY
        #ToDo: statistics_source = StatisticSources object for self.auct_statistics_source value
        #ToDo: df = statistics_source._harvest_R5_SUSHI(start_date, end_date)
        #ToDo: Change `collection_status` to "Collection complete"
        #ToDo: df.to_sql(
        #ToDo:     'COUNTERData',
        #ToDo:     con=db.engine,
        #ToDo:     if_exists='append',
        #ToDo: )
        #ToDo: add logging statement
        pass


    @hybrid_method
    def upload_nonstandard_usage_file(self):
        pass


class COUNTERData(db.Model):
    """The class representation of the `COUNTERData` relation, which contains all the data from the ingested COUNTER reports.

    The attributes of this class represent the general and parent data fields found in R4 and R5 COUNTER reports, which are loaded into this relation with no processing beyond those necessary for aligning data types.

    Attributes:
        self.COUNTER_data_ID (int): the primary key
        self.statistics_source_ID (int): the foreign key for `statisticsSources`
        self.report_type(str): the type of COUNTER report, represented by the official report abbreviation
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

    COUNTER_data_ID = db.Column(db.Integer, primary_key=True)
    statistics_source_ID = db.Column(db.Integer, db.ForeignKey('statisticsSources.statistics_source_ID'))
    report_type = db.Column(db.String(5))
    resource_name = db.Column(db.String(2000))
    publisher = db.Column(db.String(225))
    publisher_ID = db.Column(db.String(50))
    platform = db.Column(db.String(75))
    authors = db.Column(db.String(1000))
    publication_date = db.Column(db.DateTime)
    article_version = db.Column(db.String(50))
    DOI = db.Column(db.String(75))
    proprietary_ID = db.Column(db.String(100))
    ISBN = db.Column(db.String(20))
    print_ISSN = db.Column(db.String(10))
    online_ISSN = db.Column(db.String(10))
    URI = db.Column(db.String(200))
    data_type = db.Column(db.String(25))
    section_type = db.Column(db.String(10))
    YOP = db.Column(db.SmallInteger)
    access_type = db.Column(db.String(20))
    access_method = db.Column(db.String(10))
    parent_title = db.Column(db.String(2000))
    parent_authors = db.Column(db.String(1000))
    parent_publication_date = db.Column(db.DateTime)
    parent_article_version = db.Column(db.String(50))
    parent_data_type = db.Column(db.String(25))
    parent_DOI = db.Column(db.String(75))
    parent_proprietary_ID = db.Column(db.String(100))
    parent_ISBN = db.Column(db.String(20))
    parent_print_ISSN = db.Column(db.String(10))
    parent_online_ISSN = db.Column(db.String(10))
    parent_URI = db.Column(db.String(200))
    metric_type = db.Column(db.String(75))
    usage_date = db.Column(db.Date)
    usage_count = db.Column(db.Integer)
    report_creation_date = db.Column(db.DateTime)


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass