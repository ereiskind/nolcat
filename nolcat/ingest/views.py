from flask import render_template
from flask import request
from flask import abort
import pandas as pd
from . import bp


@bp.route('/initialize-database')
def start_R4_data_load():
    """Returns the page where the CSVs with R4 data are selected."""
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
        #ToDo: Return data for presenting resource matches that need to be manually confirmed
        return render_template('select-matches.html')
    else:
        return abort(404)


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return render_template('show-loaded-data.html')