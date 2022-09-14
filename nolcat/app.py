from pathlib import Path
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

"""Since GitHub is used to manage the code, and the repo is public, the AWS instance is used to save confidential information.

Flask-SQLAlchemy takes in the information for establishing a database connection through the string assigned to the config variable `SQLALCHEMY_DATABASE_URI`. Confidential information is currently set up to be imported from the `nolcat_secrets.py` file, but ultimately, all of the data in those files will be saved to environment variables. Naming the file `secrets.py` causes an ImportError with numpy.
"""
try:
    import nolcat_secrets as secrets  # This is the import statement accepted by AWS
except:
    try:
        from . import nolcat_secrets as secrets
        print("Import was `from . import nolcat_secrets`")
    except:
        from .. import nolcat_secrets as secrets
        print("Import was `from .. import nolcat_secrets`")

DATABASE_USERNAME = secrets.Username
DATABASE_PASSWORD = secrets.Password
DATABASE_HOST = secrets.Host
DATABASE_PORT = secrets.Port
DATABASE_SCHEMA_NAME = secrets.Database
SECRET_KEY = secrets.Secret


csrf = CSRFProtect()
db = SQLAlchemy()

def page_not_found(error):
    """Returns the 404 page when a HTTP 404 error is raised."""
    return render_template('404.html'), 404


def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    csrf.init_app(app)
    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = './data'

    #Section: Create Command to Build Schema
    # Documentation at https://flask.palletsprojects.com/en/2.1.x/appcontext/
    @app.cli.command('create-db')
    def create_db():
        with create_app().app_context():
            from .models import FiscalYears
            from .models import Vendors
            from .models import VendorNotes
            from .models import StatisticsSources
            from .models import StatisticsSourceNotes
            from .models import StatisticsResourceSources
            from .models import ResourceSources
            from .models import ResourceSourceNotes
            from .models import AnnualUsageCollectionTracking
            from .models import Resources
            from .models import ResourceMetadata
            from .models import ResourcePlatforms
            from .models import UsageData
            db.create_all()

    #Section: Create Homepage and Register Other Blueprints
    from nolcat import annual_stats
    app.register_blueprint(annual_stats.bp)

    from nolcat import ingest_usage
    app.register_blueprint(ingest_usage.bp)

    from nolcat import initialization
    app.register_blueprint(initialization.bp)

    from nolcat import login
    app.register_blueprint(login.bp)

    from nolcat import view_resources
    app.register_blueprint(view_resources.bp)

    from nolcat import view_sources
    app.register_blueprint(view_sources.bp)

    from nolcat import view_usage
    app.register_blueprint(view_usage.bp)

    from nolcat import view_vendors
    app.register_blueprint(view_vendors.bp)

    @app.route('/')
    def homepage():
        """Returns the homepage in response to web app root requests."""
        return render_template('index.html')
    
    
    return app