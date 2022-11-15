import logging
from flask import render_template

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')
def ingest_usage_homepage():
    """Returns the homepage for the `ingest_usage` blueprint, which has links to the different usage upload options."""
    return render_template('index.html')


#ToDo: Create route for uploading COUNTER reports
    #ToDo: form = class of form containing multi-file upload option
    #ToDo: if request.method == 'GET':
        #ToDo: return render_template('page-the-form-is-on.html', form=form)
    #ToDo: elif form.validate_on_submit():
        #ToDo: df = UploadCOUNTERReports.create_dataframe(data returned by form)
        #ToDo: new_records = RawCOUNTERReport(df)
        #ToDo: normalized_resources_in_database = RawCOUNTERReport._create_normalized_resource_data_argument()
        #ToDo: tuples_with_index_values_of_matched_records, dict_with_keys_that_are_resource_metadata_for_possible_matches_and_values_that_are_lists_of_tuples_with_index_record_pairs_corresponding_to_the_metadata = new_records.perform_deduplication_matching(normalized_resources_in_database)
        #ToDo: For all items in above dict, present the metadata in the keys and ask if the resources are the same
        #ToDo: Load new_records with metadata matches into database
        #ToDo: return redirect(url_for('name of the route function for the page that user should go to once form is submitted'))
    #ToDo: else:
        #ToDo: return abort(404)


@bp.route('/harvest')
def harvest_SUSHI_statistics():
    """A page for initiating R5 SUSHI usage statistics harvesting.
    
    This page provides inputs for all the parameters needed for an R5 SUSHI call, then executes the StatisticsSources.collect_usage_statistics() method. This is designed to allow for the development of the method without having either the database connection the StatisticsSources class, as a SQLAlchemy table class, traditionally needs or knowing if the SUSHI credentials for the different StatisticsSources objects will be sourced from the Alma API or from a file of undetermined format and location within the container but outside this repository. 
    """
    #ToDo: Create route for getting start and end dates for custom SUSHI range, then putting them into StatisticsSources.collect_usage_statistics
    pass


#ToDo: Create route to and page for adding non-COUNTER compliant usage
    #ToDo: How should non-COUNTER usage be stored? As BLOB in MySQL, as files in the container, as a Docker volume, in some other manner?
    #ToDo: Find all resources to which this applies with `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';`
    # render_template('upload-historical-non-COUNTER-data.html')