"""This module outputs the test data used in the relations as TSVs."""

import pyinputplus as pyip
import pandas as pd

from data import relations

fixture = pyip.inputMenu(
    prompt="Enter the number of the relation that should be output to a TSV.\n",
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

if fixture == "fiscalYears":
    fixture = relations.fiscalYears_relation()
elif fixture == "vendors":
    fixture = relations.vendors_relation()
elif fixture == "vendorNotes":
    #fixture = relations.vendorNotes_relation()
    pass  #ToDo: Update when dataframe is created 
elif fixture == "statisticsSources":
    fixture = relations.statisticsSources_relation()
elif fixture == "statisticsSourceNotes":
    #fixture = relations.statisticsSourceNotes_relation()
    pass  #ToDo: Update when dataframe is created
elif fixture == "statisticsResourceSources":
    fixture = relations.statisticsResourceSources_relation()
elif fixture == "resourceSources":
    fixture = relations.resourceSources_relation()
elif fixture == "resourceSourceNotes":
    #fixture = relations.resourceSourceNotes_relation()
    pass  #ToDo: Update when dataframe is created
elif fixture == "annualUsageCollectionTracking":
    fixture = relations.annualUsageCollectionTracking_relation()
elif fixture == "resources":
    fixture = relations.resources_relation()
elif fixture == "resourceMetadata":
    fixture = relations.resourceMetadata_relation()
elif fixture == "resourcePlatforms":
    fixture = relations.resourcePlatforms_relation()
elif fixture == "usageData":
    fixture = relations.usageData_relation()

TSV_file = fixture.to_csv(
    #ToDo: `Path` or write() object for where the file should go
    sep='\t',
    # na_rep=string of how nulls should be represented; defaults to empty strings
    # index_label=field label for record index; with defaults, the index name is used, but a sequence should be given if there's a MultiIndex
    # encoding='utf-8', not supported if path or buff is non-binary file object
    # chunksize=number of records to write at a time as an int
    # date_format=format string for datetime object output
    # errors='backslashreplace',  # Replace with character sequences that need `.encode('utf-8').decode('unicode-escape')`
)

print(TSV_file)