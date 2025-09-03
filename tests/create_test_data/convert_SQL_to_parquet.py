"""This procedure for changing in MySQL to parquet files is inspired by the procedure at https://estuary.dev/blog/mysql-to-parquet/."""

from pathlib import Path
import pandas as pd

#SECTION: Repeated Content
# Attempts to import `nolcat.nolcat.nolcat_glue_job.py` failed, so the content needed from that file is repeated here.

secrets = {}
with open(Path('/nolcat/nolcat/nolcat_secrets.py')) as secrets_file:
    for line in secrets_file.readlines():
        key, value = line.split(" = ")
        print(value)
        if value[0] == "'":
            value == value[1:]
        if value[-3:] == "'\n":
            value = value[:-3]
        secrets[key] = value
print(secrets)

SQLALCHEMY_DATABASE_URI = f'mysql://{secrets['Username']}:{secrets['Password']}@{secrets['Host']}:{secrets['Port']}/{secrets['Database']}'

def query_database(query):
    try:
        df = pd.read_sql(
            sql=query,
            con=SQLALCHEMY_DATABASE_URI,
        )
        print(f"The query `{query}` return a dataframe with the following metadata:\n{df.info()}")
        return df
    except Exception as error:
        message = f"Running the query `{query}` raised the error {error}."
        print(message)
        return message


#SECTION: Break Down SQL Files
#ToDo: Repeat this section for each production file
df = query_database("SELECT statistics_source_ID, report_type, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, report_creation_date;")