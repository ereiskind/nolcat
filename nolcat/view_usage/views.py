import logging
from . import bp
from ..view_usage import forms


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route for blueprint homepage
    # return view_usage.html


#ToDo: Create route for page allowing writing SQL queries
    #ToDo: Input from this field's text box is run as query against database
    # return write_SQL_queries.html


#ToDo: Create route for query wizard
    # return query_wizard.html


#ToDo: Create route for saved queries
    #ToDo: Include same text boxes with fuzzy search that allow pre-screening of results that will be pulled up for resource titles and vendor names (possibly sources as well) as in query wizard
    #ToDo: Include calculating annual numbers, not not the methods--methods save to relation
    #ToDo: Decide what other canned queries to provide