import logging
from . import bp
from ..view import forms


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route to and page for viewing list of records in `vendors`


#ToDo: Create route to and page for viewing a record in `vendors` with its associated `vendorNotes` records and creating a new `vendorNotes` record


#ToDo: Create route to and page for viewing list of records in `statisticsSources`


#ToDo: Create route to and page for viewing a record in `statisticsSources` with its accompanying data and associated `statisticsSourceNotes` records and creating a new `statisticsSourceNotes` record


#ToDo: Create route to and page for query construction which executes query and downloads results as tabular file (later, move to page with data viz and option to download tabular data)
    #ToDo: Construct queries
    #ToDo: Determine how a name from the resource name relation will be selected