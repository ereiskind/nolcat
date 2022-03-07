import logging
from pathlib import Path
import re
import pandas as pd
import recordlinkage
from fuzzywuzzy import fuzz

logging.basicConfig(level=logging.INFO, format="RawCOUNTERReport - - [%(asctime)s] %(message)s")  # This formats logging messages like Flask's logging messages, but with the class name where Flask put the server info


class RawCOUNTERReport:
    """A class for holding and processing raw COUNTER reports.
    
    This class takes a dataframe made from a R4 report CSV converted with the supplied JSONs or a R5 report harvested via SUSHI and handles its processing.
    
    Attributes:
        self.report_dataframe (dataframe): the raw COUNTER report as a pandas dataframe
    
    Methods:
        perform_deduplication_matching: Matches the line items in a COUNTER report for the same resource.
        load_data_into_database: Add the COUNTER report to the database by adding records to the Resource, Resource_Platforms, and COUNTER_Usage_Data relations.
    
    Note:
        In all methods, the dataframe appears in the parameters list as `self`, but to use pandas functionality, it must be referenced as `self.report_dataframe`.
    """
    # Constructor Method
    def __init__(self, df):
        """Creates a RawCOUNTERReport object, a dataframe with extra methods, from some external COUNTER data.

        Creates a RawCOUNTERReport object by loading either multiple reformatted R4 report binary files with a `<Statistics_Source_ID>_<report type>_<fiscal year in "yy-yy" format>.xlsx` naming convention or a R5 SUSHI API response object with its statisticsSources PK value into a dataframe.
        """
        if repr(type(df)) == "<class 'werkzeug.datastructures.ImmutableMultiDict'>":
            dataframes_to_concatenate = []
            for file in df.getlist('R4_files'):
                try:
                    statistics_source_ID = re.findall(r'(\d*)_\w{2}\d_\d{4}.xlsx', string=Path(file.filename).parts[-1])[0]
                    logging.info(f"Adding statisticsSources PK {statistics_source_ID} to {Path(file.filename).parts[-1]}")
                except:
                    logging.info(f"The name of the file {Path(file.filename).parts[-1]} doesn't follow the naming convention, so a statisticsSources PK can't be derived from it. Please rename this file and try again.")
                    #ToDo: Return an error with a message like the above that exits the constructor method
                # `file` is a FileStorage object; `file.stream` is a tempfile.SpooledTemporaryFile with content accessed via read() method
                dataframe = pd.read_excel(
                    file,
                    #ToDo: Figure out encoding--spreadsheets have non-ASCII characters that are being putput as question marks--Stack Overflow has `encoding=` argument being added, but documentation doesn't show it as a valid argument
                    engine='openpyxl',
                    dtype={
                        'Resource_Name': 'string',
                        'Publisher': 'string',
                        'Platform': 'string',
                        'DOI': 'string',
                        'Proprietary_ID': 'string',
                        'ISBN': 'string',
                        'Print_ISSN': 'string',
                        'Online_ISSN': 'string',
                        'Data_Type': 'string',
                        'Section_Type': 'string',
                        'Metric_Type': 'string',
                        # Usage_Date is fine as default datetime64[ns]
                        'Usage_Count': 'int',  # Python default used because this is a non-null field
                    },
                )
                logging.debug(f"Dataframe without Statistics_Source_ID:\n{dataframe}\n")  # `dataframe` prints the entire dataframe to the command line
                dataframe['Statistics_Source_ID'] = statistics_source_ID
                logging.debug(f"Dataframe:\n{dataframe}\n")
                dataframes_to_concatenate.append(dataframe)
            self.report_dataframe = pd.concat(
                dataframes_to_concatenate,
                ignore_index=True
            )
            #ToDo: Set all dates to first of month (https://stackoverflow.com/questions/42285130/how-floor-a-date-to-the-first-date-of-that-month)
            logging.info(f"Final dataframe:\n{self.report_dataframe}")
        #ToDo: elif df is an API response object: (R5 SUSHI call response)
            #ToDo: self.report_dataframe = the data from the response object
            #ToDo: How to get the statisticsSources PK value here so it can be added to the dataframe?
        elif repr(type(df)) == "<class 'pandas.core.frame.DataFrame'>":  # This is used to instantiate RawCOUNTERReport_fixture_from_R4_spreadsheets
            self.report_dataframe = df
        else:
            pass  #ToDo: Return an error message and quit the constructor


    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        return repr(self.report_dataframe.head())
    

    def equals(self, other):
        """Recreates the pandas `equals` method with RawCOUNTERReport objects."""
        return self.report_dataframe.equals(other.report_dataframe)
    

    def perform_deduplication_matching(self, normalized_resource_data=None):
        """Matches the line items in a COUNTER report for the same resource.

        This function looks at all the records in the parameter dataframe(s) and creates pairs with the record index values if the records are deemed to be for the same resource based on a variety of criteria. Those pairs referring to matches needing manual confirmation are grouped together and set aside so they can be added to the list of matches or not depending on user response captured via Flask.

        Args:
            normalized_resource_data (dataframe, optional): the database's normalized list of resources; has a value of None during the initial construction of that list
        
        Returns:
            tuple: the variables matched_records and matches_to_manually_confirm, described in the note, in a tuple for unpacking through multiple assignment
        
        Note:
            matched_records: a set of tuples containing the record index values of matched records
            matches_to_manually_confirm: a dict with keys that are tuples containing the metadata for two resources and values that are a list of tuples containing the record index values of record matches with one of the records corresponding to each of the resources in the tuple
        """
        logging.info(f"The new COUNTER report:\n{self}")
        if normalized_resource_data:
            logging.info(f"The normalized resource list:\n{normalized_resource_data}")
            #ToDo: SOME ISSUES TO CONSIDER
                #ToDo: The existing program uses a dataframe that includes the resource name, but the resources are stored with the names in a separate relation; how should the names be recombined with the other resource data for deduping against newly loaded reports?
                #ToDo: When the metadata for matched resources doesn't match, the user should select what data goes in the resources relation; should that occur along with or after matches are determined?
                #ToDo: Should metadata elements not being kept in the resources relation be kept? Using them for resource matching purposes would be difficult, but they could be an alternative set of metadata against which searches for resources by ISBN or ISSN could be run.
                #ToDo: Should anything be done to denote those titles where different stats sources assign different data types?
        

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
        #ALERT: See note in tests.test_RawCOUNTERReport about memory
        comparing_names_and_partials_table['index_zero_name'] = comparing_names_and_partials_table.index.map(lambda index_value: resource_data.loc[index_value[0], 'Resource_Name'])
        comparing_names_and_partials_table['index_one_name'] = comparing_names_and_partials_table.index.map(lambda index_value: resource_data.loc[index_value[1], 'Resource_Name'])
        # FuzzyWuzzy throws an error when a null value is included in the comparison, and platform records have a null value for the resource name; for FuzzyWuzzy to work, the comparison table records with platforms need to be removed, which can be done by targeting the records with null values in one of the name fields
        comparing_names_and_partials_table.dropna(
            axis='index',
            subset=['index_zero_name', 'index_one_name'],
            inplace=True,
        )
        logging.debug(f"Fuzzy matching comparison results (filtered in preparation for FuzzyWuzzy):\n{comparing_names_and_partials_table}")

        comparing_names_and_partials_table['partial_ratio'] = comparing_names_and_partials_table.apply(lambda record: fuzz.partial_ratio(record['index_zero_name'], record['index_one_name']), axis='columns')
        comparing_names_and_partials_table['token_sort_ratio'] = comparing_names_and_partials_table.apply(lambda record: fuzz.token_sort_ratio(record['index_zero_name'], record['index_one_name']), axis='columns')
        comparing_names_and_partials_table['token_set_ratio'] = comparing_names_and_partials_table.apply(lambda record: fuzz.token_set_ratio(record['index_zero_name'], record['index_one_name']), axis='columns')
        logging.debug(f"Fuzzy matching comparison results:\n{comparing_names_and_partials_table}")

        #Subsection: Filter the Comparison Results
        comparing_names_and_partials_matches_table = comparing_names_and_partials_table[
            (comparing_names_and_partials_table['levenshtein'] > 0) |
            (comparing_names_and_partials_table['jaro'] > 0) |
            (comparing_names_and_partials_table['jarowinkler'] > 0) |
            (comparing_names_and_partials_table['lcs'] > 0) |
            (comparing_names_and_partials_table['smith_waterman'] > 0) |
            (comparing_names_and_partials_table['DOI'] == 1) |
            (comparing_names_and_partials_table['ISBN'] == 1) |
            (comparing_names_and_partials_table['Print_ISSN'] == 1) |
            (comparing_names_and_partials_table['Online_ISSN'] == 1) |
            (comparing_names_and_partials_table['partial_ratio'] >= 75) |
            (comparing_names_and_partials_table['token_sort_ratio'] >= 70) |
            (comparing_names_and_partials_table['token_set_ratio'] >= 80)
        ]

        #Subsection: Remove Matches Already in `matched_records` and `matches_to_manually_confirm`
        fuzzy_match_record_pairs = []
        for potential_match in comparing_names_and_partials_matches_table.index.tolist():
            if potential_match not in matched_records:
                if potential_match not in list(matches_to_manually_confirm.keys()):
                    fuzzy_match_record_pairs.append(potential_match)

        #Subsection: Collect the Metadata for Matches to be Added to `matches_to_manually_confirm`
        # The metadata is collected in a dataframe so a groupby operation can serve as the Add Matches subsection loop
        fuzzy_match_fields = [
            "resource_PK_pairs",
            "resource_zero_title",
            "resource_one_title",
            "resource_zero_DOI",
            "resource_one_DOI",
            "resource_zero_ISBN",
            "resource_one_ISBN",
            "resource_zero_print_ISSN",
            "resource_one_print_ISSN",
            "resource_zero_online_ISSN",
            "resource_one_online_ISSN",
            "resource_zero_data_type",
            "resource_one_data_type",
        ]

        fuzzy_match_records = []
        for match in fuzzy_match_record_pairs:
            fuzzy_match_records.append(list((  # The list constructor takes an iterable, so the values going into the list must be wrapped in a tuple
                match,
                resource_data.loc[match[0]]['Resource_Name'],
                resource_data.loc[match[1]]['Resource_Name'],
                resource_data.loc[match[0]]['DOI'],
                resource_data.loc[match[1]]['DOI'],
                resource_data.loc[match[0]]['ISBN'],
                resource_data.loc[match[1]]['ISBN'],
                resource_data.loc[match[0]]['Print_ISSN'],
                resource_data.loc[match[1]]['Print_ISSN'],
                resource_data.loc[match[0]]['Online_ISSN'],
                resource_data.loc[match[1]]['Online_ISSN'],
                resource_data.loc[match[0]]['Data_Type'],
                resource_data.loc[match[1]]['Data_Type'],
            )))
        fuzzy_match_table = pd.DataFrame(
            fuzzy_match_records,
            columns=fuzzy_match_fields,
        )
        logging.info(f"The record pairs and metadata for fuzzy matching:\n{fuzzy_match_table}")

        #Subsection: Add Matches to `matches_to_manually_confirm` Based on Fuzzy Matching
        # Since null values aren't equal in tuple equality comparisons, a dataframe groupby operation is used to group records with the same metadata
        for paired_resource_metadata, record_pair in fuzzy_match_table.groupby([
            "resource_zero_title",
            "resource_zero_DOI",
            "resource_zero_ISBN",
            "resource_zero_print_ISSN",
            "resource_zero_online_ISSN",
            "resource_zero_data_type",
            "resource_one_title",
            "resource_one_DOI",
            "resource_one_ISBN",
            "resource_one_print_ISSN",
            "resource_one_online_ISSN",
            "resource_one_data_type",
        ], dropna=False):
            paired_resource_metadata = list(paired_resource_metadata)
            for i, metadata in enumerate(paired_resource_metadata):  # Changing an index referenced item in `paired_resource_metadata` makes the change independent of the loop 
                if pd.isnull(metadata):
                    paired_resource_metadata[i] = None  # This changes null values with numeric data types to None
            resources_to_manually_confirm_key = (tuple(paired_resource_metadata[:6]), tuple(paired_resource_metadata[6:]))
            matches_to_manually_confirm[resources_to_manually_confirm_key] = record_pair['resource_PK_pairs'].tolist()
            logging.debug(f"{resources_to_manually_confirm_key}: {record_pair['resource_PK_pairs'].tolist()} added to matches_to_manually_confirm")
        

        #Section: Return Record Index Pair Lists
        return (
            matched_records,
            matches_to_manually_confirm,
        )
    

    def load_data_into_database():
        """Add the COUNTER report to the database by adding records to the Resource, Resource_Platforms, and COUNTER_Usage_Data relations."""
        #ToDo: Write a more detailed docstring
        pass