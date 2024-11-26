import logging
import re
from datetime import date
from datetime import datetime
from dateutil import parser
import json
from copy import deepcopy
import io
import pandas as pd

from .app import *
# `from .models import *` to use `COUNTERData.state_data_types()` causes a circular import error

log = logging.getLogger(__name__)


class ConvertJSONDictToDataframe:
    """A class for transforming the Python dictionary versions of JSONs returned by a SUSHI API call into dataframes.

    SUSHI API calls return data in a JSON format, which is easily converted to a Python dictionary; this conversion is done in the `SUSHICallAndResponse.make_SUSHI_call()` method. The conversion from a heavily nested dictionary to a dataframe, however, is much more complicated, as none of the built-in dataframe constructors can be employed. This class exists to convert the SUSHI JSON-derived dictionaries into dataframes that can be loaded into the `COUNTERData` relation; since the desired behavior is more that of a function than a class, the would-be function becomes a class by dividing it into the traditional `__init__` method, which instantiates the dictionary as a class attribute, and the `create_dataframe()` method, which performs the actual transformation. This structure requires all instances of the class constructor to be prepended to a call to the `create_dataframe()` method, which means objects of the `ConvertJSONDictToDataframe` type are never instantiated.

    Attributes:
        self.RESOURCE_NAME_LENGTH (int): A class variable for the length of the `COUNTERData.resource_name` and `COUNTERData.parent_title` fields.
        self.PUBLISHER_LENGTH (int): A class variable for the length of the `COUNTERData.publisher` field.
        self.PUBLISHER_ID_LENGTH (int): A class variable for the length of the `COUNTERData.publisher_ID` field.
        self.PLATFORM_LENGTH (int): A class variable for the length of the `COUNTERData.platform` field.
        self.AUTHORS_LENGTH (int): A class variable for the length of the `COUNTERData.authors` and `COUNTERData.parent_authors` fields.
        self.DOI_LENGTH (int): A class variable for the length of the `COUNTERData.DOI` and `COUNTERData.parent_DOI` fields.
        self.PROPRIETARY_ID_LENGTH (int): A class variable for the length of the `COUNTERData.proprietary_ID` and `COUNTERData.parent_proprietary_ID` fields.
        self.URI_LENGTH (int): A class variable for the length of the `COUNTERData.URI` and `COUNTERData.parent_URI` fields.
        self.SUSHI_JSON_dictionary (dict): The constructor method for `ConvertJSONDictToDataframe`, which instantiates the dictionary object.

    Methods:
        create_dataframe: This method applies the appropriate private method to the dictionary derived from the SUSHI call response JSON to make it into a single dataframe ready to be loaded into the `COUNTERData` relation or saves the JSON as a file if it cannot be successfully converted into a dataframe.
        _transform_R5_JSON: This method transforms the data from the dictionary derived from a R5 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.
        _transform_R5b1_JSON: This method transforms the data from the dictionary derived from a R5.1 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.
        _serialize_dates: This method allows the `json.dumps()` method to serialize (convert) `datetime.datetime` and `datetime.date` attributes into strings.
    """
    # These field length constants allow the class to check that data in varchar fields without COUNTER-defined fixed vocabularies can be successfully uploaded to the `COUNTERData` relation; the constants are set here as class variables instead of in `models.py` to avoid a circular import
    RESOURCE_NAME_LENGTH = 3600
    PUBLISHER_LENGTH = 425
    PUBLISHER_ID_LENGTH = 150
    PLATFORM_LENGTH = 135
    AUTHORS_LENGTH = 4400
    DOI_LENGTH = 110
    PROPRIETARY_ID_LENGTH = 100
    URI_LENGTH = 450
    proprietary_ID_regex = re.compile(r"[Pp]roprietary(_ID)?")
    author_regex = re.compile("[Aa]uthor")

    def __init__(self, SUSHI_JSON_dictionary):
        """The constructor method for `ConvertJSONDictToDataframe`, which instantiates the dictionary object.

        This constructor is not meant to be used alone; all class instantiations should have a `create_dataframe()` method call appended to it.

        Args:
            SUSHI_JSON_dictionary (dict): The dictionary created by converting the JSON returned by the SUSHI API call into Python data types
        """
        self.SUSHI_JSON_dictionary = SUSHI_JSON_dictionary
    

    def create_dataframe(self):
        """This method applies the appropriate private method to the dictionary derived from the SUSHI call response JSON to make it into a single dataframe ready to be loaded into the `COUNTERData` relation or saves the JSON as a file if it cannot be successfully converted into a dataframe.

        This method is a wrapper that sends the JSON-like dictionaries containing all the data from the SUSHI API responses to either the `ConvertJSONDictToDataframe._transform_R5_JSON()` or the `ConvertJSONDictToDataframe._transform_R5b1_JSON()` methods depending on the release version of the API call. The `statistics_source_ID` and `report_type` fields are added after the dataframe is returned to the `StatisticsSources._harvest_R5_SUSHI()` method: the former because that information is proprietary to the NoLCAT instance; the latter because adding it there is less computing-intensive.

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation
            str: the error message if the conversion fails
        """
        log.info("Starting `ConvertJSONDictToDataframe.create_dataframe()`.")
        try:
            report_header_creation_date = parser.isoparse(self.SUSHI_JSON_dictionary.get('Report_Header').get('Created')).date()  # Saving as datetime.date data type removes the time data  
        except Exception as error:
            log.warning(f"Parsing the `Created` field from the SUSHI report header into a Python date data type returned the error {error}. The current date, which is the likely value, is being substituted.")
            report_header_creation_date = date.today()
        log.debug(f"Report creation date is {report_header_creation_date} of type {type(report_header_creation_date)}.")
        COUNTER_release = self.SUSHI_JSON_dictionary['Report_Header']['Release']
        if COUNTER_release == "5":
            try:
                df = self._transform_R5_JSON(report_header_creation_date)
            except Exception as error:
                message = f"Attempting to convert the JSON-like dictionary created from a R5 SUSHI call unexpectedly raised the error {error}, meaning the data couldn't be loaded into the database. The JSON data is being saved instead."
                log.error(message)
                #ToDo: Save JSON as file
                return message
        elif COUNTER_release == "5.1":
            try:
                df = self._transform_R5b1_JSON(report_header_creation_date)
            except Exception as error:
                message = f"Attempting to convert the JSON-like dictionary created from a R5.1 SUSHI call unexpectedly raised the error {error}, meaning the data couldn't be loaded into the database. The JSON data is being saved instead."
                log.error(message)
                #ToDo: Save JSON as file
                return message
        else:
            message = f"The release of the JSON-like dictionary couldn't be identified, meaning the data couldn't be loaded into the database. The JSON data is being saved instead."
            log.error(message)
            #ToDo: Save JSON as file
            return message
        return df  # The method will only get here if one of the private harvest methods was successful


    def _transform_R5_JSON(self, report_creation_date):
        """This method transforms the data from the dictionary derived from a R5 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.

        Args:
            report_creation_date (datetime.date): The date the report was created

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation
            str: the error message if the conversion fails
        """
        log.info("Starting `ConvertJSONDictToDataframe._transform_R5_JSON()`.")
        records_orient_list = []

        #Section: Set Up Tracking of Fields to Include in `df_dtypes`
        include_in_df_dtypes = {  # Using `record_dict.get()` at the end doesn't work because any field with a null value in the last record won't be included
            'resource_name': False,
            'publisher': False,
            'publisher_ID': False,
            'authors': False,
            'publication_date': False,
            'article_version': False,
            'DOI': False,
            'proprietary_ID': False,
            'ISBN': False,
            'print_ISSN': False,
            'online_ISSN': False,
            'URI': False,
            'data_type': False,
            'section_type': False,
            'YOP': False,
            'access_type': False,
            'access_method': False,
            'parent_title': False,
            'parent_authors': False,
            'parent_publication_date': False,
            'parent_article_version': False,
            'parent_data_type': False,
            'parent_DOI': False,
            'parent_proprietary_ID': False,
            'parent_ISBN': False,
            'parent_print_ISSN': False,
            'parent_online_ISSN': False,
            'parent_URI': False,
        }

        #Section: Iterate Through JSON Records to Create Single-Level Dictionaries
        for record in self.SUSHI_JSON_dictionary['Report_Items']:
            log.debug(f"Starting iteration for new JSON record {record}.")
            record_dict = {"report_creation_date": report_creation_date}  # This resets the contents of `record_dict`, including removing any keys that might not get overwritten because they aren't included in the next iteration
            for key, value in record.items():

                #Subsection: Capture `resource_name` Value
                if key == "Database" or key == "Title" or key == "Item":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    if value is None:  # This value handled first because `len()` of null value raises an error
                        record_dict['resource_name'] = value
                        log.debug(f"Added `COUNTERData.resource_name` value {record_dict['resource_name']} to `record_dict`.")
                    elif len(value) > self.RESOURCE_NAME_LENGTH:
                        message = f"Increase the `COUNTERData.resource_name` max field length to {int(len(value) + (len(value) * 0.1))}."
                        log.critical(message)
                        return message
                    else:
                        record_dict['resource_name'] = value
                        include_in_df_dtypes['resource_name'] = 'string'
                        log.debug(f"Added `COUNTERData.resource_name` value {record_dict['resource_name']} to `record_dict`.")
                
                #Subsection: Capture `publisher` Value
                elif key == "Publisher":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    if value is None:  # This value handled first because `len()` of null value raises an error
                        record_dict['publisher'] = value
                        log.debug(f"Added `COUNTERData.publisher` value {record_dict['publisher']} to `record_dict`.")
                    elif len(value) > self.PUBLISHER_LENGTH:
                        message = f"Increase the `COUNTERData.publisher` max field length to {int(len(value) + (len(value) * 0.1))}."
                        log.critical(message)
                        return message
                    else:
                        record_dict['publisher'] = value
                        include_in_df_dtypes['publisher'] = 'string'
                        log.debug(f"Added `COUNTERData.publisher` value {record_dict['publisher']} to `record_dict`.")
                
                #Subsection: Capture `publisher_ID` Value
                elif key == "Publisher_ID":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    if value is None:  # This value handled first because `len()` of null value raises an error
                        record_dict['publisher_ID'] = value
                        log.debug(f"Added `COUNTERData.publisher_ID` value {record_dict['publisher_ID']} to `record_dict`.")
                    elif len(value) == 1:
                        if len(value[0]['Value']) > self.PUBLISHER_ID_LENGTH:
                            message = f"Increase the `COUNTERData.publisher_ID` max field length to {int(len(value[0]['Value']) + (len(value[0]['Value']) * 0.1))}."
                            log.critical(message)
                            return message
                        else:
                            record_dict['publisher_ID'] = value[0]['Value']
                            include_in_df_dtypes['publisher_ID'] = 'string'
                            log.debug(f"Added `COUNTERData.publisher_ID` value {record_dict['publisher_ID']} to `record_dict`.")
                    else:
                        for type_and_value in value:
                            if self.proprietary_ID_regex.search(type_and_value['Type']):
                                if len(type_and_value['Value']) > self.PUBLISHER_ID_LENGTH:
                                    message = f"Increase the `COUNTERData.publisher_ID` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                    log.critical(message)
                                    return message
                                else:
                                    record_dict['publisher_ID'] = type_and_value['Value']
                                    include_in_df_dtypes['publisher_ID'] = 'string'
                                    log.debug(f"Added `COUNTERData.publisher_ID` value {record_dict['publisher_ID']} to `record_dict`.")
                            else:
                                continue  # The `for type_and_value in value` loop
                
                #Subsection: Capture `platform` Value
                elif key == "Platform":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    if value is None:  # This value handled first because `len()` of null value raises an error
                        record_dict['platform'] = value
                        log.debug(f"Added `COUNTERData.platform` value {record_dict['platform']} to `record_dict`.")
                    elif len(value) > self.PLATFORM_LENGTH:
                        message = f"Increase the `COUNTERData.platform` max field length to {int(len(value) + (len(value) * 0.1))}."
                        log.critical(message)
                        return message
                    else:
                        record_dict['platform'] = value
                        log.debug(f"Added `COUNTERData.platform` value {record_dict['platform']} to `record_dict`.")
                
                #Subsection: Capture `authors` Value
                elif key == "Item_Contributors":  # `Item_Contributors` uses `Name` instead of `Value`
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    for type_and_value in value:
                        if self.author_regex.search(type_and_value['Type']):
                            if record_dict.get('authors'):  # If the author name value is null, this will never be true
                                if record_dict['authors'].endswith(" et al."):
                                    continue  # The `for type_and_value in value` loop
                                elif len(record_dict['authors']) + len(type_and_value['Name']) + 8 > self.AUTHORS_LENGTH:
                                    record_dict['authors'] = record_dict['authors'] + " et al."
                                    log.debug(f"Updated `COUNTERData.authors` value to {record_dict['parent_authors']} in `record_dict`.")
                                else:
                                    record_dict['authors'] = record_dict['authors'] + "; " + type_and_value['Name']
                                    log.debug(f"Added `COUNTERData.authors` value {record_dict['authors']} to `record_dict`.")
                            
                            else:
                                if type_and_value['Name'] is None:  # This value handled first because `len()` of null value raises an error
                                    record_dict['authors'] = type_and_value['Name']
                                    log.debug(f"Added `COUNTERData.authors` value {record_dict['authors']} to `record_dict`.")
                                elif len(type_and_value['Name']) > self.AUTHORS_LENGTH:
                                    message = f"Increase the `COUNTERData.authors` max field length to {int(len(type_and_value['Name']) + (len(type_and_value['Name']) * 0.1))}."
                                    log.critical(message)
                                    return message
                                else:
                                    record_dict['authors'] = type_and_value['Name']
                                    include_in_df_dtypes['authors'] = 'string'
                                    log.debug(f"Added `COUNTERData.authors` value {record_dict['authors']} to `record_dict`.")
                
                #Subsection: Capture `publication_date` Value
                elif key == "Item_Dates":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    for type_and_value in value:
                        if type_and_value['Value'] == "1000-01-01" or type_and_value['Value'] == "1753-01-01" or type_and_value['Value'] == "1900-01-01":
                            continue  # The `for type_and_value in value` loop; these dates are common RDBMS/spreadsheet minimum date data type values and are generally placeholders for null values or bad data
                        if type_and_value['Type'] == "Publication_Date":  # Unlikely to be more than one; if there is, the field's date/datetime64 data type prevent duplicates from being preserved
                            try:
                                record_dict['publication_date'] = date.fromisoformat(type_and_value['Value'])
                                include_in_df_dtypes['publication_date'] = True
                                log.debug(f"Added `COUNTERData.publication_date` value {record_dict['publication_date']} to `record_dict`.")
                            except:  # In case `type_and_value['Value']` is null, which would cause the conversion to a datetime data type to return a TypeError
                                continue  # The `for type_and_value in value` loop
                
                #Subsection: Capture `article_version` Value
                elif key == "Item_Attributes":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    for type_and_value in value:
                        if type_and_value['Type'] == "Article_Version":  # Very unlikely to be more than one
                            record_dict['article_version'] = type_and_value['Value']
                            include_in_df_dtypes['article_version'] = 'string'
                            log.debug(f"Added `COUNTERData.article_version` value {record_dict['article_version']} to `record_dict`.")
                
                #Subsection: Capture Standard Identifiers
                # Null value handling isn't needed because all null values are removed
                elif key == "Item_ID":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    for type_and_value in value:
                        
                        #Subsection: Capture `DOI` Value
                        if type_and_value['Type'] == "DOI":
                            if len(type_and_value['Value']) > self.DOI_LENGTH:
                                message = f"Increase the `COUNTERData.DOI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                log.critical(message)
                                return message
                            else:
                                record_dict['DOI'] = type_and_value['Value']
                                include_in_df_dtypes['DOI'] = 'string'
                                log.debug(f"Added `COUNTERData.DOI` value {record_dict['DOI']} to `record_dict`.")
                        
                        #Subsection: Capture `proprietary_ID` Value
                        elif self.proprietary_ID_regex.search(type_and_value['Type']):
                            if len(type_and_value['Value']) > self.PROPRIETARY_ID_LENGTH:
                                message = f"Increase the `COUNTERData.proprietary_ID` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                log.critical(message)
                                return message
                            else:
                                record_dict['proprietary_ID'] = type_and_value['Value']
                                include_in_df_dtypes['proprietary_ID'] = 'string'
                                log.debug(f"Added `COUNTERData.proprietary_ID` value {record_dict['proprietary_ID']} to `record_dict`.")
                        
                        #Subsection: Capture `ISBN` Value
                        elif type_and_value['Type'] == "ISBN":
                            record_dict['ISBN'] = str(type_and_value['Value'])
                            include_in_df_dtypes['ISBN'] = 'string'
                            log.debug(f"Added `COUNTERData.ISBN` value {record_dict['ISBN']} to `record_dict`.")
                        
                        #Subsection: Capture `print_ISSN` Value
                        elif type_and_value['Type'] == "Print_ISSN":
                            if ISSN_regex().fullmatch(type_and_value['Value']):
                                record_dict['print_ISSN'] = type_and_value['Value'].strip()
                                include_in_df_dtypes['print_ISSN'] = 'string'
                                log.debug(f"Added `COUNTERData.print_ISSN` value {record_dict['print_ISSN']} to `record_dict`.")
                            else:
                                record_dict['print_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                include_in_df_dtypes['print_ISSN'] = 'string'
                                log.debug(f"Added `COUNTERData.print_ISSN` value {record_dict['print_ISSN']} to `record_dict`.")
                        
                        #Subsection: Capture `online_ISSN` Value
                        elif type_and_value['Type'] == "Online_ISSN":
                            if ISSN_regex().fullmatch(type_and_value['Value']):
                                record_dict['online_ISSN'] = type_and_value['Value'].strip()
                                include_in_df_dtypes['online_ISSN'] = 'string'
                                log.debug(f"Added `COUNTERData.online_ISSN` value {record_dict['online_ISSN']} to `record_dict`.")
                            else:
                                record_dict['online_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                include_in_df_dtypes['online_ISSN'] = 'string'
                                log.debug(f"Added `COUNTERData.online_ISSN` value {record_dict['online_ISSN']} to `record_dict`.")
                        
                        #Subsection: Capture `URI` Value
                        elif type_and_value['Type'] == "URI":
                            if len(type_and_value['Value']) > self.URI_LENGTH:
                                message = f"Increase the `COUNTERData.URI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                log.critical(message)
                                return message
                            else:
                                record_dict['URI'] = type_and_value['Value']
                                include_in_df_dtypes['URI'] = 'string'
                                log.debug(f"Added `COUNTERData.URI` value {record_dict['URI']} to `record_dict`.")
                        else:
                            continue  # The `for type_and_value in value` loop
                
                #Subsection: Capture `data_type` Value
                elif key == "Data_Type":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    record_dict['data_type'] = value
                    include_in_df_dtypes['data_type'] = 'string'
                    log.debug(f"Added `COUNTERData.data_type` value {record_dict['data_type']} to `record_dict`.")
                
                #Subsection: Capture `section_Type` Value
                elif key == "Section_Type":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    record_dict['section_type'] = value
                    include_in_df_dtypes['section_type'] = 'string'
                    log.debug(f"Added `COUNTERData.section_type` value {record_dict['section_type']} to `record_dict`.")

                #Subsection: Capture `YOP` Value
                elif key == "YOP":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    try:
                        record_dict['YOP'] = int(value)  # The Int16 dtype doesn't have a constructor, so this value is saved as an int for now and transformed when when the dataframe is created
                        include_in_df_dtypes['YOP'] = 'Int16'  # `smallint` in database; using the pandas data type here because it allows null values
                    except:
                        record_dict['YOP'] = None  # The dtype conversion that occurs when this becomes a dataframe will change this to pandas' `NA`
                    log.debug(f"Added `COUNTERData.YOP` value {record_dict['YOP']} to `record_dict`.")
                
                #Subsection: Capture `access_type` Value
                elif key == "Access_Type":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    record_dict['access_type'] = value
                    include_in_df_dtypes['access_type'] = 'string'
                    log.debug(f"Added `COUNTERData.access_type` value {record_dict['access_type']} to `record_dict`.")
                
                #Subsection: Capture `access_method` Value
                elif key == "Access_Method":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    record_dict['access_method'] = value
                    include_in_df_dtypes['access_method'] = 'string'
                    log.debug(f"Added `COUNTERData.access_method` value {record_dict['access_method']} to `record_dict`.")
                
                #Subsection: Capture Parent Resource Metadata
                # Null value handling isn't needed because all null values are removed
                elif key == "Item_Parent":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    if isinstance(value, list) and len(value) == 1:  # The `Item_Parent` value should be a dict, but sometimes that dict is within a one-item list; this removes the outer list
                        value = value[0]
                    for key_for_parent, value_for_parent in value.items():

                        #Subsection: Capture `parent_title` Value
                        if key_for_parent == "Item_Name":
                            log.debug(f"Preparing to add {key_for_parent} value `{value_for_parent}` to the record.")
                            if len(value_for_parent) > self.RESOURCE_NAME_LENGTH:
                                message = f"Increase the `COUNTERData.parent_title` max field length to {int(len(value_for_parent) + (len(value_for_parent) * 0.1))}."
                                log.critical(message)
                                return message
                            else:
                                record_dict['parent_title'] = value_for_parent
                                include_in_df_dtypes['parent_title'] = 'string'
                                log.debug(f"Added `COUNTERData.parent_title` value {record_dict['parent_title']} to `record_dict`.")
                        
                        #Subsection: Capture `parent_authors` Value
                        elif key_for_parent == "Item_Contributors":  # `Item_Contributors` uses `Name` instead of `Value`
                            log.debug(f"Preparing to add {key_for_parent} value `{value_for_parent}` to the record.")
                            for type_and_value in value_for_parent:
                                if self.author_regex.search(type_and_value['Type']):
                                    if record_dict.get('parent_authors'):
                                        if record_dict['parent_authors'].endswith(" et al."):
                                            continue  # The `for type_and_value in value_for_parent` loop
                                        elif len(record_dict['parent_authors']) + len(type_and_value['Name']) + 8 > self.AUTHORS_LENGTH:
                                            record_dict['parent_authors'] = record_dict['parent_authors'] + " et al."
                                            log.debug(f"Updated `COUNTERData.parent_authors` value to {record_dict['parent_authors']} in `record_dict`.")
                                        else:
                                            record_dict['parent_authors'] = record_dict['parent_authors'] + "; " + type_and_value['Name']
                                            log.debug(f"Updated `COUNTERData.parent_authors` value to {record_dict['parent_authors']} in `record_dict`.")
                                    else:
                                        if len(type_and_value['Name']) > self.AUTHORS_LENGTH:
                                            message = f"Increase the `COUNTERData.authors` max field length to {int(len(type_and_value['Name']) + (len(type_and_value['Name']) * 0.1))}."
                                            log.critical(message)
                                            return message
                                        else:
                                            record_dict['parent_authors'] = type_and_value['Name']
                                            include_in_df_dtypes['parent_authors'] = 'string'
                                            log.debug(f"Added `COUNTERData.parent_authors` value {record_dict['parent_authors']} to `record_dict`.")
                        
                        #Subsection: Capture `parent_publication_date` Value
                        elif key_for_parent == "Item_Dates":
                            log.debug(f"Preparing to add {key_for_parent} value `{value_for_parent}` to the record.")
                            for type_and_value in value_for_parent:
                                if type_and_value['Value'] == "1000-01-01" or type_and_value['Value'] == "1753-01-01" or type_and_value['Value'] == "1900-01-01":
                                    continue  # The `for type_and_value in value` loop; these dates are common RDBMS/spreadsheet minimum date data type values and are generally placeholders for null values or bad data
                                if type_and_value['Type'] == "Publication_Date":  # Unlikely to be more than one; if there is, the field's date/datetime64 data type prevent duplicates from being preserved
                                    record_dict['parent_publication_date'] = date.fromisoformat(type_and_value['Value'])
                                    include_in_df_dtypes['parent_publication_date'] = True
                                    log.debug(f"Added `COUNTERData.parent_publication_date` value {record_dict['parent_publication_date']} to `record_dict`.")
                        
                        #Subsection: Capture `parent_article_version` Value
                        elif key_for_parent == "Item_Attributes":
                            log.debug(f"Preparing to add {key_for_parent} value `{value_for_parent}` to the record.")
                            for type_and_value in value_for_parent:
                                if type_and_value['Type'] == "Article_Version":  # Very unlikely to be more than one
                                    record_dict['parent_article_version'] = type_and_value['Value']
                                    include_in_df_dtypes['parent_article_version'] = 'string'
                                    log.debug(f"Added `COUNTERData.parent_article_version` value {record_dict['parent_article_version']} to `record_dict`.")

                        #Subsection: Capture `parent_data_type` Value
                        elif key_for_parent == "Data_Type":
                            log.debug(f"Preparing to add {key_for_parent} value `{value_for_parent}` to the record.")
                            record_dict['parent_data_type'] = value_for_parent
                            include_in_df_dtypes['parent_data_type'] = 'string'
                            log.debug(f"Added `COUNTERData.parent_data_type` value {record_dict['parent_data_type']} to `record_dict`.")
                        
                        elif key_for_parent == "Item_ID":
                            log.debug(f"Preparing to add {key_for_parent} value `{value_for_parent}` to the record.")
                            for type_and_value in value_for_parent:
                                
                                #Subsection: Capture `parent_DOI` Value
                                if type_and_value['Type'] == "DOI":
                                    if len(type_and_value['Value']) > self.DOI_LENGTH:
                                        message = f"Increase the `COUNTERData.parent_DOI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['parent_DOI'] = type_and_value['Value']
                                        include_in_df_dtypes['parent_DOI'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_DOI` value {record_dict['parent_DOI']} to `record_dict`.")

                                #Subsection: Capture `parent_proprietary_ID` Value
                                elif self.proprietary_ID_regex.search(type_and_value['Type']):
                                    if len(type_and_value['Value']) > self.PROPRIETARY_ID_LENGTH:
                                        message = f"Increase the `COUNTERData.parent_proprietary_ID` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['parent_proprietary_ID'] = type_and_value['Value']
                                        include_in_df_dtypes['parent_proprietary_ID'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_proprietary_ID` value {record_dict['parent_proprietary_ID']} to `record_dict`.")

                                #Subsection: Capture `parent_ISBN` Value
                                elif type_and_value['Type'] == "ISBN":
                                    record_dict['parent_ISBN'] = str(type_and_value['Value'])
                                    include_in_df_dtypes['parent_ISBN'] = 'string'
                                    log.debug(f"Added `COUNTERData.parent_ISBN` value {record_dict['parent_ISBN']} to `record_dict`.")

                                #Subsection: Capture `parent_print_ISSN` Value
                                elif type_and_value['Type'] == "Print_ISSN":
                                    if ISSN_regex().fullmatch(type_and_value['Value']):
                                        record_dict['parent_print_ISSN'] = type_and_value['Value'].strip()
                                        include_in_df_dtypes['parent_print_ISSN'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_print_ISSN` value {record_dict['parent_print_ISSN']} to `record_dict`.")
                                    else:
                                        record_dict['parent_print_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                        include_in_df_dtypes['parent_print_ISSN'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_print_ISSN` value {record_dict['parent_print_ISSN']} to `record_dict`.")

                                #Subsection: Capture `parent_online_ISSN` Value
                                elif type_and_value['Type'] == "Online_ISSN":
                                    if ISSN_regex().fullmatch(type_and_value['Value']):
                                        record_dict['parent_online_ISSN'] = type_and_value['Value'].strip()
                                        include_in_df_dtypes['parent_online_ISSN'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_online_ISSN` value {record_dict['parent_online_ISSN']} to `record_dict`.")
                                    else:
                                        record_dict['parent_online_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                        include_in_df_dtypes['parent_online_ISSN'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_online_ISSN` value {record_dict['parent_online_ISSN']} to `record_dict`.")

                                #Subsection: Capture `parent_URI` Value
                                elif type_and_value['Type'] == "URI":
                                    if len(type_and_value['Value']) > self.URI_LENGTH:
                                        message = f"Increase the `COUNTERData.parent_URI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}."
                                        log.critical(message)
                                        return message
                                    else:
                                        record_dict['parent_URI'] = type_and_value['Value']
                                        include_in_df_dtypes['parent_URI'] = 'string'
                                        log.debug(f"Added `COUNTERData.parent_URI` value {record_dict['parent_URI']} to `record_dict`.")

                        else:
                            continue  # The `for key_for_parent, value_for_parent in value.items()` loop

                elif key == "Performance":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    record_dict['temp'] = value

                else:
                    log.warning(f"The unexpected key `{key}` was found in the JSON response to a SUSHI API call.")
                    pass
            
            #Section: Create Records by Iterating Through `Performance` Section of SUSHI JSON
            performance = record_dict.pop('temp')
            log.debug(f"Preparing to add date, metric type, and usage count values `{performance}` to the record.")
            for period_grouping in performance:
                record_dict['usage_date'] = date.fromisoformat(period_grouping['Period']['Begin_Date'])
                for instance in period_grouping['Instance']:
                    record_dict['metric_type'] = instance['Metric_Type']
                    record_dict['usage_count'] = instance['Count']
                    records_orient_list.append(deepcopy(record_dict))  # Appending `record_dict` directly adds a reference to that variable, which changes with each iteration of the loop, meaning all the records for a given set of metadata have the `usage_date`, `metric_type`, and `usage_count` values of `record_dict` during the final iteration
                    log.debug(f"Added record {record_dict} to `COUNTERData` relation.")  # Set to logging level debug because when all these logging statements are sent to AWS stdout, the only pytest output visible is the error summary statements

        #Section: Create Dataframe
        log.info(f"Unfiltered `include_in_df_dtypes`: {include_in_df_dtypes}")
        include_in_df_dtypes = {k: v for (k, v) in include_in_df_dtypes.items() if v is not False}  # Using `is` for comparison because `1 != False` returns `True` in Python
        log.debug(f"Filtered `include_in_df_dtypes`: {include_in_df_dtypes}")
        df_dtypes = {k: v for (k, v) in include_in_df_dtypes.items() if v is not True}
        df_dtypes['platform'] = 'string'
        df_dtypes['metric_type'] = 'string'
        df_dtypes['usage_count'] = 'int'
        log.info(f"`df_dtypes`: {df_dtypes}")

        log.debug(f"`records_orient_list` before `json.dumps()`  is type {type(records_orient_list)}.")
        records_orient_list = json.dumps(  # `pd.read_json` takes a string, conversion done before method for ease in handling type conversions
            records_orient_list,
            default=ConvertJSONDictToDataframe._serialize_dates,
        )
        if len(records_orient_list) > 1500:
            log.debug(f"`records_orient_list` after `json.dumps()` (type {type(records_orient_list)}) is too long to display.")
        else:
            log.debug(f"`records_orient_list` after `json.dumps()` (type {type(records_orient_list)}):\n{records_orient_list}")
        df = pd.read_json(
            io.StringIO(records_orient_list),  # Originally from https://stackoverflow.com/a/63655099 in `except` block; now only option due to `FutureWarning: Passing literal json to 'read_json' is deprecated and will be removed in a future version. To read from a literal string, wrap it in a 'StringIO' object.`
            orient='records',
            dtype=df_dtypes,  # This only sets numeric data types
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        log.info(f"Dataframe info immediately after dataframe creation:\n{return_string_of_dataframe_info(df)}")

        df = df.astype(df_dtypes)  # This sets the string data types
        log.debug(f"Dataframe dtypes after conversion:\n{return_string_of_dataframe_info(df)}")
        if include_in_df_dtypes.get('publication_date'):  # Meaning the value was changed to `True`
            df['publication_date'] = pd.to_datetime(
                df['publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
            )
        if include_in_df_dtypes.get('parent_publication_date'):  # Meaning the value was changed to `True`
            df['parent_publication_date'] = pd.to_datetime(
                df['parent_publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
            )
        df['usage_date'] = pd.to_datetime(df['usage_date'])
        df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])#.dt.tz_localize(None)

        log.info(f"Dataframe info:\n{return_string_of_dataframe_info(df)}")
        return df


    def _transform_R5b1_JSON(self, report_creation_date):
        """This method transforms the data from the dictionary derived from a R5.1 SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.

        Args:
            report_creation_date (datetime.date): The date the report was created

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation
            str: the error message if the conversion fails
        """
        log.info("Starting `ConvertJSONDictToDataframe._transform_R5b1_JSON()`.")
        records_orient_list = []
        
        #Section: Set Up Tracking of Fields to Include in `df_dtypes`
        include_in_df_dtypes = {
            'resource_name': False,
            'publisher': False,
            'publisher_ID': False,
            'authors': False,
            'publication_date': False,
            'article_version': False,
            'DOI': False,
            'proprietary_ID': False,
            'ISBN': False,
            'print_ISSN': False,
            'online_ISSN': False,
            'URI': False,
            'data_type': False,
            'section_type': False,
            'YOP': False,
            'access_type': False,
            'access_method': False,
            'parent_title': False,
            'parent_authors': False,
            'parent_publication_date': False,
            'parent_article_version': False,
            'parent_data_type': False,
            'parent_DOI': False,
            'parent_proprietary_ID': False,
            'parent_ISBN': False,
            'parent_print_ISSN': False,
            'parent_online_ISSN': False,
            'parent_URI': False,
        }

        #Section: Iterate Through `Report_Items` of SUSHI JSON to Create Single-Level Dictionaries
        for record in self.SUSHI_JSON_dictionary['Report_Items']:
            log.debug(f"Starting iteration for new JSON record {record}.")
            report_items_dict = {"report_creation_date": report_creation_date}  # This resets the contents of `report_items_dict`, including removing any keys that might not get overwritten because they aren't included in the next iteration
            for key, value in record.items():

                #Subsection: Capture `resource_name` Value
                #Subsection: Capture `publisher` Value
                #Subsection: Capture `publisher_ID` Value
                #Subsection: Capture `platform` Value
                elif key == "Platform":
                    log.debug(f"Preparing to add {key} value `{value}` to the record.")
                    if value is None:  # This value handled first because `len()` of null value raises an error
                        report_items_dict['platform'] = value
                        log.debug(f"Added `COUNTERData.platform` value {report_items_dict['platform']} to `report_items_dict`.")
                    elif len(value) > self.PLATFORM_LENGTH:
                        message = f"Increase the `COUNTERData.platform` max field length to {int(len(value) + (len(value) * 0.1))}."
                        log.critical(message)
                        return message
                    else:
                        report_items_dict['platform'] = value
                        log.debug(f"Added `COUNTERData.platform` value {report_items_dict['platform']} to `report_items_dict`.")

                #Subsection: Capture `authors` Value
                #Subsection: Capture `publication_date` Value
                #Subsection: Capture `article_version` Value
                #Subsection: Capture Standard Identifiers
                    #Subsection: Capture `DOI` Value
                    #Subsection: Capture `proprietary_ID` Value
                    #Subsection: Capture `ISBN` Value
                    #Subsection: Capture `print_ISSN` Value
                    #Subsection: Capture `online_ISSN` Value
                    #Subsection: Capture `URI` Value
                #Subsection: Capture `data_type` Value
                #Subsection: Capture `section_Type` Value
                #Subsection: Capture `YOP` Value
                #Subsection: Capture `access_type` Value
                #Subsection: Capture `access_method` Value
                #Subsection: Capture Parent Resource Metadata
                    #Subsection: Capture `parent_title` Value
                    #Subsection: Capture `parent_authors` Value
                    #Subsection: Capture `parent_publication_date` Value
                    #Subsection: Capture `parent_article_version` Value
                    #Subsection: Capture `parent_data_type` Value
                    #Subsection: Capture `parent_DOI` Value
                    #Subsection: Capture `parent_proprietary_ID` Value
                    #Subsection: Capture `parent_ISBN` Value
                    #Subsection: Capture `parent_print_ISSN` Value
                    #Subsection: Capture `parent_online_ISSN` Value
                    #Subsection: Capture `parent_URI` Value
        
                #Section: Iterate Through `Attribute_Performance` Section of SUSHI JSON
                elif key == "Attribute_Performance":
                    for attribute_performance_item in value:
                        for ap_key, ap_value in attribute_performance_item.items():
                            attribute_performance_dict = deepcopy(report_items_dict)

                        #Subsection: Capture `authors` Value
                        #Subsection: Capture `publication_date` Value
                        #Subsection: Capture `article_version` Value
                        #Subsection: Capture Standard Identifiers
                            #Subsection: Capture `DOI` Value
                            #Subsection: Capture `proprietary_ID` Value
                            #Subsection: Capture `ISBN` Value
                            #Subsection: Capture `print_ISSN` Value
                            #Subsection: Capture `online_ISSN` Value
                            #Subsection: Capture `URI` Value
                        #Subsection: Capture `data_type` Value
                        elif ap_key == "Data_Type":
                            log.debug(f"Preparing to add {ap_key} value `{ap_value}` to the record.")
                            attribute_performance_dict['data_type'] = ap_value
                            include_in_df_dtypes['data_type'] = 'string'
                            log.debug(f"Added `COUNTERData.data_type` value {attribute_performance_dict['data_type']} to `attribute_performance_dict`.")
                        
                        #Subsection: Capture `section_Type` Value
                        #Subsection: Capture `YOP` Value
                        #Subsection: Capture `access_type` Value
                        #Subsection: Capture `access_method` Value
                        elif ap_key == "Access_Method":
                            log.debug(f"Preparing to add {ap_key} value `{ap_value}` to the record.")
                            attribute_performance_dict['access_method'] = ap_value
                            include_in_df_dtypes['access_method'] = 'string'
                            log.debug(f"Added `COUNTERData.access_method` value {attribute_performance_dict['access_method']} to `attribute_performance_dict`.")
                
                        #Subsection: Capture Parent Resource Metadata
                            #Subsection: Capture `parent_title` Value
                            #Subsection: Capture `parent_authors` Value
                            #Subsection: Capture `parent_publication_date` Value
                            #Subsection: Capture `parent_article_version` Value
                            #Subsection: Capture `parent_data_type` Value
                            #Subsection: Capture `parent_DOI` Value
                            #Subsection: Capture `parent_proprietary_ID` Value
                            #Subsection: Capture `parent_ISBN` Value
                            #Subsection: Capture `parent_print_ISSN` Value
                            #Subsection: Capture `parent_online_ISSN` Value
                            #Subsection: Capture `parent_URI` Value

                        #Section: Iterate Through `Performance` Section of SUSHI JSON to Create Dataframe Lines
                        elif ap_key == "Performance":
                            for p_key, p_value in ap_value.items():
                                performance_dict = deepcopy(attribute_performance_dict)
                                log.debug(f"Preparing to add {p_key} metric_type values to the record.")
                                performance_dict['metric_type'] = p_key
                                for usage_date, usage_count in p_value.items():
                                    final_dict = {
                                        **deepcopy(performance_dict),
                                        'usage_date': usage_date,
                                        'usage_count': usage_count,
                                    }
                                    records_orient_list.append(final_dict)
                                    log.debug(f"Added record {final_dict} to `COUNTERData` relation.")  # Set to logging level debug because when all these logging statements are sent to AWS stdout, the only pytest output visible is the error summary statements
                    

        #Section: Create Dataframe
        pass
    

    def _serialize_dates(dates):
        """This method allows the `json.dumps()` method to serialize (convert) `datetime.datetime` and `datetime.date` attributes into strings.

        This method and its use in are adapted from https://stackoverflow.com/a/22238613.

        Args:
            dates (datetime.datetime or datetime.date): A date or timestamp with a data type from Python's datetime library

        Returns:
            str: the date or timestamp in ISO format
        """
        if isinstance(dates,(date, datetime)):
            return dates.isoformat()
        else:
            raise TypeError  # So any unexpected non-serializable data types raise a type error