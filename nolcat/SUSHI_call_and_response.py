import logging
import time
import re
import json
import ast
from datetime import datetime
from pathlib import Path
import random
import requests
from requests import Timeout
import pandas as pd
import pyinputplus

from .app import *

log = logging.getLogger(__name__)


class SUSHICallAndResponse:
    """A class that makes SUSHI API calls in the StatisticsSources._harvest_R5_SUSHI method.

    This class encapsulates the functionality for making SUSHI API calls. Based on the structure suggested at https://stackoverflow.com/a/48574985, the functionality for creating this SUSHI data dictionary object has been divided into the traditional __init__ method, which instantiates the class attributes, and the `make_SUSHI_call()` method, which actually performs the steps of the API call. This structure requires all instances of the class constructor to be prepended to a call to the `make_SUSHI_call()` method, which has two major results:
    * Objects of the `SUSHICallAndResponse` type are never instantiated; a dictionary, the return value of `make_SUSHI_call()`, is returned instead.
    * With multiple return statements, a single item dictionary with the key `ERROR` and a value with a message about the problem can be returned if there's a problem with the API call or the returned SUSHI value.

    Attributes:
        self.header_value (dict): a class attribute containing a value for the requests header that makes the URL request appear to come from a Chrome browser and not the requests module; some platforms return 403 errors with the standard requests header
        self.calling_to (str): the name of statistics source the SUSHI API call is going to (the `StatisticsSources.statistics_source_name` attribute)
        self.call_URL (str): the root URL for the SUSHI API call
        self.call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        self.parameters (dict): the parameter values for the API call
    
    Methods:
        make_SUSHI_call: Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.
        _make_API_call: Makes a call to the SUSHI API.
        _convert_Response_to_JSON: Converts the `text` attribute of a `requests.Response` object to native Python data types.
        _save_raw_Response_text: Saves the `text` attribute of a `requests.Response` object that couldn't be converted to native Python data types to a text file.
        _handle_SUSHI_exceptions: The method presents the user with the error in the SUSHI response(s) and asks if the `StatisticsSources._harvest_R5_SUSHI()` method should continue.
        _create_error_query_text: This method creates the text for the `handle_SUSHI_exceptions()` dialog box.
    """
    header_value = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


    def __init__(self, calling_to, call_URL, call_path, parameters):
        """The constructor method for SUSHICallAndResponse, which sets the attribute values for each instance.

        This constructor is not meant to be used alone; all class instantiations should feature a `make_SUSHI_call` method call.

        Args:
            calling_to (str): the name of statistics source the SUSHI API call is going to (the StatisticsSources.statistics_source_name attribute)
            call_URL (str): the root URL for the SUSHI API call
            call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
            parameters (dict): the parameter values for the API call
        """
        self.calling_to = calling_to
        self.call_URL = call_URL
        self.call_path = call_path
        self.parameters = {key: (requests.utils.unquote(value) if isinstance(value, str) else value.strftime("%Y-%m")) for key, value in parameters.items()}
    

    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        pass
    

    def make_SUSHI_call(self):
        """Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.

        This method calls two other methods in sequence: `_make_API_call()`, which makes the API call itself, and `_convert_Response_to_JSON()`, which changes the `Response.text` attribute of the value returned by `_make_API_call()` into native Python data types. This division is done so `Response.text` attributes that can't be changed into native Python data types can more easily be saved as text files in a S3 bucket for preservation and possible later review.

        Returns:
            dict: the API call response or an error message
        """
        #Section: Make API Call
        log.info(f"Starting `make_SUSHI_call()` to {self.calling_to} for {self.call_path}.")  # `self.parameters` not included because 1) it shows encoded values (e.g. `%3D` is an equals sign) that are appropriately unencoded in the GET request and 2) repetitions of secret information in plain text isn't secure
        API_response = self._make_API_call()
        if isinstance(API_response, dict):  # Meaning the SUSHI API call couldn't be made
            log.error(API_response)
            return API_response

        #Section: Confirm Usage Data in Response
        if API_response.text == "":
            message = f"Call to {self.calling_to} returned an empty string."
            log.warning(message)
            return {"ERROR": message}
        
        #Section: Convert Response to Python Data Types
        try:
            API_response = self._convert_Response_to_JSON(API_response)
        except Exception as error:
            return_dict_value = self._save_raw_Response_text(error, API_response.text, exception=True)
            log.error(return_dict_value)
            return {"ERROR": return_dict_value}
        if isinstance(API_response, tuple) and isinstance(API_response[1], Exception):
            return_dict_value = self._save_raw_Response_text(API_response[1], API_response[0].text, exception=True)
            log.error(return_dict_value)
            return {"ERROR": return_dict_value}
        if len(API_response.keys()) == 1 and list(API_response.keys()) == "ERROR":
            return_dict_value = self._save_raw_Response_text(API_response['ERROR'], API_response.text)
            log.error(return_dict_value)
            return {"ERROR": return_dict_value}

        #Section: Check for SUSHI Error Codes
        # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
        # JSONs for SUSHI data that's deemed problematic aren't saved as files because doing so would be keeping bad data

        try:  #ALERT: Couldn't find a statistics source to use as a test case
            log.debug(f"The report has a `Report_Header` with an `Exception` key containing a single exception or a list of exceptions: {API_response['Report_Header']['Exception']}.")
            if not self._handle_SUSHI_exceptions(API_response['Report_Header']['Exception'], self.call_path, self.calling_to):
                message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response['Report_Header']['Exception']}`."
                log.warning(message)
                return {"ERROR": message}
        except:
            pass

        try:
            log.debug(f"The report has a `Report_Header` with an `Exceptions` key containing a single exception or a list of exceptions: {API_response['Report_Header']['Exceptions']}.")
            if not self._handle_SUSHI_exceptions(API_response['Report_Header']['Exceptions'], self.call_path, self.calling_to):
                message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response['Report_Header']['Exceptions']}`."
                log.warning(message)
                return {"ERROR": message}
        except:
            pass

        try:  #ALERT: Couldn't find a statistics source to use as a test case--prior code indicates this case appears in response to `status` calls
            log.debug(f"The report has an `Exception` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Exception']}.")
            if not self._handle_SUSHI_exceptions(API_response['Exception'], self.call_path, self.calling_to):
                message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response['Exception']}`."
                log.warning(message)
                return {"ERROR": message}
        except:
            pass

        try:  #ALERT: Couldn't find a statistics source to use as a test case
            log.debug(f"The report has an `Exceptions` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Exceptions']}.")
            if not self._handle_SUSHI_exceptions(API_response['Exceptions'], self.call_path, self.calling_to):
                message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response['Exceptions']}`."
                log.warning(message)
                return {"ERROR": message}
        except:
            pass

        try:  #ALERT: Couldn't find a statistics source to use as a test case
            log.debug(f"The report has an `Alert` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Alert']}.")
            if not self._handle_SUSHI_exceptions(API_response['Alert'], self.call_path, self.calling_to):
                message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response['Alert']}`."
                log.warning(message)
                return {"ERROR": message}
        except:
            pass

        try:  #ALERT: Couldn't find a statistics source to use as a test case
            log.debug(f"The report has an `Alerts` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Alerts']}.")
            if not self._handle_SUSHI_exceptions(API_response['Alerts'], self.call_path, self.calling_to):
                message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response['Alerts']}`."
                log.warning(message)
                return {"ERROR": message}
        except:
            pass

        try:
            if "Message" in API_response.keys():
                log.debug("The report is nothing but a dictionary of the key-value pairs found in an `Exceptions` block.")
                if not self._handle_SUSHI_exceptions(API_response, self.call_path, self.calling_to):
                    message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response}`."
                    log.warning(message)
                    return {"ERROR": message}
        except:
            pass

        try:
            if "Message" in API_response[0].keys():  # The `keys()` iterator also serves as a check that the item in the list is a dictionary
                log.debug("The report is nothing but a list of dictionaries of the key-value pairs found in an `Exceptions` block.")
                if not self._handle_SUSHI_exceptions(API_response, self.call_path, self.calling_to):
                    message = f"Call to {self.calling_to} returned the SUSHI error(s) `{API_response}`."
                    log.warning(message)
                    return {"ERROR": message}
        except:
            pass

        #Subsection: Check Customizable Reports for Data
        # Some customizable reports errors weren't being caught by the error handlers above despite matching the criteria; some statistics sources offer reports for content they don't have (statistics sources without databases providing database reports is the most common example). In both cases, reports containing no data should be caught as potential errors. This check comes after the checks for common SUSHI errors because errors can cause a report to be returned with no usage data.
        custom_report_regex = re.compile(r'reports/[PpDdTtIi][Rr]')
        if custom_report_regex.search(self.call_path):
            message = f"Call to {self.calling_to} for {self.call_path} returned no usage data, which may or may not be appropriate."
            try:
                if len(API_response['Report_Items']) == 0:
                    log.warning(message)
                    return {"ERROR": message}
            except TypeError:
                log.warning(message)
                return {"ERROR": message}
        
        #Section: Display to Stdout and Return `API_response`
        if custom_report_regex.search(self.call_path):
            # For some custom reports, the complete `API_response` value can be so long that it keeps most of the pytest log from appearing in stdout; the following is meant to prevent that
            number_of_report_items = len(API_response['Report_Items'])
            log.info(f"The SUSHI API response header: {API_response['Report_Header']}")
            log.info(f"A SUSHI API report item: {API_response['Report_Items'][random.choice(range(number_of_report_items))]}")
            if number_of_report_items < 30:
                log.debug(f"The SUSHI API response as a JSON:\n{API_response}")
            else:
                log.debug(f"A sample of the SUSHI API response:")
                if number_of_report_items > 300:
                    for n in random.sample(range(number_of_report_items), k=30):
                        log.debug(API_response['Report_Items'][n])
                else:
                    for n in random.sample(range(number_of_report_items), k=int(number_of_report_items/10)):
                        log.debug(API_response['Report_Items'][n])
        else:
            log.info(f"The SUSHI API response to a {self.call_path} call as a JSON:\n{API_response}")
        return API_response


    def _make_API_call(self):
        """Makes a call to the SUSHI API.

        This method uses the requests library to handle all the possible calls in the SUSHI standard.
        
        Returns:
            requests.Response: the complete Response object returned by the GET request to the API
            dict: error message to indicate to `StatisticsSources._harvest_single_report()` that the API call failed
        """
        log.info(f"Starting `_make_API_call()` by calling {self.calling_to} for {self.call_path}.")  # `self.parameters` not included because 1) it shows encoded values (e.g. `%3D` is an equals sign) that are appropriately unencoded in the GET request and 2) repetitions of secret information in plain text isn't secure
        API_call_URL = self.call_URL + self.call_path

        try:  # `raise_for_status()` returns Exception objects if the HTTP status is 4XX or 5XX, so using it requires try/except logic (2XX codes return `None` and the redirects of 3XX are followed)
            time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this provides spacing
            API_response = requests.get(API_call_URL, params=self.parameters, timeout=90, headers=self.header_value)
            log.info(f"`API_response` HTTP code: {API_response}")  # In the past, GET requests that returned JSON downloads had HTTP status 403
            API_response.raise_for_status()

        except Timeout as error:
            try:  # Timeout errors seem to be random, so going to try get request again with more time
                log.info(f"Calling {self.calling_to} for {self.call_path} again.")
                time.sleep(1)
                API_response = requests.get(API_call_URL, params=self.parameters, timeout=299, headers=self.header_value)
                log.info(f"`API_response` HTTP code: {API_response}")
                API_response.raise_for_status()
            except Timeout as error_after_timeout:  #ALERT: On 2022-12-16, ProQuest got to this point when pulling the IR for 12 months and automatically began making GET calls with port 80 (standard HTTP requests vs. HTTPS requests with port 443), repeating the call just under five minutes later without any indication the prior request actually got a timeout error
                message = f"Call to {self.calling_to} raised timeout errors {error} and {error_after_timeout}."
                log.error(message)
                return {"ERROR": message}
            except Exception as error_after_timeout:
                message = f"Call to {self.calling_to} raised errors {error} and {error_after_timeout}."
                log.error(message)
                return {"ERROR": message}

        except Exception as error:
            #ToDo: View error information and, if data can be pulled with modification of API call, repeat call in way that works
            return {"ERROR": f"Call to {self.calling_to} raised error {error}"}

        log.info(f"GET request for {self.calling_to} at {self.call_path} successful.")
        return API_response


    def _convert_Response_to_JSON(self, API_response):
        """Converts the `text` attribute of a `requests.Response` object to native Python data types.

        Args:
            API_response (requests.Response): the response returned by the SUSHI API call
        
        Returns:
            dict: the API call response in native Python data types or an error message
        """
        #Section: Convert Text Attributes for Calls to `reports` Endpoint
        # `reports` endpoints should result in a list, not a dictionary, so they're being handled separately
        if self.call_path == "reports":
            if isinstance(API_response.text, str):
                try:
                    log.info("The returned text was read from a downloaded JSON file but was the response to a `reports` call and should thus be a list.")
                    API_response = ast.literal_eval(API_response.content.decode('utf-8'))
                except Exception as error:
                    log.error(f"Converting a string with `ast.literal_eval(string.content.decode('utf-8'))` raised {error}.")
                    return (API_response, error)
            elif isinstance(API_response.text, list):
                try:
                    log.info(f"The returned text is in list format and is the list of reports.")
                    API_response = json.loads(API_response.content.decode('utf-8'))
                except Exception as error:
                    log.error(f"Converting a list with `json.loads(list.content.decode('utf-8'))` raised {error}.")
                    return (API_response, error)
            else:
                message = f"Call to {self.calling_to} returned a downloaded JSON file with data of a {repr(type(API_response.text))} text type; it couldn't be converted to native Python data types. The raw JSON file is being saved instead."
                log.warning(message)
                return {"ERROR": message}
                
            if isinstance(API_response, list):
                API_response = dict(reports = API_response)
                log.info("The returned text was or was converted into a list of reports and, to match the other reports' data types, made the value of an one-item dictionary.")
            else:
                message = f"Call to {self.calling_to} returned a downloaded JSON file with data of a {repr(type(API_response))} text type that couldn't be converted into the value of a native Python dictionary. The raw JSON file is being saved instead."
                log.error(message)
                return {"ERROR": message}
        
        #Section: Convert Text Attributes for Calls to Other Endpoints
        else:
            if isinstance(API_response.text, str):
                log.info("The returned text was read from a downloaded JSON file.")
                try:
                    API_response = json.loads(API_response.content.decode('utf-8'))
                except:  # This will transform values that don't decode as JSONs (generally lists)
                    try:
                        API_response = ast.literal_eval(API_response.content.decode('utf-8'))
                    except Exception as error:
                        log.error(f"Converting a string with `ast.literal_eval(string.content.decode('utf-8'))` raised {error}.")
                        return (API_response, error)
                
                if isinstance(API_response, dict):
                    log.info("The returned text was converted to a dictionary.")
                
                elif isinstance(API_response, list) and len(API_response) == 1 and isinstance(API_response[0], dict):
                    log.info(f"The returned text was converted to a a dictionary wrapped in a single-item list, so the item in the list will be converted to native Python data types.")
                    API_response = API_response[0]
                
                else:
                    message = f"Call to {self.calling_to} returned a downloaded JSON file with data of a {repr(type(API_response))} text type, which doesn't match SUSHI logic; it couldn't be converted to native Python data types. The `requests.Response.text` value is being saved to a file instead."
                    log.error(message)
                    return {"ERROR": message}
            
            elif isinstance(API_response.text, dict):
                try:
                    log.info("The returned text is in dictionary format, so it's ready to be converted to native Python data types.")
                    API_response = json.loads(API_response.content.decode('utf-8'))
                except Exception as error:
                    log.error(f"Converting a dict with `json.loads(dict.content.decode('utf-8'))` raised {error}.")
                    return (API_response, error)
            
            elif isinstance(API_response.text, list) and len(API_response.text) == 1 and isinstance(API_response[0].text, dict):
                try:
                    log.info("The returned text is a dictionary wrapped in a single-item list, so the item in the list will be converted to native Python data types.")
                    API_response = json.loads(API_response[0].content.decode('utf-8'))
                except Exception as error:
                    log.error(f"Converting a list with `json.loads(list[0].content.decode('utf-8'))` raised {error}.")
                    return (API_response, error)
            
            else:
                message = f"Call to {self.calling_to} returned an object of the {repr(type(API_response))} type with a {repr(type(API_response.text))} text type; it couldn't be converted to native Python data types. The `requests.Response.text` value is being saved to a file instead."
                log.error(message)
                return {"ERROR": message}
        
        log.info(f"SUSHI data converted to {repr(type(API_response))}.")
        if isinstance(API_response, pd.core.frame.DataFrame):
            log.info(f"Sample of SUSHI data:\n{API_response.head()}")  # Because `API_response` can be very long, the `info` logging statement shows only a small portion of the dataframe
        log.debug(f"SUSHI data:\n{API_response}")
        return API_response
    

    def _save_raw_Response_text(self, error_message, Response_text, exception=False):
        """Saves the `text` attribute of a `requests.Response` object that couldn't be converted to native Python data types to a text file.

        Args:
            error_message (str): either details of the situation that raised the error if an expected situation or the name of a Python error if an unexpected situation
            Response_text (str): the Unicode string that couldn't be converted to native Python data types
            exception (bool): a Boolean indicating if the error was an uncaught exception raised during `_convert_Response_to_JSON()`; defaults to `False`
        
        Returns:
            str: the error message for the value section of the single-item `ERROR` dictionary
        """
        if exception:
            error_message = f"The `SUSHICallAndResponse._convert_Response_to_JSON()` method unexpectedly raised a(n) `{error_message}` error, meaning the `requests.Response.content` couldn't be converted to native Python data types. The `requests.Response.text` value is being saved to a file instead."
        log.error(error_message)
        
        statistics_source_ID = pd.read_sql(
            sql=f'SELECT statistics_source_ID FROM statisticsSources WHERE statistics_source_name={self.calling_to}',
            con=db.engine,
        )
        temp_file_path = Path().resolve() / 'temp.txt'
        with open(temp_file_path, 'xb', errors='backslashreplace') as file:  # The response text is being saved to a file because `upload_file_to_S3_bucket()` takes file-like objects or path-like objects that lead to file-like objects
            file.write(Response_text)
        
        upload_file_to_S3_bucket(
            temp_file_path,
            f"{statistics_source_ID.iloc[0][0]}_{self.call_path.replace('/', '-')}_{self.parameters['begin_date'].strftime('%Y-%m')}_{self.parameters['end_date'].strftime('%Y-%m')}_{datetime.now().isoformat()}.txt",
        )
        temp_file_path.unlink()
        return error_message


    def _handle_SUSHI_exceptions(self, error_contents, report_type, statistics_source):
        """The method presents the user with the error in the SUSHI response(s) and asks if the StatisticsSources._harvest_R5_SUSHI method should continue.

        This method presents the user with the error(s) returned in a SUSHI call and asks if the error should be validated. For status calls, this means not making any further SUSHI calls to the resource at the time; for report calls returning usage data, it means not loading the report data into the database.
        
        Args:
            error_contents (dict or list): the contents of the error message(s)
            report_type (str): the type of report being requested, determined by the value of `call_path`
            statistics_source (str): the name of the statistics source that returned the SUSHI call in question
        
        Returns:
            bool: if the StatisticsSources._harvest_R5_SUSHI method should continue
        """
        #Section: Create Error Message(s)
        #Subsection: Detail Each SUSHI Error
        if error_contents is None:
            log.info(f"This statistics source had a key for a SUSHI error with null value, which occurs for some status reports. Since there is no actual SUSHI error, the user is not being asked how to handle the error.")
            return True
        elif isinstance(error_contents, dict):
            if len(error_contents['Message']) == 0:
                log.info(f"This statistics source had a key for a SUSHI error with an empty value, which occurs for some status reports. Since there is no actual SUSHI error, the user is not being asked how to handle the error.")
                return True
            log.debug(f"Handling a SUSHI error for a {report_type} in dictionary format.")
            dialog_box_text = self._create_error_query_text(error_contents)
        elif isinstance(error_contents, list):
            if len(error_contents) == 0:
                log.info(f"This statistics source had a key for a SUSHI error with an empty value, which occurs for some status reports. Since there is no actual SUSHI error, the user is not being asked how to handle the error.")
                return True
            dialog_box_text = []
            log.debug(f"Handling a SUSHI error for a {report_type} in list format.")
            for error in error_contents:
                dialog_box_text.append(self._create_error_query_text(error))
            dialog_box_text = "\n".join(dialog_box_text)
        else:
            log.info(f"SUSHI error handling method for a {report_type} accepted data of an invalid type.")
            return False  # Since error_contents was of an invalid data type, something went wrong, so the method should be terminated.
        
        #Subsection: Ask the User What To Do
        if report_type == "status" or report_type == "reports":
            dialog_box_text = dialog_box_text + f"\nShould usage statistics be collected from {statistics_source}?"
        else:
            dialog_box_text = dialog_box_text + f"\nShould this usage data be loaded into the database?"
        

        #Section: Generate Dialog Box
        #ToDo: Make into a Flask dialog box with Boolean answer options (currently goes to stdout)
        stdout_response = pyinputplus.inputBool(f"{dialog_box_text} Type \"True\" or \"False\" to answer. ")
        if stdout_response:
            return True
        else:
            if report_type == "status" or report_type == "reports":
                log.info(f"The user opted not to continue collecting data from {statistics_source}.")
            else:
                log.info(f"The user opted not to load the {report_type} data from {statistics_source}.")
            return False
    

    def _create_error_query_text(self, error_contents):
        """This method creates the text for the `handle_SUSHI_exceptions` dialog box.

        The `handle_SUSHI_exceptions` method can take a single exception or a list of exceptions, and in the case of the latter, the desired behavior is to have all the errors described in a single dialog box. To that end, the procedure for creating the error descriptions has been put in this separate method so it can be called for each error sent to `handle_SUSHI_exceptions` but have the method call itself only generate a single dialog box.

        Args:
            error_contents (dict): the contents of the error message
        
        Returns:
            str: a line of `handle_SUSHI_exceptions` dialog box text describing a single error
        """
        #Section: Confirm a Valid Error
        if isinstance(error_contents['Code'], int):
            str_code = str(error_contents['Code'])
        elif error_contents['Code'].isnumeric():
            str_code = error_contents['Code']
        else:
            str_code = None
        
        
        #Section: Separate Elements of Error into Variables
        message = error_contents['Message']
        
        try:
            severity = error_contents['Severity']
        except:
            severity = None
        
        try:
            code = error_contents['Code']
        except:
            code = None
        
        try:
            data = error_contents['Data']
        except:
            data = None
        

        #Section: Create Dialog Box Text
        dialog_box_text = f"The API call returned a {message} error"

        if code is not None:
            dialog_box_text = dialog_box_text + f" (code {str_code})"
        if severity is not None:
            dialog_box_text = dialog_box_text + f" with {severity} severity"
        if data is not None:
            dialog_box_text = dialog_box_text + f" for an error about {data}"
        
        return dialog_box_text + "."