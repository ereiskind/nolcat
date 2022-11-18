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
        pass