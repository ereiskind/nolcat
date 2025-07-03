"""The repo features a wide variety of logging statements and log-like output statements. Many of these are consistent within a function or module, but others are standardized with a specific logging level and structure throughout the entire repository; to avoid repetition, such statements are established as functions here. All logging statements and log-like output statements are full sentences ending in periods.
"""

from pathlib import Path
import re


#Section: Simple Helper Functions
# These are helper functions that don't work as well in `nolcat.app` for various reasons

def file_extensions_and_mimetypes():
    """A dictionary of the file extensions for the types of files that can be downloaded to S3 via NoLCAT and their mimetypes.
    
    This helper function is called in `create_app()` and thus must be before that function.
    """
    return {
        ".xlsx": "application/vnd.ms-excel",
        ".csv": "text/csv",
        ".tsv": "text/tab-separated-values",
        ".pdf": "application/pdf",
        ".docx": "application/msword",
        ".pptx": "application/vnd.ms-powerpoint",
        ".txt": "text/plain",
        ".jpeg": "image/jpeg",
        ".jpg":"image/jpeg",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".html": "text/html",
        ".htm": "text/html",
        ".xml": "text/xml",
        ".zip": "application/zip",
    }


#Section: Files, File Organization, and File I/O
#Subsection: Error Statements
def failed_upload_to_S3_statement(file_name, error_message):
    """This statement indicates that a call to `nolcat.app.upload_file_to_S3_bucket()` returned an error, meaning the file that should've been uploaded isn't being saved.

    Args:
        file_name (str): the name of the file that wasn't uploaded to S3
        error_message (str): the return statement indicating the failure of `nolcat.app.upload_file_to_S3_bucket()`
    
    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Uploading the file {file_name} to S3 failed because {error_message[0].lower()}{error_message[1:]} NoLCAT HAS NOT SAVED THIS DATA IN ANY WAY!"


def unable_to_delete_test_file_in_S3_statement(file_name, error_message):
    """This statement indicates that a file uploaded to a S3 bucket as part of a test function couldn't be removed from the bucket.

    Args:
        file_name (str): the final part of the name of the file in S3
        error_message (str): the AWS error message returned by the attempt to delete the file

    Returns:
        str: the statement for outputting the arguments to logging
    """
    return f"Trying to remove file {file_name} from the S3 bucket raised the error {error_message}."


#Subsection: Success Regexes
def upload_file_to_S3_bucket_success_regex():
    """This regex object matches the success return statement for `nolcat.app.upload_file_to_S3_bucket()`.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.app.upload_file_to_S3_bucket()`
    """
    return re.compile(r"[Ss]uccessfully loaded the file (.+) into S3 location `.+/.+`\.?")


def upload_nonstandard_usage_file_success_regex():
    """This regex object matches the success return statement for `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()`.

    The `re.DOTALL` flag is included because update statements include line breaks.

    Returns:
        re.Pattern: the regex object for the success return statement for `nolcat.models.AnnualUsageCollectionTracking.upload_nonstandard_usage_file()`
    """
    return re.compile(r"[Ss]uccessfully loaded the file (.+) into S3 location `.+/.+` and successfully performed the update (.+)\.", flags=re.DOTALL)