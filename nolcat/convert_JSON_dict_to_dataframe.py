import logging
import re
import datetime
from dateutil import parser
import pandas as pd
from pandas import Int64Dtype


logging.basicConfig(level=logging.INFO, format="ConvertJSONDictToDataframe - - [%(asctime)s] %(message)s")


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
        create_dataframe: This method transforms the data from the dictionary derived from the SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.
    """
    # These field length constants allow the class to check that data in varchar fields without COUNTER-defined fixed vocabularies can be successfully uploaded to the `COUNTERData` relation; the constants are set here as class variables instead of in `models.py` to avoid a circular import
    RESOURCE_NAME_LENGTH = 2000
    PUBLISHER_LENGTH = 225
    PUBLISHER_ID_LENGTH = 50
    PLATFORM_LENGTH = 75
    AUTHORS_LENGTH = 1000
    DOI_LENGTH = 75
    PROPRIETARY_ID_LENGTH = 100
    URI_LENGTH = 250

    def __init__(self, SUSHI_JSON_dictionary):
        """The constructor method for `ConvertJSONDictToDataframe`, which instantiates the dictionary object.

        This constructor is not meant to be used alone; all class instantiations should have a `create_dataframe()` method call appended to it.

        Args:
            SUSHI_JSON_dictionary (dict): The dictionary created by converting the JSON returned by the SUSHI API call into Python data types
        """
        self.SUSHI_JSON_dictionary = SUSHI_JSON_dictionary
    

    def create_dataframe(self):
        """This method transforms the data from the dictionary derived from the SUSHI call response JSON into a single dataframe ready to be loaded into the `COUNTERData` relation.

        This method prepares the dictionaries containing all the data from the SUSHI API responses for upload into the database. The `statistics_source_ID` and `report_type` are added after the dataframe is returned to the `StatisticsSources._harvest_R5_SUSHI()` method: the former because that information is proprietary to the NoLCAT instance; the latter because adding it there is less computing-intensive.

        Returns:
            dataframe: COUNTER data ready to be loaded into the `COUNTERData` relation
        """
        records_orient_list = []
        report_header_creation_date = parser.isoparse(self.SUSHI_JSON_dictionary['Report_Header']['Created'])
        for record in self.SUSHI_JSON_dictionary['Report_Items']:
            logging.info(f"Starting iteration for record {record}")
            record_dict = {"report_creation_date": report_header_creation_date}  # This resets the contents of `record_dict`, including removing any keys that might not get overwritten because they aren't included in the next iteration
            for key, value in record.items():

                #Section: Capture `resource_name` Value
                if key == "Database" or key == "Title" or key == "Item":
                    if len(value) > self.RESOURCE_NAME_LENGTH:
                        logging.error(f"Increase the `COUNTERData.resource_name` max field length to {int(len(value) + (len(value) * 0.1))}.")
                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                    else:
                        record_dict['resource_name'] = value
                        logging.debug(f"Added `COUNTERData.resource_name` value {record_dict['resource_name']} to `record_dict`.")
                
                #Section: Capture `publisher` Value
                elif key == "Publisher":
                    if len(value) > self.PUBLISHER_LENGTH:
                        logging.error(f"Increase the `COUNTERData.publisher` max field length to {int(len(value) + (len(value) * 0.1))}.")
                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                    else:
                        record_dict['publisher'] = value
                        logging.debug(f"Added `COUNTERData.publisher` value {record_dict['publisher']} to `record_dict`.")
                
                #Section: Capture `publisher_ID` Value
                elif key == "Publisher_ID":
                    if len(value) == 1:
                        if len(value[0]['Value']) > self.PUBLISHER_ID_LENGTH:
                            logging.error(f"Increase the `COUNTERData.publisher_ID` max field length to {int(len(value[0]['Value']) + (len(value[0]['Value']) * 0.1))}.")
                            return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                        else:
                            record_dict['publisher_ID'] = value[0]['Value']
                            logging.debug(f"Added `COUNTERData.publisher_ID` value {record_dict['publisher_ID']} to `record_dict`.")
                    else:
                        for type_and_value in value:
                            if re.match(r'[Pp]roprietary(_ID)?', string=type_and_value['Type']):
                                if len(type_and_value['Value']) > self.PUBLISHER_ID_LENGTH:
                                    logging.error(f"Increase the `COUNTERData.publisher_ID` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                    return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                                else:
                                    record_dict['publisher_ID'] = type_and_value['Value']
                                    logging.debug(f"Added `COUNTERData.publisher_ID` value {record_dict['publisher_ID']} to `record_dict`.")
                            else:
                                continue  # The `for type_and_value in value` loop
                
                #Section: Capture `platform` Value
                elif key == "Platform":
                    if len(value) > self.PLATFORM_LENGTH:
                        logging.error(f"Increase the `COUNTERData.platform` max field length to {int(len(value) + (len(value) * 0.1))}.")
                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                    else:
                        record_dict['platform'] = value
                        logging.debug(f"Added `COUNTERData.platform` value {record_dict['platform']} to `record_dict`.")
                
                #Section: Capture `authors` Value
                elif key == "Item_Contributors":
                    for type_and_value in value:
                        if re.match(r'[Aa]uthor', string=type_and_value['Type']):
                            if record_dict.get('authors'):
                                if record_dict['authors'].endswith(" et al."):
                                    continue  # The `for type_and_value in value` loop
                                elif len(record_dict['authors']) + len(type_and_value['Value']) + 8 > self.AUTHORS_LENGTH:
                                    record_dict['authors'] = record_dict['authors'] + " et al."
                                    logging.debug(f"Updated `COUNTERData.authors` value to {record_dict['parent_authors']} in `record_dict`.")
                                else:
                                    record_dict['authors'] = record_dict['authors'] + "; " + type_and_value['Value']
                                    logging.debug(f"Added `COUNTERData.authors` value {record_dict['authors']} to `record_dict`.")
                            
                            else:
                                if len(type_and_value['Value']) > self.AUTHORS_LENGTH:
                                    logging.error(f"Increase the `COUNTERData.authors` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                    return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                                else:
                                    record_dict['authors'] = type_and_value['Value']
                                    logging.debug(f"Added `COUNTERData.authors` value {record_dict['authors']} to `record_dict`.")
                
                #Section: Capture `publication_date` Value
                elif key == "Item_Dates":
                    for type_and_value in value:
                        if type_and_value['Type'] == "Publication_Date":  # Unlikely to be more than one; if there is, the field's date/datetime64 data type prevent duplicates from being preserved
                            record_dict['publication_date'] = datetime.date.fromisoformat(type_and_value['Value'])
                            logging.debug(f"Added `COUNTERData.publication_date` value {record_dict['publication_date']} to `record_dict`.")
                
                #Section: Capture `article_version` Value
                elif key == "Item_Attributes":
                    for type_and_value in value:
                        if type_and_value['Type'] == "Article_Version":  # Very unlikely to be more than one
                            record_dict['article_version'] = type_and_value['Value']
                            logging.debug(f"Added `COUNTERData.article_version` value {record_dict['article_version']} to `record_dict`.")
                
                #Section: Capture Standard Identifiers
                elif key == "Item_ID":
                    for type_and_value in value:
                        
                        #Subsection: Capture `DOI` Value
                        if type_and_value['Type'] == "DOI":
                            if len(type_and_value['Value']) > self.DOI_LENGTH:
                                logging.error(f"Increase the `COUNTERData.DOI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                            else:
                                record_dict['DOI'] = type_and_value['Value']
                                logging.debug(f"Added `COUNTERData.DOI` value {record_dict['DOI']} to `record_dict`.")
                        
                        #Subsection: Capture `proprietary_ID` Value
                        elif re.match(r'[Pp]roprietary(_ID)?', string=type_and_value['Type']):
                            if len(type_and_value['Value']) > self.PROPRIETARY_ID_LENGTH:
                                logging.error(f"Increase the `COUNTERData.proprietary_ID` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                            else:
                                record_dict['proprietary_ID'] = type_and_value['Value']
                                logging.debug(f"Added `COUNTERData.proprietary_ID` value {record_dict['proprietary_ID']} to `record_dict`.")
                        
                        #Subsection: Capture `ISBN` Value
                        elif type_and_value['Type'] == "ISBN":
                            record_dict['ISBN'] = str(type_and_value['Value'])  #ToDo: Since hyphen placement isn't uniform, should all hyphens be stripped?
                            logging.debug(f"Added `COUNTERData.ISBN` value {record_dict['ISBN']} to `record_dict`.")
                        
                        #subsection: Capture `print_ISSN` Value
                        elif type_and_value['Type'] == "Print_ISSN":
                            if re.match(r'\d{4}\-\d{3}[\dxX]\s*', string=type_and_value['Value']):
                                record_dict['print_ISSN'] = type_and_value['Value'].strip()
                                logging.debug(f"Added `COUNTERData.print_ISSN` value {record_dict['print_ISSN']} to `record_dict`.")
                            else:
                                record_dict['print_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                logging.debug(f"Added `COUNTERData.print_ISSN` value {record_dict['print_ISSN']} to `record_dict`.")
                        
                        #Subsection: Capture `online_ISSN` Value
                        elif type_and_value['Type'] == "Online_ISSN":
                            if re.match(r'\d{4}\-\d{3}[\dxX]\s*', string=type_and_value['Value']):
                                record_dict['online_ISSN'] = type_and_value['Value'].strip()
                                logging.debug(f"Added `COUNTERData.online_ISSN` value {record_dict['online_ISSN']} to `record_dict`.")
                            else:
                                record_dict['online_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                logging.debug(f"Added `COUNTERData.online_ISSN` value {record_dict['online_ISSN']} to `record_dict`.")
                        
                        #Subsection: Capture `URI` Value
                        elif type_and_value['Type'] == "URI":
                            if len(type_and_value['Value']) > self.URI_LENGTH:
                                logging.error(f"Increase the `COUNTERData.URI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                            else:
                                record_dict['URI'] = type_and_value['Value']
                                logging.debug(f"Added `COUNTERData.URI` value {record_dict['URI']} to `record_dict`.")
                        else:
                            continue  # The `for type_and_value in value` loop
                
                #Section: Capture `data_type` Value
                elif key == "Data_Type":
                    record_dict['data_type'] = value
                    logging.debug(f"Added `COUNTERData.data_type` value {record_dict['data_type']} to `record_dict`.")
                
                #Section: Capture `section_Type` Value
                elif key == "Section_Type":
                    record_dict['section_type'] = value
                    logging.debug(f"Added `COUNTERData.section_type` value {record_dict['section_type']} to `record_dict`.")
                

                #Section: Capture `YOP` Value
                elif key == "YOP":
                    record_dict['YOP'] = Int64Dtype(value)
                    logging.debug(f"Added `COUNTERData.YOP` value {record_dict['YOP']} to `record_dict`.")
                
                #Section: Capture `access_type` Value
                elif key == "Access_Type":
                    record_dict['access_type'] = value
                    logging.debug(f"Added `COUNTERData.access_type` value {record_dict['access_type']} to `record_dict`.")
                
                #Section: Capture `access_method` Value
                elif key == "Access_Method":
                    record_dict['access_method'] = value
                    logging.debug(f"Added `COUNTERData.access_method` value {record_dict['access_method']} to `record_dict`.")
                
                #Section: Capture Parent Resource Metadata
                elif key == "Item_Parent":
                    if repr(type(value)) == "<class 'list'>" and len(value) == 1:  # The `Item_Parent` value should be a dict, but sometimes that dict is within a one-item list; this removes the outer list
                        value = value[0]
                    for key_for_parent, value_for_parent in value.items():

                        #Subsection: Capture `parent_title` Value
                        if key_for_parent == "Item_Name":
                            if len(value_for_parent) > self.RESOURCE_NAME_LENGTH:
                                logging.error(f"Increase the `COUNTERData.parent_title` max field length to {int(len(value_for_parent) + (len(value_for_parent) * 0.1))}.")
                                return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                            else:
                                record_dict['parent_title'] = value
                                logging.debug(f"Added `COUNTERData.parent_title` value {record_dict['parent_title']} to `record_dict`.")
                        
                        #Subsection: Capture `parent_authors` Value
                        elif key_for_parent == "Item_Contributors":
                            for type_and_value in value:
                                if re.match(r'[Aa]uthor', string=type_and_value['Type']):
                                    if record_dict.get('parent_authors'):
                                        if record_dict['parent_authors'].endswith(" et al."):
                                            continue  # The `for type_and_value in value` loop
                                    elif len(record_dict['parent_authors']) + len(type_and_value['Value']) + 8 > self.AUTHORS_LENGTH:
                                        record_dict['parent_authors'] = record_dict['parent_authors'] + " et al."
                                        logging.debug(f"Updated `COUNTERData.parent_authors` value to {record_dict['parent_authors']} in `record_dict`.")
                                    else:
                                        record_dict['parent_authors'] = record_dict['parent_authors'] + "; " + type_and_value['Value']
                                        logging.debug(f"Updated `COUNTERData.parent_authors` value to {record_dict['parent_authors']} in `record_dict`.")
                                else:
                                    if len(type_and_value['Value']) > self.AUTHORS_LENGTH:
                                        logging.error(f"Increase the `COUNTERData.parent_authors` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                                    else:
                                        record_dict['parent_authors'] = type_and_value['Value']
                                        logging.debug(f"Added `COUNTERData.parent_authors` value {record_dict['parent_authors']} to `record_dict`.")
                        
                        #Subsection: Capture `parent_publication_date` Value
                        elif key_for_parent == "Item_Dates":
                            for type_and_value in value:
                                if type_and_value['Type'] == "Publication_Date":  # Unlikely to be more than one; if there is, the field's date/datetime64 data type prevent duplicates from being preserved
                                    record_dict['parent_publication_date'] = datetime.date.fromisoformat(type_and_value['Value'])
                                    logging.debug(f"Added `COUNTERData.parent_publication_date` value {record_dict['parent_publication_date']} to `record_dict`.")
                        
                        #Subsection: Capture `parent_article_version` Value
                        elif key_for_parent == "Item_Attributes":
                            for type_and_value in value:
                                if type_and_value['Type'] == "Article_Version":  # Very unlikely to be more than one
                                    record_dict['parent_article_version'] = type_and_value['Value']
                                    logging.debug(f"Added `COUNTERData.parent_article_version` value {record_dict['parent_article_version']} to `record_dict`.")

                        #Subsection: Capture `parent_data_type` Value
                        elif key_for_parent == "Data_Type":
                            record_dict['parent_data_type'] = value
                            logging.debug(f"Added `COUNTERData.parent_data_type` value {record_dict['parent_data_type']} to `record_dict`.")
                        
                        elif key_for_parent == "Item_ID":
                            for type_and_value in value:
                                
                                #Subsection: Capture `parent_DOI` Value
                                if type_and_value['Type'] == "DOI":
                                    if len(type_and_value['Value']) > self.DOI_LENGTH:
                                        logging.error(f"Increase the `COUNTERData.parent_DOI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                                    else:
                                        record_dict['parent_DOI'] = type_and_value['Value']
                                        logging.debug(f"Added `COUNTERData.parent_DOI` value {record_dict['parent_DOI']} to `record_dict`.")

                                #Subsection: Capture `parent_proprietary_ID` Value
                                elif re.match(r'[Pp]roprietary(_ID)?', string=type_and_value['Type']):
                                    if len(type_and_value['Value']) > self.PROPRIETARY_ID_LENGTH:
                                        logging.error(f"Increase the `COUNTERData.parent_proprietary_ID` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                                    else:
                                        record_dict['parent_proprietary_ID'] = type_and_value['Value']
                                        logging.debug(f"Added `COUNTERData.parent_proprietary_ID` value {record_dict['parent_proprietary_ID']} to `record_dict`.")

                                #Subsection: Capture `parent_ISBN` Value
                                elif type_and_value['Type'] == "ISBN":
                                    record_dict['parent_ISBN'] = str(type_and_value['Value'])  #ToDo: Since hyphen placement isn't uniform, should all hyphens be stripped?
                                    logging.debug(f"Added `COUNTERData.parent_ISBN` value {record_dict['parent_ISBN']} to `record_dict`.")

                                #Subsection: Capture `parent_print_ISSN` Value
                                elif type_and_value['Type'] == "Print_ISSN":
                                    if re.match(r'\d{4}\-\d{3}[\dxX]\s*', string=type_and_value['Value']):
                                        record_dict['parent_print_ISSN'] = type_and_value['Value'].strip()
                                        logging.debug(f"Added `COUNTERData.parent_print_ISSN` value {record_dict['parent_print_ISSN']} to `record_dict`.")
                                    else:
                                        record_dict['parent_print_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                        logging.debug(f"Added `COUNTERData.parent_print_ISSN` value {record_dict['parent_print_ISSN']} to `record_dict`.")

                                #Subsection: Capture `parent_online_ISSN` Value
                                elif type_and_value['Type'] == "Online_ISSN":
                                    if re.match(r'\d{4}\-\d{3}[\dxX]\s*', string=type_and_value['Value']):
                                        record_dict['parent_online_ISSN'] = type_and_value['Value'].strip()
                                        logging.debug(f"Added `COUNTERData.parent_online_ISSN` value {record_dict['parent_online_ISSN']} to `record_dict`.")
                                    else:
                                        record_dict['parent_online_ISSN'] = str(type_and_value['Value'])[:5] + "-" + str(type_and_value['Value']).strip()[-4:]
                                        logging.debug(f"Added `COUNTERData.parent_online_ISSN` value {record_dict['parent_online_ISSN']} to `record_dict`.")

                                #Subsection: Capture `parent_URI` Value
                                elif type_and_value['Type'] == "URI":
                                    if len(type_and_value['Value']) > self.URI_LENGTH:
                                        logging.error(f"Increase the `COUNTERData.parent_URI` max field length to {int(len(type_and_value['Value']) + (len(type_and_value['Value']) * 0.1))}.")
                                        return pd.DataFrame()  # Returning an empty dataframe tells `StatisticsSources._harvest_R5_SUSHI()` that this report can't be loaded
                                    else:
                                        record_dict['parent_URI'] = type_and_value['Value']
                                        logging.debug(f"Added `COUNTERData.parent_URI` value {record_dict['parent_URI']} to `record_dict`.")

                        else:
                            continue  # The `for key_for_parent, value_for_parent in value.items()` loop

                else:
                    pass  # The other keys in the JSON dict are handled outside of this loop
            
            
            #Section: Create Records by Iterating Through `Performance` Section of SUSHI JSON
            for performance in record['Performance']:
                record_dict['usage_date'] = datetime.date.fromisoformat(performance['Period']['Begin_Date'])
                for instance in performance['Instance']:
                    record_dict['metric_type'] = instance['Metric_Type']
                    record_dict['usage_count'] = instance['Count']
                    records_orient_list.append(record_dict)  # This adds the dictionary with the specific date, metric, and count combinations represented by each item in the `Instance` list
                    logging.info(f"Added record {record_dict} to `COUNTERData` relation.")

        
        #Section: Create Dataframe
        df_dtypes = {
            'platform' : 'string',
            'metric_type' : 'string',
            'usage_count' : 'int',
        }
        if record_dict.get('resource_name'):
            df_dtypes['resource_name'] = 'string'
        if record_dict.get('publisher'):
            df_dtypes['publisher'] = 'string'
        if record_dict.get('publisher_ID'):
            df_dtypes['publisher_ID'] = 'string'
        if record_dict.get('authors'):
            df_dtypes['authors'] = 'string'
        if record_dict.get('article_version'):
            df_dtypes['article_version'] = 'string'
        if record_dict.get('DOI'):
            df_dtypes['DOI'] = 'string'
        if record_dict.get('proprietary_ID'):
            df_dtypes['proprietary_ID'] = 'string'
        if record_dict.get('ISBN'):
            df_dtypes['ISBN'] = 'string'
        if record_dict.get('print_ISSN'):
            df_dtypes['print_ISSN'] = 'string'
        if record_dict.get('online_ISSN'):
            df_dtypes['online_ISSN'] = 'string'
        if record_dict.get('URI'):
            df_dtypes['URI'] = 'string'
        if record_dict.get('data_type'):
            df_dtypes['data_type'] = 'string'
        if record_dict.get('section_type'):
            df_dtypes['section_type'] = 'string'
        if record_dict.get('YOP'):
            df_dtypes['YOP'] = 'Int64'  # `smallint` in database; using the pandas data type here because it allows null values
        if record_dict.get('access_type'):
            df_dtypes['access_type'] = 'string'
        if record_dict.get('access_method'):
            df_dtypes['access_method'] = 'string'
        if record_dict.get('parent_title'):
            df_dtypes['parent_title'] = 'string'
        if record_dict.get('parent_authors'):
            df_dtypes['parent_authors'] = 'string'
        if record_dict.get('parent_article_version'):
            df_dtypes['parent_article_version'] = 'string'
        if record_dict.get('parent_data_type'):
            df_dtypes['parent_data_Type'] = 'string'
        if record_dict.get('parent_DOI'):
            df_dtypes['parent_DOI'] = 'string'
        if record_dict.get('parent_proprietary_ID'):
            df_dtypes['parent_proprietary_ID'] = 'string'
        if record_dict.get('parent_ISBN'):
            df_dtypes['parent_ISBN'] = 'string'
        if record_dict.get('parent_print_ISSN'):
            df_dtypes['parent_print_ISSN'] = 'string'
        if record_dict.get('parent_online_ISSN'):
            df_dtypes['parent_online_ISSN'] = 'string'
        if record_dict.get('parent_URI'):
            df_dtypes['parent_URI'] = 'string'

        df = pd.read_json(
            records_orient_list,
            orient='records',
            dtype=df_dtypes,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )

        if record_dict.get('publication_date'):
            df['publication_date'] = pd.to_datetime(
                df['publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
                infer_datetime_format=True,
            )
        if record_dict.get('parent_publication_date'):
            df['parent_publication_date'] = pd.to_datetime(
                record_dict['parent_publication_date'],
                errors='coerce',  # Changes the null values to the date dtype's null value `NaT`
                infer_datetime_format=True,
            )
        df['usage_date'] = pd.to_datetime(df['usage_date'])
        df['report_creation_date'] = pd.to_datetime(df['report_creation_date'])

        return df