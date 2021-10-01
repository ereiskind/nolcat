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