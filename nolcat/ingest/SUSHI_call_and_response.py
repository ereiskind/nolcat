import logging

logging.basicConfig(level=logging.INFO, format="SUSHICallAndResponse - - [%(asctime)s] %(message)s")


class SUSHICallAndResponse:
    """[summary]
    #ToDo: Create class that makes SUSHI API calls with error checking for both the API calls and the SUSHI content

    [extended_summary]

    Attributes:
        self.call_URL (str): the root URL for the SUSHI API call
        self.call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        self.parameter_string (str): the parameter values of the API call as a string, converted from a dictionary to prevent encoding problems
    
    Methods:
        #ToDo: Perform API call, checking that there weren't any problems
        #ToDo: Handle API calls that trigger a JSON file download instead of putting the data in a HTML body
        #ToDo: Check the response for possible COUNTER error codes and determine if there's a problem in the data itself
    """
    # Constructor Method
    def __init__(self, call_URL, call_path, parameters):
        """[summary]
        #ToDo: This version of the constructor just turns the initial arguments into class attributes, but the class could also be designed to take in the same arguments and perform the API call as part of the constructor

        [extended_summary]

        Args:
            call_URL (str): the root URL for the SUSHI API call
            call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
            parameters (dict): the parameter values as key-value pairs
        """
        self.call_URL = call_URL
        self.call_path = call_path
        self.parameter_string = "&".join(f"{key}={value}" for key, value in parameters.items())
        

    # Representation method--using `{self}` in an f-string results in the below
    def __repr__(self):
        return 