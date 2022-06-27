import logging

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route for choosing what type of usage upload to do


#ToDo: Create route for uploading R4 reports
    #ToDo: Upload CSV of transformed R4 report, getting StatisticsSource ID from file name
    #ToDo: Make R4 a RawCOUNTERReport object
    #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = RawCOUNTERReport.perform_deduplication_matching
    #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same
    #ToDo: RawCOUNTERReport.load_data_into_database


#ToDo: Create route for uploading R5 reports--JSON FOR TABULAR R5 DOES NOT EXIST YET--Create way to change PR, DR, TR, IR from tabular report into something RawCOUNTERReport can handle
    #ToDo: Upload CSV of transformed R5 report, getting StatisticsSource ID from file name
    #ToDo: Make R5 a RawCOUNTERReport object
    #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = RawCOUNTERReport.perform_deduplication_matching
    #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same
    #ToDo: RawCOUNTERReport.load_data_into_database


#ToDo: Create route for getting start and end dates for custom SUSHI range, then putting them into StatisticsSources.collect_usage_statistics


#ToDo: Create route to and page for adding non-COUNTER compliant usage
    #ToDo: How should non-COUNTER usage be stored? As BLOB in MySQL, as files in the container, as a Docker volume, in some other manner?
    #ToDo: Find all resources to which this applies with `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';`
    # render_template('upload-historical-non-COUNTER-data.html')
