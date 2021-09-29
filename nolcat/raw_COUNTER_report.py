import logging
import pandas as pd
import recordlinkage

logging.basicConfig(level=logging.INFO, format="RawCOUNTERReport - - [%(asctime)s] %(message)s")  # This formats logging messages like Flask's logging messages, but with the class name where Flask put the server info


class RawCOUNTERReport:
    """A class for holding and processing raw COUNTER reports.
    
    This class takes a dataframe made from a R4 report CSV converted with the supplied JSONs or a R5 report harvested via SUSHI and handles its processing.
    
    Attributes:
        self.report_dataframe (dataframe): the raw COUNTER report as a pandas dataframe
    
    Methods:
        perform_deduplication_matching: Matches the line items in a COUNTER report for the same resource.
        harvest_SUSHI_report: Use the SUSHI API to collect all the master R5 reports from a given source for a set time period.
        #ToDo: Repeatedly running harvest_SUSHI_report with a list of credentials applying multithreading will be its own function/class
        load_data_into_database: Add the COUNTER report to the database by adding records to the Resource, Provided_Resources, and COUNTER_Usage_Data relations.
    
    Note:
        In all methods, the dataframe appears in the parameters list as `self`, but to use pandas functionality, it must be referenced as `self.report_dataframe`.
    """
    # Constructor Method
    def __init__(self, df):
        #ToDo: Will a more complex constructor for handling reformatted R4 CSVs and R5 SUSHI input be needed?
        self.report_dataframe = df


    # Representation method--using `{self}` in an f-string results in the below
    def __repr__(self):
        return repr(self.report_dataframe.head())
    

    def perform_deduplication_matching(self, normalized_resource_data=None):
        """Matches the line items in a COUNTER report for the same resource.

        This function looks at all the records in the parameter dataframe(s) and creates pairs with the record index values if the records are deemed to be for the same resource based on a variety of criteria. Those pairs referring to matches needing manual confirmation are grouped together and set aside so they can be added to the list of matches or not depending on user response captured via Flask.

        Args:
            normalized_resource_data (dataframe, optional): the database's normalized list of resources; has a value of None during the initial construction of that list
        
        Returns:
            [type]: [description]
        """
        logging.info(f"The new COUNTER report:\n{self}")
        if normalized_resource_data:
            logging.info(f"The normalized resource list:\n{normalized_resource_data}")
        

        #Section: Create Dataframe from New COUNTER Report with Metadata and Same Record Index
        resource_data = pd.DataFrame(self.report_dataframe[['Resource_Name', 'DOI', 'ISBN', 'Print_ISSN', 'Online_ISSN', 'Data_Type']], index=self.report_dataframe.index)


        #Section: Set Up Recordlinkage Matching
        #Subsection: Create Set to Hold All Tuples Representing Matches
        matched_records = set()  # Contains all the tuples of matched records--a set is used because any matches with the DOI will be found again without the DOI, and using a set keeps those tuples from being added twice

        #Subsection: Create MultiIndex Object
        indexing = recordlinkage.Index()
        indexing.full()  # Sets up a pandas.MultiIndex object with a cartesian product of all the pairs of records in the database--it issues a warning about taking time,but the alternative commits to matching on a certain field
        if normalized_resource_data:
            candidate_matches = indexing.index(resource_data, normalized_resource_data)  #Alert: Not tested
            #ToDo: Make sure that multiple records for a new resource in a COUNTER report get grouped together
        else:
            candidate_matches = indexing.index(resource_data)
    

    def harvest_SUSHI_report():
        """Use the SUSHI API to collect all the master R5 reports from a given source for a set time period."""
        #ToDo: Write a more detailed docstring
        pass
    

    def load_data_into_database():
        """Add the COUNTER report to the database by adding records to the Resource, Provided_Resources, and COUNTER_Usage_Data relations."""
        #ToDo: Write a more detailed docstring
        pass