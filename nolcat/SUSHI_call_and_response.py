import logging
import time
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
        Chrome_user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # Using this in the header makes the URL request appear to come from a Chrome browser and not the requests module; some platforms return 403 errors with the standard requests header
        API_call_URL = self.call_URL = self.call_path
        time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this provides spacing
        try:
            API_response = requests.get(API_call_URL, params=self.parameter_string, timeout=90, headers=Chrome_user_agent)
            API_response.raise_for_status()
            #Alert: MathSciNet doesn't have a status report, but does have the other reports with the needed data--how should this be handled so that it can pass through?
        
        except Timeout as error:
            try:  # Timeout errors seem to be random, so going to try get request again with more time
                time.sleep(1)
                API_response = requests.get(API_call_URL, params=self.parameter_string, timeout=299, headers=Chrome_user_agent)
                API_response.raise_for_status()
            
            except Timeout as error_plus_timeout:
                logging.warning(f"Call to {API_call_URL} raised timeout errors {format(error)} and {format(error_plus_timeout)}")
                #ToDo: Return something that indicates the API call failed
            
            except HTTPError as error_plus_timeout:
                if format(error_plus_timeout.response) == "<Response [403]>":
                    API_response = self.retrieve_downloaded_JSON()
                    if API_response == []:
                        logging.warning(f"Call to {API_call_URL} raised errors {format(error)} and {format(error_plus_timeout)}")
                        #ToDo: Return something that indicates the API call failed
                else:
                    logging.warning(f"Call to {API_call_URL} raised errors {format(error)} and {format(error_plus_timeout)}")
                    #ToDo: Return something that indicates the API call failed
            
            except Exception as error_plus_timeout:
                logging.warning(f"Call to {API_call_URL} raised errors {format(error)} and {format(error_plus_timeout)}")
                #ToDo: Return something that indicates the API call failed
        
        except HTTPError as error:
            if format(error.response) == "<Response [403]>":
                API_response = self.retrieve_downloaded_JSON()
                if API_response == []:
                    logging.warning(f"Call to {API_call_URL} raised error {format(error)}")
                    #ToDo: Return something that indicates the API call failed
            else:
                logging.warning(f"Call to {API_call_URL} raised error {format(error)}")
                #ToDo: Return something that indicates the API call failed
        
        except Exception as error:
            # Old note: ToDo: Be able to view error information and confirm or deny if site is safe
            # Old note: Attempt to isolate Allen Press by SSLError message and redo request without checking certificate led to ConnectionError
            logging.warning(f"Call to {API_call_URL} raised error {format(error)}")
            #ToDo: Return something that indicates the API call failed


        #Section: Convert Response to Python Data Types
        try:
            if API_response.text == "":
                logging.warning(f"Call to {API_call_URL} returned an empty string")
                #ToDo: Return something that indicates the API call failed
        except:
            pass  # In the case that API_response isn't a Requests response object, nothing needs to happen here

        if str(type(API_response)) == "<class 'requests.models.Response'>":
            try:
                API_response = API_response.json()
                #ToDo: Figure out how to get titles with Unicode replacement character to encode properly
                    # json.loads(JSON.text.encode('utf8')) still has replacement character
                    # json.loads(JSON.text.decode('utf8')) still has replacement character
                    # json.loads(JSON.text) still has replacement character
                    # json.loads(JSON.content.decode('utf8')) creates a JSON from the first item in Report_Items rather than the complete content, so ability to handle replacement characters unknown
            except:
                logging.warning(f"Call to {API_call_URL} returned a JSON that couldn't be converted into a dictionary")
                #ToDo: Return something that indicates the API call failed
        
        if str(type(API_response)) == "<class 'list'>" and len(API_response) == 1 and str(type(API_response[0])) == "<class 'dict'>":
            API_response = API_response[0]
        
        if str(type(API_response)) == "<class 'dict'>":
            pass
        else:
            logging.warning(f"Call to {API_call_URL} returned an object of the {str(type(API_response))} type and thus wasn't converted into a dict for further processing.")
                #ToDo: Return something that indicates the API call failed


        #Section: Check for SUSHI Error Codes
        # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
        try:  # status check response is JSON-like dictionary with Report_Header and information about the error
            test = API_response["Exception"]["Severity"]
            print(test)
            # if Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check["Exception"]["Message"], Status_Check_Error, Status_Check["Exception"]["Code"]): continue
        except:
            pass

        try:  # status check response is JSON-like dictionary with nothing but information about the error
            test = API_response["Severity"]
            print(test)
            # if Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check["Message"], Status_Check_Error, Status_Check["Code"]): continue
        except:
            pass

        try:  # status check response has COUNTER Alerts
            test = API_response["Alerts"]
            print(test)
            # Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check_Alert): continue
        except:
            pass

        try:  # master report response is JSON-like dictionary with top-level key of "Report_Header" that includes the key "Exceptions"
            test = API_response["Report_Header"]["Exceptions"]
            print(test)
            # if "Report_Items" in Master_Report_Response:
                # if Handle_Exception_Master_Report(SUSHI_Call_Data["JSON_Name"], Master_Report_Type, Master_Report_Exceptions, True): continue
            # else:
                # if Handle_Exception_Master_Report(SUSHI_Call_Data["JSON_Name"], Master_Report_Type, Master_Report_Exceptions): continue
        except:
            pass

        try:  # master report response is JSON-like dictionary containing only the content of a single Exception
            if "Code" in API_response or "code" in API_response:
                test = [API_response]  # Using a list constructor creates a list of the keys; what's needed is a list with one item that's a dictionary
            print(test)
            # if Handle_Exception_Master_Report(SUSHI_Call_Data["JSON_Name"], Master_Report_Type, Master_Report_Response): continue
        except:
            pass

        #ToDo: There was an issue with some master report errors not being caught by the standard error handling; a try block for a log statement with the len() of the dict's ['Report_Items'] attribute caught the remainder


    # Representation method--using `{self}` in an f-string results in the below
    def __repr__(self):
        return


    def retrieve_downloaded_JSON(self):
        """Retrieves a downloaded response to a SUSHI API call. 

        For API calls that generate a JSON file download in response, this method captures and reads the contents of the downloaded file, then removes the file.
        """
        pass