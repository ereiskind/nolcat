"""To ensure no encoding problems found in tests are from importing the test data for relations from other file types, that data is contained in the `conftest.py` fixtures for the relations. Having this data in a tabular format will also be needed at times, but having the data in both `conftest.py` and a tabular file could risk the files getting out of sync, so this function will instead produce the tabular file with data from the fixture on demand."""

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

if fixture == "fiscalYears":
    from conftest import fiscalYears_relation
    fixture = fiscalYears_relation
elif fixture == "vendors":
    from conftest import vendors_relation
    fixture = vendors_relation
#ToDo: vendorNotes
elif fixture == "statisticsSources":
    from conftest import statisticsSources_relation
    fixture = statisticsSources_relation
#ToDo: statisticsSourceNotes
elif fixture == "statisticsResourceSources":
    from conftest import statisticsResourceSources_relation
    fixture = statisticsResourceSources_relation
elif fixture == "resourceSources":
    from conftest import resourceSources_relation
    fixture = resourceSources_relation
#ToDo: resourceSourceNotes
elif fixture == "annualUsageCollectionTracking":
    from conftest import annualUsageCollectionTracking_relation
    fixture = annualUsageCollectionTracking_relation
elif fixture == "resources":
    from conftest import resources_relation
    fixture = resources_relation
elif fixture == "resourceMetadata":
    from conftest import resourceMetadata_relation
    fixture = resourceMetadata_relation
elif fixture == "resourcePlatforms":
    from conftest import resourcePlatforms_relation
    fixture = resourcePlatforms_relation
elif fixture == "usageData":
    from conftest import usageData_relation
    fixture = usageData_relation

print(type(fixture))
print(fixture)