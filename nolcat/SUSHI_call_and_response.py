import logging
import shutil
import time
import re
import os
from pathlib import Path
import json
import requests
from requests import HTTPError
from requests import Timeout
import pyinputplus
from .app import Chrome_browser_driver

logging.basicConfig(level=logging.INFO, format="SUSHICallAndResponse - - [%(asctime)s] %(message)s")


class SUSHICallAndResponse:
    """A class that makes SUSHI API calls in the StatisticsSources._harvest_R5_SUSHI method.

    Object of this class are designed to function as Python dictionaries distinguised by the data they contain--the results of a SUSHI API call. Based on the structure suggested at https://stackoverflow.com/a/48574985, the functionality for creating this SUSHI data dictionary object has been divided into the traditional __init__ method, which instantiates the class attributes, and the `make_SUSHI_call` method, which actually performs the steps of the API call. This structure, which requires all instance creations to be immediately followed by a call to the `make_SUSHI_call` method, allows a different value--a single item dictionary with the key `ERROR` and a value with a message about the problem--to be returned to the the StatisticsSources._harvest_R5_SUSHI method in the event of a problem with the API call or the returned SUSHI value, something __init__ doesn't allow.

    Attributes:
        self.Chrome_user_agent (dict): a class attribute containing a value for the requests header that makes the URL request appear to come from a Chrome browser and not the requests module; some platforms return 403 errors with the standard requests header
        self.calling_to (str): the name of statistics source the SUSHI API call is going to (the StatisticsSources.statistics_source_name attribute)
        self.call_URL (str): the root URL for the SUSHI API call
        self.call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
        self.parameter_string (str): the parameter values of the API call as a string, converted from a dictionary to prevent encoding problems
    
    Methods:
        make_SUSHI_call: Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.
        retrieve_downloaded_JSON: Retrieves a downloaded response to a SUSHI API call.
        handle_SUSHI_exceptions: The method presents the user with the error in the SUSHI response(s) and asks if the StatisticsSources._harvest_R5_SUSHI method should continue.
        create_error_query_text: This method creates the text for the `handle_SUSHI_exceptions` dialog box.
    """
    Chrome_user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


    def __init__(self, calling_to, call_URL, call_path, parameters):
        """The constructor method for SUSHICallAndResponse, which sets the attribute values for each instance.

        This constructor is not meant to be used alone; all class instantiations should feature a `make_SUSHI_call` method call.

        Args:
            calling_to (str): the name of statistics source the SUSHI API call is going to (the StatisticsSources.statistics_source_name attribute)
            call_URL (str): the root URL for the SUSHI API call
            call_path (str): the last element(s) of the API URL path before the parameters, which represent what is being requested by the API call
            parameters (dict): the parameter values as key-value pairs
        """
        self.calling_to = calling_to
        self.call_URL = call_URL
        self.call_path = call_path
        self.parameter_string = "&".join(f"{key}={value}" for key, value in parameters.items())
    

    def make_SUSHI_call(self):
        """Makes a SUSHI API call and packages the response in a JSON-like Python dictionary.

        This API call method handles all the possible calls in the SUSHI standard, converting their JSON responses into native Python data types. Errors in both the API call process and the SUSHI response are handled here, and in those instances where there is an error, a single-item dictionary with the key `ERROR` and a value describing the error is returned instead of SUSHI data.

        Returns:
            dict: the API call response or an error message
        """
        #Section: Make API Call
        API_call_URL = self.call_URL + self.call_path
        time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this provides spacing
        try:
            API_response = requests.get(API_call_URL, params=self.parameter_string, timeout=90, headers=self.Chrome_user_agent)
            API_response.raise_for_status()
            #Alert: MathSciNet doesn't have a status report, but does have the other reports with the needed data--how should this be handled so that it can pass through?
        
        except Timeout as error:
            try:  # Timeout errors seem to be random, so going to try get request again with more time
                time.sleep(1)
                API_response = requests.get(API_call_URL, params=self.parameter_string, timeout=299, headers=self.Chrome_user_agent)
                API_response.raise_for_status()
            
            except Timeout as error_plus_timeout:
                logging.warning(f"Call to {self.calling_to} raised timeout errors {format(error)} and {format(error_plus_timeout)}")
                return {"ERROR": f"Call to {self.calling_to} raised timeout errors {format(error)} and {format(error_plus_timeout)}"}
            
            except HTTPError as error_plus_timeout:
                if format(error_plus_timeout.response) == "<Response [403]>":
                    API_response = self.retrieve_downloaded_JSON()
                    if API_response == []:
                        logging.warning(f"Call to {self.calling_to} raised errors {format(error)} and {format(error_plus_timeout)}")
                        return {"ERROR": f"Call to {self.calling_to} raised errors {format(error)} and {format(error_plus_timeout)}"}
                else:
                    logging.warning(f"Call to {self.calling_to} raised errors {format(error)} and {format(error_plus_timeout)}")
                    return {"ERROR": f"Call to {self.calling_to} raised errors {format(error)} and {format(error_plus_timeout)}"}
            
            except Exception as error_plus_timeout:
                logging.warning(f"Call to {self.calling_to} raised errors {format(error)} and {format(error_plus_timeout)}")
                return {"ERROR": f"Call to {self.calling_to} raised errors {format(error)} and {format(error_plus_timeout)}"}
        
        except HTTPError as error:
            if format(error.response) == "<Response [403]>":
                API_response = self.retrieve_downloaded_JSON()
                if API_response == []:
                    logging.warning(f"Call to {self.calling_to} raised error {format(error)}")
                    return {"ERROR": f"Call to {self.calling_to} raised error {format(error)}"}
            else:
                logging.warning(f"Call to {self.calling_to} raised error {format(error)}")
                return {"ERROR": f"Call to {self.calling_to} raised error {format(error)}"}
        
        except Exception as error:
            # Old note: ToDo: Be able to view error information and confirm or deny if site is safe
            # Old note: Attempt to isolate Allen Press by SSLError message and redo request without checking certificate led to ConnectionError
            logging.warning(f"Call to {self.calling_to} raised error {format(error)}")
            return {"ERROR": f"Call to {self.calling_to} raised error {format(error)}"}


        #Section: Convert Response to Python Data Types
        try:
            if API_response.text == "":
                logging.warning(f"Call to {self.calling_to} returned an empty string")
                return {"ERROR": f"Call to {self.calling_to} returned an empty string"}
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
                logging.warning(f"Call to {self.calling_to} returned a JSON that couldn't be converted into a dictionary")
                return {"ERROR": f"Call to {self.calling_to} returned a JSON that couldn't be converted into a dictionary"}
        
        if str(type(API_response)) == "<class 'list'>" and len(API_response) == 1 and str(type(API_response[0])) == "<class 'dict'>":
            API_response = API_response[0]
        
        if str(type(API_response)) == "<class 'dict'>":
            pass
        else:
            logging.warning(f"Call to {self.calling_to} returned an object of the {str(type(API_response))} type and thus wasn't converted into a dict for further processing.")
            return {"ERROR": f"Call to {self.calling_to} returned an object of the {str(type(API_response))} type and thus wasn't converted into a dict for further processing."}


        #Section: Check for SUSHI Error Codes
        # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
        try:  # The report has a `Report_Header` with an `Exceptions` key containing a single exception or a list of exceptions
            if not self.handle_SUSHI_exceptions(API_response['Report_Header']['Exceptions'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Report_Header']['Exceptions']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Report_Header']['Exceptions']}"}
        except:
            pass
        
        try:  # The report is nothing but a dictionary of the key-value pairs found in an `Exceptions` block
            if "Message" in API_response.keys():
                if not self.handle_SUSHI_exceptions(API_response, self.call_path, self.calling_to):
                    logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}")
                    return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}"}
        except:
            pass

        try:  # The report is nothing but a list of dictionaries of the key-value pairs found in an `Exceptions` block
           if "Message" in API_response[0].keys():
               if not self.handle_SUSHI_exceptions(API_response, self.call_path, self.calling_to):
                    logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}")
                    return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response}"}
        except:
            pass

        try:  # The report has an `Exceptions` or `Alerts` key containing a single exception or a list of exceptions (the key is on the same level as `Report_Header`)
            if not self.handle_SUSHI_exceptions(API_response['Exceptions'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Exceptions']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Exceptions']}"}
            elif not self.handle_SUSHI_exceptions(API_response['Alerts'], self.call_path, self.calling_to):
                logging.warning(f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Alerts']}")
                return {"ERROR": f"Call to {self.calling_to} returned the SUSHI error(s) {API_response['Alerts']}"}
        except:
            pass

        #Subsection: Check Master Reports for Data
        # Some master reports errors weren't being caught by the error handlers above despite matching the criteria; some vendors offer reports for content they don't have (statistics sources without databases providing database reports is the most common example). In both cases, master reports containing no data should be caught as potential errors.
        master_report_regex = re.compile(r'reports/..')
        if master_report_regex.search(self.call_path):
            try:
                logging.debug(f"Returning {len(API_response['Report_Items'])} lines of data.")  # This `try` block needed to include `API_response['Report_Items']` in some way, and since this is the end of the constructor, a logging statement was appropriate
            except TypeError:
                logging.warning(f"Call to {self.calling_to} for {self.call_path} returned no data.")
                return {"ERROR": f"Call to {self.calling_to} for {self.call_path} returned no data."}
        
        return API_response


    def __repr__(self):
        """The printable representation of the class, determining what appears when `{self}` is used in an f-string."""
        return


    def retrieve_downloaded_JSON(self):
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


    def handle_SUSHI_exceptions(self, error_contents, report_type, statistics_source):
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
            if len(error_contents['Message']) == 0:  # Some interfaces always include the "Exceptions" key in the status check return value; this keeps the popups about continuing from triggering in those instances
                return True
            dialog_box_text = self.create_error_query_text(error_contents)
        elif str(type(error_contents)) == "<class 'list'>":
            dialog_box_text = []
            for error in error_contents:
                dialog_box_text.append(self.create_error_query_text(error))
            dialog_box_text = "\n".join(dialog_box_text)
        else:
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
            return False
    

    def create_error_query_text(self, error_contents):
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