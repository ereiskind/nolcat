import logging
from flask import render_template

from . import bp
from ..app import db
#from .forms import <name of form classes>
#from ..models import <name of SQLAlchemy classes used in views below>

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/')
def homepage():
    """Returns the homepage for the `view_vendors` blueprint, which lists the records in `vendors`."""
    return render_template('index.html')


#ToDo: Create route to add a new vendor or edit a vendor
    #ToDo: Adding a vendor = none of the form fields are filled in
    #ToDo: Editing a vendor = form fields are prefilled with the existing data for the vendor and whatever is in the forms when the page is saved is committed back to the database
    #ToDo: The page needs to include a way to connect vendors to statisticsSources and resourceSources


#ToDo: Create route to view vendor details
    # return view_vendor_details.html