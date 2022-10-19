class UploadCOUNTERReports:
    """A class for transforming uploaded Excel workbook(s) with COUNTER data into dataframes ready for normalization.

    This class exists to transform the tabular COUNTER reports in the Excel workbooks in the `ImmutableMultiDict` objects created by file uploads into a single dataframe ready for normalization, most frequently in the form of initialization as a `RawCOUNTERReport` object. As the description above reveals, the desired behavior is more that of a function than a class; that would-be function becomes a class by dividing it into the traditional `__init__` method, which instantiates the `ImmutableMultiDict` as a class attribute, and the `create_dataframe()` method, which performs the actual transformation. This structure requires all instances of the class constructor to be prepended to a call to the `create_dataframe()` method, which means objects of the `UploadCOUNTERReports` type are never instantiated.

    Attributes:
        self.COUNTER_report_files (ImmutableMultiDict): the uploaded Excel workbook(s) of tabular COUNTER data

    Methods:
        create_dataframe: This method transforms tabular COUNTER reports in uploaded Excel workbooks into a single dataframe ready for normalization.
    """
    def __init__(self, COUNTER_report_files):
        """The constructor method for `UploadCOUNTERReports`, which sets the attribute values for each instance.

        This constructor is not meant to be used alone; all class instantiations should feature a `create_dataframe()` method call.

        Args:
            COUNTER_report_files (ImmutableMultiDict): the uploaded Excel workbook(s) of tabular COUNTER data
        """
        self.COUNTER_report_files = COUNTER_report_files
    

    def create_dataframe(self):
        """This method transforms tabular COUNTER reports in uploaded Excel workbooks into a single dataframe ready for normalization.

        This method transforms tabular COUNTER reports on sheets in Excel workbooks into dataframes, but to become complete and valid records in the relation, data not found in the tabular report is also required. The statistics source of the data will be derived from the Excel file name, which follows the naming convention `<Statistics_Source_ID>_<calendar year assigned to fiscal year in "yyyy" format>.xlsx` (the year is used for disambiguation and file name uniqueness, not data). For each individual report, the type of report is taken from the sheet name, which is the official report type abbreviation.

        Returns:
            dataframe: COUNTER data ready for normalization
        """
        pass