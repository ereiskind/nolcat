from pathlib import Path
import logging
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import pandas as pd

"""Since GitHub is used to manage the code, and the repo is public, secret information is stored in a file named `nolcat_secrets.py` exclusive to the Docker container and imported into this file.

The overall structure of this app doesn't facilitate a separate module for a SQLAlchemy `create_engine` function: when `nolcat/__init__.py` is present, keeping these functions in a separate module and importing them causes a ``ModuleNotFoundError: No module named 'database_connectors'`` error when starting up the Flask server, but with no `__init__` file, the blueprint folder imports don't work. With Flask-SQLAlchemy, a string for the config variable `SQLALCHEMY_DATABASE_URI` is all that's needed, so the data the string needs are imported from a `nolcat_secrets.py` file saved to Docker and added to this directory during the build process. This import has been problematic; moving the file from the top-level directory to this directory and providing multiple possible import statements in try-except blocks are used to handle the problem.
"""
try:
    import nolcat_secrets as secrets
except:
    try:
        from . import nolcat_secrets as secrets
    except:
        try:
            from nolcat import nolcat_secrets as secrets
        except:
            print("None of the provided import statements for `nolcat\\nolcat_secrets.py` worked.")

DATABASE_USERNAME = secrets.Username
DATABASE_PASSWORD = secrets.Password
DATABASE_HOST = secrets.Host
DATABASE_PORT = secrets.Port
DATABASE_SCHEMA_NAME = secrets.Database
SECRET_KEY = secrets.Secret


logging.basicConfig(level=logging.DEBUG, format="Flask Factory Pattern - - [%(asctime)s] %(message)s")


csrf = CSRFProtect()
db = SQLAlchemy()

def page_not_found(error):
    """Returns the 404 page when a HTTP 404 error is raised."""
    return render_template('404.html'), 404


def internal_server_error(error):
    """Returns the 500 page when a HTTP 500 error is raised."""
    return render_template('500.html', error=error), 500  #ToDo: This doesn't seem to be working; figure out why


def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    csrf.init_app(app)
    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = './nolcat_db_data'
    logging.debug("Flask app created!")

    #Section: Create Command to Build Schema
    # Documentation for decorator at https://flask.palletsprojects.com/en/2.1.x/appcontext/
    @app.cli.command('create-db')
    def create_db():
        with create_app().app_context():  # Creates an app context using the Flask factory pattern
            # Per instructions at https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/: "To create the initial database, just import the db object[s]...and run the `SQLAlchemy.create_all()` method"
            from .models import FiscalYears
            from .models import Vendors
            from .models import VendorNotes
            from .models import StatisticsSources
            from .models import StatisticsSourceNotes
            from .models import ResourceSources
            from .models import ResourceSourceNotes
            from .models import StatisticsResourceSources
            from .models import AnnualUsageCollectionTracking
            from .models import Resources
            from .models import ResourceMetadata
            from .models import ResourcePlatforms
            from .models import UsageData
            db.create_all()

    #Section: Create Homepage and Register Other Blueprints
    #Subsection: Import Blueprints
    # The appropriate level for the relative import has changed due to currently unknown factors; to ensure the imports always work, the imports are grouped together in a try-except block
    try:
        from ..nolcat import annual_stats
        from ..nolcat import ingest_usage
        from ..nolcat import initialization
        from ..nolcat import login
        from ..nolcat import view_resources
        from ..nolcat import view_sources
        from ..nolcat import view_usage
        from ..nolcat import view_vendors
        logging.debug("Blueprints imported from `..nolcat`")
    except ValueError:  # `ValueError: attempted relative import beyond top-level package`
        try:
            from .nolcat import annual_stats
            from .nolcat import ingest_usage
            from .nolcat import initialization
            from .nolcat import login
            from .nolcat import view_resources
            from .nolcat import view_sources
            from .nolcat import view_usage
            from .nolcat import view_vendors
            logging.debug("Blueprints imported from `.nolcat`")
        except ModuleNotFoundError:  #`ModuleNotFoundError: No module named 'nolcat.nolcat'`
            from nolcat import annual_stats
            from nolcat import ingest_usage
            from nolcat import initialization
            from nolcat import login
            from nolcat import view_resources
            from nolcat import view_sources
            from nolcat import view_usage
            from nolcat import view_vendors
            logging.debug("Blueprints imported from `nolcat`")

    #Subsection: Register Blueprints
    app.register_blueprint(annual_stats.bp)
    app.register_blueprint(ingest_usage.bp)
    app.register_blueprint(initialization.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(view_resources.bp)
    app.register_blueprint(view_sources.bp)
    app.register_blueprint(view_usage.bp)
    app.register_blueprint(view_vendors.bp)
    logging.debug("Blueprints registered")

    #Subsection: Create Homepage Route
    @app.route('/')
    def homepage():
        """Returns the homepage in response to web app root requests."""
        return render_template('index.html')
    
    
    logging.debug("Flask factory pattern complete")
    return app


def date_parser(dates):
    """The function for parsing dates as part of converting ingested data into a dataframe.
    
    The `date_parser` argument of pandas's methods for reading external files to a dataframe traditionally takes a lambda expression, but due to repeated use throughout the program, a reusable function is a better option. Using the `to_datetime` method itself ensures dates will be in ISO format in dataframes, facilitating the upload of those dataframes to the database.
    """
    return pd.to_datetime(dates, format='%Y-%m-%d', errors='coerce', infer_datetime_format=True)  # The `errors` argument sets all invalid parsing values, including null values and empty strings, to `NaT`, the null value for the pandas datetime data type