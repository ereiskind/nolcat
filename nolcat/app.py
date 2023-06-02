from pathlib import Path
import io
import logging
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import pandas as pd
from numpy import datetime64, squeeze
#import boto3

"""Since GitHub is used to manage the code, and the repo is public, secret information is stored in a file named `nolcat_secrets.py` maintained in the AWS instance, copied to the Docker container during the build process, and imported into this file. This import has been problematic; copying the file into this directory and providing multiple possible import statements in try-except blocks are used to handle the problem."""
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
#AWS_ACCESS_KEY = secrets.Access_Key_ID
#AWS_SECRET_KEY = secrets.Secret_Access_Key
#AWS_SESSION_TOKEN = secrets.Session_Token
#BUCKET_NAME = secrets.Bucket


csrf = CSRFProtect()
db = SQLAlchemy()

#S3_client = boto3.client(
#    's3',
#    aws_access_key_id=AWS_ACCESS_KEY,
#    aws_secret_access_key=AWS_SECRET_KEY,
#    aws_session_token=AWS_SESSION_TOKEN,
#)


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
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Explicitly set to disable warning in tests
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = './relation_initialization_template'  # This config sets the file that handles both Flask file downloads adn uploads, but since all input, including file uploads, is handled with WTForms, this folder is only used for storing content the user will need to download.
    csrf.init_app(app)
    db.init_app(app)

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
            from .models import COUNTERData
            db.create_all()

    #Section: Register Blueprints
    try:
        from nolcat import annual_stats
    except:
        from . import annual_stats
    app.register_blueprint(annual_stats.bp)

    try:
        from nolcat import ingest_usage
    except:
        from . import ingest_usage
    app.register_blueprint(ingest_usage.bp)

    try:
        from nolcat import initialization
    except:
        from . import initialization
    app.register_blueprint(initialization.bp)

    try:
        from nolcat import login
    except:
        from . import login
    app.register_blueprint(login.bp)

    try:
        from nolcat import view_lists
    except:
        from . import view_lists
    app.register_blueprint(view_lists.bp)

    try:
        from nolcat import view_usage
    except:
        from . import view_usage
    app.register_blueprint(view_usage.bp)

    #Section: Create Homepage Route
    @app.route('/')
    def homepage():
        """Returns the homepage in response to web app root requests."""
        return render_template('index.html')
    
    
    return app


def date_parser(dates):
    """The function for parsing dates as part of converting ingested data into a dataframe.
    
    The `date_parser` argument of pandas's methods for reading external files to a dataframe traditionally takes a lambda expression, but due to repeated use throughout the program, a reusable function is a better option. Using the `to_datetime` method itself ensures dates will be in ISO format in dataframes, facilitating the upload of those dataframes to the database.

    Args:
        dates (date, datetime, string): a value in a data file being read into a pandas dataframe being interpreted as a date

    Returns:
        datetime64[ns]: a datetime value pandas inherits from numpy
    """
    return pd.to_datetime(dates, format='%Y-%m-%d', errors='coerce', infer_datetime_format=True)  # The `errors` argument sets all invalid parsing values, including null values and empty strings, to `NaT`, the null value for the pandas datetime data type


def last_day_of_month(first_day_of_month):
    """The function for returning the last day of a given month.

    When COUNTER date ranges include the day, the "End_Date" value is for the last day of the month. This function consolidates that functionality in a single location and facilitates its use in pandas `map` functions.

    Args:
        first_day_of_month (pd.Timestamp): the first day of the month; the dataframe of origin will have the date in a datetime64[n] data type, but within this function, the data type is Timestamp
    
    Returns:
        str: the last day of the given month in ISO format
    """
    year_and_month_string = first_day_of_month.date().isoformat()[0:-2]  # Returns an ISO date string, then takes off the last two digits
    return year_and_month_string + str(first_day_of_month.days_in_month)


def first_new_PK_value(relation):
    """The function for getting the next value in the primary key sequence.

    The default value of the SQLAlchemy `autoincrement` argument in the field constructor method adds `AUTO_INCREMENT` to the primary key field in the data definition language. Loading values, even ones following the sequential numbering that auto-incrementation would use, alters the relation's `AUTO_INCREMENT` attribute, causing a primary key duplication error. Stopping this error requires removing auto-incrementation from the primary key fields (by setting the `autoincrement` argument in the field constructor method to `False`); without the auto-incrementation, however, the primary key values must be included as the dataframe's record index field. This function finds the highest value in the primary key field of the given relation and returns the next integer.

    Args:
        relation (str): the name of the relation being checked
    
    Returns:
        int: the first primary key value in the data to be uploaded to the relation
    """
    logging.debug("Starting `first_new_PK_value`")
    if relation == 'fiscalYears':
        PK_field = 'fiscal_year_ID'
    elif relation == 'vendors':
        PK_field = 'vendor_ID'
    elif relation == 'vendorNotes':
        PK_field = 'vendor_notes_ID'
    elif relation == 'statisticsSources':
        PK_field = 'statistics_source_ID'
    elif relation == 'statisticsSourceNotes':
        PK_field = 'statistics_source_notes_ID'
    elif relation == 'resourceSources':
        PK_field = 'resource_source_ID'
    elif relation == 'resourceSourceNotes':
        PK_field = 'resource_source_notes_ID'
    elif relation == 'COUNTERData':
        PK_field = 'COUNTER_data_ID'
    
    largest_PK_value = pd.read_sql(
        sql=f'''
            SELECT {PK_field} FROM {relation}
            ORDER BY {PK_field} DESC
            LIMIT 1;
        ''',
        con=db.engine,
    )
    if largest_PK_value.empty:  # If there's no data in the relation, the dataframe is empty, and the primary key numbering should start at zero
        logging.debug(f"The {relation} relation is empty")
        return 0
    logging.debug(f"Result of query for largest primary key value:\n{largest_PK_value}")
    largest_PK_value = largest_PK_value.iloc[0][0]
    return int(largest_PK_value) + 1


def return_string_of_dataframe_info(df):
    """Returns the data output by `pandas.DataFrame.info()` as a string so the method can be used in logging statements.

    The `pandas.DataFrame.info()` method forgoes returning a value in favor of printing directly to stdout; as a result, it doesn't output anything when used in a logging statement. This function captures the data traditionally output directly to stdout in a string for use in a logging statement. This function is based off the one at https://stackoverflow.com/a/39440325.

    Args:
        df (dataframe): the dataframe in the logging statement
    
    Returns:
        str: the output of the `pandas.DataFrame.info()` method
    """
    in_memory_stream = io.StringIO()
    df.info(buf=in_memory_stream)
    return in_memory_stream.getvalue()


def change_single_field_dataframe_into_series(df):
    """The function for changing a dataframe with a single field into a series.

    This function transforms any dataframe with a single non-index field into a series with the same index. Dataframes with multiindexes are accepted and those indexes are preserved.

    Args:
        df (dataframe): the dataframe to be transformed
    
    Returns:
        pd.Series: a series object with the same exact data as the initial dataframe
    """
    return pd.Series(
        data=squeeze(df.values),  # `squeeze` converts the numpy array from one column with n elements to an array with n elements
        index=df.index,
        dtype=df[df.columns[0]].dtype,
        name=df.columns[0],
    )


def restore_Boolean_values_to_Boolean_field(series):
    """The function for converting the integer field used for Booleans in MySQL into a pandas `boolean` field.

    MySQL stores Boolean values in a `TINYINT(1)` field, so any Boolean fields read from the database into a pandas dataframe appear as integer or float fields with the values `1`, `0`, and, if nulls are allowed, `NaN`. For simplicity, clarity, and consistency, turning these fields back into pandas Boolean fields is often a good idea.

    Args:
        series (pd.Series): a Boolean field with numeric values and a numeric dtype from MySQL
    
    Returns:
        pd.Series: a series object with the same information as the initial series but with Boolean values and a Boolean dtype
    """
    return series.replace({
        0: False,
        1: True,
    }).astype('boolean')


#def upload_file_to_S3_bucket(file, file_name, client=S3_client, bucket=BUCKET_NAME):
#    """The function for uploading files to a S3 bucket.
#
#    SUSHI pulls that cannot be loaded into the database for any reason are saved to S3 with a file name following the convention "{statistics_source_ID}_{report path with hyphen replacing slash}_{date range start in 'yyyy-mm' format}_{date range end in 'yyyy-mm' format}_{ISO timestamp}". Non-COUNTER usage files use the file naming convention "{statistics_source_ID}_{fiscal_year_ID}".
#
#    Args:
#        file (file-like or path-like object): the file being uploaded to the S3 bucket or the path to said file as a Python object
#        file_name (str): the name the file will be saved under in the S3 bucket
#        client (S3.Client): the client for connecting to an S3 bucket; default is `S3_client` initialized at the beginning of this module
#        bucket (str): the name of the S3 bucket; default is constant derived from `nolcat_secrets.py`
#    
#    Returns:
#        str: the logging statement to indicate if uploading the data succeeded or failed
#    """
#    try:
#        client.upload_fileobj(
#            Fileobj=file,
#            Bucket=bucket,
#            Key=file_name,
#        )
#        return f"The file `{file_name}` has been successfully uploaded to the `{bucket}` S3 bucket."
#    except Exception as error:
#        logging.warning(f"Trying to upload the object `{file}` as a file-like object raised the error `{error}`.")
#
#        if file.is_file():  # Meaning `file` is a path-like object referencing an existing file
#            try:
#                client.upload_file(
#                    Filename=file,
#                    Bucket=bucket,
#                    Key=file_name,
#                )
#            except Exception as error:
#                logging.error(f"Trying to upload the file saved at `{file}` raised the error `{error}`.")
#                return f"Trying to upload the file saved at `{file}` raised the error `{error}`."
#        
#        else:
#            try:
#                file_path = Path() / file_name
#                file.save(file_path)  # `upload_file()` takes a file from a saved location, so the file must be saved first
#                
#                try:
#                    client.upload_file(
#                        Filename=file_path,
#                        Bucket=bucket,
#                        Key=file_name,
#                    )
#                except Exception as error:
#                    logging.error(f"Trying to upload the file saved at `{file_path}` raised the error `{error}`.")
#                    return f"Trying to upload the file saved at `{file_path}` raised the error `{error}`."
#            
#            except Exception as error:
#                logging.error(f"Trying to save the object `{file}` to upload it into the S3 bucket raised the error `{error}`.")
#                return f"Trying to save the object `{file}` to upload it into the S3 bucket raised the error `{error}`."
#                
#            file_path.unlink()  # This deletes the file created and saved above; if this file wasn't created, the function would've ended at the return statement above
#            return f"The file `{file_name}` has been successfully uploaded to the `{bucket}` S3 bucket."