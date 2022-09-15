"""This module outputs the test data used in the relations as TSVs."""

import pyinputplus as pyip

fixture = pyip.inputMenu(
    prompt="Enter the number of the relation that should be output to a TSV.\n",
    choices=[
        "fiscalYears",
        "vendors",
        #ToDo: vendorNotes,
        "statisticsSources",
        #ToDo: statisticsSourceNotes,
        "statisticsResourceSources",
        "resourceSources",
        #ToDo: resourceSourceNotes,
        "annualUsageCollectionTracking",
        "resources",
        "resourceMetadata",
        "resourcePlatforms",
        "usageData",
    ],
    numbered=True,
)

print(type(fixture))
print(fixture)