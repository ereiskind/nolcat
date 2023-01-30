import pathlib
import re
from datetime import date
import json
from openpyxl import load_workbook
import pandas as pd

absolute_path_to_tests_directory = pathlib.Path(__file__).parent.resolve()
directory_with_final_JSONs = absolute_path_to_tests_directory / 'data' / 'COUNTER_JSONs_for_tests'

# All methods for importing `app.py` from `nolcat` failed when running the module in both the VS Code debugger and Command Prompt, so the function is repeated here
def last_day_of_month(first_day_of_month):
    """The function for returning the last day of a given month.

    When COUNTER date ranges include the day, the "End_Date" value is for the last day of the month. This function consolidates that functionality in a single location and facilitates its use in pandas `map` functions.

    Args:
        first_day_of_month (pd.Timestamp): the first day of the month; the dataframe of origin will have the date in a datetime64[n] data type, but within this function, the data type is Timestamp
    
    Returns:
        str: the last day of the given month in ISO format
    """
    year_and_month_string = first_day_of_month.date().isoformat()[0:-2]  # Returns an ISO date string, then takes off the last two digits
    return year_and_month_string + str(first_day_of_month.days_in_month)


#Section: Load the Workbook(s)
file_path = input("Enter the complete file path for the Excel workbook output from OpenRefine: ")
file_path = pathlib.Path(file_path)
file = load_workbook(filename=file_path, read_only=True)
report_name = file_path.stem
report_type = report_name.split("_")[1]
sheet = file[report_name]


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


#Section: Create Dataframe
#Subsection: Ensure String Data Type for Potentially Numeric Metadata Fields
# Strings will be pandas object dtype at this point, but object to string conversion is fairly simple; string fields that pandas might automatically assign a numeric dtype to should be set as strings at the creation of the dataframe to head off problems.
df_dtypes = dict()
for field_name in df_field_names:
    if field_name == "Count":
        df_dtypes[field_name] = 'Int64'  # The pandas integer dtype; Python's 'int' is ignored
    else:  # JSON uses strings for dates; `Begin_Date` is changed to a date with the `converters` argument in `read_excel`
        df_dtypes[field_name] = 'string'

#Subsection: Create Dataframe from Excel Worksheet
df = pd.read_excel(
    file_path,
    sheet_name=report_name,
    engine='openpyxl',
    header=1,
    names=df_field_names,
    dtype=df_dtypes,
    converters={'Begin_Date': pd.to_datetime}  # `to_datetime` called as object, not function; adding `format` argument causes TypeError
)


#Section: Update Dataframe
df = df.replace(r'\n', '', regex=True)  # Removes errant newlines found in some reports, primarily at the end of resource names
df = df.replace("licence", "license")  # "Have `license` always use American English spelling
df['End_Date'] = df['Begin_Date'].map(last_day_of_month)
df['Begin_Date'] = df['Begin_Date'].dt.strftime('%Y-%m-%d')

#Subsection: Put Placeholder in for Null Values
'''
df = df.fillna("`None`")
df = df.replace(
    to_replace='^\s*$',
    # The regex is designed to find the blank but not null cells by finding those cells containing nothing (empty strings) or only whitespace. The whitespace metacharacter `\s` is marked with a deprecation warning, and without the anchors, the replacement is applied not just to whitespaces but to spaces between characters as well.
    value="`None`",
    regex=True
)
'''


#Section: Change Dataframe into JSON
#Subsection: Create Multiindex for Combining
fields_used_in_SUSHI_nested_groups = ['Begin_Date', 'End_Date', 'Metric_Type', 'Count']
fields_used_for_groupby_operations = [field_name for field_name in df_field_names if field_name not in fields_used_in_SUSHI_nested_groups]
fields_used_for_groupby_operations = [field_name for field_name in fields_used_for_groupby_operations if not df[field_name].isnull().all()]  # Series with nothing but null values cause ValueErrors later in the program, so they need to be removed
index_fields_for_join_operation = fields_used_for_groupby_operations + ['Begin_Date']

#Subsection: Create Instance Grouping
instance_groupby_operation_fields = fields_used_for_groupby_operations + ['Begin_Date']
instance_df = (df.groupby(instance_groupby_operation_fields)).apply(lambda instance: instance[['Metric_Type', 'Count']].to_dict('records')).reset_index().rename(columns={0: "Instance"})  # `instance_groupby_operation_fields` contains all the non-null fields that must be the same for all the records represented in a instance grouping plus a date field to keep instances where the metric and count are repeated from being combined
instance_df = instance_df.set_index(index_fields_for_join_operation)

#Subsection: Create Period Grouping
df['temp'] = range(1, len(df.index)+1)  # The way groupby works, for each resource defined by metadata, if a given instance (a metric and its count) occurs in multiple months, those months will be combined, which is not the desired behavior; this field puts a unique value in each row/record, which prevents this grouping
period_groupby_operation_fields = fields_used_for_groupby_operations + ['Metric_Type', 'Count', 'temp']
period_df = df.groupby(period_groupby_operation_fields).apply(lambda period: period[['Begin_Date','End_Date']].to_dict('records')).reset_index().rename(columns={0: "Period"})
period_df = period_df.drop(columns=['temp', 'Metric_Type', 'Count'])
period_df['Period'] = period_df['Period'].map(lambda list_like: list_like[0])
period_df['Begin_Date'] = period_df['Period'].astype('string').map(lambda string: string[16:-28])  # This turns the JSON/dict value into a string, then isolates the desired date from within each string
period_df = period_df.set_index(index_fields_for_join_operation)

#Subsection: Combine Period and Instance Groupings
combined_df = period_df.join(instance_df, how='inner')  # This contains duplicate records
combined_df = combined_df.reset_index()
combined_df = combined_df.drop(columns=['Begin_Date'])
combined_df['instance_string'] = combined_df['Instance'].astype('string')
combined_df['period_string'] = combined_df['Period'].astype('string')

#Subsection: Create Final JSON
combined_df['repeat'] = combined_df.duplicated(subset=['Platform', 'Data_Type', 'Access_Method', 'instance_string', 'period_string'], keep='first')
combined_df = combined_df.loc[combined_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
combined_df = combined_df.drop(columns=['instance_string', 'period_string', 'repeat'])
combined_df = combined_df.reset_index(drop=True)
final_df = combined_df.groupby(fields_used_for_groupby_operations).apply(lambda performance: performance[['Period', 'Instance']].to_dict('records')).reset_index().rename(columns={0: "Performance"})


#Section: Output JSON
final_df.to_json(directory_with_final_JSONs / 'result_JSON.json', force_ascii=False, indent=4, orient='table', index=False)