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
        

        #Section: Identify Pairs of Dataframe Records for the Same Resource Based on Standardized Identifiers
        # recordlinkage doesn't consider two null values (whether `None` or `NaN`) to be equal, so matching on all fields doesn't produce much in the way of results because of the rarity of resources which have both ISSN and ISBN values
        #Subsection: Create Comparison on DOI and ISBN
        logging.info("**Comparing based on DOI and ISBN**")
        comparing_DOI_and_ISBN = recordlinkage.Compare()
        comparing_DOI_and_ISBN.exact('DOI', 'DOI',label='DOI')
        comparing_DOI_and_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        comparing_DOI_and_ISBN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        comparing_DOI_and_ISBN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')
        comparing_DOI_and_ISBN.exact('Data_Type', 'Data_Type', label='Data_Type')

        # Create a dataframe with two record indexes representing the cartesian product results, a field index representing the comparison methods, and individual values representing the results of the comparison on the record pair
        if normalized_resource_data:
            comparing_DOI_and_ISBN_table = comparing_DOI_and_ISBN.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_DOI_and_ISBN_table = comparing_DOI_and_ISBN.compute(candidate_matches, resource_data)
        logging.debug(f"DOI and ISBN comparison results:\n{comparing_DOI_and_ISBN_table}")

        #Subsection: Add Matches Based on DOI and ISBN
        DOI_and_ISBN_matches = comparing_DOI_and_ISBN_table[comparing_DOI_and_ISBN_table.sum(axis='columns') == 5].index.tolist()  # Create a list of tuples with the record index values of records where all the above criteria match
        logging.info(f"DOI and ISBN matching record pairs: {DOI_and_ISBN_matches}")
        if DOI_and_ISBN_matches:
            for match in DOI_and_ISBN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on DOI and ISBN")
        else:
            logging.info("No matches on DOI and ISBN")

        #Subsection: Create Comparison on DOI and ISSNs
        logging.info("**Comparing based on DOI and ISSNs**")
        comparing_DOI_and_ISSNs = recordlinkage.Compare()
        comparing_DOI_and_ISSNs.exact('DOI', 'DOI', label='DOI')
        comparing_DOI_and_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        comparing_DOI_and_ISSNs.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        comparing_DOI_and_ISSNs.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')
        comparing_DOI_and_ISSNs.exact('Data_Type', 'Data_Type', label='Data_Type')

        if normalized_resource_data:
            comparing_DOI_and_ISSNs_table = comparing_DOI_and_ISSNs.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_DOI_and_ISSNs_table = comparing_DOI_and_ISSNs.compute(candidate_matches, resource_data)
        logging.debug(f"DOI and ISSNs comparison results:\n{comparing_DOI_and_ISSNs_table}")

        #Subsection: Add Matches Based on DOI and ISSNs
        DOI_and_ISSNs_matches = comparing_DOI_and_ISSNs_table[comparing_DOI_and_ISSNs_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"DOI and ISSNs matching record pairs: {DOI_and_ISSNs_matches}")
        if DOI_and_ISSNs_matches:
            for match in DOI_and_ISSNs_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on DOI and ISSNs")
        else:
            logging.info("No matches on DOI and ISSNs")

        #Subsection: Create Comparison Based on ISBN
        logging.info("**Comparing based on ISBN**")
        comparing_ISBN = recordlinkage.Compare()
        comparing_ISBN.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        comparing_ISBN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        comparing_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        comparing_ISBN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        comparing_ISBN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')
        comparing_ISBN.exact('Data_Type', 'Data_Type', label='Data_Type')

        if normalized_resource_data:
            comparing_ISBN_table = comparing_ISBN.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_ISBN_table = comparing_ISBN.compute(candidate_matches, resource_data)
        logging.debug(f"ISBN comparison results:\n{comparing_ISBN_table}")

        #Subsection: Add Matches Based on ISBN
        ISBN_matches = comparing_ISBN_table[comparing_ISBN_table.sum(axis='columns') == 6].index.tolist()
        logging.info(f"ISBN matching record pairs: {ISBN_matches}")
        if ISBN_matches:
            for match in ISBN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on ISBN")
        else:
            logging.info("No matches on ISBN")

        #Subsection: Create Comparison Based on ISSNs
        logging.info("**Comparing based on ISSNs**")
        comparing_ISSNs = recordlinkage.Compare()
        comparing_ISSNs.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        comparing_ISSNs.exact('DOI', 'DOI', missing_value=1, label='DOI')
        comparing_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        comparing_ISSNs.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        comparing_ISSNs.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')
        comparing_ISSNs.exact('Data_Type', 'Data_Type', label='Data_Type')

        if normalized_resource_data:
            comparing_ISSNs_table = comparing_ISSNs.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_ISSNs_table = comparing_ISSNs.compute(candidate_matches, resource_data)
        logging.debug(f"ISSNs comparison results:\n{comparing_ISSNs_table}")

        #Subsection: Add Matches Based on ISSNs
        ISSNs_matches = comparing_ISSNs_table[comparing_ISSNs_table.sum(axis='columns') == 6].index.tolist()
        logging.info(f"ISSNs matching record pairs: {ISSNs_matches}")
        if ISSNs_matches:
            for match in ISSNs_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on ISSNs")
        else:
            logging.info("No matches on ISSNs")

        #Subsection: Create Comparison Based on Print ISSN
        logging.info("**Comparing based on print ISSN**")
        comparing_print_ISSN = recordlinkage.Compare()
        comparing_print_ISSN.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        comparing_print_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        comparing_print_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        comparing_print_ISSN.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        comparing_print_ISSN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')
        comparing_print_ISSN.exact('Data_Type', 'Data_Type', label='Data_Type')

        if normalized_resource_data:
            comparing_print_ISSN_table = comparing_print_ISSN.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_print_ISSN_table = comparing_print_ISSN.compute(candidate_matches, resource_data)
        logging.debug(f"Print ISSN comparison results:\n{comparing_print_ISSN_table}")

        #Subsection: Add Matches Based on Print ISSN
        print_ISSN_matches = comparing_print_ISSN_table[comparing_print_ISSN_table.sum(axis='columns') == 6].index.tolist()
        logging.info(f"Print ISSN matching record pairs: {print_ISSN_matches}")
        if print_ISSN_matches:
            for match in print_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on print ISSN")
        else:
            logging.info("No matches on print ISSN")

        #Subsection: Create Comparison Based on Online ISSN

        #Subsection: Add Matches Based on Online ISSN
    

    def harvest_SUSHI_report():
        """Use the SUSHI API to collect all the master R5 reports from a given source for a set time period."""
        #ToDo: Write a more detailed docstring
        pass
    

    def load_data_into_database():
        """Add the COUNTER report to the database by adding records to the Resource, Provided_Resources, and COUNTER_Usage_Data relations."""
        #ToDo: Write a more detailed docstring
        pass