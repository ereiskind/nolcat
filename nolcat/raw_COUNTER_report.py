import logging
from pathlib import Path
import re
import pandas as pd
import recordlinkage
from fuzzywuzzy import fuzz

logging.basicConfig(level=logging.INFO, format="RawCOUNTERReport - - [%(asctime)s] %(message)s")  # This formats logging messages like Flask's logging messages, but with the class name where Flask put the server info
# In this class, some logging levels have very specific uses:
    # DEBUG: adding a value to a set or list or a statement that no such additions were made
    # WARNING: method return values


class RawCOUNTERReport:
    """A class for holding and processing raw COUNTER reports.
    
    This class effectively extends the pandas dataframe class by adding methods for working with COUNTER reports. The constructor method accepts COUNTER data in a dataframe prepared for normalization--achieved through either the `SUSHICallAndResponse.make_SUSHI_call()` or `UploadCOUNTERReports.make_dataframe()` methods--and adds methods facilitating the deduplication and division of the data into the appropriate relations.
    
    Attributes:
        self.report_dataframe (dataframe): the raw COUNTER report as a pandas dataframe
    
    Methods:
        _create_normalized_resource_data_argument: Creates a dataframe with a record for each resource containing the default metadata values from `resourceMetadata`, `resourcePlatforms.platform`, and `usageData.data_type`.
        perform_deduplication_matching: Matches the line items in a COUNTER report for the same resource.
        load_data_into_database: Add the COUNTER report to the database by adding records to the `resource`, `resourceMetadata`, `resourcePlatforms`, and `usageData` relations.
    
    Note:
        In all methods, the dataframe appears in the parameters list as `self`, but to use pandas functionality, it must be referenced as `self.report_dataframe`.
    """
    # Constructor Method
    def __init__(self, df):
        """Creates a RawCOUNTERReport object, a dataframe with extra methods, from a dataframe of COUNTER data prepared for normalization."""
        self.report_dataframe = df


    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        return repr(self.report_dataframe.head())
    

    def equals(self, other):
        """Recreates the pandas `equals` method with RawCOUNTERReport objects."""
        return self.report_dataframe.equals(other.report_dataframe)
    

    def _create_normalized_resource_data_argument(self):
        """Creates a dataframe with a record for each resource containing the default metadata values from `resourceMetadata`, `resourcePlatforms.platform`, and `usageData.data_type`.

        The structure of the database doesn't readily allow for the comparison of metadata elements among different resources. This function creates the dataframe enabling comparisons: all the resource IDs are collected, and for each resource, the data required for deduplication is pulled from the database and assigned to the appropriate fields. 

        Returns:
            dataframe: a dataframe with all `resources.resource_ID` values along with their default metadata, platform names, and data types
        """
        #Section: Set Up the Dataframe
        #ToDo: Get list of resources.resource_ID
        #ToDo: fields_and_data = {
            # 'resource_name': None,
            # 'DOI': None,
            # 'ISBN': None,
            # 'print_ISSN': None,
            # 'online_ISSN': None,
            # 'data_type': None,
            # 'platform': None,
        #ToDo: }
        #ToDo: df_content = dict()
        #ToDo: for ID in resources.resource_ID:
            #ToDo: df_content[ID] = fields_and_data
        #ToDo: df = pd.DataFrame(df_content).transpose()


        #Section: Get the Metadata Values
        #ToDo: Get set of resourceMetadata.resource_ID
        #ToDo: for resource ID in set:
            #ToDo: `SELECT * FROM resourceMetadata WHERE resource_ID={resource_ID} AND default=True`
            #ToDo: For each possible `metadata_field` values `resource_name`, `DOI`, `ISBN`, `print_ISSN`, and `online_ISSN`, set df[resource ID][metadata_field] = metadata_value
        

        #Section: Get the Platforms
        #ToDo: for ID in resources.resource_ID:
            #ToDo: `SELECT platform FROM resourcePlatforms WHERE resource_ID={resource_ID}`
            #ToDo: df[ID]['platform'] = above


        #Section: Get the Data Types
        #ToDo: for ID in resources.resource_ID:
            #ToDo: `SELECT
                # resourcePlatforms.resource_ID,
                # resourcePlatforms.resource_platform_ID,
                # usageData.data_type
                # (frequency counts for data types should also be included)
                # FROM resourcePlatforms
                # JOIN usageData ON resourcePlatforms.resource_platform_ID = usageData.resource_platform_ID
                # GROUP BY resourcePlatforms.resource_ID={resource_ID} (probably actually needs to be split up into a filter clause as well)
            #ToDo: `
            #ToDo: if only one data type returned:
                #ToDo: df[ID]['Data_type'] = data type returned
            #ToDo: else:
                #ToDo: df[ID]['Data_type'] = data type returned most frequently
            #ToDo: df = df.applymap(lambda cell_value: None if pd.isna(cell_value) else cell_value)
        pass
    

    def perform_deduplication_matching(self, normalized_resource_data=None):
        """Matches the line items in a COUNTER report for the same resource.

        This function looks at all the records in the parameter dataframe(s) and creates pairs with the record index values if the records are deemed to be for the same resource based on a variety of criteria. Those pairs referring to matches needing manual confirmation are grouped together and set aside so they can be added to the list of matches or not depending on user response captured via Flask.

        Args:
            normalized_resource_data (dataframe, optional): a dataframe of all the resources in the database with default metadata values; the value is `None` during database initialization and created with the `create_normalized_resource_data_argument` when adding to the database
        
        Returns:
            tuple: the variables `matched_records` and `matches_to_manually_confirm` in a tuple for unpacking through multiple assignment; "See Also" describes the individual variables
        
        See Also:
            matched_records: a set of tuples containing the record index values of matched records
            matches_to_manually_confirm: a dict with keys that are tuples containing the metadata for two resources and values that are sets of tuples containing the record index values of record matches with one of the records corresponding to each of the resources in the tuple
        """
        logging.info(f"The new COUNTER report:\n{self}")
        if normalized_resource_data:
            logging.info(f"The normalized resource list:\n{normalized_resource_data}")
        

        #Section: Create Dataframe from New COUNTER Report with Metadata and Same Record Index
        # For deduplication, only the resource name, DOI, ISBN, print ISSN, online ISSN, data type, and platform values are needed, so, to make this method more efficient, all other fields are removed. The OpenRefine JSONs used to transform the tabular COUNTER reports into a database-friendly structure standardize the field names, so the field subset operation will work regardless of the release of the COUNTER data in question.
        new_resource_data = pd.DataFrame(self.report_dataframe[['resource_name', 'DOI', 'ISBN', 'print_ISSN', 'online_ISSN', 'data_type', 'platform']], index=self.report_dataframe.index)
        # The recordlinkage `missing_value` argument doesn't recognize pd.NA, the null value for strings in dataframes, as a missing value, so those values need to be replaced with `None`. Performing this swap changes the data type of all the field back to pandas' generic `object`, but since recordlinkage can do string comparisons on strings of the object data type, this change doesn't cause problems with the program's functionality.
        new_resource_data = new_resource_data.applymap(lambda cell_value: None if pd.isna(cell_value) else cell_value)
        logging.info(f"The new data for comparison:\n{new_resource_data}")


        #Section: Set Up Recordlinkage Matching
        #Subsection: Create Collections for Holding Matches
        # The automated matching performed with recordlinkage generates pairs of record indexes for two records in a dataframe that match. The nature of relational data in a flat file format, scholarly resource metadata, and computer matching algorithms, however, means a simple list of the record index pairs won't work.
        matched_records = set()
            # For record index pairs matched through exact methods or fuzzy methods with very high thresholds, a set ensures a given match won't be added multiple times because it's identified as a match multiple times.
        matches_to_manually_confirm = dict()
            # For record index pairs matched through fuzzy methods, the match will need to be manually confirmed. Each resource, however, appears multiple times in `new_resource_data` and the potential index pairs are created through a Cartesian product, so the same two resources will be compared multiple times. So that each fuzzily matched pair is only asked about once, `matches_to_manually_confirm` will employ nested data collection structures: the variable will be a dictionary with tuples as keys and sets as values; each tuple will contain two tuples, one for each resource's metadata, in 'resource_name', 'DOI', 'ISBN', 'print_ISSN', 'online_ISSN', 'data_type', and 'platform' order (because dictionaries can't be used in dictionary keys); each set will contain tuples of record indexes for resources matching the metadata in the dictionary key. This layout is modeled below:
        # {
        #     (
        #         (first resource metadata),
        #         (second resource metadata)
        #     ): set(
        #         (record index pair),
        #         (record index pair)
        #     ),
        #     (
        #         (first resource metadata),
        #         (second resource metadata)
        #     ): set(
        #         (record index pair),
        #         (record index pair),
        #     ),
        # }

        #Subsection: Create MultiIndex Object
        # This method of indexing creates a object using a Cartesian product of all records in the dataframe. It is memory and time intensive--it can issue a warning about taking time--but the resulting object can be used in the compare method for any and all combinations of fields. Since a resource having values for all metadata fields is highly unlikely and recordlinkage doesn't consider two null values (whether `None` or `NaN`) to be equal, multiple comparisons are needed for thorough deduping; this more comprehensive indexing can be used for all comparisons, so indexing only needs to happen once. (In regards to null values, the `missing_value=1` argument makes any comparison where one of the values is null a match.)
        indexing = recordlinkage.Index()
        indexing.full()  # Sets up a pandas.MultiIndex object with a cartesian product of all the pairs of records in the database--it issues a warning about taking time, but the alternative commits to matching on a certain field
        if normalized_resource_data:
            candidate_matches = indexing.index(new_resource_data, normalized_resource_data)  #Alert: Not tested
            #ToDo: Make sure that multiple records for a new resource in a COUNTER report get grouped together
        else:
            candidate_matches = indexing.index(new_resource_data)
        

        #Section: Identify Pairs of Dataframe Records for the Same Resource Based on Standardized Identifiers
        # recordlinkage doesn't consider two null values (whether `None` or `NaN`) to be equal, so matching on all fields doesn't produce much in the way of results because of the rarity of resources which have both ISSN and ISBN values
        #Subsection: Create Comparison Based on DOI and ISBN
        logging.info("**Comparing based on DOI and ISBN**")
        compare_DOI_and_ISBN = recordlinkage.Compare()
        compare_DOI_and_ISBN.exact('DOI', 'DOI',label='DOI')
        compare_DOI_and_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        compare_DOI_and_ISBN.exact('print_ISSN', 'print_ISSN', missing_value=1, label='Print_ISSN')
        compare_DOI_and_ISBN.exact('online_ISSN', 'online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results Based on DOI and ISBN
        # Record index combines record indexes of records being compared into a multiindex, field index lists comparison objects, and values are the result--`1` is a match, `0` is not a match
        if normalized_resource_data:
            compare_DOI_and_ISBN_table = compare_DOI_and_ISBN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_DOI_and_ISBN_table = compare_DOI_and_ISBN.compute(candidate_matches, new_resource_data)
        logging.info(f"DOI and ISBN comparison results:\n{compare_DOI_and_ISBN_table}")

        #Subsection: Add Matches to `matched_records` Based on DOI and ISBN
        DOI_and_ISBN_matches = compare_DOI_and_ISBN_table[compare_DOI_and_ISBN_table.sum(axis='columns') == 4].index.tolist()  # Create a list of tuples with the record index values of records where all the above criteria match
        logging.info(f"DOI and ISBN matching record pairs: {DOI_and_ISBN_matches}")
        if DOI_and_ISBN_matches:
            for match in DOI_and_ISBN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on DOI and ISBN")
        else:
            logging.debug("No matches on DOI and ISBN")

        #Subsection: Create Comparison Based on DOI and ISSNs
        logging.info("**Comparing based on DOI and ISSNs**")
        compare_DOI_and_ISSNs = recordlinkage.Compare()
        compare_DOI_and_ISSNs.exact('DOI', 'DOI', label='DOI')
        compare_DOI_and_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_DOI_and_ISSNs.exact('print_ISSN', 'print_ISSN', label='Print_ISSN')
        compare_DOI_and_ISSNs.exact('online_ISSN', 'online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results Based on DOI and ISSNs
        if normalized_resource_data:
            compare_DOI_and_ISSNs_table = compare_DOI_and_ISSNs.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_DOI_and_ISSNs_table = compare_DOI_and_ISSNs.compute(candidate_matches, new_resource_data)
        logging.info(f"DOI and ISSNs comparison results:\n{compare_DOI_and_ISSNs_table}")

        #Subsection: Add Matches to `matched_records` Based on DOI and ISSNs
        DOI_and_ISSNs_matches = compare_DOI_and_ISSNs_table[compare_DOI_and_ISSNs_table.sum(axis='columns') == 4].index.tolist()
        logging.info(f"DOI and ISSNs matching record pairs: {DOI_and_ISSNs_matches}")
        if DOI_and_ISSNs_matches:
            for match in DOI_and_ISSNs_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on DOI and ISSNs")
        else:
            logging.debug("No matches on DOI and ISSNs")

        #Subsection: Create Comparison Based on ISBN
        logging.info("**Comparing based on ISBN**")
        compare_ISBN = recordlinkage.Compare()
        compare_ISBN.string('resource_name', 'resource_name', threshold=0.9, label='Resource_Name')
        compare_ISBN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        compare_ISBN.exact('print_ISSN', 'print_ISSN', missing_value=1, label='Print_ISSN')
        compare_ISBN.exact('online_ISSN', 'online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on ISBN
        # The various editions or volumes of a title will be grouped together by fuzzy matching, and these can sometimes be given the same ISBN even when not appropriate. To keep this from causing problems, matches where one of the resource names has a volume or edition reference will be checked manually.
        if normalized_resource_data:
            compare_ISBN_table = compare_ISBN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_ISBN_table['index_one_resource_name'] = compare_ISBN_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'resource_name'])
        else:
            compare_ISBN_table = compare_ISBN.compute(candidate_matches, new_resource_data)
            compare_ISBN_table['index_one_resource_name'] = compare_ISBN_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'resource_name'])
        
        compare_ISBN_table['index_zero_resource_name'] = compare_ISBN_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'resource_name'])
        logging.info(f"ISBN comparison result with metadata:\n{compare_ISBN_table}")

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on Regex and ISBN
        ISBN_matches = compare_ISBN_table[compare_ISBN_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"ISBN matching record pairs: {ISBN_matches}")
        volume_regex = re.compile(r'\bvol(ume)?s?\.?\b')
        edition_regex = re.compile(r'\bed(ition)?s?\.?\b')

        if ISBN_matches:
            for match in ISBN_matches:
                if compare_ISBN_table.loc[match]['index_zero_resource_name'] != compare_ISBN_table.loc[match]['index_one_resource_name']:
                    if volume_regex.search(compare_ISBN_table.loc[match]['index_zero_resource_name']) or volume_regex.search(compare_ISBN_table.loc[match]['index_one_resource_name']) or edition_regex.search(compare_ISBN_table.loc[match]['index_zero_resource_name']) or edition_regex.search(compare_ISBN_table.loc[match]['index_one_resource_name']):
                        index_zero_metadata = (
                            new_resource_data.loc[match[0]]['resource_name'],
                            new_resource_data.loc[match[0]]['DOI'],
                            new_resource_data.loc[match[0]]['ISBN'],
                            new_resource_data.loc[match[0]]['print_ISSN'],
                            new_resource_data.loc[match[0]]['online_ISSN'],
                            new_resource_data.loc[match[0]]['data_type'],
                            new_resource_data.loc[match[0]]['platform'],
                        )
                        if normalized_resource_data:
                            index_one_metadata = (
                                normalized_resource_data.loc[match[1]]['resource_name'],
                                normalized_resource_data.loc[match[1]]['DOI'],
                                normalized_resource_data.loc[match[1]]['ISBN'],
                                normalized_resource_data.loc[match[1]]['print_ISSN'],
                                normalized_resource_data.loc[match[1]]['online_ISSN'],
                                normalized_resource_data.loc[match[1]]['data_type'],
                                normalized_resource_data.loc[match[1]]['platform'],
                            )
                        else:
                            index_one_metadata = (
                                new_resource_data.loc[match[1]]['resource_name'],
                                new_resource_data.loc[match[1]]['DOI'],
                                new_resource_data.loc[match[1]]['ISBN'],
                                new_resource_data.loc[match[1]]['print_ISSN'],
                                new_resource_data.loc[match[1]]['online_ISSN'],
                                new_resource_data.loc[match[1]]['data_type'],
                                new_resource_data.loc[match[1]]['platform'],
                            )
                        # Repetition in the COUNTER reports means that resource metadata permutations can occur separate from record index permutations; as a result, the metadata in both permutations must be tested as a key
                        if matches_to_manually_confirm.get((index_zero_metadata, index_one_metadata)):
                            matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on ISBNs")
                        elif matches_to_manually_confirm.get((index_one_metadata, index_zero_metadata)):
                            matches_to_manually_confirm[(index_one_metadata, index_zero_metadata)].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on ISBNs")
                        else:
                            matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)] = set([match])  # Tuple must be wrapped in brackets to be kept as a tuple in the set
                            logging.info(f"New matches_to_manually_confirm key ({index_zero_metadata}, {index_one_metadata}) created")
                            logging.debug(f"{match} added as a match to manually confirm on ISBNs")
                        continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
                matched_records.add(match)
                logging.debug(f"{match} added as a match on ISBNs")
        else:
            logging.debug("No matches on ISBNs")

        #Subsection: Create Comparison Based on ISSNs
        logging.info("**Comparing based on ISSNs**")
        compare_ISSNs = recordlinkage.Compare()
        compare_ISSNs.string('resource_name', 'resource_name', threshold=0.9, label='Resource_Name')
        compare_ISSNs.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_ISSNs.exact('print_ISSN', 'print_ISSN', label='Print_ISSN')
        compare_ISSNs.exact('online_ISSN', 'online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results Based on ISSNs
        if normalized_resource_data:
            compare_ISSNs_table = compare_ISSNs.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_ISSNs_table = compare_ISSNs.compute(candidate_matches, new_resource_data)
        logging.info(f"ISSNs comparison results:\n{compare_ISSNs_table}")

        #Subsection: Add Matches to `matched_records`
        ISSNs_matches = compare_ISSNs_table[compare_ISSNs_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"ISSNs matching record pairs: {ISSNs_matches}")
        if ISSNs_matches:
            for match in ISSNs_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on ISSNs")
        else:
            logging.debug("No matches on ISSNs")

        #Subsection: Create Comparison Based on Print ISSN
        logging.info("**Comparing based on print ISSN**")
        compare_print_ISSN = recordlinkage.Compare()
        compare_print_ISSN.string('resource_name', 'resource_name', threshold=0.95, label='Resource_Name')
        compare_print_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_print_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_print_ISSN.exact('print_ISSN', 'print_ISSN', label='Print_ISSN')
        compare_print_ISSN.exact('online_ISSN', 'online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results Based on Print ISSN
        if normalized_resource_data:
            compare_print_ISSN_table = compare_print_ISSN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_print_ISSN_table = compare_print_ISSN.compute(candidate_matches, new_resource_data)
        logging.info(f"Print ISSN comparison results:\n{compare_print_ISSN_table}")

        #Subsection: Add Matches to `matched_records` Based on Print ISSN
        print_ISSN_matches = compare_print_ISSN_table[compare_print_ISSN_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"Print ISSN matching record pairs: {print_ISSN_matches}")
        if print_ISSN_matches:
            for match in print_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on print ISSN")
        else:
            logging.debug("No matches on print ISSN")

        #Subsection: Create Comparison Based on Online ISSN
        logging.info("**Comparing based on online ISSN**")
        compare_online_ISSN = recordlinkage.Compare()
        compare_online_ISSN.string('resource_name', 'resource_name', threshold=0.95, label='Resource_Name')
        compare_online_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_online_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_online_ISSN.exact('print_ISSN', 'print_ISSN', missing_value=1, label='Print_ISSN')
        compare_online_ISSN.exact('online_ISSN', 'online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results Based on Online ISSN
        if normalized_resource_data:
            compare_online_ISSN_table = compare_online_ISSN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_online_ISSN_table = compare_online_ISSN.compute(candidate_matches, new_resource_data)
        logging.info(f"Online ISSN comparison results:\n{compare_online_ISSN_table}")

        #Subsection: Add Matches to `matched_records` Based on Online ISSN
        online_ISSN_matches = compare_online_ISSN_table[compare_online_ISSN_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"Online ISSN matching record pairs: {online_ISSN_matches}")
        if online_ISSN_matches:
            for match in online_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on online ISSN")
        else:
            logging.debug("No matches on online ISSN")
        

        #Section: Identify Pairs of Dataframe Records for the Same Database Based on a High String Matching Threshold
        logging.info("**Comparing databases with high resource name matching threshold**")
        #Subsection: Create Comparison Based on High Database Name String Matching Threshold
        compare_database_names = recordlinkage.Compare()
        compare_database_names.string('resource_name', 'resource_name', threshold=0.925, label='Resource_Name')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on High Database Name String Matching Threshold
        if normalized_resource_data:
            compare_database_names_table = compare_database_names.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_database_names_table['index_one_data_type'] = compare_database_names_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'data_type'])
        else:
            compare_database_names_table = compare_database_names.compute(candidate_matches, new_resource_data)
            compare_database_names_table['index_one_data_type'] = compare_database_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'data_type'])
        
        compare_database_names_table['index_zero_data_type'] = compare_database_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'data_type'])
        logging.info(f"Database names comparison result with metadata:\n{compare_database_names_table}")

        #Subsection: Filter and Update Comparison Results Dataframe Based on High Database Name String Matching Threshold
        database_names_matches_table = compare_database_names_table[  # Creates dataframe with the records which meet the high name matching threshold and where both resources are databases
            (compare_database_names_table['Resource_Name'] == 1) &
            (compare_database_names_table['index_zero_data_type'] == "Database") &
            (compare_database_names_table['index_one_data_type'] == "Database")
        ]

        # Resource names and platforms are added after filtering to reduce the number of names that need to be found
        database_names_matches_table['index_zero_resource_name'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'resource_name'])
        database_names_matches_table['index_zero_platform'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'platform'])
        if normalized_resource_data:
            database_names_matches_table['index_one_resource_name'] = database_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'resource_name'])
            database_names_matches_table['index_one_platform'] = database_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'platform'])
        else:
            database_names_matches_table['index_one_resource_name'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'resource_name'])
            database_names_matches_table['index_one_platform'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'platform'])
        logging.info(f"Database names matches table with metadata:\n{database_names_matches_table}")

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on String Length and High Database Name String Matching Threshold
        # The same Levenstein distance meets a higher threshold if the strings being compared are longer, so a manual confirmation on longer strings is required
        database_names_matches_index = database_names_matches_table.index.tolist()
        logging.info(f"Database names high matching threshold record pairs: {database_names_matches_index}")

        if database_names_matches_index:
            for match in database_names_matches_index:
                if database_names_matches_table.loc[match]['index_zero_platform'] == database_names_matches_table.loc[match]['index_one_platform']:  # While some databases are available on multiple platforms, different databases on different platforms can share a name, so all databases on different platforms are manually checked with an `else` statement for this `if` statement
                    if database_names_matches_table.loc[match]['index_zero_resource_name'] != database_names_matches_table.loc[match]['index_one_resource_name']:
                        if len(database_names_matches_table.loc[match]['index_zero_resource_name']) >= 35 or len(database_names_matches_table.loc[match]['index_one_resource_name']) >= 35:
                            # The DOI, ISBN, and ISSNs are collected not to use for comparison here but to keep the number of metadata elements in the inner tuples of `matches_to_manually_confirm` keys constant
                            index_zero_metadata = (
                                new_resource_data.loc[match[0]]['resource_name'],
                                new_resource_data.loc[match[0]]['DOI'],
                                new_resource_data.loc[match[0]]['ISBN'],
                                new_resource_data.loc[match[0]]['print_ISSN'],
                                new_resource_data.loc[match[0]]['online_ISSN'],
                                new_resource_data.loc[match[0]]['data_type'],
                                new_resource_data.loc[match[0]]['platform'],
                            )
                            if normalized_resource_data:
                                index_one_metadata = (
                                    normalized_resource_data.loc[match[1]]['resource_name'],
                                    normalized_resource_data.loc[match[1]]['DOI'],
                                    normalized_resource_data.loc[match[1]]['ISBN'],
                                    normalized_resource_data.loc[match[1]]['print_ISSN'],
                                    normalized_resource_data.loc[match[1]]['online_ISSN'],
                                    normalized_resource_data.loc[match[1]]['data_type'],
                                    normalized_resource_data.loc[match[1]]['platform'],
                                )
                            else:
                                index_one_metadata = (
                                    new_resource_data.loc[match[1]]['resource_name'],
                                    new_resource_data.loc[match[1]]['DOI'],
                                    new_resource_data.loc[match[1]]['ISBN'],
                                    new_resource_data.loc[match[1]]['print_ISSN'],
                                    new_resource_data.loc[match[1]]['online_ISSN'],
                                    new_resource_data.loc[match[1]]['data_type'],
                                    new_resource_data.loc[match[1]]['platform'],
                                )
                            # Repetition in the COUNTER reports means that resource metadata permutations can occur separate from record index permutations; as a result, the metadata in both permutations must be tested as a key
                            if matches_to_manually_confirm.get((index_zero_metadata, index_one_metadata)):
                                matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)].add(match)
                                logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                            elif matches_to_manually_confirm.get((index_one_metadata, index_zero_metadata)):
                                matches_to_manually_confirm[(index_one_metadata, index_zero_metadata)].add(match)
                                logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                            else:
                                matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)] = set([match])  # Tuple must be wrapped in brackets to be kept as a tuple in the set
                                logging.info(f"New matches_to_manually_confirm key ({index_zero_metadata}, {index_one_metadata}) created")
                                logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                            continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
                    matched_records.add(match)  # The indentation is level with the `if` statement for if the resource names are exact matches
                    logging.debug(f"{match} added as a match on database names with a high matching threshold")
                else:
                    index_zero_metadata = (
                        new_resource_data.loc[match[0]]['resource_name'],
                        new_resource_data.loc[match[0]]['DOI'],
                        new_resource_data.loc[match[0]]['ISBN'],
                        new_resource_data.loc[match[0]]['print_ISSN'],
                        new_resource_data.loc[match[0]]['online_ISSN'],
                        new_resource_data.loc[match[0]]['data_type'],
                        new_resource_data.loc[match[0]]['platform'],
                    )
                    if normalized_resource_data:
                        index_one_metadata = (
                            normalized_resource_data.loc[match[1]]['resource_name'],
                            normalized_resource_data.loc[match[1]]['DOI'],
                            normalized_resource_data.loc[match[1]]['ISBN'],
                            normalized_resource_data.loc[match[1]]['print_ISSN'],
                            normalized_resource_data.loc[match[1]]['online_ISSN'],
                            normalized_resource_data.loc[match[1]]['data_type'],
                            normalized_resource_data.loc[match[1]]['platform'],
                        )
                    else:
                        index_one_metadata = (
                            new_resource_data.loc[match[1]]['resource_name'],
                            new_resource_data.loc[match[1]]['DOI'],
                            new_resource_data.loc[match[1]]['ISBN'],
                            new_resource_data.loc[match[1]]['print_ISSN'],
                            new_resource_data.loc[match[1]]['online_ISSN'],
                            new_resource_data.loc[match[1]]['data_type'],
                            new_resource_data.loc[match[1]]['platform'],
                        )
                    # Repetition in the COUNTER reports means that resource metadata permutations can occur separate from record index permutations; as a result, the metadata in both permutations must be tested as a key
                    if matches_to_manually_confirm.get((index_zero_metadata, index_one_metadata)):
                        matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)].add(match)
                        logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                    elif matches_to_manually_confirm.get((index_one_metadata, index_zero_metadata)):
                        matches_to_manually_confirm[(index_one_metadata, index_zero_metadata)].add(match)
                        logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                    else:
                        matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)] = set([match])  # Tuple must be wrapped in brackets to be kept as a tuple in the set
                        logging.info(f"New matches_to_manually_confirm key ({index_zero_metadata}, {index_one_metadata}) created")
                        logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                    continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
        else:
            logging.debug("No matches on database names with a high matching threshold")
        

        #Section: Identify Pairs of Dataframe Records for the Same Platform Based on a High String Matching Threshold
        logging.info("**Comparing platforms with high platform name matching threshold**")
        #Subsection: Create Comparison Based on High Platform Name String Matching Threshold
        compare_platform_names = recordlinkage.Compare()
        compare_platform_names.string('platform', 'platform', threshold=0.925, label='Platform')
        #ALERT: The AWS t3.2xlarge instance ends the test of this method here with the word `Killed` in lieu of a standard error message

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on High Platform Name String Matching Threshold
        if normalized_resource_data:
            compare_platform_names_table = compare_platform_names.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_platform_names_table['index_one_data_type'] = compare_platform_names_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'data_type'])
        else:
            compare_platform_names_table = compare_platform_names.compute(candidate_matches, new_resource_data)
            compare_platform_names_table['index_one_data_type'] = compare_platform_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'data_type'])
        
        compare_platform_names_table['index_zero_data_type'] = compare_platform_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'data_type'])
        logging.info(f"Platform names comparison result with metadata:\n{compare_platform_names_table}")

        #Subsection: Filter and Update Comparison Results Dataframe Based on High Platform Name String Matching Threshold
        platform_names_matches_table = compare_platform_names_table[  # Creates dataframe with the records which meet the high name matching threshold and where both resources are platforms
            (compare_platform_names_table['Platform'] == 1) &
            (compare_platform_names_table['index_zero_data_type'] == "Platform") &
            (compare_platform_names_table['index_one_data_type'] == "Platform")
        ]

        # Platform names are added after filtering to reduce the number of names that need to be found
        platform_names_matches_table['index_zero_platform_name'] = platform_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'platform'])
        if normalized_resource_data:
            platform_names_matches_table['index_one_platform_name'] = platform_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'platform'])
        else:
            platform_names_matches_table['index_one_platform_name'] = platform_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'platform'])
        logging.info(f"Platform names matches table with metadata:\n{platform_names_matches_table}")

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on String Length and High Platform Name String Matching Threshold
        # The same Levenstein distance meets a higher threshold if the strings being compared are longer, so a manual confirmation on longer strings is required
        platform_names_matches_index = platform_names_matches_table.index.tolist()
        logging.info(f"Platform names high matching threshold record pairs: {platform_names_matches_index}")

        if platform_names_matches_index:
            for match in platform_names_matches_index:
                if platform_names_matches_table.loc[match]['index_zero_platform_name'] != platform_names_matches_table.loc[match]['index_one_platform_name']:
                    if len(platform_names_matches_table.loc[match]['index_zero_platform_name']) >= 35 or len(platform_names_matches_table.loc[match]['index_one_platform_name']) >= 35:
                        # The DOI, ISBN, and ISSNs are collected not to use for comparison here but to keep the number of metadata elements in the inner tuples of `matches_to_manually_confirm` keys constant
                        index_zero_metadata = (
                            new_resource_data.loc[match[0]]['resource_name'],
                            new_resource_data.loc[match[0]]['DOI'],
                            new_resource_data.loc[match[0]]['ISBN'],
                            new_resource_data.loc[match[0]]['print_ISSN'],
                            new_resource_data.loc[match[0]]['online_ISSN'],
                            new_resource_data.loc[match[0]]['data_type'],
                            new_resource_data.loc[match[0]]['platform'],
                        )
                        if normalized_resource_data:
                            index_one_metadata = (
                                normalized_resource_data.loc[match[1]]['resource_name'],
                                normalized_resource_data.loc[match[1]]['DOI'],
                                normalized_resource_data.loc[match[1]]['ISBN'],
                                normalized_resource_data.loc[match[1]]['print_ISSN'],
                                normalized_resource_data.loc[match[1]]['online_ISSN'],
                                normalized_resource_data.loc[match[1]]['data_type'],
                                normalized_resource_data.loc[match[1]]['platform'],
                            )
                        else:
                            index_one_metadata = (
                                new_resource_data.loc[match[1]]['resource_name'],
                                new_resource_data.loc[match[1]]['DOI'],
                                new_resource_data.loc[match[1]]['ISBN'],
                                new_resource_data.loc[match[1]]['print_ISSN'],
                                new_resource_data.loc[match[1]]['online_ISSN'],
                                new_resource_data.loc[match[1]]['data_type'],
                                new_resource_data.loc[match[1]]['platform'],
                            )
                        # Repetition in the COUNTER reports means that resource metadata permutations can occur separate from record index permutations; as a result, the metadata in both permutations must be tested as a key
                        if matches_to_manually_confirm.get((index_zero_metadata, index_one_metadata)):
                            matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on platform names with a high matching threshold")
                        elif matches_to_manually_confirm.get((index_one_metadata, index_zero_metadata)):
                            matches_to_manually_confirm[(index_one_metadata, index_zero_metadata)].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on platform names with a high matching threshold")
                        else:
                            matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)] = set([match])  # Tuple must be wrapped in brackets to be kept as a tuple in the set
                            logging.info(f"New matches_to_manually_confirm key ({index_zero_metadata}, {index_one_metadata}) created")
                            logging.debug(f"{match} added as a match to manually confirm on platform names with a high matching threshold")
                        continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
                matched_records.add(match)
                logging.debug(f"{match} added as a match on platform names with a high matching threshold")
        else:
            logging.debug("No matches on platform names with a high matching threshold")


        #Section: Identify Pairs of Dataframe Records Based on a Single Standard Identifier Field
        logging.info("**Comparing based on single matching identifier**")
        #Subsection: Create Comparison Based on a Single Standard Identifier Field
        compare_identifiers = recordlinkage.Compare()
        compare_identifiers.exact('DOI', 'DOI', label='DOI')
        compare_identifiers.exact('ISBN', 'ISBN', label='ISBN')
        compare_identifiers.exact('print_ISSN', 'print_ISSN', label='Print_ISSN')
        compare_identifiers.exact('online_ISSN', 'online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results Based on a Single Standard Identifier Field
        if normalized_resource_data:
            compare_identifiers_table = compare_identifiers.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_identifiers_table = compare_identifiers.compute(candidate_matches, new_resource_data)
        logging.info(f"Single matching identifier comparison results:\n{compare_identifiers_table}")

        #Subsection: Filter Comparison Results Dataframe Based on a Single Standard Identifier Field
        compare_identifiers_matches_table = compare_identifiers_table[
            (compare_identifiers_table['DOI'] == 1) |
            (compare_identifiers_table['ISBN'] == 1) |
            (compare_identifiers_table['Print_ISSN'] == 1) |
            (compare_identifiers_table['Online_ISSN'] == 1)
        ]
        logging.info(f"Filtered single matching identifier comparison results:\n{compare_identifiers_matches_table}")

        #Subsection: Update Comparison Results Based on a Single Standard Identifier Field
        identifiers_matches_interim_index = compare_identifiers_matches_table.index.tolist()
        identifiers_matches_index = []
        # To keep the naming convention consistent, the list of record index tuples that will be loaded into `matches_to_manually_confirm` will use the `_matches_index` name; the list of all multiindex values, including would-be duplicates, has `interim` in the name. Duplicates are removed at this point rather than by the uniqueness constraint of sets to minimize the number of records for which metadata needs to be pulled.
        matches_already_found = matched_records.copy()  # `copy()` recreates the data at a different memory address
        for value_set in matches_to_manually_confirm.values():
            for index_tuple in value_set:
                matches_already_found.add(index_tuple)
        
        for potential_match in identifiers_matches_interim_index:
            if potential_match not in matches_already_found:
                identifiers_matches_index.append(potential_match)
        logging.info(f"Single matching identifier matching record pairs: {identifiers_matches_index}")

        #Subsection: Add Matches to `matches_to_manually_confirm` Based on a Single Standard Identifier Field
        if identifiers_matches_index:
            for match in identifiers_matches_index:
                index_zero_metadata = (
                    new_resource_data.loc[match[0]]['resource_name'],
                    new_resource_data.loc[match[0]]['DOI'],
                    new_resource_data.loc[match[0]]['ISBN'],
                    new_resource_data.loc[match[0]]['print_ISSN'],
                    new_resource_data.loc[match[0]]['online_ISSN'],
                    new_resource_data.loc[match[0]]['data_type'],
                    new_resource_data.loc[match[0]]['platform'],
                )
                if normalized_resource_data:
                    index_one_metadata = (
                        normalized_resource_data.loc[match[1]]['resource_name'],
                        normalized_resource_data.loc[match[1]]['DOI'],
                        normalized_resource_data.loc[match[1]]['ISBN'],
                        normalized_resource_data.loc[match[1]]['print_ISSN'],
                        normalized_resource_data.loc[match[1]]['online_ISSN'],
                        normalized_resource_data.loc[match[1]]['data_type'],
                        normalized_resource_data.loc[match[1]]['platform'],
                    )
                else:
                    index_one_metadata = (
                        new_resource_data.loc[match[1]]['resource_name'],
                        new_resource_data.loc[match[1]]['DOI'],
                        new_resource_data.loc[match[1]]['ISBN'],
                        new_resource_data.loc[match[1]]['print_ISSN'],
                        new_resource_data.loc[match[1]]['online_ISSN'],
                        new_resource_data.loc[match[1]]['data_type'],
                        new_resource_data.loc[match[1]]['platform'],
                    )
                # Repetition in the COUNTER reports means that resource metadata permutations can occur separate from record index permutations; as a result, the metadata in both permutations must be tested as a key
                if matches_to_manually_confirm.get((index_zero_metadata, index_one_metadata)):
                    matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)].add(match)
                    logging.debug(f"{match} added as a match to manually confirm on a single matching identifier")
                elif matches_to_manually_confirm.get((index_one_metadata, index_zero_metadata)):
                    matches_to_manually_confirm[(index_one_metadata, index_zero_metadata)].add(match)
                    logging.debug(f"{match} added as a match to manually confirm on a single matching identifier")
                else:
                    matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)] = set([match])  # Tuple must be wrapped in brackets to be kept as a tuple in the set
                    logging.info(f"New matches_to_manually_confirm key ({index_zero_metadata}, {index_one_metadata}) created")
                    logging.debug(f"{match} added as a match to manually confirm on a single matching identifier")
        else:
            logging.debug("No matches on single matching identifiers")


        #Section: Identify Pairs of Dataframe Records for the Same Resource Based on a High String Matching Threshold
        logging.info("**Comparing resources with high resource name matching threshold**")
        #Subsection: Create Comparison Based on High Resource Name String Matching Threshold
        compare_resource_name = recordlinkage.Compare()
        compare_resource_name.string('resource_name', 'resource_name', threshold=0.65, label='levenshtein')
        compare_resource_name.string('resource_name', 'resource_name', threshold=0.70, method='jaro', label='jaro')  # Version of jellyfish used has DepreciationWarning for this method
        compare_resource_name.string('resource_name', 'resource_name', threshold=0.70, method='jarowinkler', label='jarowinkler')  # Version of jellyfish used has DepreciationWarning for this method
        compare_resource_name.string('resource_name', 'resource_name', threshold=0.75, method='lcs', label='lcs')
        compare_resource_name.string('resource_name', 'resource_name', threshold=0.70, method='smith_waterman', label='smith_waterman')
        #Alert: On a 16GB RAM 1.61GHz workstation, with the combined R4 and R5 test data, it takes nearly four hours to get to this point in the program, at which point, the Command Prompt window closes without showing any sort of error message. Opening task manager shortly afterwords shows the `Python 3.8` process still working, using the vast majority of the workstation's memory for some 15 minutes after. At the end of that time, the program seemed to stop, leaving no evidence the test had been run despite the command line instruction including arguments for writing the logging statements to a log file.

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on High Resource Name String Matching Threshold
        if normalized_resource_data:
            compare_resource_name_table = compare_resource_name.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_resource_name_table['index_one_resource_name'] = compare_resource_name_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'resource_name'])
        else:
            compare_resource_name_table = compare_resource_name.compute(candidate_matches, new_resource_data)
            compare_resource_name_table['index_one_resource_name'] = compare_resource_name_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'resource_name'])
        
        compare_resource_name_table['index_zero_resource_name'] = compare_resource_name_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'resource_name'])
        logging.info(f"Fuzzy matching resource names comparison results (before FuzzyWuzzy):\n{compare_resource_name_table}")

        #Subsection: Update Comparison Results Dataframe Using FuzzyWuzzy Based on High Resource Name String Matching Threshold
        #ALERT: See note in tests.test_RawCOUNTERReport about memory
        # FuzzyWuzzy throws an error when a null value is included in the comparison, and platform records have a null value for the resource name; for FuzzyWuzzy to work, the comparison table records with platforms need to be removed, which can be done by targeting the records with null values in one of the name fields
        compare_resource_name_table.dropna(
            axis='index',
            subset=['index_zero_resource_name', 'index_one_resource_name'],
            inplace=True,
        )
        logging.info(f"Fuzzy matching resource names comparison results (filtered in preparation for FuzzyWuzzy):\n{compare_resource_name_table}")

        compare_resource_name_table['partial_ratio'] = compare_resource_name_table.apply(lambda record: fuzz.partial_ratio(record['index_zero_resource_name'], record['index_one_resource_name']), axis='columns')
        compare_resource_name_table['token_sort_ratio'] = compare_resource_name_table.apply(lambda record: fuzz.token_sort_ratio(record['index_zero_resource_name'], record['index_one_resource_name']), axis='columns')
        compare_resource_name_table['token_set_ratio'] = compare_resource_name_table.apply(lambda record: fuzz.token_set_ratio(record['index_zero_resource_name'], record['index_one_resource_name']), axis='columns')
        logging.info(f"Fuzzy matching resource names comparison results:\n{compare_resource_name_table}")
        
        #Subsection: Filter Comparison Results Dataframe Based on High Resource Name String Matching Threshold
        compare_resource_name_matches_table = compare_resource_name_table[
            (compare_resource_name_table['levenshtein'] > 0) |
            (compare_resource_name_table['jaro'] > 0) |
            (compare_resource_name_table['jarowinkler'] > 0) |
            (compare_resource_name_table['lcs'] > 0) |
            (compare_resource_name_table['smith_waterman'] > 0) |
            (compare_resource_name_table['partial_ratio'] >= 75) |
            (compare_resource_name_table['token_sort_ratio'] >= 70) |
            (compare_resource_name_table['token_set_ratio'] >= 80)
        ]
        logging.info(f"Filtered fuzzy matching resource names comparison results:\n{compare_resource_name_matches_table}")

        #Subsection: Update Comparison Results Based on High Resource Name String Matching Threshold
        resource_name_matches_interim_index = compare_resource_name_matches_table.index.tolist()
        resource_name_matches_index = []
        # To keep the naming convention consistent, the list of record index tuples that will be loaded into `matches_to_manually_confirm` will use the `_matches_index` name; the list of all multiindex values, including would-be duplicates, has `interim` in the name. Duplicates are removed at this point rather than by the uniqueness constraint of sets to minimize the number of records for which metadata needs to be pulled.
        matches_already_found = matched_records.copy()  # `copy()` recreates the data at a different memory address
        for value_set in matches_to_manually_confirm.values():
            for index_tuple in value_set:
                matches_already_found.add(index_tuple)
        
        for potential_match in resource_name_matches_interim_index:
            if potential_match not in matches_already_found:
                resource_name_matches_index.append(potential_match)
        logging.info(f"Fuzzy matching resource names matching record pairs: {resource_name_matches_index}")

        #Subsection: Add Matches to `matches_to_manually_confirm` Based on High Resource Name String Matching Threshold
        if resource_name_matches_index:
            for match in resource_name_matches_index:
                index_zero_metadata = (
                    new_resource_data.loc[match[0]]['resource_name'],
                    new_resource_data.loc[match[0]]['DOI'],
                    new_resource_data.loc[match[0]]['ISBN'],
                    new_resource_data.loc[match[0]]['print_ISSN'],
                    new_resource_data.loc[match[0]]['online_ISSN'],
                    new_resource_data.loc[match[0]]['data_type'],
                    new_resource_data.loc[match[0]]['platform'],
                )
                if normalized_resource_data:
                    index_one_metadata = (
                        normalized_resource_data.loc[match[1]]['resource_name'],
                        normalized_resource_data.loc[match[1]]['DOI'],
                        normalized_resource_data.loc[match[1]]['ISBN'],
                        normalized_resource_data.loc[match[1]]['print_ISSN'],
                        normalized_resource_data.loc[match[1]]['online_ISSN'],
                        normalized_resource_data.loc[match[1]]['data_type'],
                        normalized_resource_data.loc[match[1]]['platform'],
                    )
                else:
                    index_one_metadata = (
                        new_resource_data.loc[match[1]]['resource_name'],
                        new_resource_data.loc[match[1]]['DOI'],
                        new_resource_data.loc[match[1]]['ISBN'],
                        new_resource_data.loc[match[1]]['print_ISSN'],
                        new_resource_data.loc[match[1]]['online_ISSN'],
                        new_resource_data.loc[match[1]]['data_type'],
                        new_resource_data.loc[match[1]]['platform'],
                    )
                # Repetition in the COUNTER reports means that resource metadata permutations can occur separate from record index permutations; as a result, the metadata in both permutations must be tested as a key
                if matches_to_manually_confirm.get((index_zero_metadata, index_one_metadata)):
                    matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)].add(match)
                    logging.debug(f"{match} added as a match to manually confirm on fuzzy matching resource names")
                elif matches_to_manually_confirm.get((index_one_metadata, index_zero_metadata)):
                    matches_to_manually_confirm[(index_one_metadata, index_zero_metadata)].add(match)
                    logging.debug(f"{match} added as a match to manually confirm on fuzzy matching resource names")
                else:
                    matches_to_manually_confirm[(index_zero_metadata, index_one_metadata)] = set([match])  # Tuple must be wrapped in brackets to be kept as a tuple in the set
                    logging.info(f"New matches_to_manually_confirm key ({index_zero_metadata}, {index_one_metadata}) created")
                    logging.debug(f"{match} added as a match to manually confirm on fuzzy matching resource names")
        else:
            logging.debug("No matches on fuzzy matching resource names")


        #Section: Return Record Index Pair Lists
        logging.warning(f"`matched_records`:\n{matched_records}")
        logging.warning(f"`matches_to_manually_confirm`:\n{matches_to_manually_confirm}")
        #ToDo: Resources where an ISSN appears in both the print_ISSN and online_ISSN fields and/or is paired with different ISSNs still need to be paired--can the node and edge model used after this initial manual matching perform that pairing?
        # The only pairings not being found are those described by the above
        return (
            matched_records,
            matches_to_manually_confirm,
        )
    

    def load_data_into_database():
        """Add the COUNTER report to the database by adding records to the `resource`, `resourceMetadata`, `resourcePlatforms`, and `usageData` relations."""
        #ToDo: Write a more detailed docstring
        #ToDo: Filter out non-standard metrics
        pass