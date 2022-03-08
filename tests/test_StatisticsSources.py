"""Tests the methods in StatisticsSources."""

import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nolcat import Database_Credentials
from nolcat.SQLAlchemy_engine import engine
from nolcat.models import StatisticsSources
from nolcat.models import PATH_TO_CREDENTIALS_FILE
from database_seeding_fixtures import vendors_relation
from database_seeding_fixtures import statisticsSources_relation


#ToDo: Create SQLAlchemy session fixture


#ToDo: Create fixture to load into the statisticsSources relation based on the import but replacing the values in statisticsSources_relation['Statistics_Source_Retrieval_Code'] with random retrieval code values found in R5_SUSHI_credentials.json


#ToDo: Test that `engine` is of type `"<class 'sqlalchemy.engine.base.Engine'>"`


#ToDo: Load the imported vendors_relation dataframe and the above modified statisticsSources_relation dataframe into the database