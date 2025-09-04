"""This procedure for changing in MySQL to parquet files is inspired by the procedure at https://estuary.dev/blog/mysql-to-parquet/."""

import argparse
from pathlib import Path
import sys
import re
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "folder",
    help="The destination folder for the CSVs created by this program"
)
parser.add_argument(
    "-c",
    "--combine",
    help="The flag indicates if the CSVs should be transformed into parquet files; use `True` if only the newly created CSVs should be converted or another file path to combine CSVs with the same name from two folders"
)
args = parser.parse_args()

#SECTION: Repeated Content
# Attempts to import `nolcat.nolcat.nolcat_glue_job.py` failed, so the content needed from that file is repeated here.

secrets = {}
with open(Path('/nolcat/nolcat/nolcat_secrets.py')) as secrets_file:
    for line in secrets_file.readlines():
        key, value = line.split(" = ")
        value = value.replace("'", "")
        value = value.replace("\n", "")
        secrets[key] = value

SQLALCHEMY_DATABASE_URI = f'mysql://{secrets['Username']}:{secrets['Password']}@{secrets['Host']}:{secrets['Port']}/{secrets['Database']}'

def query_database(query):
    try:
        df = pd.read_sql(
            sql=query,
            con=SQLALCHEMY_DATABASE_URI,
        )
        return df
    except Exception as error:
        message = f"Running the query `{query}` raised the error {error}."
        print(message)
        return message


#SECTION: Break Down SQL Files
save_location = Path(args.folder)
record_of_CSVs = save_location / '__record.txt'

df = query_database("SELECT statistics_source_ID, report_type, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, report_creation_date;")
for record in df.iterrows():
    statistics_source_ID = record[1]['statistics_source_ID']
    report_type = record[1]['report_type']
    if isinstance(record[1]['report_creation_date'], pd._libs.tslibs.timestamps.Timestamp):
        report_creation_date = str(record[1]['report_creation_date'].isoformat())[:10]
        print(report_creation_date)
    else:
        report_creation_date = "NULL"

    #if record[1]['report_creation_date'] is None:
    #    query = f"SELECT * FROM COUNTERData WHERE statistics_source_ID={record[1]['statistics_source_ID']}, report_type={record[1]['report_type']}, AND report_creation_date IS NULL;"
    #else:
    #    query = f"SELECT * FROM COUNTERData WHERE statistics_source_ID={record[1]['statistics_source_ID']}, report_type={record[1]['report_type']}, AND report_creation_date={record[1]['report_creation_date']};"
    #df_to_save = query_database(query)

    #CSV_file_name = f"{record[1]['statistics_source_ID']}_{record[1]['report_type']}_{record[1]['report_creation_date']}"  #ToDo: Check that dates are ISO format or `NULL`
    #with open(record_of_CSVs, 'at', encoding='utf-8') as file:
    #    file.write(CSV_file_name)
    #    file.write("\tPublisher")
    #    file.write([f"\t\t{x}\n" for x in df_to_save['publisher'].unique()])
    #    file.write("\tPlatform")
    #    file.write([f"\t\t{x}\n" for x in df_to_save['platform'].unique()])
    #df_to_save.to_csv(
    #    path=save_location / CSV_file_name,
    #    index=False,
    #)


#SECTION: Create Parquet Files
#if args.combine is None:
#    sys.exit()

#regex = re.compile(r'\d+_\w{2,3}_(\d{4}\-\d{2}\-\d{2})|(NULL)')
#CSV_names_and_paths = {}
#for file in save_location.iterdir():
#    if regex.fullmatch(file.stem):
#        CSV_names_and_paths[file.stem] = [file]
#if isinstance(str, args.combine):
#    for file in Path(args.combine).iterdir():
#        if regex.fullmatch(file.stem):
#            if CSV_names_and_paths.get(file.stem):
#                CSV_names_and_paths[file.stem].append(file)
#            else:
#                CSV_names_and_paths[file.stem] = [file]

#for file_name, file_path_list in CSV_names_and_paths.items():
    #ToDo: `pd.from_csv`
    #ToDo: Combine dataframes
    #ToDo: `pd.to_parquet` in a S3 folder