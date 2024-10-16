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
from .models import *
from .statements import *

log = logging.getLogger(__name__)


class SUSHICallAndResponse:
    """A class that makes SUSHI API calls in the StatisticsSources._harvest_R5_SUSHI method.

    This class encapsulates the functionality for making SUSHI API calls. Based on the structure suggested at https://stackoverflow.com/a/48574985, the functionality for creating this SUSHI data dictionary object has been divided into the traditional __init__ method, which instantiates the class attributes, and the `make_SUSHI_call()` method, which actually performs the steps of the API call. This structure requires all instances of the class constructor to be prepended to a call to the `make_SUSHI_call()` method, which has two major results:
    * Objects of the `SUSHICallAndResponse` type are never instantiated; a tuple, the return value of `make_SUSHI_call()`, is returned instead.
    * With multiple return statements, a tuples where the first value is a string or Python error can be returned if there's a problem with the API call or the returned SUSHI value.

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
        _handle_SUSHI_exceptions: This method determines if SUSHI data with an error should be added to the database, and if so, how to update the `annualUsageCollectionTracking` relation.
        _evaluate_individual_SUSHI_exception: This method determines what to do upon the occurrence of an error depending on the type of error.
        _stdout_API_response_based_on_size: A method for limiting the amount of text written to stdout when viewing SUSHI harvest results.
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
        self.parameters = {key: (requests.utils.unquote(value) if isinstance(value, str) else value.strftime("%Y-%m-%d")) for key, value in parameters.items()}
    

    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        pass
    

    def make_SUSHI_call(self, bucket_path=PATH_WITHIN_BUCKET):
        """Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.

        This method calls two other methods in sequence: `_make_API_call()`, which makes the API call itself, and `_convert_Response_to_JSON()`, which changes the `Response.text` attribute of the value returned by `_make_API_call()` into native Python data types. This division is done so `Response.text` attributes that can't be changed into native Python data types can more easily be saved as text files in a S3 bucket for preservation and possible later review.

        Args:
            bucket_path (str, optional): the path within the bucket where the files will be saved; default is constant initialized at the beginning of this module

        Returns:
            tuple: the API call response (dict) or an error message (str); a list of the statements that should be flashed (list of str)
        """
        #Section: Make API Call
        log.info(f"Starting `make_SUSHI_call()` to {self.calling_to} for {self.call_path}.")  # `self.parameters` not included because 1) it shows encoded values (e.g. `%3D` is an equals sign) that are appropriately unencoded in the GET request and 2) repetitions of secret information in plain text isn't secure
        API_response = self._make_API_call()
        if isinstance(API_response, str):  # Meaning the SUSHI API call couldn't be made
            log.error(API_response)
            return (API_response, [API_response])

        #Section: Confirm Usage Data in Response
        if API_response.text == "":
            message = no_data_returned_by_SUSHI_statement(self.call_path, self.calling_to, is_empty_string=True)
            log.warning(message)
            return (message, [message])
        
        #Section: Convert Response to Python Data Types
        try:
            API_response, messages_to_flash = self._convert_Response_to_JSON(API_response)  # If there aren't any messages to flash, an empty list is initialized
        except Exception as error:
            message = f"Calling the `_convert_Response_to_JSON()` method raised the error {error}."
            log.error(f"{message} As a result, the `requests.Response.content` couldn't be converted to native Python data types; the `requests.Response.text` value is being saved to a file instead.")
            messages_to_flash = [message]
            flash_message = self._save_raw_Response_text(API_response.text, bucket_path)
            messages_to_flash.append(flash_message)
            if not upload_file_to_S3_bucket_success_regex().fullmatch(flash_message):
                message = f"{message[:-1]}, so the program attempted {flash_message[0].lower()}{flash_message[1:].replace(' failed', ', which failed')}"
                log.error(message)
                return (message, messages_to_flash)
            return (f"{message[:-1]}, so the program {flash_message[0].lower()}{flash_message[1:]}", messages_to_flash)
        
        if isinstance(API_response, Exception):
            message = f"A type conversion in the `_convert_Response_to_JSON()` method raised the error {str(API_response)}."
            log.error(f"{message} Since the conversion to native Python data types failed, the `requests.Response.text` value is being saved to a file instead.")
            flash_message = self._save_raw_Response_text(API_response.text, bucket_path)
            messages_to_flash.append(flash_message)
            if not upload_file_to_S3_bucket_success_regex().fullmatch(flash_message):
                message = f"{message[:-1]}, so the program attempted {flash_message[0].lower()}{flash_message[1:].replace(' failed', ', which failed')}"
                log.error(message)
                return (message, messages_to_flash)
            return (f"{message[:-1]}, so the program {flash_message[0].lower()}{flash_message[1:]}", messages_to_flash)
        log.debug(f"`_convert_Response_to_JSON()` returned an `API_response` of type {type(API_response)}.")

        #Section: Check for SUSHI Error Codes
        # JSONs for SUSHI data that's deemed problematic aren't saved as files because doing so would be keeping bad data
        #ToDo: For error 3060: InvalidReportFilter Value, redo the call without the invalid filters
        if API_response.get('Report_Header') and isinstance(API_response.get('Report_Header'), dict):  # Checks that the `Report_Header` key exists and that its value is a dict (any other data type would cause an error in the sequence of `get` methods below)
            if API_response.get('Report_Header').get('Exception') or API_response.get('Report_Header').get('Exceptions'):  #ALERT: Couldn't find a statistics source to use as a test case for the former
                if API_response.get('Report_Header').get('Exception'):
                    for_debug = "Exception"
                    SUSHI_exception_statement = API_response['Report_Header']['Exception']
                else:
                    for_debug = "Exceptions"
                    SUSHI_exception_statement = API_response['Report_Header']['Exceptions']
                log.debug(f"The report has a `Report_Header` with an `{for_debug}` key containing a single exception or a list of exceptions: {SUSHI_exception_statement}.")
                SUSHI_exceptions, flash_message_list = self._handle_SUSHI_exceptions(SUSHI_exception_statement, self.call_path)
                if flash_message_list:
                    for statement in flash_message_list:
                        messages_to_flash.append(statement)
                    log.debug(f"Added the following items to `messages_to_flash`:\n{format_list_for_stdout(flash_message_list)}")
                if flash_message_list and SUSHI_exceptions:
                    message = failed_SUSHI_call_statement(self.call_path, self.calling_to, SUSHI_exceptions, stop_API_calls=True)
                    log.warning(message)
                    return (message, messages_to_flash)

        if API_response.get('Exception') or API_response.get('Exceptions') or API_response.get('Alert') or API_response.get('Alerts'):  #ALERT: Couldn't find a statistics source to use as a test case for any (prior code indicates the first case appears in response to `status` calls)
            if API_response.get('Exception'):
                for_debug = "Exception"
                SUSHI_exception_statement = API_response['Exception']
            elif API_response.get('Exceptions'):
                for_debug = "Exceptions"
                SUSHI_exception_statement = API_response['Exceptions']
            elif API_response.get('Alert'):
                for_debug = "Alert"
                SUSHI_exception_statement = API_response['Alert']
            elif API_response.get('Alerts'):
                for_debug = "Alerts"
                SUSHI_exception_statement = API_response['Alerts']
            log.debug(f"The report has an `{for_debug}` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {SUSHI_exception_statement}.")
            SUSHI_exceptions, flash_message_list = self._handle_SUSHI_exceptions(SUSHI_exception_statement, self.call_path)
            if flash_message_list:
                for statement in flash_message_list:
                    messages_to_flash.append(statement)
                log.debug(f"Added the following items to `messages_to_flash`:\n{format_list_for_stdout(flash_message_list)}")
            if flash_message_list and SUSHI_exceptions:
                message = failed_SUSHI_call_statement(self.call_path, self.calling_to, SUSHI_exceptions, stop_API_calls=True)
                log.warning(message)
                return (message, messages_to_flash)

        if isinstance(API_response, list) or API_response.get('Message'):  # This structure is designed to enable reuse while not exposing any non-list values to the index operator
            if isinstance(API_response, list):
                if API_response[0].get('Message'):
                    for_debug = "list of dictionaries"
                else:
                    for_debug = False
            else:
                for_debug = "dictionary"
            if for_debug:
                log.debug(f"The report is nothing but a {for_debug} of the key-value pairs found in an `Exceptions` block: {API_response}.")
                SUSHI_exceptions, flash_message_list = self._handle_SUSHI_exceptions(API_response, self.call_path)
                if flash_message_list:
                    for statement in flash_message_list:
                        messages_to_flash.append(statement)
                    log.debug(f"Added the following items to `messages_to_flash`:\n{format_list_for_stdout(flash_message_list)}")
                if flash_message_list and SUSHI_exceptions:
                    message = failed_SUSHI_call_statement(self.call_path, self.calling_to, SUSHI_exceptions, stop_API_calls=True)
                    log.warning(message)
                    return (message, messages_to_flash)

        #Subsection: Check Customizable Reports for Data
        # Customizable reports can contain no data for various reasons; no actions that qualify as COUNTER metrics may occur, which may be because the action isn't possible on the platform (an empty DR from a statistics source without databases is a common example.) These are usually, but not always, marked with SUSHI error codes in the header, but in all cases, there should be a flashed message to let the user know about the empty report. This subsection ensures that the aforementioned flash message exists, then returns a tuple containing a message stopping the processing of the SUSHI data (which doesn't exist) and all flash messages.
        custom_report_regex = re.compile(r"reports/[PpDdTtIi][Rr]")
        Report_Items_status = len(API_response.get('Report_Items', 'No `Report_Items` key'))  # Combining the check for the existence of the key and the length of its value list allows for deduplication of log and return statements
        if Report_Items_status == 0 or Report_Items_status == 'No `Report_Items` key':
            if custom_report_regex.search(self.call_path):
                log.debug("Report has no data; checking to see why and if existing flash statements from SUSHI errors provide an explanation.")
                SUSHI_error_flash_messages = []
                for message in messages_to_flash:
                    if '3030' in message or '3031' in message or '3032' in message:
                        SUSHI_error_flash_messages.append(message)
                        
                if messages_to_flash and SUSHI_error_flash_messages:
                    for message in SUSHI_error_flash_messages:
                        messages_to_flash.append(message)
                    message = failed_SUSHI_call_statement(self.call_path, self.calling_to, message, no_usage_data=True)
                    log.warning(message)
                    return (message, messages_to_flash)
                elif messages_to_flash:
                    if Report_Items_status == 0:
                        message = no_data_returned_by_SUSHI_statement(self.call_path, self.calling_to)
                    elif Report_Items_status == 'No `Report_Items` key':
                        message = no_data_returned_by_SUSHI_statement(self.call_path, self.calling_to, has_Report_Items=False)
                    messages_to_flash.append(message)
                    log.warning(message)
                    return (message, messages_to_flash)
                else:
                    if Report_Items_status == 0:
                        message = no_data_returned_by_SUSHI_statement(self.call_path, self.calling_to)
                    elif Report_Items_status == 'No `Report_Items` key':
                        message = no_data_returned_by_SUSHI_statement(self.call_path, self.calling_to, has_Report_Items=False)
                    log.warning(message)
                    return (message, [message])
        
        #Section: Display to Stdout and Return `API_response`
        if custom_report_regex.search(self.call_path):
            number_of_report_items = len(API_response['Report_Items'])
            log.info(f"The SUSHI API response header: {API_response['Report_Header']}")
            log.info(f"A SUSHI API report item: {API_response['Report_Items'][random.choice(range(number_of_report_items))]}")
            log.debug(self._stdout_API_response_based_on_size(API_response))
        else:
            log.info(f"The SUSHI API response to a {self.call_path} call as a JSON:\n{API_response}")
        if messages_to_flash:
            log.info(f"The messages to flash:\n{messages_to_flash}")
            return (API_response, messages_to_flash)
        else:
            return (API_response, [])


    def _make_API_call(self):
        """Makes a call to the SUSHI API.

        This method uses the requests library to handle all the possible calls in the SUSHI standard.
        
        Returns:
            requests.Response: the complete Response object returned by the GET request to the API
            str: error message to indicate to `StatisticsSources._harvest_single_report()` that the API call failed
        """
        log.info(f"Starting `_make_API_call()` by calling {self.calling_to} for {self.call_path}.")  # `self.parameters` not included because 1) it shows encoded values (e.g. `%3D` is an equals sign) that are appropriately unencoded in the GET request and 2) repetitions of secret information in plain text isn't secure
        API_call_URL = self.call_URL + self.call_path

        try:  # `raise_for_status()` returns Exception objects if the HTTP status is 4XX or 5XX, so using it requires try/except logic (2XX codes return `None` and the redirects of 3XX are followed)
            time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this provides spacing
            API_response = requests.get(API_call_URL, params=self.parameters, timeout=90, headers=self.header_value)
            log.info(f"GET response code: {API_response}")  # In the past, GET requests that returned JSON downloads had HTTP status 403
            API_response.raise_for_status()

        except Timeout as error:
            try:  # Timeout errors seem to be random, so going to try get request again with more time
                log.info(f"Calling {self.calling_to} for {self.call_path} again.")
                time.sleep(1)
                API_response = requests.get(API_call_URL, params=self.parameters, timeout=299, headers=self.header_value)
                log.info(f"GET response code: {API_response}")
                API_response.raise_for_status()
            except Timeout as error_after_timeout:
                message = f"GET request to {self.calling_to} raised timeout errors {error} and {error_after_timeout}."
                log.error(message)
                return message
            except Exception as error_after_timeout:
                message = f"GET request to {self.calling_to} raised errors {error} and {error_after_timeout}."
                log.error(message)
                return message

        except Exception as error:
            #ToDo: View error information and, if data can be pulled with modification of API call, repeat call in way that works
            message = f"GET request to {self.calling_to} raised error {error}"
            log.error(message)
            return message

        log.info(f"GET request to {self.calling_to} at {self.call_path} successful.")
        return API_response


    def _convert_Response_to_JSON(self, API_response):
        """Converts the `text` attribute of a `requests.Response` object to native Python data types.

        Args:
            API_response (requests.Response): the response returned by the SUSHI API call
        
        Returns:
            tuple: the API call response as a dict using native Python data types or a Python Exception raised when attempting the conversion; any messages to be flashed (list of str)
        """
        log.info("Starting `_convert_Response_to_JSON()`.")
        #Section: Convert Text Attributes for Calls to `reports` Endpoint
        # `reports` endpoints should result in a list, not a dictionary, so they're being handled separately
        if self.call_path == "reports":
            #TEST: temp -- How does file of type dict in final else message compare to other responses? PNAS had `\t\n` in a string
            log.warning(f"API_response:\n{API_response}")
            log.warning(f"repr(type(API_response)):\n{repr(type(API_response))}")
            log.warning(f"API_response.text:\n{API_response.text}")
            #TEST: end temp
            if isinstance(API_response.text, str):
                try:
                    log.debug("The returned text was read from a downloaded JSON file but was the response to a `reports` call and should thus be a list.")
                    API_response = ast.literal_eval(API_response.content.decode('utf-8'))
                except Exception as error:
                    message = f"Converting a string with `ast.literal_eval(string.content.decode('utf-8'))` raised {error}."
                    log.error(message)
                    return (SyntaxError(error), [message])
            elif isinstance(API_response.text, list):
                try:
                    log.debug("The returned text is in list format and is the list of reports.")
                    API_response = json.loads(API_response.content.decode('utf-8'))
                except Exception as error:
                    message = f"Converting a list with `json.loads(list.content.decode('utf-8'))` raised {error}."
                    log.error(message)
                    return (json.JSONDecodeError(error), [message])
            else:
                message = f"Call to {self.calling_to} returned a downloaded JSON file with data of a {repr(type(API_response.text))} text type; it couldn't be converted to native Python data types."
                log.error(message)
                return (json.JSONDecodeError(message), [message])
                
            if isinstance(API_response, list):
                if API_response[0].get('Exception') or API_response[0].get('Exceptions') or API_response[0].get('Alert') or API_response[0].get('Alerts'):  # Because the usual reports response is in a list, the error checking in `make_SUSHI_call()` doesn't work
                    message = failed_SUSHI_call_statement("reports", self.calling_to, API_response)
                    log.error(message)
                    return (ValueError(message), [message])
                log.debug("The returned text was or was converted into a list of reports and, to match the other reports' data types, made the value of an one-item dictionary.")
                API_response = dict(reports = API_response)
            else:
                message = f"Call to {self.calling_to} returned a downloaded JSON file with data of a {repr(type(API_response))} text type that couldn't be converted into the value of a native Python dictionary."
                log.error(message)
                return (json.JSONDecodeError(message), [message])
        
        #Section: Convert Text Attributes for Calls to Other Endpoints
        else:
            if isinstance(API_response.text, str):
                log.debug("The returned text was read from a downloaded JSON file.")
                try:
                    API_response = json.loads(API_response.content.decode('utf-8'))
                except:  # This will transform values that don't decode as JSONs (generally lists)
                    try:
                        API_response = ast.literal_eval(API_response.content.decode('utf-8'))
                    except Exception as error:
                        message = f"Converting a string with `ast.literal_eval(string.content.decode('utf-8'))` raised {error}."
                        log.error(message)
                        return (SyntaxError(error), [message])
                
                if isinstance(API_response, dict):
                    log.debug("The returned text was converted to a dictionary.")
                
                elif isinstance(API_response, list) and len(API_response) == 1 and isinstance(API_response[0], dict):
                    log.debug("The returned text was converted to a a dictionary wrapped in a single-item list, so the item in the list will be converted to native Python data types.")
                    API_response = API_response[0]
                
                else:
                    message = f"Call to {self.calling_to} returned a downloaded JSON file with data of a {repr(type(API_response))} text type, which doesn't match SUSHI logic; it couldn't be converted to native Python data types."
                    log.error(message)
                    return (json.JSONDecodeError(message), [message])
            
            elif isinstance(API_response.text, dict):
                try:
                    log.debug("The returned text is in dictionary format, so it's ready to be converted to native Python data types.")
                    API_response = json.loads(API_response.content.decode('utf-8'))
                except Exception as error:
                    message = f"Converting a dict with `json.loads(dict.content.decode('utf-8'))` raised {error}."
                    log.error(message)
                    return (json.JSONDecodeError(error), [message])
            
            elif isinstance(API_response.text, list) and len(API_response.text) == 1 and isinstance(API_response[0].text, dict):
                try:
                    log.debug("The returned text is a dictionary wrapped in a single-item list, so the item in the list will be converted to native Python data types.")
                    API_response = json.loads(API_response[0].content.decode('utf-8'))
                except Exception as error:
                    message = f"Converting a list with `json.loads(list[0].content.decode('utf-8'))` raised {error}."
                    log.error(message)
                    return (json.JSONDecodeError(error), [message])
            
            else:
                message = f"Call to {self.calling_to} returned an object of the {repr(type(API_response))} type with a {repr(type(API_response.text))} text type; it couldn't be converted to native Python data types."
                log.error(message)
                return (json.JSONDecodeError(message), [message])
        
        log.info(f"SUSHI data converted to {repr(type(API_response))}.")
        log.debug(self._stdout_API_response_based_on_size(API_response))
        return (API_response, [])
    

    def _save_raw_Response_text(self, Response_text, bucket_path=PATH_WITHIN_BUCKET):
        """Saves the `text` attribute of a `requests.Response` object that couldn't be converted to native Python data types to a text file.

        Args:
            Response_text (str): the Unicode string that couldn't be converted to native Python data types
            bucket_path (str, optional): the path within the bucket where the files will be saved; default is constant initialized in `nolcat.app`
        
        Returns:
            str: an error message to flash indicating the creation of the bailout file
        """
        log.info("Starting `_save_raw_Response_text()`.")
        statistics_source_ID = query_database(
            query=f"SELECT statistics_source_ID FROM statisticsSources WHERE statistics_source_name='{self.calling_to}';",
            engine=db.engine,
        )
        if isinstance(statistics_source_ID, str):
            return database_query_fail_statement(statistics_source_ID, "return requested value")
        
        if self.parameters.get('begin_date') and self.parameters.get('end_date'):
            file_name_stem=f"{extract_value_from_single_value_df(statistics_source_ID)}_{self.call_path.replace('/', '-')}_{self.parameters['begin_date'][:-3]}_{self.parameters['end_date'][:-3]}_{datetime.now().isoformat()}"
        else:  # `status` and `report` requests don't include dates
            file_name_stem=f"{extract_value_from_single_value_df(statistics_source_ID)}_{self.call_path.replace('/', '-')}__{datetime.now().strftime(S3_file_name_timestamp())}"
        log.debug(file_IO_statement(file_name_stem + ".txt", f"temporary file location {file_name_stem}.txt", f"S3 location `{BUCKET_NAME}/{bucket_path}`"))
        logging_message = save_unconverted_data_via_upload(
            Response_text,
            file_name_stem,
            bucket_path,
        )
        if not upload_file_to_S3_bucket_success_regex().fullmatch(logging_message):
            message = f"NoLCAT HAS NOT SAVED THIS DATA IN ANY WAY: {logging_message[0].lower()}{logging_message[1:]}"
            log.critical(message)
        else:
            message = logging_message
            log.debug(message)
        return message


    def _handle_SUSHI_exceptions(self, error_contents, report_type):
        """This method handles all the SUSHI exceptions included in a SUSHI call, splitting apart multiple exceptions and determining what to do based on all of the exceptions combined.

        Args:
            error_contents (dict or list): the contents of the error message(s)
            report_type (str): the type of report being requested, determined by the value of `call_path`
        
        Returns:
            tuple: an error message (str) or `None` if the harvesting should continue (None); a list of the statements that should be flashed (list of str) or `None` if the program doesn't need to alert the user about the error (None)
        """
        log.info(f"Starting `_handle_SUSHI_exceptions()` for error(s) {error_contents}.")
        if error_contents is None:
            log.info("This statistics source had a key for a SUSHI error with null value, which occurs for some status reports. Since there is no actual SUSHI error, the API call will continue as normal.")
            return (None, None)
        elif isinstance(error_contents, dict):
            if len(error_contents['Message']) == 0:
                log.info("This statistics source had a key for a SUSHI error with an empty value, which occurs for some status reports. Since there is no actual SUSHI error, the API call will continue as normal.")
                return (None, None)
            log.debug(f"Handling a SUSHI error for a {report_type} in dictionary format.")
            SUSHI_exception, flash_message = self._evaluate_individual_SUSHI_exception(error_contents)
            flash_message = report_type + flash_message
            if isinstance(SUSHI_exception, str):
                SUSHI_exception = report_type + SUSHI_exception
            log.debug(f"`_evaluate_individual_SUSHI_exception()` raised the error {SUSHI_exception} and the flash message {flash_message}.")
            return (SUSHI_exception, [flash_message])
        elif isinstance(error_contents, list):
            if len(error_contents) == 0:
                log.info("This statistics source had a key for a SUSHI error with an empty value, which occurs for some status reports. Since there is no actual SUSHI error, the API call will continue as normal.")
                return (None, None)
            log.debug(f"Handling a SUSHI error for a {report_type} in list format.")
            if len(error_contents) == 1:
                SUSHI_exception, flash_message = self._evaluate_individual_SUSHI_exception(error_contents[0])
                flash_message = report_type + flash_message
                if isinstance(SUSHI_exception, str):
                    SUSHI_exception = report_type + SUSHI_exception
                log.debug(f"`_evaluate_individual_SUSHI_exception()` raised the error {SUSHI_exception} and the flash message {flash_message}.")
                return (SUSHI_exception, [flash_message])
            else:
                flash_messages_list = []
                errors_list = set()  # A set automatically dedupes as items are added
                for error in error_contents:
                    SUSHI_exception, flash_message = self._evaluate_individual_SUSHI_exception(error)
                    flash_message = report_type + flash_message
                    flash_messages_list.append(flash_message)
                    if SUSHI_exception:
                        if isinstance(SUSHI_exception, str):
                            errors_list.add(report_type + SUSHI_exception)
                if len(errors_list) == 1:  # One error indicating API calls should stop
                    return_value = (errors_list.pop(), flash_messages_list)
                    log.debug(f"`_evaluate_individual_SUSHI_exception()` raised the error {return_value[0]} and the flash messages\n{format_list_for_stdout(flash_messages_list)}")
                    return return_value
                elif len(errors_list) > 1:  # Multiple errors indicating API calls should stop
                    log.debug(f"`_evaluate_individual_SUSHI_exception()` raised the errors\n{format_list_for_stdout(errors_list)}\nand the flash messages\n{format_list_for_stdout(flash_messages_list)}")
                    return (f"All of the following errors were raised:\n{format_list_for_stdout(errors_list)}", flash_messages_list)
                else:  # API calls should continue
                    log.debug(f"`_evaluate_individual_SUSHI_exception()` raised no errors and the flash messages\n{format_list_for_stdout(flash_messages_list)}")
                    return (None, flash_messages_list)
        else:
            message = f"SUSHI error handling method for a {report_type} accepted {repr(type(error_contents))} data, which is an invalid type."
            log.info(message)
            return (message, [message])
    

    def _evaluate_individual_SUSHI_exception(self, error_contents):
        """This method determines what to do upon the occurrence of an error depending on the type of error.

        For the messages, the report type is added to the start of the sentence in `_handle_SUSHI_exceptions()`.

        Args:
            error_contents (dict): the contents of the error message
        
        Returns:
            tuple: an error message if the error indicates harvesting should stop (None or str); the message to flash (str)
        """
        log.info(f"Starting `_evaluate_individual_SUSHI_exception()` for error {error_contents}.")

        #Section: Identify Error Code
        errors_and_codes = {
            'Service Not Available': '1000',
            'Service Busy': '1010',
            'Report Queued for Processing': '1011',
            'Client has made too many requests': '1020',
            'Insufficient Information to Process Request': '1030',
            'Requestor Not Authorized to Access Service': '2000',
            'Requestor is Not Authorized to Access Usage for Institution': '2010',
            'APIKey Invalid': '2020',
            'IP Address Not Authorized to Access Service': '2030',  #R5.0 only
            'Report Not Supported': '3000',  # Would only come up with an individual report request, R5.0 only
            'Report Version Not Supported': '3010',  #R5.0 only
            'Invalid Date Arguments': '3020',
            'No Usage Available for Requested Dates': '3030',
            'Usage Not Ready for Requested Dates': '3031',
            'Usage No Longer Available for Requested Dates': '3032',
            'Partial Data Returned': '3040',
            'Parameter Not Recognized in this Context': '3050',
            'Invalid ReportFilter Value': '3060',
            'Incongruous ReportFilter Value': '3061',
            'Invalid ReportAttribute Value': '3062',
            'Components Not Supported': '3063',
            'Required ReportFilter Missing': '3070'
        }
        if error_contents.get('Message') is None:
            message = f" had no key `Message`; this is not a standard error message and thus isn't being managed as such."
            log.debug(message)
            return (None, message)
        error_code = errors_and_codes.get(error_contents['Message'])
        if error_code is None:
            if error_contents.get('Code') in [v for v in errors_and_codes.values()] or error_contents.get('Code') in [int(v) for v in errors_and_codes.values()]:
                error_code = str(error_contents['Code'])
                error_contents['Message'] = [k for (k, v) in errors_and_codes.items() if v==error_code][0]
            else:
                try:
                    message = f" had `error_contents['Message']` {error_contents.get('Message')} and `error_contents['Code']` {error_contents.get('Code')}, neither of which matched a known error."
                    log.error(message)
                    return (message, message)
                except Exception as error:
                    message = f" had the error message {error_contents}, but trying to match it to a known COUNTER error raised the error {error}."
                    log.error(message)
                    return (message, message)
        log.info(f"The error code is {error_code} and the message is {error_contents['Message']}.")
        
        #Section: Handle Error
        message = f" request raised error {error_code}: {error_contents['Message']}."
        if error_contents.get('Data'):
            message = message[:-1] + f" due to {error_contents['Data'][0].lower()}{error_contents['Data'][1:]}."
        
        #Subsection: Handle Errors Only Needing Flash Message
        if error_code == '3030' or error_code == '3032' or error_code == '3040':
            if error_code == '3032' or error_code == '3040':
                #ToDo: Should there be an attempt to get the dates for the request if they aren't already in the message?
                df = query_database(
                    query=f"SELECT * FROM statisticsSources WHERE statistics_source_name='{self.calling_to}';",
                    engine=db.engine,
                )
                if isinstance(df, str):
                    error_message = database_query_fail_statement(df, "create StatisticsSources object to use `add_note()` method")
                    return (error_message, [message, error_message])
                try:
                    statistics_source_object = StatisticsSources(  # Even with one value, the field of a single-record dataframe is still considered a series, making type juggling necessary
                        statistics_source_ID = int(df.at[0,'statistics_source_ID']),
                        statistics_source_name = str(df.at[0,'statistics_source_name']),
                        statistics_source_retrieval_code = str(df.at[0,'statistics_source_retrieval_code']).split(".")[0],  #String created is of a float (aka `n.0`), so the decimal and everything after it need to be removed
                        vendor_ID = int(df.at[0,'vendor_ID']),
                    )  # Without the `int` constructors, a numpy int type is used
                    log.debug(f"The following `StatisticsSources` object was initialized based on the query results:\n{statistics_source_object}.")
                    statistics_source_object.add_note(message)
                except NameError as error:  # This handles the intermittent raising of `NameError: name 'StatisticsSources' is not defined`. Between its infrequent, unpredictable appearance and the importing of the module in which it's defined, the cause of the error is unclear.
                    log.critical(f"Due to the error {error}, the error message {message} is not being saved to the database.")
            elif error_code == '1030' or error_code == '3050' or error_code == '3060' or error_code == '3061' or error_code == '3062':
                message = message + " If the error can be solved by changing the nature of the call, then do so, otherwise, request this report in tabular form from the admin platform and upload that file instead."
            log.error(message)
            return (None, message)

        #Subsection: Handle Errors Stopping API Calls
        elif error_code == '1000' or error_code == '1010' or error_code == '1011' or error_code == '1020' or error_code == '3031':
            message = message + " Try the call again later."
        elif error_code == '2000' or error_code == '2010' or error_code == '2020':
            message = message + " Check and Update the credentials in the R5 SUSHI credentials JSON, then try the call again."
        elif error_code == '3020' :
            message = message + " Adjust the date range, splitting it up into two calls with date ranges contained within a calendar year if necessary, then try the call again."
        log.error(message)
        return (message, message)
    

    def _stdout_API_response_based_on_size(self, API_response):
        """A method for limiting the amount of text written to stdout when viewing SUSHI harvest results.

        For some custom reports, the complete `API_response` value can be so long that it keeps most of the pytest log from appearing in stdout; this limits the amount of data shown in stdout.

        Args:
            API_response (dict): the SUSHI harvest response in Python data types
        
        Returns:
            str: the content for stdout, including whatever amount of `API_response` is necessary
        """
        log.info("Starting `_stdout_API_response_based_on_size()`.")
        if API_response.get('Report_Items'):
            number_of_report_items = len(API_response['Report_Items'])
            if number_of_report_items < 30:
                return f"The SUSHI API response as a JSON:\n{API_response}"
            else:
                if number_of_report_items > 300:
                    for n in random.sample(range(number_of_report_items), k=30):
                        return f"A sample of the SUSHI API response:\n{API_response['Report_Items'][n]}"
                else:
                    for n in random.sample(range(number_of_report_items), k=int(number_of_report_items/10)):
                        return f"A sample of the SUSHI API response:\n{API_response['Report_Items'][n]}"
        else:  # For `status` and `reports` calls
            return f"The SUSHI API response as a JSON:\n{API_response}"