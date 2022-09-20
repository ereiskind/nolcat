"""This module outputs the test data used in the relations as TSVs. By running this module to create a TSV file, committing the file, and pushing the commit to GitHub, these file can be downloaded to a local machine for further manipulation in a spreadsheet program, like Excel."""

from pathlib import Path
import pyinputplus as pyip
import pandas as pd

from data import relations

relation_name = pyip.inputMenu(
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

try:
    TSV_file_name = Path('/', 'nolcat', 'tests', 'data', 'relation_TSVs', f'{relation_name}_relation.tsv')
    TSV_file = relation_data.to_csv(
        TSV_file_name,
        sep='\t',
        # na_rep=string of how nulls should be represented; defaults to empty strings
        # index_label=field label for record index; with defaults, the index name is used, but a sequence should be given if there's a MultiIndex
        # chunksize=number of records to write at a time as an int
        # date_format=format string for datetime object output
        # errors='backslashreplace',  # Replace with character sequences that need `.encode('utf-8').decode('unicode-escape')`
    )
    print(f"Using Path object and `relation_TSVs`\n`TSV_file_name` (type {type(TSV_file_name)}):\n{TSV_file_name}\n\n`TSV_file` (type {type(TSV_file)}):\n{TSV_file}\n\n")
except Exception as error1:
    try:
        TSV_file_name = Path('/', 'nolcat', 'tests', 'data', f'{relation_name}_relation.tsv')
        TSV_file = relation_data.to_csv(
            TSV_file_name,
            sep='\t',
            # na_rep=string of how nulls should be represented; defaults to empty strings
            # index_label=field label for record index; with defaults, the index name is used, but a sequence should be given if there's a MultiIndex
            # chunksize=number of records to write at a time as an int
            # date_format=format string for datetime object output
            # errors='backslashreplace',  # Replace with character sequences that need `.encode('utf-8').decode('unicode-escape')`
        )
        print(f"Using Path object; Path object with folder `relation_TSVs` caused error `{error1}`\n`TSV_file_name` (type {type(TSV_file_name)}):\n{TSV_file_name}\n\n`TSV_file` (type {type(TSV_file)}):\n{TSV_file}\n\n")
    except Exception as error2:
        try:
            TSV_file_name = f'{relation_name}_relation.tsv'
            TSV_file_name = r'/nolcat/tests/data/relation_TSVs/' + TSV_file_name
            TSV_file = relation_data.to_csv(
                TSV_file_name,
                sep='\t',
                # na_rep=string of how nulls should be represented; defaults to empty strings
                # index_label=field label for record index; with defaults, the index name is used, but a sequence should be given if there's a MultiIndex
                # chunksize=number of records to write at a time as an int
                # date_format=format string for datetime object output
                # errors='backslashreplace',  # Replace with character sequences that need `.encode('utf-8').decode('unicode-escape')`
            )
            print(f"Using string and `relation_TSVs`; Path object with folder `relation_TSVs` caused error `{error1}`; Path object without folder `relation_TSVs` caused error `{error2}`\n`TSV_file_name` (type {type(TSV_file_name)}):\n{TSV_file_name}\n\n`TSV_file` (type {type(TSV_file)}):\n{TSV_file}\n\n")
        except Exception as error3:
            try:
                TSV_file_name = f'{relation_name}_relation.tsv'
                TSV_file_name = r'/nolcat/tests/data/' + TSV_file_name
                TSV_file = relation_data.to_csv(
                    TSV_file_name,
                    sep='\t',
                    # na_rep=string of how nulls should be represented; defaults to empty strings
                    # index_label=field label for record index; with defaults, the index name is used, but a sequence should be given if there's a MultiIndex
                    # chunksize=number of records to write at a time as an int
                    # date_format=format string for datetime object output
                    # errors='backslashreplace',  # Replace with character sequences that need `.encode('utf-8').decode('unicode-escape')`
                )
                print(f"Using string; Path object with folder `relation_TSVs` caused error `{error1}`; Path object without folder `relation_TSVs` caused error `{error2}`; string with folder `relation_TSVs` caused error `{error3}`\n`TSV_file_name` (type {type(TSV_file_name)}):\n{TSV_file_name}\n\n`TSV_file` (type {type(TSV_file)}):\n{TSV_file}\n\n")
            except Exception as error4:
                print(f"Path object with folder `relation_TSVs` caused error `{error1}`; Path object without folder `relation_TSVs` caused error `{error2}`; string with folder `relation_TSVs` caused error `{error3}`; string without folder `relation_TSVs` caused error `{error4}`.")