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
    if field_name == "Count" or field_name == "YOP":
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
    converters={  # `to_datetime` called as object, not function; adding `format` argument causes TypeError
    'Begin_Date': pd.to_datetime,
    'Publication_Date': pd.to_datetime,
    'Parent_Publication_Date': pd.to_datetime,
    }
)


#Section: Update Dataframe
df = df.replace(r'\n', '', regex=True)  # Removes errant newlines found in some reports, primarily at the end of resource names
df = df.replace("licence", "license")  # "Have `license` always use American English spelling
df['End_Date'] = df['Begin_Date'].map(last_day_of_month)
df['Begin_Date'] = df['Begin_Date'].dt.strftime('%Y-%m-%d')
if 'YOP' in list(df.columns):
    df['YOP'] = df['YOP'].astype('string')  # Setting the dtype to string when reading in the data means every value in the field ends with `.0`

#Subsection: Put Placeholder in for Null Values
# Null values and fields with nothing but null values cause problems and errors in groupby functions, so they're replaced with placeholder strings
df = df.fillna("`None`")
df = df.replace(
    to_replace='^\s*$',
    # The regex is designed to find the blank but not null cells by finding those cells containing nothing (empty strings) or only whitespace. The whitespace metacharacter `\s` is marked with a deprecation warning, and without the anchors, the replacement is applied not just to whitespaces but to spaces between characters as well.
    value="`None`",
    regex=True
)


######Section: CHANGE DATAFRAME INTO JSON #####

#Section: Create Field Lists and Dataframes for Multiindexes, Groupby Operations, and Dataframe Recombination
fields_used_in_performance_nested_groups = ['Begin_Date', 'End_Date', 'Metric_Type', 'Count']
fields_used_for_groupby_operations = [field_name for field_name in df_field_names if field_name not in fields_used_in_performance_nested_groups]

fields_used_in_performance_join_multiindex = fields_used_for_groupby_operations + ['Begin_Date']
performance_join_multiindex_df = df[fields_used_in_performance_join_multiindex].set_index(fields_used_for_groupby_operations, drop=False)
fields_to_drop_at_end = []


#Section: Create Nested JSON Section for Publisher IDs
if 'Publisher_ID' in list(performance_join_multiindex_df.columns):  # If the publisher ID field exists
    fields_to_drop_at_end.append('Publisher_ID')
    if not performance_join_multiindex_df['Publisher_ID'].eq("`None`").all():  # If the publisher ID field has values
        publisher_ID_values_df = performance_join_multiindex_df.copy()
        non_publisher_ID_fields = [field_name for field_name in fields_used_for_groupby_operations if field_name != "Publisher_ID"]
        publisher_ID_values_df = publisher_ID_values_df.drop(columns=non_publisher_ID_fields)
        publisher_ID_values_df['Type'] = "Proprietary"
        publisher_ID_values_df = publisher_ID_values_df.rename(columns={"Publisher_ID": "Value"})
        publisher_ID_values_df = publisher_ID_values_df.reset_index()
        publisher_ID_values_df['repeat'] = publisher_ID_values_df.duplicated(subset=fields_used_for_groupby_operations, keep='first')
        publisher_ID_values_df =  publisher_ID_values_df.loc[publisher_ID_values_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
        publisher_ID_values_df =  publisher_ID_values_df.drop(columns=['repeat'])
        publisher_ID_values_df = (publisher_ID_values_df.groupby(fields_used_for_groupby_operations)).apply(lambda publisher_ID: publisher_ID[['Type', 'Value']].to_dict('records')).rename("Publisher_ID")


#Section: Create Nested JSON Section for Item IDs
if 'DOI' in list(performance_join_multiindex_df.columns) or 'Proprietary_ID' in list(performance_join_multiindex_df.columns) or 'ISBN' in list(performance_join_multiindex_df.columns) or 'Print_ISSN' in list(performance_join_multiindex_df.columns) or 'Online_ISSN' in list(performance_join_multiindex_df.columns) or 'URI' in list(performance_join_multiindex_df.columns):  # If the fields in the item ID section exist
    if not performance_join_multiindex_df['DOI'].eq("`None`").all() or not performance_join_multiindex_df['Proprietary_ID'].eq("`None`").all() or not performance_join_multiindex_df['ISBN'].eq("`None`").all() or not performance_join_multiindex_df['Print_ISSN'].eq("`None`").all() or not performance_join_multiindex_df['Online_ISSN'].eq("`None`").all() or not performance_join_multiindex_df['URI'].eq("`None`").all():  # If the fields in the item ID section have values
        item_ID_values_df = performance_join_multiindex_df.copy()

        #Subsection: Determine All the Fields Going in the Nested Section
        possible_fields_in_item_ID = ['DOI', 'Proprietary_ID', 'ISBN', 'Print_ISSN', 'Online_ISSN', 'URI']
        fields_in_item_ID = []
        for field_name in item_ID_values_df.columns:
            if field_name in possible_fields_in_item_ID:
                fields_to_drop_at_end.append(field_name)
                if not item_ID_values_df[field_name].eq("`None`").all():
                    fields_in_item_ID.append(field_name)

        #Subsection: Remove Fields Not Being Nested
        non_item_ID_fields = [field_name for field_name in fields_used_for_groupby_operations if field_name not in fields_in_item_ID]
        item_ID_values_df = item_ID_values_df.drop(columns=non_item_ID_fields).drop(columns=['Begin_Date'])
        item_ID_values_df = item_ID_values_df.stack().reset_index()  # If the index isn't reset, the stack method returns a series
        item_ID_values_df = item_ID_values_df.rename(columns={item_ID_values_df.columns[-2]: 'Type', 0: 'Value'})  # The name of the `Type` field is `level_#` where `#` is the position in a zero-based order of the columns in the dataframe; since the exact name that needs to be changed cannot be know in advanced, it must be found from its penultimate position in the list of field names

        #Subsection: Remove Null Values and Repetitions
        item_ID_values_df = item_ID_values_df.loc[item_ID_values_df['Value'] != "`None`"]
        item_ID_values_df['repeat'] = item_ID_values_df.duplicated(keep='first')
        item_ID_values_df = item_ID_values_df.loc[item_ID_values_df['repeat'] == False]
        item_ID_values_df = item_ID_values_df.drop(columns=['repeat'])

        #Subsection: Complete Nested JSON Section for Item IDs
        item_ID_values_df = (item_ID_values_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_ID: item_ID[['Type', 'Value']].to_dict('records')).rename("Item_ID")


#Section: Create Nested JSON Section for Authors
if 'Authors' in list(performance_join_multiindex_df.columns):  # If the author field exists
    fields_to_drop_at_end.append('Authors')
    if not performance_join_multiindex_df['Authors'].eq("`None`").all():  # If the author field has values
        author_values_df = performance_join_multiindex_df.copy()
        non_author_fields = [field_name for field_name in fields_used_for_groupby_operations if field_name != "Authors"]
        author_values_df = author_values_df.drop(columns=non_author_fields)
        author_values_df['Type'] = "Author"
        author_values_df = author_values_df.rename(columns={"Authors": "Name"})
        author_values_df = author_values_df.reset_index()
        author_values_df['repeat'] = author_values_df.duplicated(subset=fields_used_for_groupby_operations, keep='first')
        author_values_df =  author_values_df.loc[author_values_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
        author_values_df =  author_values_df.drop(columns=['repeat'])
        author_values_df = (author_values_df.groupby(fields_used_for_groupby_operations)).apply(lambda authors: authors[['Type', 'Name']].to_dict('records')).rename("Item_Contributors")  # `Item_Contributors` uses `Type` and `Name` as the keys in its dictionaries


#Section: Create Nested JSON Section for Publication Date
if 'Publication_Date' in list(performance_join_multiindex_df.columns):  # If the publication date field exists
    fields_to_drop_at_end.append('Publication_Date')
    if not performance_join_multiindex_df['Publication_Date'].eq("`None`").all():  # If the publication date field has values
        publication_date_values_df = performance_join_multiindex_df.copy()
        publication_date_values_df['Publication_Date'] = publication_date_values_df['Publication_Date'].dt.strftime('%Y-%m-%d')
        non_publication_date_fields = [field_name for field_name in fields_used_for_groupby_operations if field_name != "Publication_Date"]
        publication_date_values_df = publication_date_values_df.drop(columns=non_publication_date_fields)
        publication_date_values_df['Type'] = "Publication_Date"
        publication_date_values_df = publication_date_values_df.rename(columns={"Publication_Date": "Value"})
        publication_date_values_df = publication_date_values_df.reset_index()
        publication_date_values_df['repeat'] = publication_date_values_df.duplicated(subset=fields_used_for_groupby_operations, keep='first')
        publication_date_values_df =  publication_date_values_df.loc[publication_date_values_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
        publication_date_values_df =  publication_date_values_df.drop(columns=['repeat'])
        publication_date_values_df = (publication_date_values_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_dates: item_dates[['Type', 'Value']].to_dict('records')).rename("Item_Dates")


#Section: Create Nested JSON Section for Article Version
if 'Article_Version' in list(performance_join_multiindex_df.columns):  # If the article version field exists
    fields_to_drop_at_end.append('Article_Version')
    if not performance_join_multiindex_df['Article_Version'].eq("`None`").all():  # If the article version field has values
        article_version_values_df = performance_join_multiindex_df.copy()
        non_article_version_fields = [field_name for field_name in fields_used_for_groupby_operations if field_name != "Article_Version"]
        article_version_values_df = article_version_values_df.drop(columns=non_article_version_fields)
        article_version_values_df['Type'] = "Article_Version"
        article_version_values_df = article_version_values_df.rename(columns={"Article_Version": "Value"})
        article_version_values_df = article_version_values_df.reset_index()
        article_version_values_df['repeat'] = article_version_values_df.duplicated(subset=fields_used_for_groupby_operations, keep='first')
        article_version_values_df =  article_version_values_df.loc[article_version_values_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
        article_version_values_df =  article_version_values_df.drop(columns=['repeat'])
        article_version_values_df = (article_version_values_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_attributes: item_attributes[['Type', 'Value']].to_dict('records')).rename("Item_Attributes")


#Section: Create Nested JSON Section for Item Parent Data
# Parent data fields and their labels with nesting in the JSON
    # Parent_Title --> Item_Parent > Item_Name
    # Parent_Authors --> Item_Parent > Item_Contributors > Name
    # Parent_Publication_Date --> Item_Parent > Item_Dates > Value
    # Parent_Article_Version --> Item_Parent > Item_Attributes > Value
    # Parent_Data_Type --> Item_Parent > Data_Type
    # Parent_DOI --> Item_Parent > Item_ID > Value
    # Parent_Proprietary_ID --> Item_Parent > Item_ID > Value
    # Parent_ISBN --> Item_Parent > Item_ID > Value
    # Parent_Print_ISSN --> Item_Parent > Item_ID > Value
    # Parent_Online_ISSN --> Item_Parent > Item_ID > Value
    # Parent_URI --> Item_Parent > Item_ID > Value
#ToDo: if '' in list(performance_join_multiindex_df.columns) or...:  # If the fields in the item parent section exist
    #ToDo: if not performance_join_multiindex_df[''].eq("`None`").all() or...:  # If the fields in the item parent section have values
        #ToDo: item_parent_values_df = performance_join_multiindex_df.copy()

        #Subsection: Determine All the Fields Going in the Nested Section
        #ToDo: possible_fields_in_item_parent = ['Parent_Title', 'Parent_Authors', 'Parent_Publication_Date', 'Parent_Article_Version', 'Parent_Data_Type', 'Parent_DOI', 'Parent_Proprietary_ID', 'Parent_ISBN', 'Parent_Print_ISSN', 'Parent_Online_ISSN', 'Parent_URI']
        #ToDo: fields_in_item_parent = []
        #ToDo: for field_name in item_parent_values_df.columns:
            #ToDo: if field_name in possible_fields_in_item_parent:
                #ToDo: fields_to_drop_at_end.append(field_name)
                #ToDo: if not item_parent_values_df[field_name].eq("`None`").all():
                    #ToDo: fields_in_item_parent.append(field_name)
        #ToDo: if 'Parent_Publication_Date' in fields_in_item_parent:
            #ToDo: item_parent_values_df['Parent_Publication_Date'] = item_parent_values_df['Parent_Publication_Date'].dt.strftime('%Y-%m-%d')
        
        #Subsection: Remove Fields Not Being Nested
        #ToDo: non_item_parent_fields = [field_name for field_name in fields_used_for_groupby_operations if field_name not in fields_in_item_parent]
        #ToDo: item_parent_values_df = item_parent_values_df.drop(columns=non_item_parent_fields).drop(columns=['Begin_Date'])

        #Subsection: Prepare for Inner Nesting
        #ToDo: item_parent_values_df = item_parent_values_df.stack().reset_index()  # If the index isn't reset, the stack method returns a series
        #ToDo: item_parent_values_df = item_parent_values_df.rename(columns={item_parent_values_df.columns[-2]: 'Type', 0: 'Value'})  # The name of the `Type` field is `level_#` where `#` is the position in a zero-based order of the columns in the dataframe; since the exact name that needs to be changed cannot be know in advanced, it must be found from its penultimate position in the list of field names
        #ToDo: item_parent_values_df['Type'] = item_parent_values_df['Type'].map(lambda type: re.search(r'Parent_(.*)', type)[1] if isinstance(type, str) else type).replace("Title", "Item_Name")

        #Subsection: Remove Null Values and Repetitions
        #ToDo: item_parent_values_df = item_parent_values_df.loc[item_parent_values_df['Value'] != "`None`"]
        #ToDo: item_parent_values_df['repeat'] = item_parent_values_df.duplicated(keep='first')
        #ToDo: item_parent_values_df = item_parent_values_df.loc[item_parent_values_df['repeat'] == False]
        #ToDo: item_parent_values_df = item_parent_values_df.drop(columns=['repeat'])

        #Subsection: Create Inner Nested JSON Section for Author
        #ToDo: Create new dataframe with only item_parent_values_df['Type'] == 'Authors' values
        #ToDo: if new dataframe isn't empty:
            #ToDo: Rename `Value` field to `Name`
            #ToDo: (???_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_contributors: item_contributors[['Type', 'Name']].to_dict('records')).rename("Item_Contributors")
            #ToDo: Join new dataframe back to `item_parent_values_df`

        #Subsection: Create Inner Nested JSON Section for Publication Date
        #ToDo: Create new dataframe with only item_parent_values_df['Type'] == 'Publication_Date' values
        #ToDo: if new dataframe isn't empty:
            #ToDo: (???_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_dates: item_dates[['Type', 'Value']].to_dict('records')).rename("Item_Dates")
            #ToDo: Join new dataframe back to `item_parent_values_df`

        #Subsection: Create Inner Nested JSON Section for Article Version
        #ToDo: Create new dataframe with only item_parent_values_df['Type'] == 'Article_Version' values
        #ToDo: if new dataframe isn't empty:
            #ToDo: (???_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_attributes: item_attributes[['Type', 'Name']].to_dict('records')).rename("Item_Attributes")
            #ToDo: Join new dataframe back to `item_parent_values_df`

        #Subsection: Create Inner Nested JSON Section for Item IDs
        #ToDo: Create new dataframe with only item_parent_values_df['Type'] == 'DOI' or item_parent_values_df['Type'] == 'Proprietary_ID' or item_parent_values_df['Type'] == 'ISBN' or item_parent_values_df['Type'] == 'Print_ISSN' or item_parent_values_df['Type'] == 'Online_ISSN' or item_parent_values_df['Type'] == 'URI' values
        #ToDo: if new dataframe isn't empty:
            #ToDo: (???_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_ID: item_ID[['Type', 'Value']].to_dict('records')).rename("Item_ID")
            #ToDo: Join new dataframe back to `item_parent_values_df`

        #Subsection: Combine All Inner Nested Sections
        #ToDo: Stack `Item_Contributor`, `Item_Dates`, `Item_Attributes`, `Item_ID` fields so those values are in the same field as `Item_Name` and `Data_Type`
        #ToDo: (???_df.groupby(fields_used_for_groupby_operations)).apply(lambda item_parent: item_parent[['name_of_field_with_values_listed_above', 'name_of_field_with_content']].to_dict('records')).rename("Item_Parent")


#Section: Create Nested JSON Section for Performance
#Subsection: Create Instance Grouping
instance_groupby_operation_fields = fields_used_for_groupby_operations + ['Begin_Date']
instance_df = (df.groupby(instance_groupby_operation_fields)).apply(lambda instance: instance[['Metric_Type', 'Count']].to_dict('records')).reset_index().rename(columns={0: "Instance"})  # `instance_groupby_operation_fields` contains all the non-null fields that must be the same for all the records represented in a instance grouping plus a date field to keep instances where the metric and count are repeated from being combined
instance_df = instance_df.set_index(fields_used_in_performance_join_multiindex)

#Subsection: Create Period Grouping
df['temp'] = range(1, len(df.index)+1)  # The way groupby works, for each resource defined by metadata, if a given instance (a metric and its count) occurs in multiple months, those months will be combined, which is not the desired behavior; this field puts a unique value in each row/record, which prevents this grouping
period_groupby_operation_fields = fields_used_for_groupby_operations + ['Metric_Type', 'Count', 'temp']
period_df = df.groupby(period_groupby_operation_fields).apply(lambda period: period[['Begin_Date','End_Date']].to_dict('records')).reset_index().rename(columns={0: "Period"})
period_df = period_df.drop(columns=['temp', 'Metric_Type', 'Count'])
period_df['Period'] = period_df['Period'].map(lambda list_like: list_like[0])
period_df['Begin_Date'] = period_df['Period'].astype('string').map(lambda string: string[16:-28])  # This turns the JSON/dict value into a string, then isolates the desired date from within each string
period_df = period_df.set_index(fields_used_in_performance_join_multiindex)


#Section: Combine Nested JSON Groupings
#Subsection: Combine Period and Instance Groupings
combined_df = period_df.join(instance_df, how='inner')  # This contains duplicate records
combined_df = combined_df.reset_index()
combined_df = combined_df.drop(columns=['Begin_Date'])

#Subsection: Deduplicate Records
# Using pandas' `duplicated` method on dict data type fields raises a TypeError, so their contents must be compared as equivalent strings
combined_df['instance_string'] = combined_df['Instance'].astype('string')
combined_df['period_string'] = combined_df['Period'].astype('string')
fields_to_use_in_deduping = fields_used_for_groupby_operations + ['instance_string'] + ['period_string']
combined_df['repeat'] = combined_df.duplicated(subset=fields_to_use_in_deduping, keep='first')
combined_df = combined_df.loc[combined_df['repeat'] == False]  # Where the Boolean indicates if the record is the same as an earlier record
combined_df = combined_df.drop(columns=['instance_string', 'period_string', 'repeat'])


#Subsection: Create Performance Grouping
combined_df = combined_df.reset_index(drop=True)
joining_df = combined_df.groupby(fields_used_for_groupby_operations).apply(lambda performance: performance[['Period', 'Instance']].to_dict('records')).reset_index().rename(columns={0: "Performance"})

#Subsection: Add Other JSON Groupings
joining_df = joining_df.set_index(fields_used_for_groupby_operations)
if dict(locals()).get('publisher_ID_values_df') is not None:
    joining_df = joining_df.join(publisher_ID_values_df, how='left')
if dict(locals()).get('item_ID_values_df') is not None:
    joining_df = joining_df.join(item_ID_values_df, how='left')
if dict(locals()).get('author_values_df') is not None:
    joining_df = joining_df.join(author_values_df, how='left')
if dict(locals()).get('publication_date_values_df') is not None:
    joining_df = joining_df.join(publication_date_values_df, how='left')
if dict(locals()).get('article_version_values_df') is not None:
    joining_df = joining_df.join(article_version_values_df, how='left')
if dict(locals()).get('item_parent_values_df') is not None:
    joining_df = joining_df.join(item_parent_values_df, how='left')


#Section: Create Final JSON
final_df = joining_df.reset_index()
final_df = final_df.drop(columns=fields_to_drop_at_end)
final_df.to_json(directory_with_final_JSONs / 'result_JSON.json', force_ascii=False, indent=4, orient='table', index=False)