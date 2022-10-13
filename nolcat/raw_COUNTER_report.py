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
    
    This class effectively extends the pandas dataframe class by adding methods for working with COUNTER reports. The constructor method accepts COUNTER data--as a download of multiple Excel workbooks for R4 and as an API call response (or possibly Excel workbooks) for R5--and changes it into a normalized dataframe. The methods facilitate the deduplication and division of the data into the appropriate relations.
    
    Attributes:
        self.report_dataframe (dataframe): the raw COUNTER report as a pandas dataframe
    
    Methods:
        create_normalized_resource_data_argument: Creates a dataframe with a record for each resource containing the default metadata values from resourceMetadata, the resourcePlatforms.platform value, and the usageData.data_type value.
        perform_deduplication_matching: Matches the line items in a COUNTER report for the same resource.
        load_data_into_database: Add the COUNTER report to the database by adding records to the `resource`, `resourceMetadata`, `resourcePlatforms`, and `usageData` relations.
    
    Note:
        In all methods, the dataframe appears in the parameters list as `self`, but to use pandas functionality, it must be referenced as `self.report_dataframe`.
    """
    # Constructor Method
    def __init__(self, df):
        """Creates a RawCOUNTERReport object, a dataframe with extra methods, from some external COUNTER data.
        
        Creates a RawCOUNTERReport object from (1) Excel workbooks using the naming convention `<Statistics_Source_ID>_<calendar year assigned to fiscal year in "yyyy" format>.xlsx` containing tabs named for the COUNTER report they contain or (2) a R5 SUSHI API response from the `FiscalYears.collect_fiscal_year_usage_statistics()`, `StatisticsSources.collect_usage_statistics()`, or `AnnualUsageCollectionTracking.collect_annual_usage_statistics()` methods.
        """
        if repr(type(df)) == "<class 'werkzeug.datastructures.ImmutableMultiDict'>":  #ToDo: Confirm this is the class returned by a Flask-WTF `MultipleFileField` object
            # For Excel file(s) uploaded through Flask
            dataframes_to_concatenate = []
            valid_COUNTER_report_names = [  # This is the order of the sheets in the test data
                "JR1",
                "JR2",
                "JR3",
                "DB1",
                "DB2",
                "PR1",
                "BR1",
                "BR2",
                "BR3",
                "BR5",
                "MR1",
                "TR1",
                "TR2",
                "TR3",
                "PR",
                "DR",
                "TR",
                "IR",
            ]
            #ToDo: for workbook in ImmutableMultiDict (previously represented by `df.getlist('R4_files')`):

                #Section: Load Workbook and Sheets with Naming Convention Confirmation
                #Subsection: Confirm Workbook Naming Convention
                try:
                    statistics_source_ID = re.findall(r'(\d*)_\d{4}.xlsx', string=Path(workbook.filename).parts[-1])[0]
                    logging.info(f"Adding statisticsSources PK {statistics_source_ID} to {Path(workbook.filename).parts[-1]}")
                except:
                    logging.error(f"The name of the file {Path(workbook.filename).parts[-1]} doesn't follow the naming convention, so a statisticsSources PK can't be derived from it. Please rename this file and try again.")
                    #ToDo: Return an error with a message like the above
                    #ToDo: continue

                #Subsection: Load Workbook
                #ToDo: file_path = the path to workbook
                #ToDo: loaded_workbook = load_workbook(filename=file_path, read_only=True)
                #ToDo: 

                #Subsection: Confirm Worksheet Naming Convention
                #ToDo: for sheet in workbook: (the iterator may not take this structure; `file.active` gets the sheet for a one-sheet workbook):
                    #ToDo: try:
                        #ToDo: report_type = sheet name if in valid_COUNTER_report_names
                        #toDo: logging.info(f"Adding report {report_type} to statisticsSources {statistics_source_ID}")
                    #ToDo: except:
                        #ToDo: logging.error(f"The name of the sheet {method for pulling sheet name} doesn't follow the naming convention, so data can't be derived from it. Please rename this sheet and try again.")
                        #ToDo: Return an error with a message like the above
                        #ToDo: continue
                    

                    #Section: Find and Save Field Names
                    #Subsection: Identify the Header Row
                    # COUNTER R4 standard has header row as 8, but this isn't always followed
                    '''
                    looking_for_header_row = True
                    header_row_number = 1

                    while looking_for_header_row:
                        count_of_month_labels = 0
                        for cell in sheet[header_row_number]:
                            if cell.value is None:
                                continue  # `None` causes a `TypeError` in `re.fullmatch`, so it needs to be weeded out here
                            elif repr(type(cell.value)) == "<class 'datetime.datetime'>" or re.fullmatch(r'[A-Z][a-z]{2}\-\d{4}', cell.value) is not None:
                                count_of_month_labels += 1
                        if count_of_month_labels == 12:
                            number_of_fields = len(sheet[header_row_number])
                            looking_for_header_row = False
                            break
                        else:
                            header_row_number += 1
                    '''

                    #Subsection: Get the Field Names
                    '''
                    df_field_names = []
                    df_date_field_names = []
                    for list_of_field_names in sheet.iter_rows(
                        min_row=header_row_number,
                        max_row=header_row_number,
                        min_col=1,
                        max_col=number_of_fields,
                        values_only=True,
                    ):  # Creates a tuple with the field names as elements
                        for field_name in list_of_field_names:
                            #print(f"Field {field_name} (type {type(field_name)})")
                            try:
                                date_as_string = re.findall(r'([A-Z][a-z]{2})\-(\d{4})', string=field_name)  # `None` in `findall` raises an error, so it needs to be in a `try-except` block
                            except:
                                date_as_string = False
                            
                            if field_name == "ISSN" and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5'):
                                df_field_names.append("Online_ISSN")  # This is the first name replacement because assigning a certain type of ISSN changes the meaning slightly
                            
                            elif date_as_string:
                                date_tuple = date_as_string[0]
                                if date_tuple[0] == "Jan":
                                    month_int = 1
                                elif date_tuple[0] == "Feb":
                                    month_int = 2
                                elif date_tuple[0] == "Mar":
                                    month_int = 3
                                elif date_tuple[0] == "Apr":
                                    month_int = 4
                                elif date_tuple[0] == "May":
                                    month_int = 5
                                elif date_tuple[0] == "Jun":
                                    month_int = 6
                                elif date_tuple[0] == "Jul":
                                    month_int = 7
                                elif date_tuple[0] == "Aug":
                                    month_int = 8
                                elif date_tuple[0] == "Sep":
                                    month_int = 9
                                elif date_tuple[0] == "Oct":
                                    month_int = 10
                                elif date_tuple[0] == "Nov":
                                    month_int = 11
                                elif date_tuple[0] == "Dec":
                                    month_int = 12
                                df_field_names.append(datetime.date(int(date_tuple[1]), month_int, 1))
                                df_date_field_names.append(datetime.date(int(date_tuple[1]), month_int, 1))
                            elif repr(type(field_name)) == "<class 'datetime.datetime'>":
                                df_field_names.append(datetime.date(field_name.year, field_name.month, 1))  # This both ensures the date is the first of the month and removes the unneeded time data
                                df_date_field_names.append(datetime.date(field_name.year, field_name.month, 1))
                            
                            elif field_name is None and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5'):
                                df_field_names.append("Resource_Name")
                            elif field_name == "Collection" and report_type == 'MR1':
                                df_field_names.append("Resource_Name")
                            elif field_name == "Database" and (report_type == 'DB1' or report_type == 'DB2'):
                                df_field_names.append("Resource_Name")
                            elif field_name == "Item" and report_type == 'IR':
                                df_field_names.append("Resource_Name")
                            elif field_name == "Journal" and (report_type == 'JR1' or report_type == 'JR2'):
                                df_field_names.append("Resource_Name")
                            elif field_name == "Title" and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5' or report_type == 'TR1' or report_type == 'TR2'):
                                df_field_names.append("Resource_Name")
                            
                            elif field_name == "Content Provider" and report_type == 'MR1':
                                df_field_names.append("Publisher")
                            elif field_name == "User Activity" and (report_type == 'BR5' or report_type == 'DB1'or report_type == 'PR1'):
                                df_field_names.append("Metric_Type")
                            elif (field_name == "Access Denied Category" or field_name == "Access denied category") and (report_type == 'BR3' or report_type == 'DB2'or report_type == 'JR2'):
                                df_field_names.append("Metric_Type")
                            
                            # These changes are for bringing R4 reports in line with R5 naming conventions, so they don't need to be limited to certain reports
                            elif field_name == "Proprietary Identifier":
                                df_field_names.append("Proprietary_ID")
                            elif field_name == "Book DOI" or field_name == "Journal DOI" or field_name == "Title DOI":
                                df_field_names.append("DOI")
                            elif field_name == "Data type" or field_name == "Data Type":
                                df_field_names.append("Data_Type")
                            elif field_name == "Online ISSN":
                                df_field_names.append("Online_ISSN")
                            elif field_name == "Print ISSN":
                                df_field_names.append("Print_ISSN")

                            else:
                                df_field_names.append(field_name)
                    df_non_date_field_names = [field_name for field_name in df_field_names if field_name not in df_date_field_names]  # List comprehension used to preserve order
                    '''


                    #Section: Create Dataframe
                    '''
                    df = pd.read_excel(
                        file_path,
                        engine='openpyxl',
                        header=header_row_number-1,  # This gives the row number with the headings in Excel, which is also the row above where the data starts
                        names=df_field_names,
                        dtype=df_dtypes,
                    )
                    print(f"Dataframe immediately after creation:\n{df}\n")
                    #print(df.info())
                    '''


                    #Section: Make Pre-Stacking Updates
                    #ToDo: dataframe['Statistics_Source_ID'] = statistics_source_ID
                    '''
                    df = df.replace(r'\n', '', regex=True)  # Removes errant newlines found in some reports, primarily at the end of resource names
                    df = df.replace("licence", "license")  # "Have `license` always use American English spelling
                    '''
                    #ToDo: try:  # From https://stackoverflow.com/a/42285489
                        #ToDo: dataframe['Usage_Date'] = dataframe['Usage_Date'].astype('datetime64[M]')
                    #ToDo: except:  # Handles if for some reason `parse_dates` doesn't turn 'Usage_Date' into datetime64[ns]
                        #ToDo: dataframe['Usage_Date'] = pd.to_datetime(dataframe['Usage_Date'].astype('datetime64[M]'))

                    #Subsection: Remove `Reporting Period` Field
                    '''
                    df_field_names_sans_reporting_period_fields = [field_name for field_name in df_non_date_field_names if not re.search(r'[Rr]eporting\s[Pp]eriod', field_name)]
                    reporting_period_field_names = [field_name for field_name in df_non_date_field_names if field_name not in df_field_names_sans_reporting_period_fields]  # List comprehension used to preserve list order
                    df = df.drop(columns=reporting_period_field_names)
                    df_field_names = df_field_names_sans_reporting_period_fields + df_date_field_names
                    print(f"`df_field_names` with reporting period removed: {df_field_names}")
                    '''


                    #Subsection: Remove Total Rows
                    '''
                    common_summary_rows = df['Resource_Name'].str.contains(r'^[Tt]otal\s[Ff]or\s[Aa]ll\s[Tt]itles', regex=True)
                    uncommon_summary_rows = df['Resource_Name'].str.contains(r'^[Tt]otal\s[Ss]earches', regex=True)
                    summary_rows_are_false = ~(common_summary_rows + uncommon_summary_rows)
                    df = df[summary_rows_are_false]
                    '''

                    #Subsection: Put Placeholder in for Null Values
                    '''
                    df = df.fillna("`None`")
                    df = df.replace(
                        to_replace='^\s*$',  # The anchors ensure this is only applied to whitespace-only cells; without them, this is applied to all spaces, even the ones between letters
                        value="`None`",
                        regex=True
                    )
                    '''

                    #Subsection: Split ISBNs and ISSNs in TR
                    """
                        "description": "Create column ``Print_ISSN`` by taking the ISSNs from column ``Print ID``"
                        "description": "Create column ``Online_ISSN`` by taking the ISSNs from column ``Online ID``"
                        "description": "Create column ``ISBN`` with the values from ``Print ID`` and ``Online ID`` not in an ISSN column"
                        "description": "Remove column ``Print ID``"
                        "description": "Remove column ``Online ID``"

                        {
                            "op": "core/column-addition",
                            "engineConfig": {
                                "facets": [],
                                "mode": "row-based"
                            },
                            "baseColumnName": "Print ID",
                            "expression": "grel:value.match(/(\\d{4}\\-\\d{3}[\\dxX])/)[0]",
                            "onError": "set-to-blank",
                            "newColumnName": "Print_ISSN",
                            "columnInsertIndex": 6,
                            "description": "Create column ``Print_ISSN`` by taking the ISSNs from column ``Print ID``"
                        },
                        {
                            "op": "core/column-addition",
                            "engineConfig": {
                                "facets": [],
                                "mode": "row-based"
                            },
                            "baseColumnName": "Online ID",
                            "expression": "grel:value.match(/(\\d{4}\\-\\d{3}[\\dxX])/)[0]",
                            "onError": "set-to-blank",
                            "newColumnName": "Online_ISSN",
                            "columnInsertIndex": 6,
                            "description": "Create column ``Online_ISSN`` by taking the ISSNs from column ``Online ID``"
                        },
                        {
                            "op": "core/column-addition",
                            "engineConfig": {
                                "facets": [],
                                "mode": "row-based"
                            },
                            "baseColumnName": "Print ID",
                            "expression": "grel:if(and(isBlank(cells.Print_ISSN.value), isBlank(cells.Online_ISSN.value)), if(isBlank(value), if(isBlank(cells[\"Online ID\"].value),null,cells[\"Online ID\"].value),value),null)",
                            "onError": "set-to-blank",
                            "newColumnName": "ISBN",
                            "columnInsertIndex": 6,
                            "description": "Create column ``ISBN`` with the values from ``Print ID`` and ``Online ID`` not in an ISSN column"
                        },
                        {
                    """
                    #ToDo: print(f"Dataframe with pre-stacking changes:\n{df}\n")


                    #Section: Stack Dataframe
                    #Subsection: Create Temp Index Field with All Metadata Values
                    '''
                    df_non_date_field_names = [field_name for field_name in df_field_names if field_name not in df_date_field_names]  # Reassigning this variable with the same statement because one of the values in the statement has changed
                    list_of_field_names_from_df = df.columns.values.tolist()
                    boolean_identifying_metadata_fields = [True if field_name in df_non_date_field_names else False for field_name in list_of_field_names_from_df]
                    df['temp_index'] = df[df.columns[boolean_identifying_metadata_fields]].apply(
                        lambda cell_value: '~'.join(cell_value.astype(str)),  # Combines all values in the fields specified by the index operator of the dataframe to which the `apply` method is applied; `~` is used as the delimiter because pandas 1.3 doesn't seem to handle multi-character literal string delimiters
                        axis='columns'
                    )
                    df = df.drop(columns=df_non_date_field_names)
                    print(f"Dataframe with without metadata columns:\n{df}\n")
                    df = df.set_index('temp_index')
                    print(f"Dataframe with new index column:\n{df}\n")
                    '''

                    #Subsection: Reshape with Stacking
                    '''
                    df = df.stack()  # This creates a series with a multiindex: the multiindex is the metadata, then the dates; the data is the usage counts
                    print(f"Dataframe immediately after stacking:\n{df}\n")
                    df = df.reset_index()
                    df = df.rename(columns={
                        'level_1': 'Usage_Date',
                        0: 'Usage_Count',
                    })
                    print(f"Dataframe with reset index:\n{df}\n")
                    '''

                    #Subsection: Recreate Metadata Fields
                    '''
                    df[df_non_date_field_names] = df['temp_index'].str.split(pat="~", expand=True)  # This splits the metadata values in the index, which are separated by `~`, into their own fields and applies the appropriate names to those fields
                    df = df.drop(columns='temp_index')
                    print(f"Fully transposed dataframe:\n{df}\n")
                    '''


                    #Section: Adjust Data in Dataframe
                    #Subsection: Remove Rows with No Usage
                    '''
                    df = df[df['Usage_Count'] != 0]
                    df = df.reset_index(drop=True)
                    '''

                    #Subsection: Replace Null Placeholder with Null Values
                    '''
                    df = df.replace(["`None`"], [None])  # Values must be enclosed in lists for method to work
                    '''

                    #Subsection: Correct Data Types
                    '''
                    non_string_fields = ["index", "Usage_Date", "Usage_Count"]  # Unable to combine not equal to clauses in list comprehension below
                    fields_to_convert_to_string_dtype = [field_name for field_name in df.columns.values.tolist() if field_name not in non_string_fields]
                    string_dtype_conversion_dict = {'Usage_Count': 'int'}
                    for field_name in fields_to_convert_to_string_dtype:
                        string_dtype_conversion_dict[field_name] = 'string'
                    df = df.astype(string_dtype_conversion_dict)

                    df['Usage_Date'] = pd.to_datetime(df['Usage_Date'])
                    print(f"Dataframe with updated data and its dtypes:\n{df}\n{df.dtypes}\n")
                    '''

                    #Subsection: Set Dates to the First of the Month
                    #ToDo: Set all dates to first of month (https://stackoverflow.com/questions/42285130/how-floor-a-date-to-the-first-date-of-that-month)
                    
                    #Subsection: Add Fields Missing from R4 Reports
                    '''
                    if report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5':
                        df['Data_Type'] = "Book"
                    elif report_type == 'DB1' or report_type == 'DB2':
                        df['Data_Type'] = "Database"
                    elif report_type == 'JR1' or report_type == 'JR2':
                        df['Data_Type'] = "Journal"
                    elif report_type == 'MR1':
                        df['Data_Type'] = "Multimedia"
                    elif report_type == 'PR1':
                        df['Data_Type'] = "Platform"

                    if report_type == 'BR1' or report_type == 'BR3' or report_type == 'BR5':
                        df['Section_Type'] = "Book"
                    elif report_type =='BR2':
                        df['Section_Type'] = "Book_Segment"
                    elif report_type == 'JR1' or report_type == 'JR2':
                        df['Section_Type'] = "Article"
                    """TR1, TR2
                    {
                            "op": "core/column-addition",
                            "engineConfig": {
                                "facets": [],
                                "mode": "row-based"
                            },
                            "baseColumnName": "Data_Type",
                            "expression": "grel:if(value==\"Journal\",\"Article\",if(value==\"Book\",\"Chapter\",\"Other\"))",
                            "onError": "set-to-blank",
                            "newColumnName": "Section_Type",
                            "columnInsertIndex": 9,
                            "description": "Create column ``Section_Type`` with the value `Article`, `Chapter`, or `Other` depending on the value in ``Data_Type``"
                    },
                    """

                    if report_type =='BR1' or report_type == 'TR1':
                        df['Metric_Type'] = "Successful Title Requests"
                    elif report_type =='BR2':
                        df['Metric_Type'] = "Successful Section Requests"
                    elif report_type =='JR1':
                        df['Metric_Type'] = "Successful Full-text Article Requests"
                    elif report_type =='MR1':
                        df['Metric_Type'] = "Successful Content Unit Requests"
                    '''

                    #Section: Add Dataframe to Concatenation List
                    #ToDo: dataframes_to_concatenate.append(dataframe)
            
            
            #ToDo: self.report_dataframe = pd.concat(
            #ToDo:     dataframes_to_concatenate,
            #ToDo:     ignore_index=True
            #ToDo: )
            
            #ToDo: logging.info(f"Final dataframe:\n{self.report_dataframe}")
                    

        elif repr(type(df)) == "<class 'pandas.core.frame.DataFrame'>":  # `StatisticsSources._harvest_R5_SUSHI()`, the method that invokes the `SUSHICallAndResponse` class, returns a dataframe
            #ToDo: self.report_dataframe = df
        else:
            pass  #ToDo: Return an error message and quit the constructor


    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        return repr(self.report_dataframe.head())
    

    def equals(self, other):
        """Recreates the pandas `equals` method with RawCOUNTERReport objects."""
        return self.report_dataframe.equals(other.report_dataframe)
    

    def create_normalized_resource_data_argument(self):
        """Creates a dataframe with a record for each resource containing the default metadata values from `resourceMetadata`, the `resourcePlatforms.platform` value, and the `usageData.data_type` value.

        The structure of the database doesn't readily allow for the comparison of metadata elements among different resources. This function creates the dataframe enabling comparisons: all the resource IDs are collected, and for each resource, the data required for deduplication is pulled from the database and assigned to the appropriate fields. 

        Returns:
            dataframe: a dataframe with all `resources.resource_ID` values along with their default metadata, platform names, and data types
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
        # The recordlinkage `missing_value` argument doesn't recognize pd.NA, the null value for strings in dataframes, as a missing value, so those values need to be replaced with `None`. Performing this swap changes the data type of all the field back to pandas' generic `object`, but since recordlinkage can do string comparisons on strings of the object data type, this change doesn't cause problems with the program's functionality.
        new_resource_data = new_resource_data.applymap(lambda cell_value: None if pd.isna(cell_value) else cell_value)
        logging.info(f"The new data for comparison:\n{new_resource_data}")


        #Section: Set Up Recordlinkage Matching
        #Subsection: Create Collections for Holding Matches
        # The automated matching performed with recordlinkage generates pairs of record indexes for two records in a dataframe that match. The nature of relational data in a flat file format, scholarly resource metadata, and computer matching algorithms, however, means a simple list of the record index pairs won't work.
        matched_records = set()
            # For record index pairs matched through exact methods or fuzzy methods with very high thresholds, a set ensures a given match won't be added multiple times because it's identified as a match multiple times.
        matches_to_manually_confirm = dict()
            # For record index pairs matched through fuzzy methods, the match will need to be manually confirmed. Each resource, however, appears multiple times in `new_resource_data` and the potential index pairs are created through a Cartesian product, so the same two resources will be compared multiple times. So that each fuzzily matched pair is only asked about once, `matches_to_manually_confirm` will employ nested data collection structures: the variable will be a dictionary with tuples as keys and sets as values; each tuple will contain two tuples, one for each resource's metadata, in 'Resource_Name', 'DOI', 'ISBN', 'Print_ISSN', 'Online_ISSN', 'Data_Type', and 'Platform' order (because dictionaries can't be used in dictionary keys); each set will contain tuples of record indexes for resources matching the metadata in the dictionary key. This layout is modeled below:
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
        compare_DOI_and_ISBN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        compare_DOI_and_ISBN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')

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
        compare_DOI_and_ISSNs.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_DOI_and_ISSNs.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

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
        compare_ISBN.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        compare_ISBN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_ISBN.exact('ISBN', 'ISBN', label='ISBN')
        compare_ISBN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        compare_ISBN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on ISBN
        # The various editions or volumes of a title will be grouped together by fuzzy matching, and these can sometimes be given the same ISBN even when not appropriate. To keep this from causing problems, matches where one of the resource names has a volume or edition reference will be checked manually.
        if normalized_resource_data:
            compare_ISBN_table = compare_ISBN.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_ISBN_table['index_one_resource_name'] = compare_ISBN_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Resource_Name'])
        else:
            compare_ISBN_table = compare_ISBN.compute(candidate_matches, new_resource_data)
            compare_ISBN_table['index_one_resource_name'] = compare_ISBN_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Resource_Name'])
        
        compare_ISBN_table['index_zero_resource_name'] = compare_ISBN_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Resource_Name'])
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
        compare_ISSNs.string('Resource_Name', 'Resource_Name', threshold=0.9, label='Resource_Name')
        compare_ISSNs.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_ISSNs.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_ISSNs.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_ISSNs.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

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
        compare_print_ISSN.string('Resource_Name', 'Resource_Name', threshold=0.95, label='Resource_Name')
        compare_print_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_print_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_print_ISSN.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_print_ISSN.exact('Online_ISSN', 'Online_ISSN', missing_value=1, label='Online_ISSN')

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
        compare_online_ISSN.string('Resource_Name', 'Resource_Name', threshold=0.95, label='Resource_Name')
        compare_online_ISSN.exact('DOI', 'DOI', missing_value=1, label='DOI')
        compare_online_ISSN.exact('ISBN', 'ISBN', missing_value=1, label='ISBN')
        compare_online_ISSN.exact('Print_ISSN', 'Print_ISSN', missing_value=1, label='Print_ISSN')
        compare_online_ISSN.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

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
        compare_database_names.string('Resource_Name', 'Resource_Name', threshold=0.925, label='Resource_Name')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on High Database Name String Matching Threshold
        if normalized_resource_data:
            compare_database_names_table = compare_database_names.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_database_names_table['index_one_data_type'] = compare_database_names_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Data_Type'])
        else:
            compare_database_names_table = compare_database_names.compute(candidate_matches, new_resource_data)
            compare_database_names_table['index_one_data_type'] = compare_database_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Data_Type'])
        
        compare_database_names_table['index_zero_data_type'] = compare_database_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Data_Type'])
        logging.info(f"Database names comparison result with metadata:\n{compare_database_names_table}")

        #Subsection: Filter and Update Comparison Results Dataframe Based on High Database Name String Matching Threshold
        database_names_matches_table = compare_database_names_table[  # Creates dataframe with the records which meet the high name matching threshold and where both resources are databases
            (compare_database_names_table['Resource_Name'] == 1) &
            (compare_database_names_table['index_zero_data_type'] == "Database") &
            (compare_database_names_table['index_one_data_type'] == "Database")
        ]

        # Resource names and platforms are added after filtering to reduce the number of names that need to be found
        database_names_matches_table['index_zero_resource_name'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Resource_Name'])
        database_names_matches_table['index_zero_platform'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Platform'])
        if normalized_resource_data:
            database_names_matches_table['index_one_resource_name'] = database_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Resource_Name'])
            database_names_matches_table['index_one_platform'] = database_names_matches_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Platform'])
        else:
            database_names_matches_table['index_one_resource_name'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Resource_Name'])
            database_names_matches_table['index_one_platform'] = database_names_matches_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Platform'])
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
        compare_platform_names.string('Platform', 'Platform', threshold=0.925, label='Platform')

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on High Platform Name String Matching Threshold
        if normalized_resource_data:
            compare_platform_names_table = compare_platform_names.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_platform_names_table['index_one_data_type'] = compare_platform_names_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Data_Type'])
        else:
            compare_platform_names_table = compare_platform_names.compute(candidate_matches, new_resource_data)
            compare_platform_names_table['index_one_data_type'] = compare_platform_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Data_Type'])
        
        compare_platform_names_table['index_zero_data_type'] = compare_platform_names_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Data_Type'])
        logging.info(f"Platform names comparison result with metadata:\n{compare_platform_names_table}")

        #Subsection: Filter and Update Comparison Results Dataframe Based on High Platform Name String Matching Threshold
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
        compare_identifiers.exact('Print_ISSN', 'Print_ISSN', label='Print_ISSN')
        compare_identifiers.exact('Online_ISSN', 'Online_ISSN', label='Online_ISSN')

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
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.65, label='levenshtein')
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.70, method='jaro', label='jaro')  # Version of jellyfish used has DepreciationWarning for this method
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.70, method='jarowinkler', label='jarowinkler')  # Version of jellyfish used has DepreciationWarning for this method
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.75, method='lcs', label='lcs')
        compare_resource_name.string('Resource_Name', 'Resource_Name', threshold=0.70, method='smith_waterman', label='smith_waterman')
        # This comparison will take about an hour on a 16GB RAM 1.61GHz workstation

        #Subsection: Return Dataframe with Comparison Results and Filtering Values Based on High Resource Name String Matching Threshold
        if normalized_resource_data:
            compare_resource_name_table = compare_resource_name.compute(candidate_matches, new_resource_data, normalized_resource_data)  #Alert: Not tested
            compare_resource_name_table['index_one_resource_name'] = compare_resource_name_table.index.map(lambda index_value: normalized_resource_data.loc[index_value[1], 'Resource_Name'])
        else:
            compare_resource_name_table = compare_resource_name.compute(candidate_matches, new_resource_data)
            compare_resource_name_table['index_one_resource_name'] = compare_resource_name_table.index.map(lambda index_value: new_resource_data.loc[index_value[1], 'Resource_Name'])
        
        compare_resource_name_table['index_zero_resource_name'] = compare_resource_name_table.index.map(lambda index_value: new_resource_data.loc[index_value[0], 'Resource_Name'])
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
        #ToDo: Resources where an ISSN appears in both the Print_ISSN and Online_ISSN fields and/or is paired with different ISSNs still need to be paired--can the node and edge model used after this initial manual matching perform that pairing?
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