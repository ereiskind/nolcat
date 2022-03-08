"""This script holds the SQLAlchemy engine creation function because when the function is in `app.py`, an ImportError due to circular imports occurs."""

from sqlalchemy import create_engine
import nolcat.Database_Credentials as Database_Credentials  # The "nolcat/Database_Credentials.py" file is added to the repo as part of the container build; there is a placeholder for it in the repo at present

def _DATABASE_SCHEMA_NAME():
    """Contains the constant for the name of the database.
    
    In production, the Database_Credentials.py file will have a `Database` variable with the name of the MySQL schema in it. At this point in the development process, however, that variable is not in that file in the AWS container. This function looks for that variable but provides the schema name as a string constant if it can't be found; once the variable has been added to that file in the AWS container, this function will be removed and the function call replaced with `Database_Credentials.Database`.
    """
    try:
        return Database_Credentials.Database
    except:
        return "nolcat_db_dev"


DATABASE_SCHEMA_NAME = _DATABASE_SCHEMA_NAME()
DATABASE_USERNAME = Database_Credentials.Username
DATABASE_PASSWORD = Database_Credentials.Password
DATABASE_HOST = Database_Credentials.Host
DATABASE_PORT = Database_Credentials.Post

# https://docs.sqlalchemy.org/en/14/dialects/mysql.html#dialect-mysql for all possible MySQL DBAPI options

def engine():
    """Returns a SQLAlchemy engine object."""
    engine = create_engine(f'mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}')
    return engine