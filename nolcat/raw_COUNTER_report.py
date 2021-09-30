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
        #Subsection: Create Collections for Holding Matches
        # The automated matching performed with recordlinkage generates pairs of record indexes for two records in a dataframe that match. The nature of relational data in a flat file format, scholarly resource metadata and computer matching algorithms, however, means a simple list of the record index pairs won't work.
        matched_records = set()
            # For record index pairs matched through exact methods or fuzzy methods with very high thresholds, a set ensures a given match won't be added multiple times because it's identified as a match multiple times.
        matches_to_manually_confirm = dict()
            # For record index pairs matched through fuzzy methods, the match will need to be manually confirmed. Each resource, however, appears multiple times in resource_data and the potential index pairs are created through a Caretesian product, so the same two resources will be compared multiple times. So that each fuzzily matched pair is only asked about once, the relevant metadata for the resource pairs will be put into tuples which will serve as dictionary keys to dictionary values of lists of tuples containing record indexes matching the resources in the dictionary key, as shown below.
        # {
        #     (first resource metadata, second resource metadata): [
        #         (record index pair),
        #         (record index pair)
        #     ],
        #     (first resource metadata, second resource metadata): [
        #         (record index pair),
        #         (record index pair)
        #     ]
        # }

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

        #Subsection: Add Matches to `matched_records` Based on DOI and ISBN
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

        #Subsection: Add Matches to `matched_records` Based on DOI and ISSNs
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

        #Subsection: Add Matches to `matched_records` Based on ISBN
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

        #Subsection: Add Matches to `matched_records` Based on ISSNs
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

        #Subsection: Add Matches to `matched_records` Based on Print ISSN
        print_ISSN_matches = comparing_print_ISSN_table[comparing_print_ISSN_table.sum(axis='columns') == 6].index.tolist()
        logging.info(f"Print ISSN matching record pairs: {print_ISSN_matches}")
        if print_ISSN_matches:
            for match in print_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on print ISSN")
        else:
            logging.info("No matches on print ISSN")

        #Subsection: Create Comparison Based on Online ISSN
        logging.info("**Comparing based on online ISSN**")
        comparing_online_ISSN = recordlinkage.Compare()
        comparing_online_ISSN.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        comparing_online_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        comparing_online_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        comparing_online_ISSN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        comparing_online_ISSN.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')
        comparing_online_ISSN.exact('Data_Type', 'Data_Type', label='Data_Type')

        if normalized_resource_data:
            comparing_online_ISSN_table = comparing_online_ISSN.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_online_ISSN_table = comparing_online_ISSN.compute(candidate_matches, resource_data)
        logging.debug(f"Online ISSN comparison results:\n{comparing_online_ISSN_table}")

        #Subsection: Add Matches to `matched_records` Based on Online ISSN
        online_ISSN_matches = comparing_online_ISSN_table[comparing_online_ISSN_table.sum(axis='columns') == 6].index.tolist()
        logging.info(f"Online ISSN matching record pairs: {online_ISSN_matches}")
        if online_ISSN_matches:
            for match in online_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on online ISSN")
        else:
            logging.info("No matches on online ISSN")
        

        #Section: Identify Pairs of Dataframe Records for the Same Database Based on a High String Matching Threshold
        logging.info("**Comparing databases with high name matching threshold**")
        #Subsection: Create Comparison Based on High String Matching Threshold
        comparing_database_names = recordlinkage.Compare()
        comparing_database_names.string('Resource_Name', 'Resource_Name', threshold=0.925, label='Resource_Name')
        comparing_database_names.exact('Data_Type', 'Data_Type', label='Data_Type')

        if normalized_resource_data:
            comparing_database_names_table = comparing_database_names.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_database_names_table = comparing_database_names.compute(candidate_matches, resource_data)
        logging.debug(f"Database names high matching threshold comparison results:\n{comparing_database_names_table}")

        #Subsection: Filter the Comparison Results
        comparing_database_names_table['index_zero_data_type'] = comparing_database_names_table.index.map(lambda index_value: resource_data.loc[index_value[0], 'Data_Type'])
        comparing_database_names_table['index_one_data_type'] = comparing_database_names_table.index.map(lambda index_value: resource_data.loc[index_value[1], 'Data_Type'])
        database_names_matches_table = comparing_database_names_table[  # Creates dataframe with the records which meet the high name matching threshold and where both resources are databases
            (comparing_database_names_table['Resource_Name'] == 1) &
            (comparing_database_names_table['Data_Type'] == 1) &
            (comparing_database_names_table['index_zero_data_type'] == "Database") &
            (comparing_database_names_table['index_one_data_type'] == "Database")
        ]

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on a High String Matching Threshold
        database_names_matches = database_names_matches_table.index.tolist()
        logging.info(f"Database names high matching threshold record pairs: {database_names_matches}")
        database_names_matches_table['index_zero_name'] = database_names_matches_table.index.map(lambda index_value: resource_data.loc[index_value[0], 'Resource_Name'])
        database_names_matches_table['index_one_name'] = database_names_matches_table.index.map(lambda index_value: resource_data.loc[index_value[1], 'Resource_Name'])
        logging.debug(f"Database names matches table with metadata:\n{database_names_matches_table}")

        for match in database_names_matches:
            # The same Levenstein distance meets a higher threshold if the strings being compared are longer, so a manual confirmation on longer strings is required
            if database_names_matches_table.loc[match]['index_zero_name'] != database_names_matches_table.loc[match]['index_one_name']:
                if len(database_names_matches_table.loc[match]['index_zero_name']) >= 35 or len(database_names_matches_table.loc[match]['index_one_name']) >= 35:
                    matches_to_manually_confirm_key = (database_names_matches_table.loc[match]['index_zero_name'], database_names_matches_table.loc[match]['index_one_name'])
                    try:
                        matches_to_manually_confirm[matches_to_manually_confirm_key].append(match)
                    except:  # If the `matches_to_manually_confirm_key` isn't already in `matches_to_manually_confirm`
                        matches_to_manually_confirm[matches_to_manually_confirm_key] = [match]
                    continue
            matched_records.add(match)
            logging.debug(f"{match} added as a match on database names with a high matching threshold")
        

        #Section: Identify Pairs of Dataframe Records for the Same Resource Based on Fuzzy Matching
        logging.info("**Comparing based on fuzzy name matching and partially matching identifiers**")
        #Subsection: Create Comparison Based on Fuzzy String Matching and Standardized Identifiers
        comparing_names_and_partials = recordlinkage.Compare()
        
        comparing_names_and_partials.string('Resource_Name', 'Resource_Name', threshold=0.65, label='levenshtein')
        comparing_names_and_partials.string('Resource_Name', 'Resource_Name', threshold=0.70, method='jaro', label='jaro')  #ToDo: From jellyfish: `DeprecationWarning: the jaro_distance function incorrectly returns the jaro similarity, replace your usage with jaro_similarity before 1.0`
        comparing_names_and_partials.string('Resource_Name', 'Resource_Name', threshold=0.70, method='jarowinkler', label='jarowinkler')  #ToDo: From jellyfish: `DeprecationWarning: the name 'jaro_winkler' is deprecated and will be removed in jellyfish 1.0, for the same functionality please use jaro_winkler_similarity`
        comparing_names_and_partials.string('Resource_Name', 'Resource_Name', threshold=0.75, method='lcs', label='lcs')
        comparing_names_and_partials.string('Resource_Name', 'Resource_Name', threshold=0.70, method='smith_waterman', label='smith_waterman')

        comparing_names_and_partials.exact('DOI', 'DOI', label='DOI')
        comparing_names_and_partials.exact('ISBN', 'ISBN', label='ISBN')
        comparing_names_and_partials.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        comparing_names_and_partials.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

        if normalized_resource_data:
            comparing_names_and_partials_table = comparing_names_and_partials.compute(candidate_matches, resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            comparing_names_and_partials_table = comparing_names_and_partials.compute(candidate_matches, resource_data)
        logging.debug(f"Fuzzy matching comparison results (before FuzzyWuzzy):\n{comparing_names_and_partials_table}")

        #Subsection: Add FuzzyWuzzy Fuzzy String Matching to Comparison

        #Subsection: Filter the Comparison Results

        #Subsection: Collect the Metadata for Matches to be Added to `matches_to_manually_confirm`

        #Subsection: Add Matches to `matches_to_manually_confirm` Based on Fuzzy Matching
    

    def harvest_SUSHI_report():
        """Use the SUSHI API to collect all the master R5 reports from a given source for a set time period."""
        #ToDo: Write a more detailed docstring
        pass
    

    def load_data_into_database():
        """Add the COUNTER report to the database by adding records to the Resource, Provided_Resources, and COUNTER_Usage_Data relations."""
        #ToDo: Write a more detailed docstring
        pass