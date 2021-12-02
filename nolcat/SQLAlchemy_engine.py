"""This script holds the SQLAlchemy engine creation function because when the function is in `app.py`, an ImportError due to circular imports occurs."""

from sqlalchemy import create_engine
import nolcat.Database_Credentials as Database_Credentials  # The "nolcat/Database_Credentials.py" file is added to the repo as part of the container build; there is a placeholder for it in the repo at present

DATABASE_SCHEMA_NAME = "nolcat"
DATABASE_USERNAME = Database_Credentials.Username
DATABASE_PASSWORD = Database_Credentials.Password
DATABASE_HOST = Database_Credentials.Host
DATABASE_PORT = Database_Credentials.Post

# https://docs.sqlalchemy.org/en/14/dialects/mysql.html#dialect-mysql for all possible MySQL DBAPI options

def engine():
    """Returns a SQLAlchemy engine object."""
    return create_engine(f'mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA_NAME}')