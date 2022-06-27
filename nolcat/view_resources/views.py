import logging

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


#ToDo: Create route to view resources list
    # return view_resources.html


#ToDo: Create route to add a new resource or edit a resource
    #ToDo: Adding a resource = none of the form fields are filled in
    #ToDo: Editing a resource = form fields are prefilled with the existing data for the resource and whatever is in the forms when the page is saved is committed back to the database
    #ToDo: This format would require a way to add metadata elements to the `resourceMetadata` relation from the page


#ToDo: Create route to view resource details