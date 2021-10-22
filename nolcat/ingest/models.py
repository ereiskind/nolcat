"""These classes represent all the relations used only in the `ingest` blueprint."""

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from nolcat.models import Base


class FiscalYears(Base):
    """A relation representing the fiscal years for which data has been collected."""
    __tablename__ = 'fiscalYears'
    __table_args__ = {'schema': 'nolcat'}

    fiscal_year_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    fiscal_year = Column()  #ToDo: CHAR(4) NOT NULL
    start_date = Column()  #ToDo: DATE NOT NULL
    end_date = Column()  #ToDo: DATE NOT NULL
    acrl_60b = Column()  #ToDo: SMALLINT
    acrl_63 = Column()  #ToDo: SMALLINT
    arl_18 = Column()  #ToDo: SMALLINT
    arl_19 = Column()  #ToDo: SMALLINT
    arl_20 = Column()  #ToDo: SMALLINT
    notes_on_corrections_after_submission = Column()  #ToDo: TEXT


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    def calculate_ACRL_60b():
        pass


    def calculate_ACRL_63():
        pass


    def calculate_ARL_18():
        pass

    
    def calculate_ARL_19():
        pass


    def calculate_ARL_20():
        pass


    def create_usage_tracking_records_for_fiscal_year():
        #ToDo: For every stats source that doesn't have deactivation date earlier than FY start date, create a record in annual usage collection tracking relation with this FY and the stats source as the composite key
        pass


class Vendors(Base):
    """A relation representing resource providers."""
    __tablename__ = 'vendors'
    __table_args__ = {'schema': 'nolcat'}

    vendor_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    vendor_name = Column()  #ToDo: VARCHAR(80) NOT NULL
    alma_vendor_code = Column()  #ToDo: VARCHAR(10)


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    def get_SUSHI_credentials_from_Alma():
        pass


    def get_SUSHI_credentials_from_JSON():
        pass


class VendorNotes(Base):
    """A relation containing notes about vendors."""
    __tablename__ = 'vendorNotes'
    __table_args__ = {'schema': 'nolcat'}

    vendor_notes_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    note = Column()  #ToDo: TEXT
    written_by = Column()  #ToDo: VARCHAR(100)
    date_written = Column()  #ToDo: TIMESTAMP
    vendor_id = Column(ForeignKey('nolcat.Vendors.vendor_id'))  #ToDo: INT NOT NULL

    vendors_FK_vendorNotes = relationship('Vendors', backref='vendor_id')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


class StatisticsSources(Base):
    """A relation containing information about sources of usage statistics."""
    __tablename__ = 'statisticsSources'
    __table_args__ = {'schema': 'nolcat'}

    statistics_source_id = Column()  #ToDo: INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    statistics_source_name = Column()  #ToDo: VARCHAR(100) NOT NULL
    statistics_source_retrieval_code = Column()  #ToDo: VARCHAR(30)
    current_access = Column()  #ToDo: BOOLEAN NOT NULL
    access_stop_date = Column()  #ToDo: TIMESTAMP
    vendor_id = Column(ForeignKey('nolcat.Vendors.vendor_id'))  #ToDo: INT NOT NULL

    vendors_FK_statisticsSources = relationship('Vendors', backref='vendor_id')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    def show_SUSHI_credentials():
        #ToDo: Need a way to display SUSHI base URL and parameters (requestor ID, customer ID, API key, platform)--is a method for the record class the best way to do it?
        pass


    def _harvest_R5_SUSHI(self, usage_start_date, usage_end_date):
        """Collects the COUNTER R5 reports for the given statistics source and loads it into the database.

        For a given statistics source and date range, this method uses SUSHI to harvest all available COUNTER R5 reports at their most granular level, then combines them in a RawCOUNTERReport object for loading into the database. This is a private method meant to be called by other methods which will provide additional context at the method call and wrap the result in the RawCOUNTERReport class.

        Args:
            usage_start_date (datetime.date): the first day of the usage collection date range, which is the first day of the month 
            usage_end_date (datetime.date): the last day of the usage collection date range, which is the last day of the month
        
        Returns:
            dataframe: a dataframe containing all of the R5 COUNTER data
        """
        #ToDo: For given start date and end date, harvests all available reports at greatest level of detail
        #ToDo: Should there be an option to start by removing all usage from that source for the given time period

        #Section: Helper Methods for the Method
        #ToDo: Handle_Status_Check_Problem(Source, Message, Error = None, Type = "alert"): Handles results of SUSHI API call for status that countain an error or alert by presenting the message and asking if the interface's stats should be collected.
        #ToDo: Handle_Exception_Master_Report(Source, Report, Exception_List, Load_Report_Items = False): Handles results of a SUSHI API call for a master report that is or contains exceptions. | The function parses the list of exceptions, remaking each exception into a string. Then, if the response contained a Report_Items section, it asks if the usage should be loaded into the database. Finally, if the usage isn't to be loaded into the database, the report is added to Error_Log and the corresponding log statement is output to the terminal. Note that because there are two different possible parmeters for including parent details, "include_parent_details" and "include_component_details", which an item report might use, most item reports will require handling through this function.
        #ToDo: API_Download_Not_Empty(): Prints a message indicating that the "API_Download" folder isn't empty and that it needs to be for the program to work properly, then exits the program.

        #Section: Other Inputs and Questions Related to Loop Removal
        #ToDo: Is the CSV DictWriter error log needed?

        #Section: Start the Method
        #ToDo: Confirm an empty location for JSON files that download when API call is made
        #ToDo: Create a dict with the SUSHI API URL, stats source name, stats source ID, and customer ID, as well as the requestor ID, API key, and/or platform if available/needed
        #ToDo: Get the start and end dates from the user via PyInputPlus
        #ToDo: Create a dict with just the available of customer ID, requestor ID, API key, and platform for API call parameters
        #ToDo: API call for status {Single_Element_API_Call("status", SUSHI_Call_Data["URL"], Credentials_String)}
        #ToDo: Check if returned JSON has any error codes in it
        #ToDo: API call for reports offered {Single_Element_API_Call("reports", SUSHI_Call_Data["URL"], Credentials_String)}
        #ToDo: Get master reports and standard reports for which the master report isn't offered
        #ToDo: Add dates to API call parameters
        #ToDo: For each master report:
            #ToDo: Check if the data was already harvested for the given date range and ask if it should be removed or if the report should be skipped
            #ToDo: Add attributes_to_show with appropriate values to API parameters
            #ToDo: for IR, add include_parent_details and include_component_details
            #ToDo: API call for master report {Master_Report_API_Call(Master_Report_Type, SUSHI_Call_Data["URL"], Credentials_String)}
            #ToDo: Check if returned JSON has any error codes in it
            #ToDo: Handle empty JSONs (JSON is returned, but there's no usage data)
            #ToDo: Pass to RawCOUNTERReport class for deduplication, normalization, and loading into database
        pass


    def add_access_stop_date():
        #ToDo: Put value in access_stop_date when current_access goes from True to False
        pass


    def remove_access_stop_date():
        #ToDo: Null value in access_stop_date when current_access goes from False to True
        pass


class AnnualUsageCollectionTracking():
    """A relation for tracking the usage statistics collection process. """
    __tablename__ = 'annualUsageCollectionTracking'
    __table_args__ = {'schema': 'nolcat'}

    auct_statistics_source = Column(ForeignKey('nolcat.StatisticsSources.statistics_source_id'))  #ToDo: INT NOT NULL
    auct_fiscal_year = Column(ForeignKey('nolcat.FiscalYears.fiscal_year_id'))  #ToDo: INT NOT NULL
    usage_is_being_collected = Column()  #ToDo: BOOLEAN NOT NULL
    manual_collection_required = Column()  #ToDo: BOOLEAN
    collection_via_email = Column()  #ToDo: BOOLEAN
    is_counter_compliant = Column()  #ToDo: BOOLEAN
    collection_status = Column()  #ToDo: ENUM(
        #'N/A: Paid by Law',
        #'N/A: Paid by Med',
        #'N/A: Paid by Music',
        #'N/A: Open access',
        #'N/A: Other (see notes)',
        #'Collection not started',
        #'Collection in process (see notes)',
        #'Collection issues requiring resolution',
        #'Collection complete',
        #'Usage not provided',
        #'No usage to report'
    usage_file_path = Column()  #ToDo: VARCHAR(150)
    notes = Column()  #ToDo: TEXT

    statisticsSources_FK_annualUsageCollectionTracking = relationship('StatisticsSources', backref='statistics_source_id')
    fiscalYears_FK_annualUsageCollectionTracking = relationship('FiscalYears', backref='fiscal_year_id')


    def __repr__(self):
        #ToDo: Create an f-string to serve as a printable representation of the record
        pass


    def collect_usage_via_SUSHI():
        #ToDo: Run StatisticsSources.harvest_R5_SUSHI() for the source using the FY start and end dates for the request timeframe; if successful, should change `collection_status` to "Collection complete"
        pass


    def upload_nonstandard_usage_file():
        pass