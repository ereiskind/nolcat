import logging
from . import bp


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route to and page for viewing list of records in `vendors`


#ToDo: Create route to and page for viewing a record in `vendors` with its associated `vendorNotes` records and creating a new `vendorNotes` record


#ToDo: Create route to and page for viewing list of records in `statisticsSources`


#ToDo: Create route to and page for viewing a record in `statisticsSources` with its accompanying data and associated `statisticsSourceNotes` records and creating a new `statisticsSourceNotes` record


#ToDo: Create route to and page for viewing records in `fiscalYears` with the fields/attributes