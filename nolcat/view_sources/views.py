import logging
from . import bp
from ..view import forms


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route to view sources list
    #ToDo: Use variable route to determine if viewing resourceSources or statisticsSources
    # return view_sources.html


#ToDo: Create route to view source details
    #ToDo: Details includes all linked other sources and notes
    # Are the source types similar enough that they can use the same template?


#ToDo: Create routes to pages to
    # Add statisticsSources
    # Edit statisticsSources details
    # Add resourceSources
    # Edit resourceSources details
    #ToDo: Adding sources uses blank fields where editing resources prepopulates them and saves any changes--are the source types similar enough that they can use the same template?
    #ToDo: This includes adding to notes relations for sources