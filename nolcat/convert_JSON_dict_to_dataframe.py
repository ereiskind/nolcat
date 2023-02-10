import logging
import re
from dateutil import parser
import pandas as pd

import models

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
    # Class variables
    RESOURCE_NAME_LENGTH = models.RESOURCE_NAME_LENGTH
    PUBLISHER_LENGTH = models.PUBLISHER_LENGTH
    PUBLISHER_ID_LENGTH = models.PUBLISHER_ID_LENGTH
    PLATFORM_LENGTH = models.PLATFORM_LENGTH
    AUTHORS_LENGTH = models.AUTHORS_LENGTH
    DOI_LENGTH = models.DOI_LENGTH
    PROPRIETARY_ID_LENGTH = models.PROPRIETARY_ID_LENGTH
    URI_LENGTH = models.URI_LENGTH

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
            #ToDo: For each of the below, determine if `record[listed_item]` exists, and if it does, add it with the appropriately lowercase field name to `record_dict`
                #ToDo: `platform`
                #ToDo: `authors`
                #ToDo: `publication_date`
                #ToDo: `article_version`
                #ToDo: `DOI`
                #ToDo: `proprietary_ID`
                #ToDo: `ISBN`
                #ToDo: `print_ISSN`
                #ToDo: `online_ISSN`
                #ToDo: `URI`
                #ToDo: `data_type`
                #ToDo: `section_type`
                #ToDo: `YOP`
                #ToDo: `access_type`
                #ToDo: `access_method`
                #ToDo: `parent_title`
                #ToDo: `parent_authors`
                #ToDo: `parent_publication_date`
                #ToDo: `parent_article_version`
                #ToDo: `parent_data_type`
                #ToDo: `parent_DOI`
                #ToDo: `parent_proprietary_ID`
                #ToDo: `parent_ISBN`
                #ToDo: `parent_print_ISSN`
                #ToDo: `parent_online_ISSN`
                #ToDo: `parent_URI`
                #ToDo: `metric_type`
                #ToDo: `usage_date`
                #ToDo: `usage_count`
            records_orient_list.append(record_dict)
        df_dtypes = {
            # 'COUNTER_data_ID' : '',
            # 'statistics_source_ID' : '',
            # 'report_type' : '',
            # 'resource_name' : '',
            # 'publisher' : '',
            # 'publisher_ID' : '',
            # 'platform' : '',
            # 'authors' : '',
            # 'publication_date' : '',
            # 'article_version' : '',
            # 'DOI' : '',
            # 'proprietary_ID' : '',
            # 'ISBN' : '',
            # 'print_ISSN' : '',
            # 'online_ISSN' : '',
            # 'URI' : '',
            # 'data_type' : '',
            # 'section_type' : '',
            # 'YOP' : '',
            # 'access_type' : '',
            # 'access_method' : '',
            # 'parent_title' : '',
            # 'parent_authors' : '',
            # 'parent_publication_date' : '',
            # 'parent_article_version' : '',
            # 'parent_data_type' : '',
            # 'parent_DOI' : '',
            # 'parent_proprietary_ID' : '',
            # 'parent_ISBN' : '',
            # 'parent_print_ISSN' : '',
            # 'parent_online_ISSN' : '',
            # 'parent_URI' : '',
            # 'metric_type' : '',
            # 'usage_date' : '',
            # 'usage_count' : '',
        }
        df = pd.read_json(
            records_orient_list,
            orient='records',
            dtype=df_dtypes,
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        return df

        



        
        
        
        
        
        
        
        
        
        
    












