import logging
import requests
from requests import HTTPError
from requests import Timeout

logging.basicConfig(level=logging.INFO, format="SUSHICallAndResponse - - [%(asctime)s] %(message)s")


class SUSHICallAndResponse:
    """A class that makes SUSHI API calls.

    This class is functionally a Python dictionary--the constructor method makes a SUSHI API call and returns the call's results with Python data types. Objects of this class can and should be used as dictionaries.

    Attributes:
        self.call_URL (str): the root URL for the SUSHI API call
        self.call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        self.parameter_string (str): the parameter values of the API call as a string, converted from a dictionary to prevent encoding problems
    
    Methods:
        retrieve_downloaded_JSON: Retrieves a downloaded response to a SUSHI API call.
        #ToDo: Check the response for possible COUNTER error codes and determine if there's a problem in the data itself
    """
    # Constructor Method
    def __init__(self, call_URL, call_path, parameters):
        """Makes a SUSHI API call, returning a JSON-like dictionary that uses Python data types.

        This API call method handles all the possible calls in the SUSHI standard. It then converts the responses to native Python data types and handles any error codes the response may have had.

        Args:
            call_URL (str): the root URL for the SUSHI API call
            call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
            parameters (dict): the parameter values as key-value pairs
        """
        self.call_URL = call_URL
        self.call_path = call_path
        self.parameter_string = "&".join(f"{key}={value}" for key, value in parameters.items())

        #Section: Make API Call


        #Section: Convert Response to Python Data Types


        #Section: Check for SUSHI Error Codes
        

    # Representation method--using `{self}` in an f-string results in the below
    def __repr__(self):
        return


    def retrieve_downloaded_JSON(self):
        """Retrieves a downloaded response to a SUSHI API call. 

        For API calls that generate a JSON file download in response, this method captures and reads the contents of the downloaded file, then removes the file.
        """
        pass