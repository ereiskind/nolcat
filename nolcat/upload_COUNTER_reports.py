import logging
import re
from flask import request
from openpyxl import load_workbook

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
                        looking_for_header_row = False
                        break
                    else:
                        header_row_number += 1
        pass