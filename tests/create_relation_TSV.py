"""This module outputs the test data used in the relations as TSVs."""

import pyinputplus as pyip

from .data import relations

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

print(type(fixture))
print(fixture)