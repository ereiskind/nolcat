import logging
from pathlib import Path
import re
import pandas as pd
import recordlinkage
from fuzzywuzzy import fuzz

logging.basicConfig(level=logging.INFO, format="RawCOUNTERReport - - [%(asctime)s] %(message)s")  # This formats logging messages like Flask's logging messages, but with the class name where Flask put the server info


class RawCOUNTERReport:
    """A class for holding and processing raw COUNTER reports.
    
    This class effectively extends the pandas dataframe class by adding methods for working with COUNTER reports. The constructor method accepts the data types by which COUNTER data is added to this web app--as a download of multiple CSV files for R4 and as an API call response (or possibly a CSV) for R5--and changes it into a dataframe. The methods facilitate the deduplication and division of the data into the appropriate relations.
    
    Attributes:
        self.report_dataframe (dataframe): the raw COUNTER report as a pandas dataframe
    
    Methods:
        create_normalized_resource_data_argument: Creates a dataframe with a record for each resource containing the default metadata values from resourceMetadata, the resourcePlatforms.platform value, and the usageData.data_type value.
        perform_deduplication_matching: Matches the line items in a COUNTER report for the same resource.
        load_data_into_database: Add the COUNTER report to the database by adding records to the resource, resourceMetadata, resourcePlatforms, and usageData relations.
    
    Note:
        In all methods, the dataframe appears in the parameters list as `self`, but to use pandas functionality, it must be referenced as `self.report_dataframe`.
    """
    # Constructor Method
    def __init__(self, df):
        """Creates a RawCOUNTERReport object, a dataframe with extra methods, from some external COUNTER data.

        The constructor for a RawCOUNTERReport object, it can take in objects of multiple other data types:
        * `werkzeug.datastructures.ImmutableMultiDict` objects, which contain one or more CSV files uploaded via Flask
        * API response objects, which are the result of SUSHI calls
        * `pandas.core.frame.DataFrame` objects, which are used to test the `perform_deduplication_matching` method in isolation of the constructor
        Files containing COUNTER data must be reformatted, a process explained on the Flask pages where such files can be uploaded, and named with the statistics source ID, the report type, and the fiscal year separated by underscores.
        """
        if repr(type(df)) == "<class 'werkzeug.datastructures.ImmutableMultiDict'>":  #ToDo: Confirm that R5 works as well
            dataframes_to_concatenate = []
            for file in df.getlist('R4_files'):  #ToDo: Make sure this isn't locked to a single Flask input form
                try:
                    statistics_source_ID = re.findall(r'(\d*)_\w{2}\d?_\d{4}.csv', string=Path(file.filename).parts[-1])[0]
                    logging.info(f"Adding statisticsSources PK {statistics_source_ID} to {Path(file.filename).parts[-1]}")
                except:
                    logging.info(f"The name of the file {Path(file.filename).parts[-1]} doesn't follow the naming convention, so a statisticsSources PK can't be derived from it. Please rename this file and try again.")
                    #ToDo: Return an error with a message like the above that exits the constructor method
                # `file` is a FileStorage object; `file.stream` is a tempfile.SpooledTemporaryFile with content accessed via read() method
                dataframe = pd.read_csv(
                    file,
                    encoding='utf-8',  # Some of the CSVs are coming in with encoding errors and strings of non-ASCII characters as question marks
                    encoding_errors='backslashreplace',
                    dtype={  # Null values represented by "NaN"/`numpy.nan` in number fields, "NaT".`pd.nat` in datetime fields, and "<NA>"/`pd.NA` in string fields
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
                    #ToDo: parse_dates=['Usage_Date'],
                    #ToDo: infer_datetime_format=True,
                    #ToDo: Perform methods `.encode('utf-8').decode('unicode-escape')` on all fields that might have non-ASCII escaped characters
                    #ToDo: Is iterating through the file (https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#iterating-through-files-chunk-by-chunk) a good idea?
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
        elif repr(type(df)) == "<class 'pandas.core.frame.DataFrame'>":
            self.report_dataframe = df
        else:
            pass  #ToDo: Return an error message and quit the constructor


    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        return repr(self.report_dataframe.head())
    

    def equals(self, other):
        """Recreates the pandas `equals` method with RawCOUNTERReport objects."""
        return self.report_dataframe.equals(other.report_dataframe)
    

    def create_normalized_resource_data_argument(self):
        """Creates a dataframe with a record for each resource containing the default metadata values from resourceMetadata, the resourcePlatforms.platform value, and the usageData.data_type value.

        The structure of the database doesn't readily allow for the comparison of metadata elements among different resources. This function creates the dataframe enabling comparisons: all the resource IDs are collected, and for each resource, the data required for deduplication is pulled from the database and assigned to the appropriate fields. 

        Returns:
            dataframe: a dataframe with all resources.resource_ID values along with their default metadata, platform names, and data types
        """
        #Section: Set Up the Dataframe
        #ToDo: Get list of resources.resource_ID
        #ToDo: fields_and_data = {
            # 'Resource_Name': None,
            # 'DOI': None,
            # 'ISBN': None,
            # 'Print_ISSN': None,
            # 'Online_ISSN': None,
            # 'Data_Type': None,
            # 'Platform': None,
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
            #ToDo: df[ID]['Platform'] = above


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
        new_resource_data = pd.DataFrame(self.report_dataframe[['Resource_Name', 'DOI', 'ISBN', 'Print_ISSN', 'Online_ISSN', 'Data_Type', 'Platform']], index=self.report_dataframe.index)
        # The recordlinkage `missing_value` argument doesn't recognize pd.NA, the null value for strings in dataframes, as a missing value, so those values need to be replaced with `None`. Performing this swap changes the data type of all the field back to pandas' generic `object`, but since recordlinkage can do string comparisons on string of the object data type, this change doesn't cause problems with the program's functionality.
        new_resource_data = new_resource_data.applymap(lambda cell_value: None if pd.isna(cell_value) else cell_value)
        logging.debug(f"The new data for comparison:\n{new_resource_data}")


        #Section: Set Up Recordlinkage Matching
        #Subsection: Create Collections for Holding Matches
        # The automated matching performed with recordlinkage generates pairs of record indexes for two records in a dataframe that match. The nature of relational data in a flat file format, scholarly resource metadata, and computer matching algorithms, however, means a simple list of the record index pairs won't work.
        matched_records = set()  # For record index pairs matched through exact methods or fuzzy methods with very high thresholds, a set ensures a given match won't be added multiple times because it's identified as a match multiple times.
        matches_to_manually_confirm = dict()  # For record index pairs matched through fuzzy methods, the match will need to be manually confirmed. Each resource, however, appears multiple times in new_resource_data and the potential index pairs are created through a Cartesian product, so the same two resources will be compared multiple times. So that each fuzzily matched pair is only asked about once, `matches_to_manually_confirm` will employ nested data collection structures: the variable will be a dictionary with tuples as keys and sets as values; each tuple will contain two tuples, one for each resource's metadata, in 'Resource_Name', 'DOI', 'ISBN', 'Print_ISSN', 'Online_ISSN', 'Data_Type', and 'Platform' order (because dictionaries can't be used in dictionary keys); each set will contain tuples of record indexes for resources matching the metadata in the dictionary key. This layout is modeled below:
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
        indexing.full()
        if normalized_resource_data:
            candidate_matches = indexing.index(new_resource_data, normalized_resource_data)  #Alert: Not tested
            #ToDo: Make sure that multiple records for a new resource in a COUNTER report get grouped together
        else:
            candidate_matches = indexing.index(new_resource_data)
        

        #Section: Find Matches--DOIs and ISBNs
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on DOI and ISBN**")
        compare_DOI_and_ISBN = recordlinkage.Compare()
        compare_DOI_and_ISBN.exact('DOI', 'DOI',label='DOI')
        compare_DOI_and_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        compare_DOI_and_ISBN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        compare_DOI_and_ISBN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results
        # Record index combines record indexes of records being compared into a multiindex, field index lists comparison objects, and values are the result--`1` is a match, `0` is not a match
        if normalized_resource_data:
            compare_DOI_and_ISBN_table = compare_DOI_and_ISBN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_DOI_and_ISBN_table = compare_DOI_and_ISBN.compute(candidate_matches, new_resource_data)
        logging.debug(f"DOI and ISBN comparison results:\n{compare_DOI_and_ISBN_table}")

        #Subsection: Add Matches to `matched_records`
        DOI_and_ISBN_matches = compare_DOI_and_ISBN_table[compare_DOI_and_ISBN_table.sum(axis='columns') == 4].index.tolist()  # Create a list of tuples with the record index values of records where all the above criteria match
        logging.info(f"DOI and ISBN matching record pairs: {DOI_and_ISBN_matches}")
        if DOI_and_ISBN_matches:
            for match in DOI_and_ISBN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on DOI and ISBN")
        else:
            logging.info("No matches on DOI and ISBN")


        #Section: Find Matches--DOIs and ISSNs
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on DOI and ISSNs**")
        compare_DOI_and_ISSNs = recordlinkage.Compare()
        compare_DOI_and_ISSNs.exact('DOI', 'DOI', label='DOI')
        compare_DOI_and_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_DOI_and_ISSNs.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_DOI_and_ISSNs.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results
        if normalized_resource_data:
            compare_DOI_and_ISSNs_table = compare_DOI_and_ISSNs.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_DOI_and_ISSNs_table = compare_DOI_and_ISSNs.compute(candidate_matches, new_resource_data)
        logging.debug(f"DOI and ISSNs comparison results:\n{compare_DOI_and_ISSNs_table}")

        #Subsection: Add Matches to `matched_records`
        DOI_and_ISSNs_matches = compare_DOI_and_ISSNs_table[compare_DOI_and_ISSNs_table.sum(axis='columns') == 4].index.tolist()
        logging.info(f"DOI and ISSNs matching record pairs: {DOI_and_ISSNs_matches}")
        if DOI_and_ISSNs_matches:
            for match in DOI_and_ISSNs_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on DOI and ISSNs")
        else:
            logging.info("No matches on DOI and ISSNs")


        #Section: Find Matches--ISBNs with Close Fuzzy Match on Resource Titles
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on ISBN**")
        compare_ISBN = recordlinkage.Compare()
        compare_ISBN.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        compare_ISBN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        compare_ISBN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        compare_ISBN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values
        # The various editions or volumes of a title will be grouped together by fuzzy matching, and these can sometimes be given the same ISBN even when not appropriate. To keep this from causing problems, matches where one of the resource names has a volume or edition reference will be checked manually.
        if normalized_resource_data:
            compare_ISBN_table = compare_ISBN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_ISBN_table['index_one_resource_name'] = compare_ISBN_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Resource_Name'])
        else:
            compare_ISBN_table = compare_ISBN.compute(candidate_matches, new_resource_data)
            compare_ISBN_table['index_one_resource_name'] = compare_ISBN_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Resource_Name'])
        
        compare_ISBN_table['index_zero_resource_name'] = compare_ISBN_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Resource_Name'])
        logging.debug(f"ISBN comparison result with metadata:\n{compare_ISBN_table}")

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on Regex
        ISBN_matches = compare_ISBN_table[compare_ISBN_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"ISBN matching record pairs: {ISBN_matches}")
        volume_regex = re.compile(r'\svol\.?(ume)?^\w')
        edition_regex = re.compile(r'\sed\.?(ition)?^\w')

        if ISBN_matches:
            for match in ISBN_matches:  #ALERT: Not tested--the R4 test data contains no titles meeting the criteria below 
                if compare_ISBN_table.loc[match]['index_zero_resource_name'] != compare_ISBN_table.loc[match]['index_zero_resource_name']:
                    if volume_regex.search(compare_ISBN_table.loc[match]['index_zero_resource_name']) or volume_regex.search(compare_ISBN_table.loc[match]['index_one_resource_name']) or edition_regex.search(compare_ISBN_table.loc[match]['index_zero_resource_name']) or edition_regex.search(compare_ISBN_table.loc[match]['index_one_resource_name']):
                        index_zero_metadata = (
                            new_resource_data.loc[match[0]]['Resource_Name'],
                            new_resource_data.loc[match[0]]['DOI'],
                            new_resource_data.loc[match[0]]['ISBN'],
                            new_resource_data.loc[match[0]]['Print_ISSN'],
                            new_resource_data.loc[match[0]]['Online_ISSN'],
                            new_resource_data.loc[match[0]]['Data_Type'],
                            new_resource_data.loc[match[0]]['Platform'],
                        )
                        if normalized_resource_data:
                            index_one_metadata = (
                                normalized_resource_data.loc[match[1]]['Resource_Name'],
                                normalized_resource_data.loc[match[1]]['DOI'],
                                normalized_resource_data.loc[match[1]]['ISBN'],
                                normalized_resource_data.loc[match[1]]['Print_ISSN'],
                                normalized_resource_data.loc[match[1]]['Online_ISSN'],
                                normalized_resource_data.loc[match[1]]['Data_Type'],
                                normalized_resource_data.loc[match[1]]['Platform'],
                            )
                        else:
                            index_one_metadata = (
                                new_resource_data.loc[match[1]]['Resource_Name'],
                                new_resource_data.loc[match[1]]['DOI'],
                                new_resource_data.loc[match[1]]['ISBN'],
                                new_resource_data.loc[match[1]]['Print_ISSN'],
                                new_resource_data.loc[match[1]]['Online_ISSN'],
                                new_resource_data.loc[match[1]]['Data_Type'],
                                new_resource_data.loc[match[1]]['Platform'],
                            )
                        matches_to_manually_confirm_key = (index_zero_metadata, index_one_metadata)
                        try:
                            matches_to_manually_confirm[matches_to_manually_confirm_key].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on ISBNs")
                        except:  # If the `matches_to_manually_confirm_key` isn't already in `matches_to_manually_confirm`
                            matches_to_manually_confirm[matches_to_manually_confirm_key] = set(match)
                            logging.debug(f"{match} added as a match to manually confirm on ISBNs with a new key")
                        continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
                matched_records.add(match)
                logging.debug(f"{match} added as a match on ISBNs")
        else:
            logging.info("No matches on ISBNs")


        #Section: Find Matches--ISSNs with Close Fuzzy Match on Resource Titles
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on ISSNs**")
        compare_ISSNs = recordlinkage.Compare()
        compare_ISSNs.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        compare_ISSNs.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_ISSNs.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_ISSNs.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results
        if normalized_resource_data:
            compare_ISSNs_table = compare_ISSNs.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_ISSNs_table = compare_ISSNs.compute(candidate_matches, new_resource_data)
        logging.debug(f"ISSNs comparison results:\n{compare_ISSNs_table}")

        #Subsection: Add Matches to `matched_records`
        ISSNs_matches = compare_ISSNs_table[compare_ISSNs_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"ISSNs matching record pairs: {ISSNs_matches}")
        if ISSNs_matches:
            for match in ISSNs_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on ISSNs")
        else:
            logging.info("No matches on ISSNs")


        #Section: Find Matches--Print ISSNs with Very Close Fuzzy Match on Resource Titles
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on print ISSN**")
        compare_print_ISSN = recordlinkage.Compare()
        compare_print_ISSN.string('Resource_Name', 'Resource_Name', threshold=0.95, label='Resource_Name')
        compare_print_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_print_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_print_ISSN.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_print_ISSN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results
        if normalized_resource_data:
            compare_print_ISSN_table = compare_print_ISSN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_print_ISSN_table = compare_print_ISSN.compute(candidate_matches, new_resource_data)
        logging.debug(f"Print ISSN comparison results:\n{compare_print_ISSN_table}")

        #Subsection: Add Matches to `matched_records`
        print_ISSN_matches = compare_print_ISSN_table[compare_print_ISSN_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"Print ISSN matching record pairs: {print_ISSN_matches}")
        if print_ISSN_matches:
            for match in print_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on print ISSN")
        else:
            logging.info("No matches on print ISSN")


        #Section: Find Matches--Online ISSNs with Very Close Fuzzy Match on Resource Titles
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on online ISSN**")
        compare_online_ISSN = recordlinkage.Compare()
        compare_online_ISSN.string('Resource_Name', 'Resource_Name', threshold=0.95, label='Resource_Name')
        compare_online_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_online_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_online_ISSN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        compare_online_ISSN.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results
        if normalized_resource_data:
            compare_online_ISSN_table = compare_online_ISSN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_online_ISSN_table = compare_online_ISSN.compute(candidate_matches, new_resource_data)
        logging.debug(f"Online ISSN comparison results:\n{compare_online_ISSN_table}")

        #Subsection: Add Matches to `matched_records`
        online_ISSN_matches = compare_online_ISSN_table[compare_online_ISSN_table.sum(axis='columns') == 5].index.tolist()
        logging.info(f"Online ISSN matching record pairs: {online_ISSN_matches}")
        if online_ISSN_matches:
            for match in online_ISSN_matches:
                matched_records.add(match)
                logging.debug(f"{match} added as a match on online ISSN")
        else:
            logging.info("No matches on online ISSN")
        

        #Section: Find Matches--Very Close Fuzzy Match on Resource Titles with `Database`-Type Resources
        #Subsection: Create Comparison Objects
        logging.info("**Comparing databases based on names**")
        compare_database_names = recordlinkage.Compare()
        compare_database_names.string('Resource_Name', 'Resource_Name', threshold=0.925, label='Resource_Name')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values
        if normalized_resource_data:
            compare_database_names_table = compare_database_names.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_database_names_table['index_one_data_type'] = compare_database_names_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Data_Type'])
        else:
            compare_database_names_table = compare_database_names.compute(candidate_matches, new_resource_data)
            compare_database_names_table['index_one_data_type'] = compare_database_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Data_Type'])
        
        compare_database_names_table['index_zero_data_type'] = compare_database_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Data_Type'])
        logging.debug(f"Database names comparison result with metadata:\n{compare_database_names_table}")

        #Subsection: Filter and Update Comparison Results Dataframe
        database_names_matches_table = compare_database_names_table[  # Creates dataframe with the records which meet the high name matching threshold and where both resources are databases
            (compare_database_names_table['Resource_Name'] == 1) &
            (compare_database_names_table['index_zero_data_type'] == "Database") &
            (compare_database_names_table['index_one_data_type'] == "Database")
        ]

        # Resource names are added after filtering to reduce the number of names that need to be found
        database_names_matches_table['index_zero_resource_name'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Resource_Name'])
        if normalized_resource_data:
            database_names_matches_table['index_one_resource_name'] = database_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Resource_Name'])
        else:
            database_names_matches_table['index_one_resource_name'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Resource_Name'])
        logging.debug(f"Database names matches table with metadata:\n{database_names_matches_table}")

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on String Length
        # The same Levenstein distance meets a higher threshold if the strings being compared are longer, so a manual confirmation on longer strings is required
        database_names_matches_index = database_names_matches_table.index.tolist()
        logging.info(f"Database names high matching threshold record pairs: {database_names_matches_index}")

        if database_names_matches_index:
            for match in database_names_matches_index:
                if database_names_matches_table.loc[match]['index_zero_resource_name'] != database_names_matches_table.loc[match]['index_one_resource_name']:
                    if len(database_names_matches_table.loc[match]['index_zero_resource_name']) >= 35 or len(database_names_matches_table.loc[match]['index_one_resource_name']) >= 35:
                        index_zero_metadata = (
                            new_resource_data.loc[match[0]]['Resource_Name'],
                            new_resource_data.loc[match[0]]['DOI'],
                            new_resource_data.loc[match[0]]['ISBN'],
                            new_resource_data.loc[match[0]]['Print_ISSN'],
                            new_resource_data.loc[match[0]]['Online_ISSN'],
                            new_resource_data.loc[match[0]]['Data_Type'],
                            new_resource_data.loc[match[0]]['Platform'],
                        )
                        if normalized_resource_data:
                            index_one_metadata = (
                                normalized_resource_data.loc[match[1]]['Resource_Name'],
                                normalized_resource_data.loc[match[1]]['DOI'],
                                normalized_resource_data.loc[match[1]]['ISBN'],
                                normalized_resource_data.loc[match[1]]['Print_ISSN'],
                                normalized_resource_data.loc[match[1]]['Online_ISSN'],
                                normalized_resource_data.loc[match[1]]['Data_Type'],
                                normalized_resource_data.loc[match[1]]['Platform'],
                            )
                        else:
                            index_one_metadata = (
                                new_resource_data.loc[match[1]]['Resource_Name'],
                                new_resource_data.loc[match[1]]['DOI'],
                                new_resource_data.loc[match[1]]['ISBN'],
                                new_resource_data.loc[match[1]]['Print_ISSN'],
                                new_resource_data.loc[match[1]]['Online_ISSN'],
                                new_resource_data.loc[match[1]]['Data_Type'],
                                new_resource_data.loc[match[1]]['Platform'],
                            )
                        matches_to_manually_confirm_key = (index_zero_metadata, index_one_metadata)
                        try:
                            matches_to_manually_confirm[matches_to_manually_confirm_key].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold")
                        except:  # If the `matches_to_manually_confirm_key` isn't already in `matches_to_manually_confirm`
                            matches_to_manually_confirm[matches_to_manually_confirm_key] = set(match)
                            logging.debug(f"{match} added as a match to manually confirm on database names with a high matching threshold with a new key")
                        continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
                matched_records.add(match)
                logging.debug(f"{match} added as a match on database names with a high matching threshold")
        else:
            logging.info("No matches on database names with a high matching threshold")
        

        #Section: Find Matches--Very Close Fuzzy Match on Platform Name with `Platform`-Type Resources
        #Subsection: Create Comparison Objects
        logging.info("**Comparing platforms based on names**")
        compare_platform_names = recordlinkage.Compare()
        compare_platform_names.string('Platform', 'Platform', threshold=0.925, label='Platform')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values
        if normalized_resource_data:
            compare_platform_names_table = compare_platform_names.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_platform_names_table['index_one_data_type'] = compare_platform_names_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Data_Type'])
        else:
            compare_platform_names_table = compare_platform_names.compute(candidate_matches, new_resource_data)
            compare_platform_names_table['index_one_data_type'] = compare_platform_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Data_Type'])
        
        compare_platform_names_table['index_zero_data_type'] = compare_platform_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Data_Type'])
        logging.debug(f"Platform names comparison result with metadata:\n{compare_platform_names_table}")

        #Subsection: Filter Comparison Results Dataframe
        platform_names_matches_table = compare_platform_names_table[  # Creates dataframe with the records which meet the high name matching threshold and where both resources are platforms
            (compare_platform_names_table['Platform'] == 1) &
            (compare_platform_names_table['index_zero_data_type'] == "Platform") &
            (compare_platform_names_table['index_one_data_type'] == "Platform")
        ]

        # Platform names are added after filtering to reduce the number of names that need to be found
        platform_names_matches_table['index_zero_platform_name'] = platform_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Platform'])
        if normalized_resource_data:
            platform_names_matches_table['index_one_platform_name'] = platform_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Platform'])
        else:
            platform_names_matches_table['index_one_platform_name'] = platform_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Platform'])
        logging.debug(f"Platform names matches table with metadata:\n{platform_names_matches_table}")

        #Subsection: Add Matches to `matched_records` or `matches_to_manually_confirm` Based on String Length
        # The same Levenstein distance meets a higher threshold if the strings being compared are longer, so a manual confirmation on longer strings is required
        platform_names_matches_index = platform_names_matches_table.index.tolist()
        logging.info(f"Platform names high matching threshold record pairs: {platform_names_matches_index}")

        if platform_names_matches_index:
            for match in platform_names_matches_index:
                if platform_names_matches_table.loc[match]['index_zero_platform_name'] != platform_names_matches_table.loc[match]['index_one_platform_name']:
                    if len(platform_names_matches_table.loc[match]['index_zero_platform_name']) >= 35 or len(platform_names_matches_table.loc[match]['index_one_platform_name']) >= 35:
                        index_zero_metadata = (
                            new_resource_data.loc[match[0]]['Resource_Name'],
                            new_resource_data.loc[match[0]]['DOI'],
                            new_resource_data.loc[match[0]]['ISBN'],
                            new_resource_data.loc[match[0]]['Print_ISSN'],
                            new_resource_data.loc[match[0]]['Online_ISSN'],
                            new_resource_data.loc[match[0]]['Data_Type'],
                            new_resource_data.loc[match[0]]['Platform'],
                        )
                        if normalized_resource_data:
                            index_one_metadata = (
                                normalized_resource_data.loc[match[1]]['Resource_Name'],
                                normalized_resource_data.loc[match[1]]['DOI'],
                                normalized_resource_data.loc[match[1]]['ISBN'],
                                normalized_resource_data.loc[match[1]]['Print_ISSN'],
                                normalized_resource_data.loc[match[1]]['Online_ISSN'],
                                normalized_resource_data.loc[match[1]]['Data_Type'],
                                normalized_resource_data.loc[match[1]]['Platform'],
                            )
                        else:
                            index_one_metadata = (
                                new_resource_data.loc[match[1]]['Resource_Name'],
                                new_resource_data.loc[match[1]]['DOI'],
                                new_resource_data.loc[match[1]]['ISBN'],
                                new_resource_data.loc[match[1]]['Print_ISSN'],
                                new_resource_data.loc[match[1]]['Online_ISSN'],
                                new_resource_data.loc[match[1]]['Data_Type'],
                                new_resource_data.loc[match[1]]['Platform'],
                            )
                        matches_to_manually_confirm_key = (index_zero_metadata, index_one_metadata)
                        try:
                            matches_to_manually_confirm[matches_to_manually_confirm_key].add(match)
                            logging.debug(f"{match} added as a match to manually confirm on platform names with a high matching threshold")
                        except:  # If the `matches_to_manually_confirm_key` isn't already in `matches_to_manually_confirm`
                            matches_to_manually_confirm[matches_to_manually_confirm_key] = set(match)
                            logging.debug(f"{match} added as a match to manually confirm on platform names with a high matching threshold with a new key")
                        continue  # This restarts the loop if the above steps were taken; in contrast, if one of the above if statements evaluated to false, the loop would've gone directly to the step below
                matched_records.add(match)
                logging.debug(f"{match} added as a match on platform names with a high matching threshold")
        else:
            logging.info("No matches on platform names with a high matching threshold")


        #Section: Find Matches--Single Standard Identifier Field for All Non-`Platform`-Type Resources
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on single matching identifier**")
        compare_identifiers = recordlinkage.Compare()
        """
        compare_names_and_partials.exact('DOI', 'DOI', label='DOI')
        compare_names_and_partials.exact('ISBN', 'ISBN', label='ISBN')
        compare_names_and_partials.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_names_and_partials.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')
        """

        #Subsection: Return Dataframe with Comparison Results
        """
        if normalized_resource_data:
            compare_names_and_partials_table = compare_names_and_partials.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
        else:
            compare_names_and_partials_table = compare_names_and_partials.compute(candidate_matches, new_resource_data)
        logging.debug(f"Fuzzy matching comparison results (before FuzzyWuzzy):\n{compare_names_and_partials_table}")
        """

        #Subsection: Filter Comparison Results Dataframe
        """
        compare_names_and_partials_matches_table = compare_names_and_partials_table[
            (compare_names_and_partials_table['DOI'] == 1) |
            (compare_names_and_partials_table['ISBN'] == 1) |
            (compare_names_and_partials_table['Print_ISSN'] == 1) |
            (compare_names_and_partials_table['Online_ISSN'] == 1) |
        ]
        """

        #Subsection: Remove Matches Already in `matched_records` and `matches_to_manually_confirm`
        """
        fuzzy_match_record_pairs = []
        #ToDo: List and tuple with same data NOT equal, but list wrapped in tuple constructor is
        for potential_match in compare_names_and_partials_matches_table.index.tolist():
            if potential_match not in matched_records:
                if potential_match not in list(matches_to_manually_confirm.keys()): #ToDo: Is this iterating through the list of tuples?
                    fuzzy_match_record_pairs.append(potential_match)
        """

        #Subsection: Add Matches to `matches_to_manually_confirm`
        #ToDo: For the comparison `compare_something`
        #ToDo: something_matches_index = something_matches_table.index.tolist()
        logging.info(f"Single identifier matching record pairs: {something_matches_index}")
        #ToDo: if something_matches_index:
            #ToDo: for match in something_matches_index:
                #ToDo: index_zero_metadata = (
                    '''new_resource_data.loc[match[0]]['Resource_Name'],
                    new_resource_data.loc[match[0]]['DOI'],
                    new_resource_data.loc[match[0]]['ISBN'],
                    new_resource_data.loc[match[0]]['Print_ISSN'],
                    new_resource_data.loc[match[0]]['Online_ISSN'],
                    new_resource_data.loc[match[0]]['Data_Type'],
                    new_resource_data.loc[match[0]]['Platform'],
                )'''
                #ToDo: if normalized_resource_data:
                    '''index_one_metadata = (
                        normalized_resource_data.loc[match[1]]['Resource_Name'],
                        normalized_resource_data.loc[match[1]]['DOI'],
                        normalized_resource_data.loc[match[1]]['ISBN'],
                        normalized_resource_data.loc[match[1]]['Print_ISSN'],
                        normalized_resource_data.loc[match[1]]['Online_ISSN'],
                        normalized_resource_data.loc[match[1]]['Data_Type'],
                        normalized_resource_data.loc[match[1]]['Platform'],
                    )
                else:
                    index_one_metadata = (
                        new_resource_data.loc[match[1]]['Resource_Name'],
                        new_resource_data.loc[match[1]]['DOI'],
                        new_resource_data.loc[match[1]]['ISBN'],
                        new_resource_data.loc[match[1]]['Print_ISSN'],
                        new_resource_data.loc[match[1]]['Online_ISSN'],
                        new_resource_data.loc[match[1]]['Data_Type'],
                        new_resource_data.loc[match[1]]['Platform'],
                    )
                matches_to_manually_confirm_key = (index_zero_metadata, index_one_metadata)'''
                #ToDo: try:
                    #ToDo: matches_to_manually_confirm[matches_to_manually_confirm_key].append(match)
                    logging.debug(f"{match} added as a match to manually confirm on a single identifier")
                #ToDo: except:  # If the `matches_to_manually_confirm_key` isn't already in `matches_to_manually_confirm`
                    #ToDo: matches_to_manually_confirm[matches_to_manually_confirm_key] = [match]
                    logging.debug(f"{match} added as a match to manually confirm on a single identifier with a new key")
        #ToDo: else:
            #ToDo: logging.info("No matches on single identifiers")


        #Section: Find Matches--Loose Fuzzy Match on Resource Name
        #Subsection: Create Comparison Objects
        logging.info("**Comparing based on fuzzy resource name matching**")
        compare_resource_name = recordlinkage.Compare()
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.65, label='levenshtein')
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.70, method='jaro', label='jaro')  #ToDo: From jellyfish: `DeprecationWarning: the jaro_distance function incorrectly returns the jaro similarity, replace your usage with jaro_similarity before 1.0`
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.70, method='jarowinkler', label='jarowinkler')  #ToDo: From jellyfish: `DeprecationWarning: the name 'jaro_winkler' is deprecated and will be removed in jellyfish 1.0, for the same functionality please use jaro_winkler_similarity`
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.75, method='lcs', label='lcs')
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.70, method='smith_waterman', label='smith_waterman')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values
        if normalized_resource_data:
            compare_resource_name_table = compare_resource_name.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_resource_name_table['index_one_resource_name'] = compare_resource_name_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Resource_Name'])
        else:
            compare_resource_name_table = compare_resource_name.compute(candidate_matches, new_resource_data)
            compare_resource_name_table['index_one_resource_name'] = compare_resource_name_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Resource_Name'])
        
        compare_resource_name_table['index_zero_resource_name'] = compare_resource_name_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Resource_Name'])
        logging.debug(f"Fuzzy matching comparison results (before FuzzyWuzzy):\n{compare_resource_name_table}")

        #Subsection: Filter and Update Comparison Results Dataframe for FuzzyWuzzy
        #ALERT: See note in tests.test_RawCOUNTERReport about memory
        # FuzzyWuzzy throws an error when a null value is included in the comparison, and platform records have a null value for the resource name; for FuzzyWuzzy to work, the comparison table records with platforms need to be removed, which can be done by targeting the records with null values in one of the name fields
        compare_resource_name_table.dropna(
            axis='index',
            subset=['index_zero_resource_name', 'index_one_resource_name'],
            inplace=True,
        )
        logging.debug(f"Fuzzy matching comparison results (filtered in preparation for FuzzyWuzzy):\n{compare_resource_name_table}")

        compare_resource_name_table['partial_ratio'] = compare_resource_name_table.apply(lambda record: fuzz.partial_ratio(record['index_zero_name'], record['index_one_name']), axis='columns')
        compare_resource_name_table['token_sort_ratio'] = compare_resource_name_table.apply(lambda record: fuzz.token_sort_ratio(record['index_zero_name'], record['index_one_name']), axis='columns')
        compare_resource_name_table['token_set_ratio'] = compare_resource_name_table.apply(lambda record: fuzz.token_set_ratio(record['index_zero_name'], record['index_one_name']), axis='columns')
        logging.debug(f"Fuzzy matching comparison results:\n{compare_resource_name_table}")
        
        #Subsection: Filter Comparison Results Dataframe
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

        #Subsection: Remove Matches Already in `matched_records` and `matches_to_manually_confirm`
        """
        fuzzy_match_record_pairs = []
        #ToDo: List and tuple with same data NOT equal, but list wrapped in tuple constructor is
        for potential_match in compare_names_and_partials_matches_table.index.tolist():
            if potential_match not in matched_records:
                if potential_match not in list(matches_to_manually_confirm.keys()): #ToDo: Is this iterating through the list of tuples?
                    fuzzy_match_record_pairs.append(potential_match)
        """

        #Subsection: Add Matches to `matches_to_manually_confirm`
        #ToDo: For the comparison `compare_something`
        #ToDo: something_matches_index = something_matches_table.index.tolist()
        logging.info(f"Resource names with a low matching threshold matching record pairs: {something_matches_index}")
        #ToDo: if something_matches_index:
            #ToDo: for match in something_matches_index:
                #ToDo: index_zero_metadata = (
                    '''new_resource_data.loc[match[0]]['Resource_Name'],
                    new_resource_data.loc[match[0]]['DOI'],
                    new_resource_data.loc[match[0]]['ISBN'],
                    new_resource_data.loc[match[0]]['Print_ISSN'],
                    new_resource_data.loc[match[0]]['Online_ISSN'],
                    new_resource_data.loc[match[0]]['Data_Type'],
                    new_resource_data.loc[match[0]]['Platform'],
                )'''
                #ToDo: if normalized_resource_data:
                    '''index_one_metadata = (
                        normalized_resource_data.loc[match[1]]['Resource_Name'],
                        normalized_resource_data.loc[match[1]]['DOI'],
                        normalized_resource_data.loc[match[1]]['ISBN'],
                        normalized_resource_data.loc[match[1]]['Print_ISSN'],
                        normalized_resource_data.loc[match[1]]['Online_ISSN'],
                        normalized_resource_data.loc[match[1]]['Data_Type'],
                        normalized_resource_data.loc[match[1]]['Platform'],
                    )
                else:
                    index_one_metadata = (
                        new_resource_data.loc[match[1]]['Resource_Name'],
                        new_resource_data.loc[match[1]]['DOI'],
                        new_resource_data.loc[match[1]]['ISBN'],
                        new_resource_data.loc[match[1]]['Print_ISSN'],
                        new_resource_data.loc[match[1]]['Online_ISSN'],
                        new_resource_data.loc[match[1]]['Data_Type'],
                        new_resource_data.loc[match[1]]['Platform'],
                    )
                matches_to_manually_confirm_key = (index_zero_metadata, index_one_metadata)'''
                #ToDo: try:
                    #ToDo: matches_to_manually_confirm[matches_to_manually_confirm_key].append(match)
                    logging.debug(f"{match} added as a match to manually confirm on resource names with a low matching threshold")
                #ToDo: except:  # If the `matches_to_manually_confirm_key` isn't already in `matches_to_manually_confirm`
                    #ToDo: matches_to_manually_confirm[matches_to_manually_confirm_key] = [match]
                    logging.debug(f"{match} added as a match to manually confirm on resource names with a low matching threshold with a new key")
        #ToDo: else:
            logging.info("No matches on resource names with a high matching threshold")


        """
        #Section: Return Record Index Pair Lists
        return (
            matched_records,
            matches_to_manually_confirm,
        )
        """
    

    def load_data_into_database():
        """Add the COUNTER report to the database by adding records to the resource, resourceMetadata, resourcePlatforms, and usageData relations."""
        #ToDo: Write a more detailed docstring
        #ToDo: Filter out non-standard metrics
        pass
