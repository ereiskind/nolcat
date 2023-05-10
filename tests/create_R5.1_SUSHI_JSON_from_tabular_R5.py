"""Transform Excel worksheet produced by "tests\\data\\create_JSON_base.json" into a COUNTER R5.1 SUSHI JSON. This module requires pandas 1.4 or higher to run due to the bug described at https://github.com/pandas-dev/pandas/pull/43949."""

import logging
import pathlib
import io
import re
import json
from openpyxl import load_workbook
import pandas as pd


# `from ..nolcat import app` raises `ImportError: attempted relative import with no known parent package`
# `from nolcat import app` raises `ModuleNotFoundError: No module named 'nolcat'`
# `from .. import nolcat` raises `ImportError: attempted relative import with no known parent package`
# `from .nolcat import app` raises `ImportError: attempted relative import with no known parent package`
# `from nolcat.app import return_string_of_dataframe_info` raises `ModuleNotFoundError: No module named 'nolcat'`

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

absolute_path_to_tests_directory = pathlib.Path(__file__).parent.resolve()
directory_with_final_JSONs = absolute_path_to_tests_directory / 'data' / 'R5.1_COUNTER_JSONs_for_tests'


def return_string_of_dataframe_info(df):
    # This is a copy of a function in `nolcat.nolcat.app`, which can't be imported
    in_memory_stream = io.StringIO()
    df.info(buf=in_memory_stream)
    return in_memory_stream.getvalue()


def last_day_of_month(first_day_of_month):
    # This is a copy of a function in `nolcat.nolcat.app`, which can't be imported
    year_and_month_string = first_day_of_month.date().isoformat()[0:-2]  # Returns an ISO date string, then takes off the last two digits
    return year_and_month_string + str(first_day_of_month.days_in_month)


#Section: Load the Workbook(s)
file_path = input("Enter the complete file path for the Excel workbook output from OpenRefine: ")
file_path = pathlib.Path(file_path)
file = load_workbook(filename=file_path, read_only=True)
report_name = file_path.stem
report_type = report_name.split("_")[1]
sheet = file[report_name]
logging.info(f"Creating JSON from report {report_name} for a {report_type}.")


#Section: Get the Field Names
# Excel workbooks created by Apache POI programs like OpenRefine don't have their `max_column` and `max_row` attributes set properly, so those values must be reset, after which a loop through rows that breaks after the first row can be used
sheet.reset_dimensions()
df_field_names = []
for row in sheet.rows:
    for field_name in row:
        
        # `None` in regex methods raises a TypeError, so they need to be in try-except blocks
        try:
            if re.match(r'^[Cc]omponent', field_name.value):
                continue  # The rarely used `Component` subtype fields aren't captured by this program
        except TypeError:
            pass
        
        if field_name.value is None:
            continue  # Deleted data and merged cells for header values can make Excel think null columns are in use; when read, these columns add `None` to `df_field_names`, causing a `ValueError: Number of passed names did not patch number of header fields in the file` when reading the worksheet contents into a dataframe
        else:
            df_field_names.append(field_name.value)
    break
logging.info(f"The field names are {df_field_names}.")


#Section: Create Dataframe
#Subsection: Ensure String Data Type for Potentially Numeric Metadata Fields
# Strings will be pandas object dtype at this point, but object to string conversion is fairly simple; string fields that pandas might automatically assign a numeric dtype to should be set as strings at the creation of the dataframe to head off problems.
df_dtypes = dict()
for field_name in df_field_names:
    if field_name == "Count" or field_name == "YOP":
        df_dtypes[field_name] = 'Int64'  # The pandas integer dtype; Python's 'int' is ignored
    else:  # JSON uses strings for dates; `Begin_Date` is changed to a date with the `converters` argument in `read_excel`
        df_dtypes[field_name] = 'string'

#Subsection: Create Dataframe from Excel Worksheet
df = pd.read_excel(
    file_path,
    sheet_name=report_name,
    engine='openpyxl',
    header=0,  # This means the first row of the spreadsheet will be treated as the row with the headers, meaning the data starts on the second row
    names=df_field_names,
    dtype=df_dtypes,
    converters={  # `to_datetime` called as object, not function; adding `format` argument causes TypeError
    'Begin_Date': pd.to_datetime,
    'Publication_Date': pd.to_datetime,
    'Parent_Publication_Date': pd.to_datetime,
    }
)
logging.debug(f"Complete dataframe:\n{df}")
logging.info(f"Dataframe summary info:\n{return_string_of_dataframe_info(df)}")


#Section: Update Dataframe
df = df.replace(r'\n', '', regex=True)  # Removes errant newlines found in some reports, primarily at the end of resource names
df = df.replace("licence", "license")  # "Have `license` always use American English spelling
try:
    df['Begin_Date'] = df['Begin_Date'].dt.strftime('%Y-%m-%d')
except:
    df['Begin_Date'] = pd.to_datetime(df['Begin_Date'])
    df['Begin_Date'] = df['Begin_Date'].dt.strftime('%Y-%m-%d')

#Subsection: Put Placeholder in for Null Values
# Null values and fields with nothing but null values cause problems and errors in groupby functions, so they're replaced with placeholder strings
df = df.fillna("`None`")
df = df.replace(
    to_replace='^\s*$',
    # The regex is designed to find the blank but not null cells by finding those cells containing nothing (empty strings) or only whitespace. The whitespace metacharacter `\s` is marked with a deprecation warning, and without the anchors, the replacement is applied not just to whitespaces but to spaces between characters as well.
    value="`None`",
    regex=True
)
logging.debug(f"Dataframe after initial updates:\n{df}")
####################
output = df.copy()
purpose = "after-initial-updates"
number = 1
output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
try:
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=False)
except ValueError:
    new_index_names = {name:f"_index_{name}" for name in output.index.names}
    output.index = output.index.set_names(new_index_names)
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################


######Section: CHANGE DATAFRAME INTO JSON #####

#Section: Create Field Lists and Dataframes for Multiindexes, Groupby Operations, and Dataframe Recombination
fields_in_performance = ['Begin_Date', 'Metric_Type', 'Count']
metadata_multiindex_fields = [field_name for field_name in df_field_names if field_name not in fields_in_performance]

fields_used_in_join_multiindex = metadata_multiindex_fields + ['Begin_Date']
join_multiindex_df = df[fields_used_in_join_multiindex].set_index(metadata_multiindex_fields, drop=False)
####################
#output = join_multiindex_df.copy()
#purpose = "multiindex-for-joining"
#number = number + 1
#output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
#try:
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=False)
#except ValueError:
#    new_index_names = {name:f"_index_{name}" for name in output.index.names}
#    output.index = output.index.set_names(new_index_names)
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
groupby_multiindex = [f"index_{field_name}" for field_name in metadata_multiindex_fields]  # All sections have `index_` appended to the beginning of the index field names before the index reset for record deduplication, so `index_` needs to be at the beginning of the fields in the list in the groupby operation
fields_to_drop_at_end = []

# The default text sorting methods in OpenRefine and Pandas order non-letter characters differently, meaning applying a pandas sort to the resource names won't put them in the same order as they were in openRefine after the sort; to return the records to their same order at the end of the module, their order must be saved at this point
record_sorting_strings = df[metadata_multiindex_fields].apply(
    lambda cell_value: '|'.join(cell_value.astype(str)),  # Combines all values in the fields specified by the index operator of the dataframe to which the `apply` method is applied
    axis='columns',
)
record_sorting_strings = record_sorting_strings.drop_duplicates().reset_index(drop=True)
logging.debug(f"Complete metadata in order from OpenRefine:\n{record_sorting_strings}")
record_sorting_dict = record_sorting_strings.to_dict()
record_sorting_dict = {metadata_string: order_number for (order_number, metadata_string) in record_sorting_dict.items()}
logging.info(f"Metadata strings with ordering numbers:\n{record_sorting_dict}")

#Subsection: Create `Attribute_Performance` Metadata Field Lists
fields_outside_attribute_performance = [
    "Platform",  # PR
]
metadata_outside_attribute_performance = [field for field in df_field_names if field in fields_outside_attribute_performance]

fields_inside_attribute_performance = [
    "Data_Type",  # PR
    "Access_Method",  # PR
]
metadata_inside_attribute_performance = [field for field in df_field_names if field in fields_inside_attribute_performance]

#Section: Organize Metadata Outside `Attribute_Performance`
outside_attribute_performance_df = join_multiindex_df.copy()
outside_attribute_performance_df = outside_attribute_performance_df[metadata_outside_attribute_performance]
####################
#output = outside_attribute_performance_df.copy()
#purpose = "create-outside-attribute-df"
#number = number + 1
#output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
#try:
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
#except ValueError:
#    new_index_names = {name:f"_index_{name}" for name in output.index.names}
#    output.index = output.index.set_names(new_index_names)
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
outside_attribute_performance_df = outside_attribute_performance_df.replace({"`None`": None})
outside_attribute_performance_index_names = {field_name:f"index_{field_name}" for field_name in outside_attribute_performance_df.index.names}
outside_attribute_performance_df.index = outside_attribute_performance_df.index.set_names(outside_attribute_performance_index_names)
####################
#output = outside_attribute_performance_df.copy()
#purpose = "outside-attribute-df-rename-index"
#number = number + 1
#output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
#try:
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
#except ValueError:
#    new_index_names = {name:f"_index_{name}" for name in output.index.names}
#    output.index = output.index.set_names(new_index_names)
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
outside_attribute_performance_df = outside_attribute_performance_df.reset_index()
####################
#output = outside_attribute_performance_df.copy()
#purpose = "outside-attribute-df-index-reset"
#number = number + 1
#output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
#try:
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=False)
#except ValueError:
#    new_index_names = {name:f"_index_{name}" for name in output.index.names}
#    output.index = output.index.set_names(new_index_names)
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
outside_attribute_performance_df['repeat'] = outside_attribute_performance_df.duplicated(keep='first')
outside_attribute_performance_df =  outside_attribute_performance_df.loc[outside_attribute_performance_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
outside_attribute_performance_df =  outside_attribute_performance_df.drop(columns=['repeat'])
####################
#output = outside_attribute_performance_df.copy()
#purpose = "outside-attribute-df-remove-duplicate-records"
#number = number + 1
#output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
#try:
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=False)
#except ValueError:
#    new_index_names = {name:f"_index_{name}" for name in output.index.names}
#    output.index = output.index.set_names(new_index_names)
#    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
outside_attribute_performance_df = outside_attribute_performance_df.set_index([field_name for field_name in outside_attribute_performance_index_names.values()])
####################
output = outside_attribute_performance_df.copy()
purpose = "outside-attribute-df-restore-index"
number = number + 1
output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
try:
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
except ValueError:
    new_index_names = {name:f"_index_{name}" for name in output.index.names}
    output.index = output.index.set_names(new_index_names)
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
logging.debug(f"`outside_attribute_performance_df`\n{outside_attribute_performance_df}")

#Section: Organize Metadata Inside `Attribute_Performance` Metadata
inside_attribute_performance_df = join_multiindex_df.copy()
inside_attribute_performance_df = inside_attribute_performance_df[metadata_inside_attribute_performance]
####################
output = inside_attribute_performance_df.copy()
purpose = "create-inside-attribute-df"
number = number + 1
output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
try:
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
except ValueError:
    new_index_names = {name:f"_index_{name}" for name in output.index.names}
    output.index = output.index.set_names(new_index_names)
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
inside_attribute_performance_df = inside_attribute_performance_df.replace({"`None`": None})
inside_attribute_performance_index_names = {field_name:f"index_{field_name}" for field_name in inside_attribute_performance_df.index.names}
inside_attribute_performance_df.index = inside_attribute_performance_df.index.set_names(inside_attribute_performance_index_names)
####################
output = inside_attribute_performance_df.copy()
purpose = "inside-attribute-df-rename-index"
number = number + 1
output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
try:
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
except ValueError:
    new_index_names = {name:f"_index_{name}" for name in output.index.names}
    output.index = output.index.set_names(new_index_names)
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
inside_attribute_performance_df = inside_attribute_performance_df.reset_index()
####################
output = inside_attribute_performance_df.copy()
purpose = "inside-attribute-df-index-reset"
number = number + 1
output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
try:
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=False)
except ValueError:
    new_index_names = {name:f"_index_{name}" for name in output.index.names}
    output.index = output.index.set_names(new_index_names)
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################
inside_attribute_performance_df['repeat'] = inside_attribute_performance_df.duplicated(keep='first')
inside_attribute_performance_df =  inside_attribute_performance_df.loc[inside_attribute_performance_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
inside_attribute_performance_df =  inside_attribute_performance_df.drop(columns=['repeat'])
####################
output = inside_attribute_performance_df.copy()
purpose = "inside-attribute-df-remove-duplicate-records"
number = number + 1
output.to_csv(directory_with_final_JSONs / f'__{number}_test_{purpose}.csv', encoding='utf-8', errors='backslashreplace')
try:
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=False)
except ValueError:
    new_index_names = {name:f"_index_{name}" for name in output.index.names}
    output.index = output.index.set_names(new_index_names)
    output.to_json(directory_with_final_JSONs / f'__{number}_test_{purpose}.json', force_ascii=False, indent=4, orient='table', index=True)
####################

#Section: Organize Metadata in `Performance`


#####################################
#Section: Create Nested JSON Section for Publisher IDs



#Section: Create Nested JSON Section for Item IDs
#Subsection: Create Nested JSON Section for DR Item IDs



#Subsection: Create Nested JSON Section for TR and IR Item IDs


            #Subsection: Determine All the Fields Going in the Nested Section
            

            #Subsection: Remove Fields Not Being Nested
            

            #Subsection: Remove Null Values and Repetitions
            

            #Subsection: Complete Nested JSON Section for Item IDs
            


#Section: Create Nested JSON Section for Authors



#Section: Create Nested JSON Section for Publication Date


#Section: Create Nested JSON Section for Article Version



#Section: Create Nested JSON Section for Item Parent Data


            #Subsection: Determine All the Fields Going in the Nested Section
            
            
            #Subsection: Remove Fields Not Being Nested
            

            #Subsection: Prepare for Inner Nesting
            

            #Subsection: Remove Null Values and Repetitions
            

            #Subsection: Create Inner Nested JSON Section for Author
            

            #Subsection: Create Inner Nested JSON Section for Publication Date
            

            #Subsection: Create Inner Nested JSON Section for Article Version
            

            #Subsection: Create Inner Nested JSON Section for Item IDs
            

            #Subsection: Deduplicate Dataframe with All Inner Nested Sections
            

            #Subsection: Combine All Inner Nested Sections
            

#Section: Create Nested JSON Section for Performance
#Subsection: Create Instance Grouping

#Subsection: Create Period Grouping



#Section: Combine Nested JSON Groupings
#Subsection: Combine Period and Instance Groupings


#Subsection: Deduplicate Records


#Subsection: Create Performance Grouping


#Subsection: Add Other JSON Groupings


#Section: Create Final JSON
#Subsection: Restore Initial Record Order


#Subsection: Organize Fields and Data Types
