from flask import render_template
from flask import request
from flask import abort
import pandas as pd
from . import bp
from nolcat.raw_COUNTER_report import *


#ToDo: After creating the first account with ingest permissions, come here
@bp.route('/initialize-database')
def initialize_initial_relations():
    render_template('start-database-initialization.html')


@bp.route('/initialize-collection-tracking')
def save_historical_collection_tracking_info():
    #ToDo: Load "initialize_fiscalYears.csv" into titular relation
    #ToDo: Load "initialize_vendors.csv" into titular relation
    #ToDo: Load "initialize_statisticsSources.csv" into titular relation
    #ToDo: `SELECT statisticsSources.Statistics_Source_ID, fiscalYears.Fiscal_Year_ID, statisticsSources.Statistics_Source_Name, fiscalYears.Year FROM statisticsSources JOIN fiscalYears;` (this is an intentional cartesian product)
    #ToDo: Create downloadable CSV "initialize_annualUsageCollectionTracking.csv" with results of above as first four columns and the following field names in the rest of the first row
        # Usage_Is_Being_Collected
        # Manual_Collection_Required
        # Collection_Via_Email
        # Is_COUNTER_Compliant
        # Collection_Status
        # Usage_File_Path
        # Notes
    render_template('historical-collection-tracking.html')


@bp.route('/historical-non-COUNTER-data')
def upload_historical_non_COUNTER_usage():
    #ToDo: Load "initialize_annualUsageCollectionTracking.csv" into titular relation
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    #ToDo: `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';`
    #ToDo: Create an iterable to pass all the records returned by the above to a form
    render_template('upload-historical-non-COUNTER-data.html')


@bp.route('/historical-COUNTER-data')
def upload_historical_COUNTER_usage():
    """Saves non-COUNTER compliant usage data files and their locations, then returns the page for uploading reformatted COUNTER R4 CSVs."""
    #Alert: The procedure below is based on non-COUNTER compliant usage being in files saved in container and retrieved by having their paths saved in the database; if the files themselves are saved in the database as BLOB objects, this will need to change
    #ToDo: For each file uploaded in the form
        #ToDo: Save the file in a TBD location in the container using the AUCT_Statistics_Source and AUCT_Fiscal_Year values for the file name
        #ToDo: `UPDATE annualUsageCollectionTracking SET Usage_File_Path='<file path of the file saved above>' WHERE AUCT_Statistics_Source=<the composite PK value> AND AUCT_Fiscal_Year=<the composite PK value>`
    return render_template('select-R4-CSVs.html')


@bp.route('/matching', methods=['GET', 'POST'])
def determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    if request.method == "POST":
        R4_dataframe = pd.concat(
            [
                pd.read_csv(
                    CSV,
                    dtype={
                        # 'Interface' is fine as default float64
                        'Resource_Name': 'string',
                        'Publisher': 'string',
                        'Platform': 'string',
                        'DOI': 'string',
                        'Proprietary_ID': 'string',
                        'ISBN': 'string',
                        'Print_ISSN': 'string',
                        'Online_ISSN': 'string',
                        'Data_Type': 'string',
                        'Metric_Type': 'string',
                        # R4_Month uses parse_dates
                        # R4_Count is fine as default int64
                    },
                    parse_dates=['R4_Month'],  # For this to work, the dates need to be ISO-formatted strings (with CSVs, all the values are strings)
                    encoding='unicode_escape',  # This allows for CSVs with non-ASCII characters
                    infer_datetime_format=True  # Speeds up the parsing process if the format can be inferred; since all dates will be in the same format, this should be easy to do
                ) for CSV in request.files.getlist('R4_files')
            ],
            ignore_index=True
        )
        R4_reports = RawCOUNTERReport(R4_dataframe)
        confirmed_matches, matches_needing_confirmation = R4_reports.perform_deduplication_matching()
        return render_template('select-matches.html')  #ToDo: Add variables to pass to Jinja, next route function
    else:
        return abort(404)


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')