import logging
import re
import datetime
from flask import request
from openpyxl import load_workbook
import pandas as pd

logging.basicConfig(level=logging.INFO, format="UploadCOUNTERReports - - [%(asctime)s] %(message)s")


class UploadCOUNTERReports:
    """A class for transforming uploaded Excel workbook(s) with COUNTER data into dataframes ready for normalization.

    COUNTER reports not delivered by SUSHI are given in a tabular format and usually saved in Excel workbooks. These workbooks can be ingested into this program via a Flask-WTF MultipleFileField form field, but that workbook data requires a great deal of manipulation and cleaning to become a single dataframe ready for normalization, most frequently in the form of initialization as a `RawCOUNTERReport` object. This class exists to make those changes; since the desired behavior is more that of a function than a class, the would-be function becomes a class by dividing it into the traditional `__init__` method, which instantiates the MultipleFileField object encapsulating the selected Excel workbook(s) as a class attribute, and the `create_dataframe()` method, which performs the actual transformation. This structure requires all instances of the class constructor to be prepended to a call to the `create_dataframe()` method, which means objects of the `UploadCOUNTERReports` type are never instantiated.

    Attributes:
        self.COUNTER_report_files (MultipleFileField): The constructor method for `UploadCOUNTERReports`, which instantiates the MultipleFileField object.

    Methods:
        create_dataframe: This method transforms the data from the tabular COUNTER reports in uploaded Excel workbooks into a single dataframe ready for normalization.
    """
    def __init__(self, COUNTER_report_files):
        """The constructor method for `UploadCOUNTERReports`, which instantiates the MultipleFileField object.

        This constructor is not meant to be used alone; all class instantiations should have a `create_dataframe()` method call appended to it.

        Args:
            COUNTER_report_files (MultipleFileField): The MultipleFileField object containing the uploaded Excel workbook(s) of tabular COUNTER data
        """
        self.COUNTER_report_files = COUNTER_report_files
    

    def create_dataframe(self):
        """This method transforms the data from the tabular COUNTER reports in uploaded Excel workbooks into a single dataframe ready for normalization.

        This method prepares the data from tabular COUNTER reports for upload into the database. This method transforms tabular COUNTER reports on sheets in Excel workbooks into dataframes, but to become complete and valid records in the relation, enhancements are needed, including cleaning the data, filling in data R4 provided through its multiple different report types, and adding the statistics source of the data, which is taken from the first part of the file name.

        Returns:
            dataframe: COUNTER data ready for normalization
        """
        '''Known issues with specific stats sources (taken from webpage instructions):
            * Gale reports needed to be copied and pasted as values with the paste special dialog box to work in OpenRefine
            * iG Press/BEP reports have multiple ISBNs and ISSNs in the fields for those values
        '''
        all_dataframes_to_concatenate = []
        valid_report_types = ("BR1", "BR2", "BR3", "BR5", "DB1", "DB2", "JR1", "JR2", "MR1", "PR1", "TR1", "TR2", "PR", "DR", "TR", "IR")


        #Section: Load the Workbook(s)
        list_of_file_names = request.files.getlist(self.COUNTER_report_files.name)
        for file_name in list_of_file_names:
            try:
                statistics_source_ID = int(re.findall(r'(\d*).xlsx', string=file_name)[0])  # `findall` always produces a list
                file = load_workbook(filename=file_name, read_only=True)
            except:
                logging.warning(f"The workbook {file_name} couldn't be loaded. Please confirm that it is an Excel workbook with a name that begins with the statistics source ID followed by an underscore.")
                continue

            for report_type in file.sheetnames:
                if report_type not in valid_report_types:
                    logging.warning(f"The sheet name {report_type} isn't a valid report type, so the sheet couldn't be loaded. Please correct the sheet name and try again.")
                    continue
                sheet = file[report_type]  # `report_type` is the name of the sheet as a string, so it can be used as an index operator
                logging.info(f"Loading data from sheet {report_type} from workbook {file_name}.")


                #Section: Identify the Header Row
                # To handle both R4 and R5 reports, as well as noncompliance with the standard in regards to empty rows in and after the header, the header row of the table is searched for instead of using any presets
                looking_for_header_row = True
                header_row_number = 1

                while looking_for_header_row:
                    count_of_month_labels = 0
                    for cell in sheet[header_row_number]:
                        if cell.value is None or repr(type(cell.value)) == "<class 'int'>":
                            continue  # `None` and integers (which appear in the "Release" field of the header) cause `TypeError` in `re.fullmatch`, so they need to be weeded out here
                        elif repr(type(cell.value)) == "<class 'datetime.datetime'>" or re.fullmatch(r'[A-Z][a-z]{2}\-\d{4}', cell.value) is not None:
                            count_of_month_labels += 1
                    if count_of_month_labels > 1:  # This stops at the first row with multiple dates, which won't be true of any header row
                        number_of_fields = len(sheet[header_row_number])
                        logging.debug(f"The table's header is at row {header_row_number}.")
                        looking_for_header_row = False
                        break
                    else:
                        header_row_number += 1
                

                #Section: Get the Field Names
                df_field_names = []
                df_date_field_names = []
                for iterable_of_field_names in sheet.iter_rows(
                    min_row=header_row_number,
                    max_row=header_row_number,
                    min_col=1,
                    max_col=number_of_fields,
                    values_only=True,
                ):  # Creates a tuple with the field names as elements
                    for field_name in iterable_of_field_names:
                        logging.debug(f"Getting standardized field name for field {field_name} (type {type(field_name)})")
                        try:
                            date_as_string = re.findall(r'([A-Z][a-z]{2})\-(\d{4})', string=field_name)  # `None` in `findall` raises an error, so it needs to be in a `try-except` block
                        except:
                            date_as_string = False
                        
                        if field_name == "ISSN" and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5'):
                            df_field_names.append("Online_ISSN")  # This is the first name replacement because assigning a certain type of ISSN changes the meaning slightly
                        
                        elif re.match(r'^[Cc]omponent'):
                            continue  # The rarely used `Component` subtype fields aren't captured by this program
                        
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
                        
                        elif field_name == "Journal" and (report_type == 'JR1' or report_type == 'JR2'):
                            df_field_names.append("Resource_Name")
                        elif field_name == "Title" and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5' or report_type == 'TR1' or report_type == 'TR2'):
                            df_field_names.append("Resource_Name")
                        elif field_name == "Database" and report_type == 'DR':
                            df_field_names.append("Resource_Name")
                        elif field_name == "Title" and report_type == 'TR':
                            df_field_names.append("Resource_Name")
                        elif field_name == "Item" and report_type == 'IR':
                            df_field_names.append("Resource_Name")
                        
                        elif field_name == "Content Provider" and report_type == 'MR1':
                            df_field_names.append("Publisher")
                        elif field_name == "User Activity" and (report_type == 'BR5' or report_type == 'DB1'or report_type == 'PR1'):
                            df_field_names.append("Metric_Type")
                        elif (field_name == "Access Denied Category" or field_name == "Access denied category") and (report_type == 'BR3' or report_type == 'DB2' or report_type == 'JR2' or report_type == 'TR2'):
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

                        elif field_name is None:
                            continue  # Deleted data and merged cells for header values can make Excel think null columns are in use; when read, these columns add `None` to `df_field_names`, causing a `ValueError: Number of passed names did not patch number of header fields in the file` when reading the worksheet contents into a dataframe
                        
                        else:
                            df_field_names.append(field_name)
                df_non_date_field_names = [field_name for field_name in df_field_names if field_name not in df_date_field_names]  # List comprehension used to preserve order
                logging.info(f"The COUNTER report contains the fields {df_non_date_field_names} and data for the dates {df_date_field_names}.")


                #Section: Ensure String Data Type for Metadata
                df_dtypes = {'Platform': 'string'}
                if "Resource_Name" in df_field_names:
                    df_dtypes['Resource_Name'] = 'string'
                if "Publisher" in df_field_names:
                    df_dtypes['Publisher'] = 'string'
                if "DOI" in df_field_names:
                    df_dtypes['DOI'] = 'string'
                if "Proprietary_ID" in df_field_names:
                    df_dtypes['Proprietary_ID'] = 'string'
                if "ISBN" in df_field_names:
                    df_dtypes['ISBN'] = 'string'
                if "Print_ISSN" in df_field_names:
                    df_dtypes['Print_ISSN'] = 'string'
                if "Online_ISSN" in df_field_names:
                    df_dtypes['Online_ISSN'] = 'string'
                if "Data_Type" in df_field_names:
                    df_dtypes['Data_Type'] = 'string'
                if "Section_Type" in df_field_names:
                    df_dtypes['Section_Type'] = 'string'
                if "Metric_Type" in df_field_names:
                    df_dtypes['Metric_Type'] = 'string'
                

                #Section: Create Dataframe
                df = pd.read_excel(
                    file_name,
                    sheet_name=report_type,
                    engine='openpyxl',
                    header=header_row_number-1,  # This gives the row number with the headings in Excel, which is also the row above where the data starts
                    names=df_field_names,
                    dtype=df_dtypes,
                )
                logging.info(f"Dataframe immediately after creation:\n{df}")


                #Section: Make Pre-Stacking Updates
                df = df.replace(r'\n', '', regex=True)  # Removes errant newlines found in some reports, primarily at the end of resource names
                df = df.replace("licence", "license")  # "Have `license` always use American English spelling

                #Subsection: Add `Statistics_Source_ID` Field
                df['Statistics_Source_ID'] = statistics_source_ID
                # Adding the name of the field any earlier would make the list of field names longer than the number of fields in the spreadsheet being imported
                df_field_names.append("Statistics_Source_ID")
                df_non_date_field_names.append("Statistics_Source_ID")

                #Subsection: Remove `Reporting Period` Field
                df_field_names_sans_reporting_period_fields = [field_name for field_name in df_non_date_field_names if not re.search(r'[Rr]eporting[\s_][Pp]eriod', field_name)]
                reporting_period_field_names = [field_name for field_name in df_non_date_field_names if field_name not in df_field_names_sans_reporting_period_fields]  # List comprehension used to preserve list order
                df = df.drop(columns=reporting_period_field_names)
                df_field_names = df_field_names_sans_reporting_period_fields + df_date_field_names
                logging.info(f"`df_field_names` with statistics source ID and without reporting period: {df_field_names}")

                #Subsection: Remove Total Rows
                if re.match(r'PR1?', string=report_type) is None:  # `re.match` returns `None` if there isn't a match, so this selects everything but platform reports in both R4 and R5
                    common_summary_rows = df['Resource_Name'].str.contains(r'^[Tt]otal\s[Ff]or\s[Aa]ll\s\w*', regex=True)  # `\w*` is because values besides `title` are used in various reports
                    uncommon_summary_rows = df['Resource_Name'].str.contains(r'^[Tt]otal\s[Ss]earches', regex=True)
                    summary_rows_are_false = ~(common_summary_rows + uncommon_summary_rows)
                    df = df[summary_rows_are_false]

                #Subsection: Split ISBNs and ISSNs in TR
                if re.match(r'TR[1|2]', string=report_type) is not None:  # `re.match` returns `None` if there isn't a match, so this selects all title reports
                    # Creates fields containing `True` if the original field's value matches the regex, `False` if it doesn't match the regex, and null if the original field is also null
                    df['Print_ISSN'] = df['Print ID'].str.match(r'\d{4}\-\d{3}[\dXx]')
                    df['Online_ISSN'] = df['Online ID'].str.match(r'\d{4}\-\d{3}[\dXx]')
                    # Returns `True` if the values of `Print_ISSN` and `Online_ISSN` are `True`, otherwise, returns `False`
                    df['ISBN'] = df['Print_ISSN'] & df['Online_ISSN']

                    # Replaces Booleans signaling value with values from `Print ID` and `Online ID`
                    df.loc[df['Print_ISSN'] == True, 'Print_ISSN'] = df['Print ID']
                    df.loc[df['Online_ISSN'] == True, 'Online_ISSN'] = df['Online ID']
                    df.loc[df['Print_ISSN'] == False, 'ISBN'] = df['Print ID']
                    df.loc[df['Online_ISSN'] == False, 'ISBN'] = df['Online ID']
                    # Replace Booleans not signaling value with null placeholder string (replacing with `None` causes the values to fill down instead of the desired replacement)
                    df['Print_ISSN'] = df['Print_ISSN'].replace(False, "`None`")  
                    df['Online_ISSN'] = df['Online_ISSN'].replace(False, "`None`")
                    df['ISBN'] = df['ISBN'].replace(True, "`None`")
                    df['ISBN'] = df['ISBN'].replace(False, "`None`")  # These cells occur when the ID columns have a null value and an ISSN

                    # Update field names and order in `df_field_names` and dataframe
                    df = df.drop(columns=['Print ID', 'Online ID'])
                    df_field_names.remove("Print ID")
                    df_field_names.remove("Online ID")
                    df_field_names.insert(len(df_field_names)-len(df_date_field_names)-1, "ISBN")
                    df_field_names.insert(len(df_field_names)-len(df_date_field_names)-1, "Print_ISSN")
                    df_field_names.insert(len(df_field_names)-len(df_date_field_names)-1, "Online_ISSN")
                    df = df[df_field_names]

                #Subsection: Put Placeholder in for Null Values
                df = df.fillna("`None`")
                df = df.replace(
                    to_replace='^\s*$',  # The anchors ensure this is only applied to whitespace-only cells; without them, this is applied to all spaces, even the ones between letters
                    value="`None`",
                    regex=True
                )

                logging.info(f"Dataframe with pre-stacking changes:\n{df}")


                #Section: Stack Dataframe
                #Subsection: Create Temp Index Field with All Metadata Values
                list_of_field_names_from_df = df.columns.values.tolist()
                df_non_date_field_names = [field_name for field_name in df_field_names if field_name not in df_date_field_names]  # Reassigning this variable with the same statement because one of the values in the statement has changed
                boolean_identifying_metadata_fields = [True if field_name in df_non_date_field_names else False for field_name in list_of_field_names_from_df]
                df['temp_index'] = df[df.columns[boolean_identifying_metadata_fields]].apply(
                    lambda cell_value: '~'.join(cell_value.astype(str)),  # Combines all values in the fields specified by the index operator of the dataframe to which the `apply` method is applied; `~` is used as the delimiter because pandas 1.3 doesn't seem to handle multi-character literal string delimiters
                    axis='columns'
                )
                df = df.drop(columns=df_non_date_field_names)
                logging.debug(f"Dataframe with without metadata columns:\n{df}")
                df = df.set_index('temp_index')
                logging.debug(f"Dataframe with new index column:\n{df}")

                #Subsection: Reshape with Stacking
                df = df.stack()  # This creates a series with a multiindex: the multiindex is the metadata, then the dates; the data is the usage counts
                logging.debug(f"Dataframe immediately after stacking:\n{df}")
                df = df.reset_index()
                df = df.rename(columns={
                    'level_1': 'Usage_Date',
                    0: 'Usage_Count',
                })
                logging.debug(f"Dataframe with reset index:\n{df}")

                #Subsection: Recreate Metadata Fields
                df[df_non_date_field_names] = df['temp_index'].str.split(pat="~", expand=True)  # This splits the metadata values in the index, which are separated by `~`, into their own fields and applies the appropriate names to those fields
                df = df.drop(columns='temp_index')
                logging.info(f"Fully transposed dataframe:\n{df}")


                #Section: Adjust Data in Dataframe
                #Subsection: Remove Rows with No Usage
                df = df[df['Usage_Count'] != 0]
                df = df[df['Usage_Count'] != "`None`"]  # Some zero `Usage_Count` values may have been null values replaced by the null placeholder; retaining them interferes with correcting data types
                df = df.reset_index(drop=True)

                #Subsection: Correct Data Types, Including Replacing Null Placeholders with Null Values
                non_string_fields = ["index", "Usage_Date", "Usage_Count"]  # Unable to combine not equal to clauses in list comprehension below
                fields_to_convert_to_string_dtype = [field_name for field_name in df.columns.values.tolist() if field_name not in non_string_fields]
                string_dtype_conversion_dict = {'Usage_Count': 'int'}
                for field_name in fields_to_convert_to_string_dtype:
                    string_dtype_conversion_dict[field_name] = 'string'
                df = df.astype(string_dtype_conversion_dict)

                # Placing this before the data type conversion can cause it to fail due to `NoneType` values in fields being converted to strings
                df = df.replace(["`None`"], [None])  # Values must be enclosed in lists for method to work

                df['Usage_Date'] = pd.to_datetime(df['Usage_Date'])
                logging.debug(f"Updated dataframe dtypes:\n{df.dtypes}")

                #Subsection: Add Fields Missing from R4 Reports
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
                elif report_type == 'TR1' or report_type == 'TR2':
                    df.loc[df['Data_Type'] == "Journal", 'Section_Type'] = "Article"
                    df.loc[df['Data_Type'] == "Book", 'Section_Type'] = "Book_Segment"
                    # Any data types besides `Book` or `Journal` won't have a section type

                if report_type =='BR1' or report_type == 'TR1':
                    df['Metric_Type'] = "Successful Title Requests"
                elif report_type =='BR2':
                    df['Metric_Type'] = "Successful Section Requests"
                elif report_type =='JR1':
                    df['Metric_Type'] = "Successful Full-text Article Requests"
                elif report_type =='MR1':
                    df['Metric_Type'] = "Successful Content Unit Requests"
                
                logging.info(f"Dataframe being used in concatenation:\n{df}")
                all_dataframes_to_concatenate.append(df)
        
        
        #Section: Create Final Combined Dataframe
        #Subsection: Combine Dataframes
        combined_df = pd.concat(
            all_dataframes_to_concatenate,
            ignore_index=True,  # Resets index
        )
        logging.info(f"Combined dataframe:\n{df}")

        #Subsection: Set Data Types
        combined_df_field_names = combined_df.columns.values.tolist()

        combined_df_dtypes = {
            'Platform': 'string',
            # Usage_Date retains datetime64[ns] type from heading conversion
            # Usage_Count is a numpy int type, let the program determine the number of bits used for storage
            'Statistics_Source_ID': 'int',
        }
        if "Resource_Name" in combined_df_field_names:
            combined_df_dtypes['Resource_Name'] = 'string'
        if "Publisher" in combined_df_field_names:
            combined_df_dtypes['Publisher'] = 'string'
        if "Publisher_ID" in combined_df_field_names:
            combined_df_dtypes['Publisher_ID'] = 'string'
        if "DOI" in combined_df_field_names:
            combined_df_dtypes['DOI'] = 'string'
        if "Proprietary_ID" in combined_df_field_names:
            combined_df_dtypes['Proprietary_ID'] = 'string'
        if "ISBN" in combined_df_field_names:
            combined_df_dtypes['ISBN'] = 'string'
        if "Print_ISSN" in combined_df_field_names:
            combined_df_dtypes['Print_ISSN'] = 'string'
        if "Online_ISSN" in combined_df_field_names:
            combined_df_dtypes['Online_ISSN'] = 'string'
        if "Authors" in combined_df_field_names:
            combined_df_dtypes['Authors'] = 'string'
        if "Publication_Date" in combined_df_field_names:
            combined_df_dtypes['Publication_Date'] = 'datetime64[ns]'
        if "Article_Version" in combined_df_field_names:
            combined_df_dtypes['Article_Version'] = 'string'
        if "Data_Type" in combined_df_field_names:
            combined_df_dtypes['Data_Type'] = 'string'
        if "Section_Type" in combined_df_field_names:
            combined_df_dtypes['Section_Type'] = 'string'
        if "YOP" in combined_df_field_names:
            combined_df_dtypes['YOP'] = 'int'  # `smallint` in database
        if "Access_Type" in combined_df_field_names:
            combined_df_dtypes['Access_Type'] = 'string'
        if "Parent_Title" in combined_df_field_names:
            combined_df_dtypes['Parent_Title'] = 'string'
        if "Parent_Authors" in combined_df_field_names:
            combined_df_dtypes['Parent_Authors'] = 'string'
        if "Parent_Publication_Date" in combined_df_field_names:
            combined_df_dtypes['Parent_Publication_Date'] = 'datetime64[ns]'
        if "Parent_Article_Version" in combined_df_field_names:
            combined_df_dtypes['Parent_Article_Version'] = 'string'
        if "Parent_Data_Type" in combined_df_field_names:
            combined_df_dtypes['Parent_Data_Type'] = 'string'
        if "Parent_DOI" in combined_df_field_names:
            combined_df_dtypes['Parent_DOI'] = 'string'
        if "Parent_Proprietary_ID" in combined_df_field_names:
            combined_df_dtypes['Parent_Proprietary_ID'] = 'string'
        if "Parent_ISBN" in combined_df_field_names:
            combined_df_dtypes['Parent_ISBN'] = 'string'
        if "Parent_Print_ISSN" in combined_df_field_names:
            combined_df_dtypes['Parent_Print_ISSN'] = 'string'
        if "Parent_Online_ISSN" in combined_df_field_names:
            combined_df_dtypes['Parent_Online_ISSN'] = 'string'
        if "Parent_URI" in combined_df_field_names:
            combined_df_dtypes['Parent_URI'] = 'string'
        if "Metric_Type" in combined_df_field_names:
            combined_df_dtypes['Metric_Type'] = 'string'
        

        #Section: Return Dataframe
        logging.info(f"Final dataframe and its dtypes:\n{df}\n{df.dtypes}")
        return df