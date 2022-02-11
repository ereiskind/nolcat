"""These classes represent the relations in the database."""

from pathlib import Path
import logging
import json
from sqlalchemy import Column
from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, SmallInteger, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method  # Initial example at https://pynash.org/2013/03/01/Hybrid-Properties-in-SQLAlchemy/

Base = declarative_base()

#ALERT: A global constant is used for the path to the JSON with the R5 SUSHI credentials for general ease of use. At this time, the final location of the JSON in the container's file system has yet to be determined, so this file path will need to be adjusted as that is finalized. Currently, the absolute file path references a file in a shared network drive that everyone in FSU Libraries working on NoLCAT should be able to access.
PATH_TO_CREDENTIALS_FILE = str(Path('J:', 'nolcat_containers', 'nolcat_build_files', 'database_build_files', 'R5_SUSHI_Credentials.json'))


class FiscalYears(Base):
    """A relation representing the fiscal years for which data has been collected."""
    __tablename__ = 'fiscalYears'
    __table_args__ = {'schema': 'nolcat'}

    fiscal_year_id = Column(Integer, primary_key=True)
    fiscal_year = Column(String(4))
    start_date = Column(Date)
    end_date = Column(Date)
    acrl_60b = Column(SmallInteger)
    acrl_63 = Column(SmallInteger)
    arl_18 = Column(SmallInteger)
    arl_19 = Column(SmallInteger)
    arl_20 = Column(SmallInteger)
    notes_on_statisticsSources_used = Column(Text)
    notes_on_corrections_after_submission = Column(Text)


    def __init__(self, fiscal_year_id, fiscal_year, start_date, end_date, acrl_60b, acrl_63, arl_18, arl_19, arl_20, notes_on_statisticsSources_used,  notes_on_corrections_after_submission):
        """A constructor setting the field values as class attributes."""
        self.fiscal_year_id = fiscal_year_id
        self.fiscal_year = fiscal_year
        self.start_date = start_date
        self.end_date = end_date
        self.acrl_60b = acrl_60b
        self.acrl_63 = acrl_63
        self.arl_18 = arl_18
        self.arl_19 = arl_19
        self.arl_20 = arl_20
        self.notes_on_statisticsSources_used = notes_on_statisticsSources_used
        self.notes_on_corrections_after_submission = notes_on_corrections_after_submission


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def calculate_ACRL_60b():
        pass


    @hybrid_method
    def calculate_ACRL_63():
        pass


    @hybrid_method
    def calculate_ARL_18():
        pass

    
    @hybrid_method
    def calculate_ARL_19():
        pass


    @hybrid_method
    def calculate_ARL_20():
        pass


    @hybrid_method
    def create_usage_tracking_records_for_fiscal_year():
        #ToDo: For every record in statisticsSources
            #ToDo: For all of its statisticsResourceSources records
                #ToDo: If statisticsResourceSources.Current_Statistics_Source for any of those records is `True`, create a record in annualUsageCollectionTracking where annualUsageCollectionTracking.AUCT_Statistics_Source is the statisticsSources.Statistics_Source_ID for the statisticsSource record for this iteration and annualUsageCollectionTracking.AUCT_Fiscal_Year is the FiscalYears.fiscal_year_id of the instance this method is being run on
        pass


    @hybrid_method
    def collect_fiscal_year_usage_statistics(self):
        """A method invoking the RawCOUNTERReport constructor for all of a fiscal year's usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to change its return value from a dataframe to a RawCOUNTERReport object (RawCOUNTERReport objects are what get loaded into the database).

        Returns:
            RawCOUNTERReport: a RawCOUNTERReport object for all the usage for the given fiscal year
        """
        #ToDo: dfs = []
        #ToDo: For every AnnualUsageCollectionTracking object with the given FY where usage_is_being_collected=True and manual_collection_required=False
            #ToDo: statistics_source = Get the matching StatisticsSources object
            #ToDo: df = statistics_source._harvest_R5_SUSHI(self.start_date, self.end_date)
            #ToDo: dfs.append(df)
        #ToDo: df = pd.concat(dfs)
        #ToDo: return RawCOUNTERReport(df)
        pass


class Vendors(Base):
    """A relation representing resource providers."""
    __tablename__ = 'vendors'
    __table_args__ = {'schema': 'nolcat'}

    vendor_id = Column(Integer, primary_key=True)
    vendor_name = Column(String(80))
    alma_vendor_code = Column(String(10))


    def __init__(self, vendor_id, vendor_name, alma_vendor_code):
        """A constructor setting the field values as class attributes."""
        self.vendor_id = vendor_id
        self.vendor_name = vendor_name
        self.alma_vendor_code = alma_vendor_code


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def get_SUSHI_credentials_from_Alma():
        pass


    @hybrid_method
    def get_SUSHI_credentials_from_JSON():
        pass


class VendorNotes(Base):
    """A relation containing notes about vendors."""
    __tablename__ = 'vendorNotes'
    __table_args__ = {'schema': 'nolcat'}

    vendor_notes_id = Column(Integer, primary_key=True)
    note = Column(Text)
    written_by = Column(String(100))
    date_written = Column(Date)
    vendor_id = Column(Integer, ForeignKey('nolcat.Vendors.vendor_id'))

    vendors_FK_vendorNotes = relationship('Vendors', backref='vendor_id')


    def __init__(self, vendor_notes_id, note, written_by, date_written, vendor_id):
        """A constructor setting the field values as class attributes."""
        self.vendor_notes_id = vendor_notes_id
        self.note = note
        self.written_by = written_by
        self.date_written = date_written
        self.vendor_id = vendor_id


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class StatisticsSources(Base):
    """A relation containing information about sources of usage statistics."""
    __tablename__ = 'statisticsSources'
    __table_args__ = {'schema': 'nolcat'}

    statistics_source_id = Column(Integer, primary_key=True)
    statistics_source_name = Column(String(100))
    statistics_source_retrieval_code = Column(String(30))
    vendor_id = Column(Integer, ForeignKey('nolcat.Vendors.vendor_id'))

    vendors_FK_statisticsSources = relationship('Vendors', backref='vendor_id')


    def __init__(self, statistics_source_id, statistics_source_name, statistics_source_retrieval_code, vendor_id):
        """A constructor setting the field values as class attributes."""
        self.statistics_source_id = statistics_source_id
        self.statistics_source_name = statistics_source_name
        self.statistics_source_retrieval_code = statistics_source_retrieval_code
        self.vendor_id = vendor_id


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Should the name of the vendor be returned instead of or in addition to the ID?
        return f"<'statistics_source_id': '{self.statistics_source_id}', 'statistics_source_name': '{self.statistics_source_name}', 'statistics_source_retrieval_code': '{self.statistics_source_retrieval_code}', 'vendor_id': '{self.vendor_id}'>"


    @hybrid_method
    def fetch_SUSHI_credentials(self, for_API_call=True):
        """A method for fetching the information form making a SUSHI API call for the statistics source.

        This method fetches the information for making a SUSHI API call and, depending on the optional argument value, returns them for use in an API call or for display to the user.

        Args:
            for_API_call (bool, optional): a Boolean indicating if the return value should be formatted for use in an API call, which is the default; the other option is formatting the return value for display to the user
        
        Returns:
            dict: a dictionary with the SUSHI API call parameters and values and the API call root
            TBD: a user display format in Flask
        """
        #ToDo: Determine if info for API calls is coming from the Alma API or a JSON file saved in a secure location
        #Section: Retrieve Data
        #Subsection: Retrieve Data from JSON
        with open(PATH_TO_CREDENTIALS_FILE) as JSON_file:
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
        """Collects the COUNTER R5 reports for the given statistics source and loads it into the database.

        For a given statistics source and date range, this method uses SUSHI to harvest all available COUNTER R5 reports at their most granular level, then combines them in a RawCOUNTERReport object for loading into the database. This is a private method meant to be called by other methods which will provide additional context at the method call and wrap the result in the RawCOUNTERReport class.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month 
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
        
        Returns:
            dataframe: a dataframe containing all of the R5 COUNTER data
        """
        #Section: Get API Call URL and Parameters
        #ToDo: Determine if info for API calls is coming from the Alma API or a file saved in a secure location
        #ToDo: Using self.statistics_source_retrieval_code, create dict SUSHI_info with the following key-value pairs:
            #ToDo: URL=the URL for the API call
            #ToDo: customer_ID=the customer ID
            #ToDo: requestor_ID=the requestor ID, if an API call parameter
            #ToDo: API_key=the API key, if an API call parameter
            #ToDo: SUSHI_platform=the platform parameter value, if part of the API call
        #ToDo: SUSHI_parameters = {key: value for key, value in SUSHI_info.items() if key != "URL"}


        #Section: Confirm SUSHI API Functionality
        #ToDo: SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "status", SUSHI_parameters).make_SUSHI_call()
        #ToDo: If a single-item dict with the key `ERROR` is returned, there was a problem--exit the function, providing information about the problem


        #Section: Get List of Resources
        #Subsection: Make API Call
        #ToDo: SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], "reports", SUSHI_parameters).make_SUSHI_call()
        #ToDo: If a single-item dict with the key `ERROR` is returned, there was a problem--exit the function, providing information about the problem
        #ToDo: If a single-item dict with the key "reports" is returned, interate through the list so the ultimate result is all_available_reports = a list of all available reports

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
                #ToDo: Get number of records in usage data relation with self.statistics_source_id, the month, and master_report
                #ToDo: If the above returns data
                    #ToDo: Ask if data should be loaded
            #ToDo: If any months shouldn't be loaded, check if the date range is still contiguous; if not, figure out a way to make call as many times as necessary to call for all dates that need to be pulled

            #Subsection: Add Parameters for Master Report Type
            #ToDo: if master_report_name == "PR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
                #ToDo: try:
                    #ToDo: del SUSHI_parameters["include_parent_details"]
                    #ToDo: del SUSHI_parameters["include_component_details"]
            #ToDo: if master_report_name == "DR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method"
                    #ToDo: try:
                        #ToDo: del SUSHI_parameters["include_parent_details"]
                        #ToDo: del SUSHI_parameters["include_component_details"]
            #ToDo: if master_report_name == "TR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
                #ToDo: try:
                    #ToDo: del SUSHI_parameters["include_parent_details"]
                    #ToDo: del SUSHI_parameters["include_component_details"]
            #ToDo: if master_report_name == "IR":
                #ToDo: SUSHI_parameters["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type"
                #ToDo: SUSHI_parameters["include_parent_details"] = "True"
                #ToDo: SUSHI_parameters["include_component_details"] = "True"
            
            #Subsection: Make Master Report API Call
            #ToDo: SUSHICallAndResponse(self.statistics_source_name, SUSHI_info['URL'], f"reports/{master_report_name.lower()}", SUSHI_parameters).make_SUSHI_call()
            #ToDo: If a single-item dict with the key `ERROR` is returned, there was a problem--exit the function, providing information about the problem
            #ToDo: If a JSON-like dictionary is returned, convert it into a dataframe
            #ToDo: master_report_dataframes.append(dataframe created from JSON-like dictionary)
        

        #Section: Return a Single Dataframe
        #ToDo: return pd.concat(master_report_dataframes)
        pass


    @hybrid_method
    def collect_usage_statistics(self, usage_start_date, usage_end_date):
        """A method invoking the RawCOUNTERReport constructor for usage in the specified time range.

        A helper method encapsulating `_harvest_R5_SUSHI` to change its return value from a dataframe to a RawCOUNTERReport object (RawCOUNTERReport objects are what get loaded into the database).

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month 
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
        
        Returns:
            RawCOUNTERReport: a RawCOUNTERReport object for all the usage from the given statistics source in the given date range
        """
        #ToDo: a dataframe of all the reports = self._harvest_R5_SUSHI(usage_start_date, usage_end_date)
        #ToDo: return RawCOUNTERReport(above dataframe)
        pass


    @hybrid_method
    def upload_R4_report(self):
        #ToDo: Create a method for uploading a transformed R4 report after the creation of the database into the database
        pass


    @hybrid_method
    def upload_R5_report(self):
        #ToDo: Create a method for uploading a R5 report obtained by a method other than SUSHI into the database
        pass


class StatisticsSourceNotes(Base):
    """A relation containing notes about statistics sources."""
    __tablename__ = 'statisticsSourceNotes'
    __table_args__ = {'schema': 'nolcat'}

    statistics_source_notes_id = Column(Integer, primary_key=True)
    note = Column(Text)
    written_by = Column(String(100))
    date_written = Column(Date)
    statistics_source_id = Column(Integer, ForeignKey('nolcat.StatisticsSources.statistics_source_id'))

    statisticsSources_FK_statisticsSourceNotes = relationship('StatisticsSources', backref='statistics_source_id')


    def __init__(self, statistics_source_notes_id, note, written_by, date_written, statistics_source_id):
        """A constructor setting the field values as class attributes."""
        self.statistics_source_notes_id = statistics_source_notes_id
        self.note = note
        self.written_by = written_by
        self.date_written = date_written
        self.statistics_source_id = statistics_source_id
    

    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def write_note(self):
        #ToDo: Create a method for adding notes
        pass


class StatisticsResourceSources(Base):
    """A relation connecting sources of usage statistics and sources of resources.
    
    The relationship between resource sources and statistics sources can be complex. A single vendor can have multiple platforms, each with their own statistics source (e.g. Taylor & Francis); a single statistics source can provide usage for multiple separate platforms/domains from a single vendor (e.g. Oxford) or from different vendors (e.g. HighWire); statistics sources can be combined (e.g. Peterson's Prep) or split apart (e.g. UN/OECD iLibrary); changes in publisher (e.g. Nature) or platform hosting service (e.g. Company of Biologists) can change where to get the usage for a given resource. This complexity creates a many-to-many relationship between resource sources and statistics sources, which relational databases implement through a junction table such as this one. The third field in this relation, `Current_Statistics_Source`, indicates if the given statistics source is the current source of usage for the resource source.
    """
    __tablename__ = 'statisticsResourceSources'
    __table_args__ = {'schema': 'nolcat'}

    srs_statistics_sources = Column(Integer, ForeignKey('nolcat.StatisticsSources.statistics_source_id'))
    srs_resource_sources = Column(Integer, ForeignKey('nolcat.ResourceSources.resource_source_id'))
    current_statistics_source = Column(Boolean)

    statisticsSources_FK_statisticsResourceSources = relationship('StatisticsSources', backref='statistics_source_id')
    resourceSources_FK_statisticsResourceSources = relationship('ResourceSources', backref='resource_source_id')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class ResourceSources(Base):
    """A relation containing information about the sources of resources.
    
    This relation lists where users go to get resources. Often called platforms, they are frequently a HTTP domain. Alma calls them interfaces.
    """
    __tablename__ = 'resourceSources'
    __table_args__ = {'schema': 'nolcat'}

    resource_source_id = Column(Integer, primary_key=True)
    resource_source_name = Column(String(100))
    source_in_use = Column(Boolean)
    use_stop_date = Column(Date)
    vendor_id = Column(Integer, ForeignKey('nolcat.Vendors.vendor_id'))

    vendors_FK_resourceSources = relationship('Vendors', backref='vendor_id')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def add_access_stop_date():
        #ToDo: Put value in access_stop_date when current_access goes from True to False
        pass


    @hybrid_method
    def remove_access_stop_date():
        #ToDo: Null value in access_stop_date when current_access goes from False to True
        pass


class ResourceSourceNotes(Base):
    """A relation containing notes about resource sources."""
    __tablename__ = 'resourceSourceNotes'
    __table_args__ = {'schema': 'nolcat'}

    resource_source_notes_id = Column(Integer, primary_key=True)
    note = Column(Text)
    written_by = Column(String(100))
    date_written = Column(Date)
    resource_source_id = Column(Integer, ForeignKey('nolcat.ResourceSources.resource_source_id'))

    resourceSources_FK_resourceSourceNotes = relationship('ResourceSources', backref='resource_source_id')


    def __init__(self, resource_source_notes_id, note, written_by, date_written, resource_source_id):
        """A constructor setting the field values as class attributes."""
        self.resource_source_notes_id = resource_source_notes_id
        self.note = note
        self.written_by = written_by
        self.date_written = date_written
        self.resource_source_id = resource_source_id
    

    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def write_note(self):
        #ToDo: Create a method for adding notes
        pass


class AnnualUsageCollectionTracking(Base):
    """A relation for tracking the usage statistics collection process. """
    __tablename__ = 'annualUsageCollectionTracking'
    __table_args__ = {'schema': 'nolcat'}

    auct_statistics_source = Column(Integer, ForeignKey('nolcat.StatisticsSources.statistics_source_id'), primary_key=True)
    auct_fiscal_year = Column(Integer, ForeignKey('nolcat.FiscalYears.fiscal_year_id'), primary_key=True)
    usage_is_being_collected = Column(Boolean)
    manual_collection_required = Column(Boolean)
    collection_via_email = Column(Boolean)
    is_counter_compliant = Column(Boolean)
    collection_status = Column('COLLECTION_STATUS', Enum(  # The first argument seems to be meant as a name, but what's being named is unclear; the argument value is named to represent the constant that is the values in the enumeration
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
    usage_file_path = Column(String(150))
    notes = Column(Text)

    statisticsSources_FK_annualUsageCollectionTracking = relationship('StatisticsSources', backref='statistics_source_id')
    fiscalYears_FK_annualUsageCollectionTracking = relationship('FiscalYears', backref='fiscal_year_id')


    def __init__(self, auct_statistics_source, auct_fiscal_year, usage_is_being_collected, manual_collection_required, collection_via_email, is_counter_compliant, collection_status, usage_file_path, notes):
        """A constructor setting the field values as class attributes."""
        self.auct_statistics_source = auct_statistics_source
        self.auct_fiscal_year = auct_fiscal_year
        self.usage_is_being_collected = usage_is_being_collected
        self.manual_collection_required = manual_collection_required
        self.collection_via_email = collection_via_email
        self.is_counter_compliant = is_counter_compliant
        self.collection_status = collection_status
        self.usage_file_path = usage_file_path
        self.notes = notes


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    @hybrid_method
    def collect_annual_usage_statistics(self):
        """A method invoking the RawCOUNTERReport constructor for the given resource's fiscal year usage.

        A helper method encapsulating `_harvest_R5_SUSHI` to change its return value from a dataframe to a RawCOUNTERReport object (RawCOUNTERReport objects are what get loaded into the database).

        Returns:
            RawCOUNTERReport: a RawCOUNTERReport object for all the usage from the given statistics source in the given fiscal year
        """
        #ToDo: start_date = start date for FY
        #ToDo: end_date = end date for FY
        #ToDo: statistics_source = StatisticSources object for self.auct_statistics_source value
        #ToDo: df = statistics_source._harvest_R5_SUSHI(start_date, end_date)
        #ToDo: Change `collection_status` to "Collection complete"
        #ToDo: return RawCOUNTERReport(df)
        pass


    @hybrid_method
    def upload_nonstandard_usage_file():
        pass


class Resources(Base):
    """A relation for resource metadata that's consistant across all platforms."""
    __tablename__ = 'resources'
    __table_args__ = {'schema': 'nolcat'}

    resource_id = Column(Integer, primary_key=True)
    doi = Column(String(75))
    isbn = Column(String(17))
    print_issn = Column(String(9))
    online_issn = Column(String(9))
    data_type = Column(String(25))
    section_type = Column(String(10))


    def __init__(self, resource_id, doi, isbn, print_issn, online_issn, data_type, section_type):
        """A constructor setting the field values as class attributes."""
        self.resource_id = resource_id
        self.doi = doi
        self.isbn = isbn
        self.print_issn = print_issn
        self.online_issn = online_issn
        self.data_type = data_type
        self.section_type = section_type


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class ResourceTitles(Base):
    """A relation containing all the title strings found in COUNTER reports for resources, compiled to preserve all of a resource's names."""
    #ToDo: Figure out handling having the `Database`, `Title`, and `Item` fields from the DR, TR, IR come into this single table; should the granularity/report of origin be recorded?
    __tablename__ = 'resourceTitles'
    __table_args__ = {'schema': 'nolcat'}

    resource_title_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    resource_title = Column()  #ToDo: VARCHAR(2000)
    resource_id = Column(ForeignKey('nolcat.Resources.resource_id'))  #ToDo: INT NOT NULL

    resources_FK_resourceTitles = relationship('Resources', backref='resource_id')


    def __init__(self, resource_title_id, resource_title, resource_id):
        """A constructor setting the field values as class attributes."""
        self.resource_title_id = resource_title_id
        self.resource_title = resource_title
        self.resource_id = resource_id
    

    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class ResourcePlatforms(Base):
    """A relation for the platform-specific resource metadata."""
    __tablename__ = 'resourcePlatforms'
    __table_args__ = {'schema': 'nolcat'}

    resource_platform_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    publisher = Column()  #ToDo: VARCHAR(225)
    publisher_id = Column()  #ToDo: VARCHAR(50)
    platform = Column()  #ToDo: VARCHAR(75) NOT NULL
    proprietary_id = Column()  #ToDo: VARCHAR(100)
    uri = Column()  #ToDo: VARCHAR(200)
    interface = Column(ForeignKey('nolcat.StatisticsSources.statistics_source_id'))  #ToDo: INT NOT NULL
    resource_id = Column(ForeignKey('nolcat.Resources.resource_id'))  #ToDo: INT NOT NULL

    resources_FK_resourcePlatforms = relationship('Resources', backref='resource_id')
    statisticsSources_FK_resourcePlatforms = relationship('StatisticsSources', backref='interface')


    def __init__(self, resource_platform_id, publisher, publisher_id, platform, proprietary_id, uri, interface, resource_id):
        """A constructor setting the field values as class attributes."""
        self.resource_platform_id = resource_platform_id
        self.publisher = publisher
        self.publisher_id = publisher_id
        self.platform = platform
        self.proprietary_id = proprietary_id
        self.uri = uri
        self.interface = interface
        self.resource_id = resource_id


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class UsageData(Base):
    """A relation containing usage metrics."""
    __tablename__ = 'usageData'
    __table_args__ = {'schema': 'nolcat'}

    usage_data_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    resource_platform_id = Column(ForeignKey('nolcat.ResourcePlatforms.resource_platform_id'))  #ToDo: INT NOT NULL
    metric_type = Column()  #ToDo: VARCHAR(75) NOT NULL
    usage_date = Column()  #ToDo: DATE NOT NULL
    usage_count = Column()  #ToDo: MEDIUMINT UNSIGNED NOT NULL
    yop = Column()  #ToDo: SMALLINT
    access_type = Column()  #ToDo: VARCHAR(20)
    access_method = Column()  #ToDo: VARCHAR(10)
    report_creation_date = Column()  #ToDo: DATETIME

    resourcePlatforms_FK_usageData = relationship('ResourcePlatforms', backref='resource_platform_id')


    def __init__(self, usage_data_id, resource_platform_id, metric_type, usage_date, usage_count, yop, access_type, access_method, report_creation_date):
        """A constructor setting the field values as class attributes."""
        self.usage_data_id = usage_data_id
        self.resource_platform_id = resource_platform_id
        self.metric_type = metric_type
        self.usage_date = usage_date
        self.usage_count = usage_count
        self.yop = yop
        self.access_type = access_type
        self.access_method = access_method
        self.report_creation_date = report_creation_date


    def __repr__(self):
        """The printable representation of the record."""
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass