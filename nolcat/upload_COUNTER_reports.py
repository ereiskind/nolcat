import logging
import os
from pathlib import Path
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
        if repr(type(self.COUNTER_report_files)) == "<class 'wtforms.fields.core.UnboundField'>":
            # The MultipleFileField fixture created for testing is an UnboundField object because it uses a constructor for an object that inherits from the WTForms Form base class but lacks the `_form` and `_name` parameters, which are automatically supplied during standard Form object construction. While that fixture would ideally be an actual MultipleFileField object, without appropriate values for the above parameters, the test will feature the rarely-occurring UnboundField instead, at which point, the list of file names will be reconstructed through reuse of the loop found in the fixture.
            list_of_file_names = os.listdir(Path('tests', 'bin', 'COUNTER_workbooks_for_tests'))
            logging.debug(f"File names: {list_of_file_names}")
        else:
            list_of_file_names = request.files.getlist(self.COUNTER_report_files.name)
            logging.debug(f"File names: {list_of_file_names}")
        
        for file_name in list_of_file_names:
            try:
                statistics_source_ID = int(re.findall(r'(\d*)_.*\.xlsx', string=file_name)[0])  # `findall` always produces a list
                file = load_workbook(filename=file_name, read_only=True)
                logging.debug(f"Loading data from workbook {file_name}")
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

                        # `None` in regex methods raises a TypeError, so they need to be in try-except blocks
                        try:
                            if re.match(r'^[Cc]omponent', field_name):
                                continue  # The rarely used `Component` subtype fields aren't captured by this program
                        except TypeError:
                            pass

                        try:  
                            date_as_string = re.findall(r'([A-Z][a-z]{2})\-(\d{4})', string=field_name)
                        except TypeError:
                            date_as_string = False
                        
                        if field_name == "ISSN" and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5'):
                            df_field_names.append("online_ISSN")  # This is the first name replacement because assigning a certain type of ISSN changes the meaning slightly
                        
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
                            df_field_names.append("resource_name")
                        elif field_name == "Collection" and report_type == 'MR1':
                            df_field_names.append("resource_name")
                        elif field_name == "Database" and (report_type == 'DB1' or report_type == 'DB2'):
                            df_field_names.append("resource_name")
                        
                        elif field_name == "Journal" and (report_type == 'JR1' or report_type == 'JR2'):
                            df_field_names.append("resource_name")
                        elif field_name == "Title" and (report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5' or report_type == 'TR1' or report_type == 'TR2'):
                            df_field_names.append("resource_name")
                        elif field_name == "Database" and report_type == 'DR':
                            df_field_names.append("resource_name")
                        elif field_name == "Title" and report_type == 'TR':
                            df_field_names.append("resource_name")
                        elif field_name == "Item" and report_type == 'IR':
                            df_field_names.append("resource_name")
                        
                        elif field_name == "Content Provider" and report_type == 'MR1':
                            df_field_names.append("publisher")
                        elif field_name == "User Activity" and (report_type == 'BR5' or report_type == 'DB1'or report_type == 'PR1'):
                            df_field_names.append("metric_type")
                        elif (field_name == "Access Denied Category" or field_name == "Access denied category") and (report_type == 'BR3' or report_type == 'DB2' or report_type == 'JR2' or report_type == 'TR2'):
                            df_field_names.append("metric_type")
                        
                        # These change field names from R4 and R5 reports to use R5 naming conventions with lowercase letters, so they don't need to be limited to certain reports
                        elif field_name == "Proprietary Identifier" or field_name == "Proprietary_ID":
                            df_field_names.append("proprietary_ID")
                        elif field_name == "Book DOI" or field_name == "Journal DOI" or field_name == "Title DOI":
                            df_field_names.append("DOI")
                        elif field_name == "Data type" or field_name == "Data Type" or field_name == "Data_Type":
                            df_field_names.append("data_type")
                        elif field_name == "Online ISSN" or field_name == "Online_ISSN":
                            df_field_names.append("online_ISSN")
                        elif field_name == "Print ISSN" or field_name == "Print_ISSN":
                            df_field_names.append("print_ISSN")

                        elif field_name is None:
                            continue  # Deleted data and merged cells for header values can make Excel think null columns are in use; when read, these columns add `None` to `df_field_names`, causing a `ValueError: Number of passed names did not patch number of header fields in the file` when reading the worksheet contents into a dataframe
                        
                        elif re.search(r'_((ID)|(DOI)|(URI)|(IS[SB]N))$', field_name):  # The regex captures strings ending with `ID`, `DOI`, `URI`, `ISSN`, and `ISBN` after an underscore; no try-except block is needed because `None` values were filtered out above
                            df_field_names.append("_".join(field_name.split("_")[0:-1]).lower() + "_" + field_name.split("_")[-1])
                        
                        else:
                            df_field_names.append(field_name.lower())
                df_non_date_field_names = [field_name for field_name in df_field_names if field_name not in df_date_field_names]  # List comprehension used to preserve order
                logging.info(f"The COUNTER report contains the fields {df_non_date_field_names} and data for the dates {df_date_field_names}.")


                #Section: Create Dataframe
                #Subsection: Ensure String Data Type for Potentially Numeric Metadata Fields
                # Strings will be pandas object dtype at this point, but object to string conversion is fairly simple; string fields that pandas might automatically assign a numeric dtype to should be set as strings at the creation of the dataframe to head off problems.
                df_dtypes = dict()
                if "resource_name" in df_field_names:  # Dates and numbers, especially years, can be used as titles
                    df_dtypes['resource_name'] = 'string'
                if "publisher_ID" in df_field_names:
                    df_dtypes['publisher_ID'] = 'string'
                if "DOI" in df_field_names:
                    df_dtypes['DOI'] = 'string'
                if "proprietary_ID" in df_field_names:
                    df_dtypes['proprietary_ID'] = 'string'
                if "ISBN" in df_field_names:
                    df_dtypes['ISBN'] = 'string'
                if "print_ISSN" in df_field_names:
                    df_dtypes['print_ISSN'] = 'string'
                if "online_ISSN" in df_field_names:
                    df_dtypes['online_ISSN'] = 'string'
                if "parent_DOI" in df_field_names:
                    df_dtypes['parent_DOI'] = 'string'
                if "parent_proprietary_ID" in df_field_names:
                    df_dtypes['parent_proprietary_ID'] = 'string'
                if "parent_ISBN" in df_field_names:
                    df_dtypes['parent_ISBN'] = 'string'
                if "parent_print_ISSN" in df_field_names:
                    df_dtypes['parent_print_ISSN'] = 'string'
                if "parent_online_ISSN" in df_field_names:
                    df_dtypes['parent_online_ISSN'] = 'string'
                
                #Subsection: Create Dataframe from Excel Worksheet
                df = pd.read_excel(
                    file_name,
                    sheet_name=report_type,
                    engine='openpyxl',
                    header=header_row_number-1,  # This gives the row number with the headings in Excel, which is also the row above where the data starts
                    names=df_field_names,
                    dtype=df_dtypes,
                )
                logging.info(f"Dataframe immediately after creation:\n{df}\n{df.info()}")


                #Section: Make Pre-Stacking Updates
                df = df.replace(r'\n', '', regex=True)  # Removes errant newlines found in some reports, primarily at the end of resource names
                df = df.replace("licence", "license")  # "Have `license` always use American English spelling

                #Subsection: Add `Statistics_Source_ID` Field
                df['statistics_source_ID'] = statistics_source_ID
                # Adding the name of the field any earlier would make the list of field names longer than the number of fields in the spreadsheet being imported
                df_field_names.append("statistics_source_ID")
                df_non_date_field_names.append("statistics_source_ID")
                logging.debug(f"Dataframe field names: {df_field_names}")

                #Subsection: Remove `Reporting Period` Field
                df_field_names_sans_reporting_period_fields = [field_name for field_name in df_non_date_field_names if not re.search(r'[Rr]eporting[\s_][Pp]eriod', field_name)]
                reporting_period_field_names = [field_name for field_name in df_non_date_field_names if field_name not in df_field_names_sans_reporting_period_fields]  # List comprehension used to preserve list order
                df = df.drop(columns=reporting_period_field_names)
                df_field_names = df_field_names_sans_reporting_period_fields + df_date_field_names
                logging.debug(f"`df_field_names` with statistics source ID and without reporting period: {df_field_names}")

                #Subsection: Remove Total Rows
                if re.match(r'PR1?', string=report_type) is None:  # `re.match` returns `None` if there isn't a match, so this selects everything but platform reports in both R4 and R5
                    number_of_rows_with_totals = df.shape[1]
                    common_summary_rows = df['resource_name'].str.contains(r'^[Tt]otal\s[Ff]or\s[Aa]ll\s\w*', regex=True)  # `\w*` is because values besides `title` are used in various reports
                    uncommon_summary_rows = df['resource_name'].str.contains(r'^[Tt]otal\s[Ss]earches', regex=True)
                    summary_rows_are_false = ~(common_summary_rows + uncommon_summary_rows)
                    df = df[summary_rows_are_false]
                    logging.debug(f"Number of rows in report of type {report_type} reduced from {number_of_rows_with_totals} to {df.shape[1]}.")

                #Subsection: Split ISBNs and ISSNs in TR
                if re.match(r'TR[1|2]', string=report_type) is not None:  # `re.match` returns `None` if there isn't a match, so this selects all title reports
                    # Creates fields containing `True` if the original field's value matches the regex, `False` if it doesn't match the regex, and null if the original field is also null
                    df['print_ISSN'] = df['Print ID'].str.match(r'\d{4}\-\d{3}[\dXx]')
                    df['online_ISSN'] = df['Online ID'].str.match(r'\d{4}\-\d{3}[\dXx]')
                    # Returns `True` if the values of `print_ISSN` and `online_ISSN` are `True`, otherwise, returns `False`
                    df['ISBN'] = df['print_ISSN'] & df['online_ISSN']

                    # Replaces Booleans signaling value with values from `Print ID` and `Online ID`
                    df.loc[df['print_ISSN'] == True, 'print_ISSN'] = df['Print ID']
                    df.loc[df['online_ISSN'] == True, 'online_ISSN'] = df['Online ID']
                    df.loc[df['print_ISSN'] == False, 'ISBN'] = df['Print ID']
                    df.loc[df['online_ISSN'] == False, 'ISBN'] = df['Online ID']
                    # Replace Booleans not signaling value with null placeholder string (replacing with `None` causes the values to fill down instead of the desired replacement)
                    df['print_ISSN'] = df['print_ISSN'].replace(False, "`None`")  
                    df['online_ISSN'] = df['online_ISSN'].replace(False, "`None`")
                    df['ISBN'] = df['ISBN'].replace(True, "`None`")
                    df['ISBN'] = df['ISBN'].replace(False, "`None`")  # These cells occur when the ID columns have a null value and an ISSN

                    # Update field names and order in `df_field_names` and dataframe
                    df = df.drop(columns=['Print ID', 'Online ID'])
                    df_field_names.remove("Print ID")
                    df_field_names.remove("Online ID")
                    df_field_names.insert(len(df_field_names)-len(df_date_field_names)-1, "ISBN")
                    df_field_names.insert(len(df_field_names)-len(df_date_field_names)-1, "print_ISSN")
                    df_field_names.insert(len(df_field_names)-len(df_date_field_names)-1, "online_ISSN")
                    df = df[df_field_names]
                    logging.debug(f"Dataframe with identifiers in standardized fields:\n{df}")

                #Subsection: Put Placeholder in for Null Values
                df = df.fillna("`None`")
                df = df.replace(
                    to_replace='^\s*$',
                    # The regex is designed to find the blank but not null cells by finding those cells containing nothing (empty strings) or only whitespace. The whitespace metacharacter `\s` is marked with a deprecation warning, and without the anchors, the replacement is applied not just to whitespaces but to spaces between characters as well.
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
                    'level_1': 'usage_date',
                    0: 'usage_count',
                })
                logging.debug(f"Dataframe with reset index:\n{df}")

                #Subsection: Recreate Metadata Fields
                df[df_non_date_field_names] = df['temp_index'].str.split(pat="~", expand=True)  # This splits the metadata values in the index, which are separated by `~`, into their own fields and applies the appropriate names to those fields
                df = df.drop(columns='temp_index')
                logging.info(f"Fully transposed dataframe:\n{df}")


                #Section: Adjust Data in Dataframe
                #Subsection: Remove Rows with No Usage
                df = df[df['usage_count'] != 0]
                df = df[df['usage_count'] != "`None`"]  # Some zero `usage_count` values may have been null values replaced by the null placeholder; retaining them interferes with correcting data types
                df = df.reset_index(drop=True)
                logging.debug(f"Dataframe with zero usage records removed:\n{df}")

                #Subsection: Correct Data Types, Including Replacing Null Placeholders with Null Values
                non_string_fields = ["index", "usage_date", "usage_count"]  # Unable to combine not equal to clauses in list comprehension below
                fields_to_convert_to_string_dtype = [field_name for field_name in df.columns.values.tolist() if field_name not in non_string_fields]
                string_dtype_conversion_dict = {'usage_count': 'int'}
                for field_name in fields_to_convert_to_string_dtype:
                    string_dtype_conversion_dict[field_name] = 'string'
                df = df.astype(string_dtype_conversion_dict)

                # Placing this before the data type conversion can cause it to fail due to `NoneType` values in fields being converted to strings
                df = df.replace(["`None`"], [None])  # Values must be enclosed in lists for method to work

                df['usage_date'] = pd.to_datetime(df['usage_date'])
                logging.debug(f"Updated dataframe dtypes:\n{df.dtypes}")

                #Subsection: Add Fields Missing from R4 Reports
                if report_type == 'BR1' or report_type == 'BR2' or report_type == 'BR3' or report_type == 'BR5':
                    df['data_type'] = "Book"
                elif report_type == 'DB1' or report_type == 'DB2':
                    df['data_type'] = "Database"
                elif report_type == 'JR1' or report_type == 'JR2':
                    df['data_type'] = "Journal"
                elif report_type == 'MR1':
                    df['data_type'] = "Multimedia"
                elif report_type == 'PR1':
                    df['data_type'] = "Platform"

                if report_type == 'BR1' or report_type == 'BR3' or report_type == 'BR5':
                    df['section_type'] = "Book"
                elif report_type =='BR2':
                    df['section_type'] = "Book_Segment"
                elif report_type == 'JR1' or report_type == 'JR2':
                    df['section_type'] = "Article"
                elif report_type == 'TR1' or report_type == 'TR2':
                    df.loc[df['data_type'] == "Journal", 'section_type'] = "Article"
                    df.loc[df['data_type'] == "Book", 'section_type'] = "Book_Segment"
                    # Any data types besides `Book` or `Journal` won't have a section type

                if report_type =='BR1' or report_type == 'TR1':
                    df['metric_type'] = "Successful Title Requests"
                elif report_type =='BR2':
                    df['metric_type'] = "Successful Section Requests"
                elif report_type =='JR1':
                    df['metric_type'] = "Successful Full-text Article Requests"
                elif report_type =='MR1':
                    df['metric_type'] = "Successful Content Unit Requests"
                
                logging.info(f"Dataframe being used in concatenation:\n{df}")
                all_dataframes_to_concatenate.append(df)
        
        
        #Section: Create Final Combined Dataframe
        #Subsection: Combine Dataframes
        combined_df = pd.concat(
            all_dataframes_to_concatenate,
            ignore_index=True,  # Resets index
        )
        logging.info(f"Combined dataframe:\n{combined_df}")

        #Subsection: Set Data Types
        combined_df_field_names = combined_df.columns.values.tolist()

        combined_df_dtypes = {
            'platform': 'string',
            # usage_date retains datetime64[ns] type from heading conversion
            # usage_count is a numpy int type, let the program determine the number of bits used for storage
            'statistics_source_ID': 'int',
        }
        if "resource_name" in combined_df_field_names:
            combined_df_dtypes['resource_name'] = 'string'
        if "publisher" in combined_df_field_names:
            combined_df_dtypes['publisher'] = 'string'
        if "publisher_ID" in combined_df_field_names:
            combined_df_dtypes['publisher_ID'] = 'string'
        if "authors" in combined_df_field_names:
            combined_df_dtypes['authors'] = 'string'
        if "article_version" in combined_df_field_names:
            combined_df_dtypes['article_version'] = 'string'
        if "DOI" in combined_df_field_names:
            combined_df_dtypes['DOI'] = 'string'
        if "proprietary_ID" in combined_df_field_names:
            combined_df_dtypes['proprietary_ID'] = 'string'
        if "ISBN" in combined_df_field_names:
            combined_df_dtypes['ISBN'] = 'string'
        if "print_ISSN" in combined_df_field_names:
            combined_df_dtypes['print_ISSN'] = 'string'
        if "online_ISSN" in combined_df_field_names:
            combined_df_dtypes['online_ISSN'] = 'string'
        if "URI" in combined_df_field_names:
            combined_df_dtypes['URI'] = 'string'
        if "data_type" in combined_df_field_names:
            combined_df_dtypes['data_type'] = 'string'
        if "section_type" in combined_df_field_names:
            combined_df_dtypes['section_type'] = 'string'
        if "YOP" in combined_df_field_names:
            combined_df_dtypes['YOP'] = 'Int64'  # `smallint` in database; using the pandas data type here because it allows null values
        if "access_type" in combined_df_field_names:
            combined_df_dtypes['access_type'] = 'string'
        if "access_method" in combined_df_field_names:
            combined_df_dtypes['access_method'] = 'string'
        if "parent_title" in combined_df_field_names:
            combined_df_dtypes['parent_title'] = 'string'
        if "parent_authors" in combined_df_field_names:
            combined_df_dtypes['parent_authors'] = 'string'
        if "parent_article_version" in combined_df_field_names:
            combined_df_dtypes['parent_article_version'] = 'string'
        if "parent_data_Type" in combined_df_field_names:
            combined_df_dtypes['parent_data_Type'] = 'string'
        if "parent_DOI" in combined_df_field_names:
            combined_df_dtypes['parent_DOI'] = 'string'
        if "parent_proprietary_ID" in combined_df_field_names:
            combined_df_dtypes['parent_proprietary_ID'] = 'string'
        if "parent_ISBN" in combined_df_field_names:
            combined_df_dtypes['parent_ISBN'] = 'string'
        if "parent_print_ISSN" in combined_df_field_names:
            combined_df_dtypes['parent_print_ISSN'] = 'string'
        if "parent_online_ISSN" in combined_df_field_names:
            combined_df_dtypes['parent_online_ISSN'] = 'string'
        if "parent_URI" in combined_df_field_names:
            combined_df_dtypes['parent_URI'] = 'string'
        if "metric_type" in combined_df_field_names:
            combined_df_dtypes['metric_type'] = 'string'
        
        combined_df = combined_df.astype(combined_df_dtypes, errors='ignore')  #ToDo: Will ignoring data type conversion errors cause problems with loading into MySQL?
        if "publication_date" in combined_df_field_names:
            combined_df['publication_date'] = pd.to_datetime(combined_df['publication_date'])
        if "parent_publication_date" in combined_df_field_names:
            combined_df['parent_publication_date'] = pd.to_datetime(combined_df['parent_publication_date'])


        #Section: Return Dataframe
        logging.info(f"Final dataframe:\n{combined_df}\n{combined_df.dtypes}")
        return df