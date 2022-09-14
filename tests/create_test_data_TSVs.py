"""To ensure no encoding problems found in tests are from importing the test data for relations from other file types, that data is contained in the `conftest.py` fixtures for the relations. Having this data in a tabular format will also be needed at times, but having the data in both `conftest.py` and a tabular file could risk the files getting out of sync, so this function will instead produce the tabular file with data from the fixture on demand."""

import pyinputplus as pyip

fixture = pyip.inputMenu(
    prompt="Enter the number of the relation that should be output to a TSV. ",
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

print(fixture)