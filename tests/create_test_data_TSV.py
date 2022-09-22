"""This module outputs the test data used in the relations as TSVs. By running this module to create a TSV file, committing the file, and pushing the commit to GitHub, these file can be downloaded to a local machine for further manipulation in a spreadsheet program, like Excel."""

import os
from pathlib import Path
import pyinputplus as pyip
import pandas as pd

from data import relations
from data import COUNTER_reports

relation_name = pyip.inputMenu(
    prompt="Enter the number of the test data dataframe that should be output to a TSV.\n",
    choices=[
        "fiscalYears",
        "vendors",
        #"vendorNotes",  #ToDo: Uncomment when dataframe is created
        "statisticsSources",
        #"statisticsSourceNotes",  #ToDo: Uncomment when dataframe is created
        "statisticsResourceSources",
        "resourceSources",
        #"resourceSourceNotes",  #ToDo: Uncomment when dataframe is created
        "annualUsageCollectionTracking",
        "resources",
        "resourceMetadata",
        "resourcePlatforms",
        "usageData",
    ],
    numbered=True,
)

if relation_name == "fiscalYears":
    relation_data = relations.fiscalYears_relation()
elif relation_name == "vendors":
    relation_data = relations.vendors_relation()
elif relation_name == "vendorNotes":
    #relation_data = relations.vendorNotes_relation()
    pass  #ToDo: Update when dataframe is created 
elif relation_name == "statisticsSources":
    relation_data = relations.statisticsSources_relation()
elif relation_name == "statisticsSourceNotes":
    #relation_data = relations.statisticsSourceNotes_relation()
    pass  #ToDo: Update when dataframe is created
elif relation_name == "statisticsResourceSources":
    relation_data = relations.statisticsResourceSources_relation()
elif relation_name == "resourceSources":
    relation_data = relations.resourceSources_relation()
elif relation_name == "resourceSourceNotes":
    #relation_data = relations.resourceSourceNotes_relation()
    pass  #ToDo: Update when dataframe is created
elif relation_name == "annualUsageCollectionTracking":
    relation_data = relations.annualUsageCollectionTracking_relation()
elif relation_name == "resources":
    relation_data = relations.resources_relation()
elif relation_name == "resourceMetadata":
    relation_data = relations.resourceMetadata_relation()
elif relation_name == "resourcePlatforms":
    relation_data = relations.resourcePlatforms_relation()
elif relation_name == "usageData":
    relation_data = relations.usageData_relation()

# Ideally, this module can run in the container in the AWS instance, but an inability to authenticate from that command line to GitHub makes running the module on the local machine the only way to access the TSVs on the local machine. This module is thus set up to determine if it's running in the AWS instance or on a local machine and create a `pathlib.Path` object for the absolute path of the file based on the environment and folder the module is run from.
TSV_file_name = Path('/', 'nolcat', 'tests', 'data')
if TSV_file_name.exists():
    TSV_file_name = TSV_file_name / f'{relation_name}_relation.tsv'
else:
    TSV_file_name_start_elements = os.getcwd().split('nolcat')[0].split('\\')
    TSV_file_name_start = Path(TSV_file_name_start_elements[0], '/')
    for element in TSV_file_name_start_elements[1:-1]:  # This removes the drive letter from the beginning and the empty string from the end
        TSV_file_name_start = TSV_file_name_start / element
    TSV_file_name = TSV_file_name_start / 'nolcat' / 'tests' / 'data' / f'{relation_name}_relation.tsv'

TSV_file = relation_data.to_csv(
    TSV_file_name,
    sep='\t',
    encoding='utf-16',  # Using the `utf-8` encoding, opening TSV directly in Excel causes encoding issues, but `utf-16` is fine
    # `None` values in dataframes meet Excel's `isblank` criteria in TSVs, so `na_rep=` argument left as default
    # Dates are ISO-formatted strings when opened in text editors and date data types when opened in Excel, so `date_format=` argument left as default
)