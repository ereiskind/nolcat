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


    def harvest_R5_SUSHI():
        #ToDo: For given start date and end date, harvests all available reports at greatest level of detail
        #ToDo: Should there be an option to start by removing all usage from that source for the given time period
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
        #ToDo: Run StatisticsSources.harvest_R5_SUSHI() for the source using the FY start and end dates for the request timeframe
        pass


    def upload_nonstandard_usage_file():
        pass