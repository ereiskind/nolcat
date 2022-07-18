import logging
import shutil
import time
import re
import os
from pathlib import Path
import json
import ast
import requests
from requests import HTTPError
from requests import Timeout
import pyinputplus
from .app import Chrome_browser_driver

logging.basicConfig(level=logging.INFO, format="SUSHICallAndResponse - - [%(asctime)s] %(message)s")


class SUSHICallAndResponse:
    """A class that makes SUSHI API calls in the StatisticsSources._harvest_R5_SUSHI method.

    This class encapsulates the functionality for making SUSHI API calls. Based on the structure suggested at https://stackoverflow.com/a/48574985, the functionality for creating this SUSHI data dictionary object has been divided into the traditional __init__ method, which instantiates the class attributes, and the `make_SUSHI_call` method, which actually performs the steps of the API call. This structure requires all instances of the class constructor to be prepended to a call to the `make_SUSHI_call` method, which has two major results:
    * Objects of the SUSHICallAndResponse type are never instantiated; a dictionary, the return value of `make_SUSHI_call`, is returned instead.
    * With multiple return statements, a single item dictionary with the key `ERROR` and a value with a message about the problem can be returned if there's a problem with the API call or the returned SUSHI value.

    Attributes:
        self.Chrome_user_agent (dict): a class attribute containing a value for the requests header that makes the URL request appear to come from a Chrome browser and not the requests module; some platforms return 403 errors with the standard requests header
        self.calling_to (str): the name of statistics source the SUSHI API call is going to (the StatisticsSources.statistics_source_name attribute)
        self.call_URL (str): the root URL for the SUSHI API call
        self.call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        parameters (dict): the parameter values for the API call
        #ToDo: DELETE IF UNNEEDED: self.parameter_string (str): the parameter values of the API call as a string, converted from a dictionary to prevent encoding problems
    
    Methods:
        make_SUSHI_call: Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.
        _retrieve_downloaded_JSON: Retrieves a downloaded response to a SUSHI API call.
        _handle_SUSHI_exceptions: The method presents the user with the error in the SUSHI response(s) and asks if the StatisticsSources._harvest_R5_SUSHI method should continue.
        _create_error_query_text: This method creates the text for the `handle_SUSHI_exceptions` dialog box.
    """
    Chrome_user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


    def __init__(self, calling_to, call_URL, call_path, parameters):
        """The constructor method for SUSHICallAndResponse, which sets the attribute values for each instance.

        This constructor is not meant to be used alone; all class instantiations should feature a `make_SUSHI_call` method call.

        Args:
            calling_to (str): the name of statistics source the SUSHI API call is going to (the StatisticsSources.statistics_source_name attribute)
            call_URL (str): the root URL for the SUSHI API call
            call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
            parameters (dict): the parameter values for the API call  #ToDo: Change to string if needed
        """
        self.calling_to = calling_to
        self.call_URL = call_URL
        self.call_path = call_path
        #ToDo: DELETE IF UNNEEDED: self.parameter_string = "&".join(f"{key}={value}" for key, value in parameters.items())
        self.parameters = {key: (requests.utils.unquote(value) if str(type(value)) == "<class 'str'>" else value.strftime("%Y-%m")) for key, value in parameters.items()}
    

    def make_SUSHI_call(self):
        """Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.

        This API call method handles all the possible calls in the SUSHI standard, converting their JSON responses into native Python data types. Errors in both the API call process and the SUSHI response are handled here, and in those instances where there is an error, a single-item dictionary with the key `ERROR` and a value describing the error is returned instead of SUSHI data.

        To handle statistics sources that respond to SUSHI API calls by downloading a JSON file with the requested data without using Selenium, the API call is in a block for writing binary data to a file, so when the response object contains binary data, it's written to a file. Another block for reading a text file copies the data if a JSON file in the response object into a new file. At this point, the response data is written to a file regardless of how it was initially delivered, so the method can read the data from the file and move on to processing it.

        Returns:
            dict: the API call response or an error message
        """
        #Section: Make API Call
        logging.info(f"Calling {self.calling_to} for {self.call_path}.")  # `self.parameters` not included because 1) it shows encoded values (e.g. `%3D` is an equals sign)that are appropriately unencoded in the GET request and 2) repetitions of secret information in plain text isn't secure
        API_call_URL = self.call_URL + self.call_path

        #Subsection: Make GET Request
        time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this provides spacing
        try:  # `raise_for_status()` returns Exception objects if the HTTP status is 4XX or 5XX, so using it requires try/except logic (2XX codes return `None` and the redirects of 3XX are followed)
            API_response = requests.get(API_call_URL, params=self.parameters, timeout=90, headers=self.Chrome_user_agent)
            logging.debug(f"`API_response` HTTP code: {API_response}")  # In the past, GET requests that returned JSON downloads had HTTP status 403
            API_response.raise_for_status()
        except Timeout as error:
            try:  # Timeout errors seem to be random, so going to try get request again with more time
                logging.debug(f"Calling {self.calling_to} for {self.call_path} again.")
                time.sleep(1)
                API_response = requests.get(API_call_URL, params=self.parameter_string, timeout=299, headers=self.Chrome_user_agent)
                API_response.raise_for_status()
            except Timeout as error_after_timeout:
                logging.warning(f"Call to {self.calling_to} raised timeout errors {format(error)} and {format(error_after_timeout)}")
                return {"ERROR": f"Call to {self.calling_to} raised timeout errors {format(error)} and {format(error_after_timeout)}"}
            except Exception as error_after_timeout:
                logging.warning(f"Call to {self.calling_to} raised errors {format(error)} and {format(error_after_timeout)}")
                return {"ERROR": f"Call to {self.calling_to} raised errors {format(error)} and {format(error_after_timeout)}"}
        except Exception as error:
            #Alert: MathSciNet doesn't have a status report, but does have the other reports with the needed data--how should this be handled so that it can pass through?
            logging.warning(f"Call to {self.calling_to} raised error {format(error)}")
            return {"ERROR": f"Call to {self.calling_to} raised error {format(error)}"}

        logging.info(f"GET request for {self.calling_to} at {self.call_path} successful.")
        logging.debug(f"GET request returned text {API_response.text}")

        #Subsection: Convert Response to Python Data Types
        if API_response.text == "":
            logging.warning(f"Call to {self.calling_to} returned an empty string")
            return {"ERROR": f"Call to {self.calling_to} returned an empty string"}

        elif str(type(API_response.text)) == "<class 'dict'>":
            logging.debug("The returned text is in dict format, so it's ready for JSON conversion.")
            API_response = json.loads(API_response.content.decode('utf-8'))
            # Old note says above creates a JSON from the first item in Report_Items rather than the complete content
        
        elif str(type(API_response.text)) == "<class 'list'>" and self.call_path == "reports":
            logging.debug(f"The returned text is in list format and is the list of reports, so it will be converted into a {str(type(json.loads(API_response.content.decode('utf-8'))))} and, to match the other reports' data types, made the value of an one-item dict.")
            API_response = json.loads(API_response.content.decode('utf-8'))
            API_response = dict(reports = API_response)
        
        elif str(type(API_response.text)) == "<class 'list'>" and len(API_response) == 1 and str(type(API_response[0].text)) == "<class 'dict'>":
            logging.debug("The returned text is a dict wrapped in a single-item list, so the item in the list will be converted to JSON.")
            API_response = json.loads(API_response[0].content.decode('utf-8'))
        
        elif str(type(API_response.text)) == "<class 'str'>":
            logging.debug("The returned text was read from a downloaded JSON file.")
            API_response = ast.literal_eval(API_response.content.decode('utf-8'))
        
        else:
            logging.warning(f"Call to {self.calling_to} returned an object of the {str(type(API_response))} type with a {str(type(API_response.text))} text type; it couldn't be converted to native Python data types.")
            return {"ERROR": f"Call to {self.calling_to} returned an object of the {str(type(API_response))} type with a {str(type(API_response.text))} text type; it couldn't be converted to native Python data types."}
      
        logging.debug(f"SUSHI data converted to {str(type(API_response))}:\n{API_response}")

        return API_response
        '''
        #Section: Check for SUSHI Error Codes
        # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
        try:
            logging.debug(f"The report has a `Report_Header` with an `Exception` key containing a single exception or a list of exceptions: {API_response['Report_Header']['Exception']}.")
            if not self.handle_SUSHI_exceptions(API_response['Report_Header']['Exception'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Report_Header']['Exception']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Report_Header']['Exception']}"}
        except:
            pass

        try:
            logging.debug(f"The report has a `Report_Header` with an `Exceptions` key containing a single exception or a list of exceptions: {API_response['Report_Header']['Exceptions']}.")
            if not self.handle_SUSHI_exceptions(API_response['Report_Header']['Exceptions'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Report_Header']['Exceptions']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Report_Header']['Exceptions']}"}
        except:
            pass

        #ToDo: Before reformatting, a `status` response with the key-value pair `'Alerts': []` didn't trigger any of the method calls below, but the exact same status call with the exact same response 11 minutes later did--investigate the issue
        try:
            logging.debug(f"The report has an `Exception` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Exception']}.")
            if not self.handle_SUSHI_exceptions(API_response['Exception'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Exception']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Exception']}"}
        except:
            pass

        try:
            logging.debug(f"The report has an `Exceptions` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Exceptions']}.")
            if not self.handle_SUSHI_exceptions(API_response['Exceptions'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Exceptions']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Exceptions']}"}
        except:
            pass

        try:
            logging.debug(f"The report has an `Alert` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Alert']}.")
            if not self.handle_SUSHI_exceptions(API_response['Alert'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Alert']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Alert']}"}
        except:
            pass

        try:
            logging.debug(f"The report has an `Alerts` key on the same level as `Report_Header` containing a single exception or a list of exceptions: {API_response['Alerts']}.")
            if not self.handle_SUSHI_exceptions(API_response['Alerts'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Alerts']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Alerts']}"}
        except:
            pass
        
        try:
            if "Message" in API_response.keys():
                logging.debug("The report is nothing but a dictionary of the key-value pairs found in an `Exceptions` block.")
                if not self.handle_SUSHI_exceptions(API_response, self.call_path, self.calling_to):
                    logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}")
                    return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}"}
        except:
            pass

        try:
            if "Message" in API_response[0].keys():
                logging.debug("The report is nothing but a list of dictionaries of the key-value pairs found in an `Exceptions` block.")
                if not self.handle_SUSHI_exceptions(API_response, self.call_path, self.calling_to):
                    logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}")
                    return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}"}
        except:
            pass

        #Subsection: Check Master Reports for Data
        # Some master reports errors weren't being caught by the error handlers above despite matching the criteria; some vendors offer reports for content they don't have (statistics sources without databases providing database reports is the most common example). In both cases, master reports containing no data should be caught as potential errors.
        master_report_regex = re.compile(r'reports/..')
        if master_report_regex.search(self.call_path):
            try:
                lines_of_data = len(API_response['Report_Items'])
                if lines_of_data == 0:
                    logging.warning(f"Call to {self.calling_to} for {self.call_path} returned no data.")
                    return {"ERROR": f"Call to {self.calling_to} for {self.call_path} returned no data."}
            except TypeError:
                logging.warning(f"Call to {self.calling_to} for {self.call_path} returned no data.")
                return {"ERROR": f"Call to {self.calling_to} for {self.call_path} returned no data."}
        
        logging.info(f"The SUSHI API response:\n{API_response}")
        return API_response
        '''


    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        return


    def _retrieve_downloaded_JSON(self):
        """Retrieves a downloaded response to a SUSHI API call. 

        Some vendors, most notably Silverchair, respond to SUSHI API call responses by downloading a JSON file with the requested data. This method captures and reads the contents of the downloaded file, then removes the file. Functionality related to downloading the file taken from https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196.

        Returns:
            dict: the SUSHI data in the downloaded JSON file
        """
        webdriver = Chrome_browser_driver()
        URL = self.call_URL + self.call_path + "?" + self.parameter_string
        temp_folder = str(Path.cwd()) + r"/temp"
        Path(temp_folder).mkdir()
        logging.info(f"Folder at {temp_folder} created.")
        
        # From source: "function to handle setting up headless download"
        webdriver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': temp_folder}}
        webdriver.execute("send_command", params)
        logging.debug(f"Calling {self.calling_to} for {self.call_path} as JSON download.")
        webdriver.get(URL) # From source: "get request to target the site selenium is active on"

        time.sleep(0.1) # This delay allows the downloaded JSON to be in the folder for long enough that the walk method can detect it
        for folder, subfolder, files in os.walk(temp_folder):
            if files == []: # This means the 403 error was the result of something other than the data being downloaded as a JSON file
                os.rmdir(temp_folder)
                logging.info("No JSON found, temp folder deleted.")
                return files
            for file in files: # There is actually only one file, but the iterator is needed to extract it from the list data structure
                download_file_path = Path(temp_folder, file)
                with open(download_file_path, 'rb') as JSONfile: #Alert: Not yet tested with bytes
                    file_data = json.load(JSONfile)
                    logging.info(f"Data from JSON {file} saved to memory.")
        
        shutil.rmtree(temp_folder)
        logging.info(f"Folder at {temp_folder} deleted.")
        return file_data


    def _handle_SUSHI_exceptions(self, error_contents, report_type, statistics_source):
        """The method presents the user with the error in the SUSHI response(s) and asks if the StatisticsSources._harvest_R5_SUSHI method should continue.

        This method presents the user with the error(s) returned in a SUSHI call and asks if the error should be validated. For status calls, this means not making any further SUSHI calls to the resource at the time; for master report calls, it means not loading the master report data into the database.
        
        Args:
            error_contents (dict or list): the contents of the error message(s)
            report_type (str): the type of report being requested, determined by the value of `call_path`
            statistics_source (str): the name of the statistics source that returned the SUSHI call in question
        
        Returns:
            bool: if the StatisticsSources._harvest_R5_SUSHI method should continue
        """
        #Section: Create Error Message(s)
        #Subsection: Detail Each SUSHI Error
        if str(type(error_contents)) == "<class 'dict'>":
            if len(error_contents['Message']) == 0:
                logging.debug(f"This statistics source had a key for a SUSHI error with an empty value, which occurs for some status reports. Since there is no actual SUSHI error, the user is not being asked how to handle the error.")
                return True
            logging.info(f"Handling a SUSHI error for a {report_type} in dictionary format.")
            dialog_box_text = self.create_error_query_text(error_contents)
        elif str(type(error_contents)) == "<class 'list'>":
            if len(error_contents) == 0:
                logging.debug(f"This statistics source had a key for a SUSHI error with an empty value, which occurs for some status reports. Since there is no actual SUSHI error, the user is not being asked how to handle the error.")
                return True
            dialog_box_text = []
            logging.info(f"Handling a SUSHI error for a {report_type} in list format.")
            for error in error_contents:
                dialog_box_text.append(self.create_error_query_text(error))
            dialog_box_text = "\n".join(dialog_box_text)
        else:
            logging.info(f"SUSHI error handling method for a {report_type} accepted data of an invalid type.")
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
                logging.info(f"The user opted not to continue collecting data from {statistics_source}.")
            else:
                logging.info(f"The user opted not to load the {report_type} data from {statistics_source}.")
            return False
    

    def _create_error_query_text(self, error_contents):
        """This method creates the text for the `handle_SUSHI_exceptions` dialog box.

        The `handle_SUSHI_exceptions` method can take a single exception or a list of exceptions, and in the case of the latter, the desired behavior is to have all the errors described in a single dialog box. To that end, the procedure for creating the error descriptions has been put in this separate method so it can be called for each error sent to `handle_SUSHI_exceptions` but have the method call itself only generate a single doalog box.

        Args:
            error_contents (dict): the contents of the error message
        
        Returns:
            str: a line of `handle_SUSHI_exceptions` dialog box text describing a single error
        """
        #Section: Confirm a Valid Error
        if str(type(error_contents['Code'])) == "<class 'int'>":
            str_code = str(error_contents['Code'])
        elif error_contents['Code'].isnumeric():
            str_code = error_contents['Code']
        #ToDo: What if anything should be done if the error code isn't valid?
        
        
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