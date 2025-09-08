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
with open(Path('/nolcat/nolcat/new_nolcat_secrets.py')) as secrets_file:
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

def COUNTERData_data_types():
    return {
        "statistics_source_ID": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        "report_type": 'string',
        "resource_name": 'string',
        "publisher": 'string',
        "publisher_ID": 'string',
        "platform": 'string',
        "authors": 'string',
        "publication_date": 'datetime64[ns]',
        "article_version": 'string',
        "DOI": 'string',
        "proprietary_ID": 'string',
        "ISBN": 'string',
        "print_ISSN": 'string',
        "online_ISSN": 'string',
        "URI": 'string',
        "data_type": 'string',
        "section_type": 'string',
        "YOP": 'Int16',  # Relation uses two-byte integer type, so code uses two-byte integer data type from pandas, which allows nulls
        "access_type": 'string',
        "access_method": 'string',
        "parent_title": 'string',
        "parent_authors": 'string',
        "parent_publication_date": 'datetime64[ns]',
        "parent_article_version": 'string',
        "parent_data_type": 'string',
        "parent_DOI": 'string',
        "parent_proprietary_ID": 'string',
        "parent_ISBN": 'string',
        "parent_print_ISSN": 'string',
        "parent_online_ISSN": 'string',
        "parent_URI": 'string',
        "metric_type": 'string',
        "usage_date": 'datetime64[ns]',
        "usage_count": 'int',  # Python's `int` is used to reinforce that this is a non-null field
        "report_creation_date": 'datetime64[ns]',
    }


#SECTION: Break Down SQL Files
save_location = Path(args.folder)
save_location.mkdir(parents=True, exist_ok=True)
record_of_CSVs = save_location / '__record.txt'

df = query_database("SELECT statistics_source_ID, report_type, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, report_creation_date;")
for record in df.iterrows():
    statistics_source_ID = record[1]['statistics_source_ID']
    report_type = record[1]['report_type']
    if isinstance(record[1]['report_creation_date'], pd._libs.tslibs.timestamps.Timestamp):
        report_creation_date = str(record[1]['report_creation_date'].isoformat())[:10]
    else:
        report_creation_date = "NULL"

    if report_creation_date == "NULL":
        query = f"SELECT * FROM COUNTERData WHERE statistics_source_ID={statistics_source_ID} AND report_type='{report_type}' AND report_creation_date IS NULL;"
    else:
        query = f"SELECT * FROM COUNTERData WHERE statistics_source_ID={statistics_source_ID} AND report_type='{report_type}' AND report_creation_date='{report_creation_date}';"
    df_to_save = query_database(query)

    CSV_file_name = f"{statistics_source_ID}_{report_type}_{report_creation_date}.csv"
    with open(record_of_CSVs, 'a+', encoding='utf-8') as file:
        file.write(f"{CSV_file_name}\n")
        #file.write("\tPublisher\n")
        #for publisher in df_to_save['publisher'].unique():
        #    file.write(f"\t\t{publisher}\n")
        file.write("\tPlatform\n")
        for platform in df_to_save['platform'].unique():
            file.write(f"\t\t{platform}\n")
    df_to_save.to_csv(
        save_location / CSV_file_name,
        index=False,
    )


#SECTION: Create Parquet Files
if args.combine is None:
    sys.exit()

regex = re.compile(r'\d+_\w{2}\d?_((\d{4}\-\d{2}\-\d{2})|(NULL))')
CSV_names_and_paths = {}
for file in save_location.iterdir():
    if regex.fullmatch(file.stem):
        CSV_names_and_paths[file.stem] = [file]

second_folder_location = Path(args.combine)
if second_folder_location.exists():
    for file in second_folder_location.iterdir():
        if regex.fullmatch(file.stem):
            if CSV_names_and_paths.get(file.stem):
                CSV_names_and_paths[file.stem].append(file)
            else:
                CSV_names_and_paths[file.stem] = [file]

for file_name, file_path_list in CSV_names_and_paths.items():
    data_from_CSVs = []
    for file_path in file_path_list:
        df_from_CSV = pd.read_csv(
            file_path,
            index_col=None,
            parse_dates=['publication_date', 'parent_publication_date', 'usage_date'],
            date_format='ISO8601',
            encoding='utf-8',
            encoding_errors='backslashreplace',
        )
        df_from_CSV = df_from_CSV.astype({k: v for (k, v) in COUNTERData_data_types().items() if k in df_from_CSV.columns})
        data_from_CSVs.append(df_from_CSV)
    combined_df = pd.concat(
        data_from_CSVs,
        ignore_index=True,
    )
    try:
        combined_df.to_parquet(
            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
            index=False,
            storage_options={
                "key": secrets['AWS_ACCESS_KEY_ID'],
                "secret": secrets['Secret'],
                "token": secrets['AWS_SESSION_TOKEN'],
            },
        )
        print("Use Key='AWS_ACCESS_KEY_ID', Secret='Secret', Token='AWS_SESSION_TOKEN'")
    except Exception as e:
        print(f"Key='AWS_ACCESS_KEY_ID', Secret='Secret', Token='AWS_SESSION_TOKEN' raised `{e}`")
        try:
            combined_df.to_parquet(
                f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                index=False,
                storage_options={
                    "key": secrets['AWS_ACCESS_KEY_ID'],
                    "secret": secrets['Secret'],
                    "token": secrets['AWS_SECRET_ACCESS_KEY'],
                },
            )
            print("Use Key='AWS_ACCESS_KEY_ID', Secret='Secret', Token='AWS_SECRET_ACCESS_KEY'")
        except Exception as e:
            print(f"Key='AWS_ACCESS_KEY_ID', Secret='Secret', Token='AWS_SECRET_ACCESS_KEY' raised `{e}`")
            try:
                combined_df.to_parquet(
                    f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                    index=False,
                    storage_options={
                        "key": secrets['AWS_SECRET_ACCESS_KEY'],
                        "secret": secrets['Secret'],
                        "token": secrets['AWS_SESSION_TOKEN'],
                    },
                )
                print("Use Key='AWS_SECRET_ACCESS_KEY', Secret='Secret', Token='AWS_SESSION_TOKEN'")
            except Exception as e:
                print(f"Key='AWS_SECRET_ACCESS_KEY', Secret='Secret', Token='AWS_SESSION_TOKEN' raised `{e}`")
                try:
                    combined_df.to_parquet(
                        f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                        index=False,
                        storage_options={
                            "key": secrets['AWS_ACCESS_KEY_ID'],
                            "secret": secrets['AWS_SECRET_ACCESS_KEY'],
                            "token": secrets['AWS_SESSION_TOKEN'],
                        },
                    )
                    print("Use Key='AWS_ACCESS_KEY_ID', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_SESSION_TOKEN'")
                except Exception as e:
                    print(f"Key='AWS_ACCESS_KEY_ID', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_SESSION_TOKEN' raised `{e}`")
                    try:
                        combined_df.to_parquet(
                            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                            index=False,
                            storage_options={
                                "key": secrets['Secret'],
                                "secret": secrets['AWS_SECRET_ACCESS_KEY'],
                                "token": secrets['AWS_SESSION_TOKEN'],
                            },
                        )
                        print("Use Key='Secret', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_SESSION_TOKEN'")
                    except Exception as e:
                        print(f"Key='Secret', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_SESSION_TOKEN' raised `{e}`")
                        try:
                            combined_df.to_parquet(
                                f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                index=False,
                                storage_options={
                                    "key": secrets['AWS_ACCESS_KEY_ID'],
                                    "secret": secrets['AWS_SECRET_ACCESS_KEY'],
                                    "token": secrets['Secret'],
                                },
                            )
                            print("Use Key='AWS_ACCESS_KEY_ID', Secret='AWS_SECRET_ACCESS_KEY', Token='Secret'")
                        except Exception as e:
                            print(f"Key='AWS_ACCESS_KEY_ID', Secret='AWS_SECRET_ACCESS_KEY', Token='Secret' raised `{e}`")
                            try:
                                combined_df.to_parquet(
                                    f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                    index=False,
                                    storage_options={
                                        "key": secrets['AWS_SECRET_ACCESS_KEY'],
                                        "secret": secrets['Secret'],
                                        "token": secrets['AWS_ACCESS_KEY_ID'],
                                    },
                                )
                                print("Use Key='AWS_SECRET_ACCESS_KEY', Secret='Secret', Token='AWS_ACCESS_KEY_ID'")
                            except Exception as e:
                                print(f"Key='AWS_SECRET_ACCESS_KEY', Secret='Secret', Token='AWS_ACCESS_KEY_ID' raised `{e}`")
                                try:
                                    combined_df.to_parquet(
                                        f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                        index=False,
                                        storage_options={
                                            "key": secrets['AWS_SECRET_ACCESS_KEY'],
                                            "secret": secrets['AWS_ACCESS_KEY_ID'],
                                            "token": secrets['AWS_SESSION_TOKEN'],
                                        },
                                    )
                                    print("Use Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SESSION_TOKEN'")
                                except Exception as e:
                                    print(f"Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SESSION_TOKEN' raised `{e}`")
                                    try:
                                        combined_df.to_parquet(
                                            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            index=False,
                                            storage_options={
                                                "key": secrets['Secret'],
                                                "secret": secrets['AWS_ACCESS_KEY_ID'],
                                                "token": secrets['AWS_SECRET_ACCESS_KEY'],
                                            },
                                        )
                                        print("Use Key='Secret', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SECRET_ACCESS_KEY'")
                                    except Exception as e:
                                        print(f"Key='Secret', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SECRET_ACCESS_KEY' raised `{e}`")
                                        try:
                                            combined_df.to_parquet(
                                                f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                                index=False,
                                                storage_options={
                                                    "key": secrets['Secret'],
                                                    "secret": secrets['AWS_ACCESS_KEY_ID'],
                                                    "token": secrets['AWS_SESSION_TOKEN'],
                                                },
                                            )
                                            print("Use Key='Secret', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SESSION_TOKEN'")
                                        except Exception as e:
                                            print(f"Key='Secret', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SESSION_TOKEN' raised `{e}`")
                                            #try:
                                            #    combined_df.to_parquet(
                                            #        f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #        index=False,
                                            #        storage_options={
                                            #            "key": secrets['Secret'],
                                            #            "secret": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #            "token": secrets['AWS_ACCESS_KEY_ID'],
                                            #        },
                                            #    )
                                            #    print("Use Key='Secret', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_ACCESS_KEY_ID'")
                                            #except Exception as e:
                                            #    print(f"Key='Secret', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_ACCESS_KEY_ID' raised `{e}`")
                                            #    try:
                                            #        combined_df.to_parquet(
                                            #            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #            index=False,
                                            #            storage_options={
                                            #                "key": secrets['Secret'],
                                            #                "secret": secrets['AWS_SESSION_TOKEN'],
                                            #                "token": secrets['AWS_ACCESS_KEY_ID'],
                                            #            },
                                            #        )
                                            #        print("Use Key='Secret', Secret='AWS_SESSION_TOKEN', Token='AWS_ACCESS_KEY_ID'")
                                            #    except Exception as e:
                                            #        print(f"Key='Secret', Secret='AWS_SESSION_TOKEN', Token='AWS_ACCESS_KEY_ID' raised `{e}`")
                                            #        try:
                                            #            combined_df.to_parquet(
                                            #                f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                index=False,
                                            #                storage_options={
                                            #                    "key": secrets['Secret'],
                                            #                    "secret": secrets['AWS_SESSION_TOKEN'],
                                            #                    "token": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                },
                                            #            )
                                            #            print("Use Key='Secret', Secret='AWS_SESSION_TOKEN', Token='AWS_SECRET_ACCESS_KEY'")
                                            #        except Exception as e:
                                            #            print(f"Key='Secret', Secret='AWS_SESSION_TOKEN', Token='AWS_SECRET_ACCESS_KEY' raised `{e}`")
                                            #            try:
                                            #                combined_df.to_parquet(
                                            #                    f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                    index=False,
                                            #                    storage_options={
                                            #                        "key": secrets['AWS_ACCESS_KEY_ID'],
                                            #                        "secret": secrets['AWS_SESSION_TOKEN'],
                                            #                        "token": secrets['Secret'],
                                            #                    },
                                            #                )
                                            #                print("Use Key='AWS_ACCESS_KEY_ID', Secret='AWS_SESSION_TOKEN', Token='Secret'")
                                            #            except Exception as e:
                                            #                print(f"Key='AWS_ACCESS_KEY_ID', Secret='AWS_SESSION_TOKEN', Token='Secret' raised `{e}`")
                                            #                try:
                                            #                    combined_df.to_parquet(
                                            #                        f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                        index=False,
                                            #                        storage_options={
                                            #                            "key": secrets['AWS_ACCESS_KEY_ID'],
                                            #                            "secret": secrets['AWS_SESSION_TOKEN'],
                                            #                            "token": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                        },
                                            #                    )
                                            #                    print("Use Key='AWS_ACCESS_KEY_ID', Secret='AWS_SESSION_TOKEN', Token='AWS_SECRET_ACCESS_KEY'")
                                            #                except Exception as e:
                                            #                    print(f"Key='AWS_ACCESS_KEY_ID', Secret='AWS_SESSION_TOKEN', Token='AWS_SECRET_ACCESS_KEY' raised `{e}`")
                                            #                    try:
                                            #                        combined_df.to_parquet(
                                            #                            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                            index=False,
                                            #                            storage_options={
                                            #                                "key": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                "secret": secrets['AWS_ACCESS_KEY_ID'],
                                            #                                "token": secrets['Secret'],
                                            #                            },
                                            #                        )
                                            #                        print("Use Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_ACCESS_KEY_ID', Token='Secret'")
                                            #                    except Exception as e:
                                            #                        print(f"Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_ACCESS_KEY_ID', Token='Secret' raised `{e}`")
                                            #                        try:
                                            #                            combined_df.to_parquet(
                                            #                                f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                index=False,
                                            #                                storage_options={
                                            #                                    "key": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                    "secret": secrets['AWS_SESSION_TOKEN'],
                                            #                                    "token": secrets['Secret'],
                                            #                                },
                                            #                            )
                                            #                            print("Use Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_SESSION_TOKEN', Token='Secret'")
                                            #                        except Exception as e:
                                            #                            print(f"Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_SESSION_TOKEN', Token='Secret' raised `{e}`")
                                            #                            try:
                                            #                                combined_df.to_parquet(
                                            #                                    f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                    index=False,
                                            #                                    storage_options={
                                            #                                        "key": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                        "secret": secrets['AWS_SESSION_TOKEN'],
                                            #                                        "token": secrets['AWS_ACCESS_KEY_ID'],
                                            #                                    },
                                            #                                )
                                            #                                print("Use Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_SESSION_TOKEN', Token='AWS_ACCESS_KEY_ID'")
                                            #                            except Exception as e:
                                            #                                print(f"Key='AWS_SECRET_ACCESS_KEY', Secret='AWS_SESSION_TOKEN', Token='AWS_ACCESS_KEY_ID' raised `{e}`")
                                            #                                try:
                                            #                                    combined_df.to_parquet(
                                            #                                        f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                        index=False,
                                            #                                        storage_options={
                                            #                                            "key": secrets['AWS_SESSION_TOKEN'],
                                            #                                            "secret": secrets['Secret'],
                                            #                                            "token": secrets['AWS_ACCESS_KEY_ID'],
                                            #                                        },
                                            #                                    )
                                            #                                    print("Use Key='AWS_SESSION_TOKEN', Secret='Secret', Token='AWS_ACCESS_KEY_ID'")
                                            #                                except Exception as e:
                                            #                                    print(f"Key='AWS_SESSION_TOKEN', Secret='Secret', Token='AWS_ACCESS_KEY_ID' raised `{e}`")
                                            #                                    try:
                                            #                                        combined_df.to_parquet(
                                            #                                            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                            index=False,
                                            #                                            storage_options={
                                            #                                                "key": secrets['AWS_SESSION_TOKEN'],
                                            #                                                "secret": secrets['Secret'],
                                            #                                                "token": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                            },
                                            #                                        )
                                            #                                        print("Use Key='AWS_SESSION_TOKEN', Secret='Secret', Token='AWS_SECRET_ACCESS_KEY'")
                                            #                                    except Exception as e:
                                            #                                        print(f"Key='AWS_SESSION_TOKEN', Secret='Secret', Token='AWS_SECRET_ACCESS_KEY' raised `{e}`")
                                            #                                        try:
                                            #                                            combined_df.to_parquet(
                                            #                                                f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                                index=False,
                                            #                                                storage_options={
                                            #                                                    "key": secrets['AWS_SESSION_TOKEN'],
                                            #                                                    "secret": secrets['AWS_ACCESS_KEY_ID'],
                                            #                                                    "token": secrets['Secret'],
                                            #                                                },
                                            #                                            )
                                            #                                            print("Use Key='AWS_SESSION_TOKEN', Secret='AWS_ACCESS_KEY_ID', Token='Secret'")
                                            #                                        except Exception as e:
                                            #                                            print(f"Key='AWS_SESSION_TOKEN', Secret='AWS_ACCESS_KEY_ID', Token='Secret' raised `{e}`")
                                            #                                            try:
                                            #                                                combined_df.to_parquet(
                                            #                                                    f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                                    index=False,
                                            #                                                    storage_options={
                                            #                                                        "key": secrets['AWS_SESSION_TOKEN'],
                                            #                                                        "secret": secrets['AWS_ACCESS_KEY_ID'],
                                            #                                                        "token": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                                    },
                                            #                                                )
                                            #                                                print("Use Key='AWS_SESSION_TOKEN', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SECRET_ACCESS_KEY'")
                                            #                                            except Exception as e:
                                            #                                                print(f"Key='AWS_SESSION_TOKEN', Secret='AWS_ACCESS_KEY_ID', Token='AWS_SECRET_ACCESS_KEY' raised `{e}`")
                                            #                                                try:
                                            #                                                    combined_df.to_parquet(
                                            #                                                        f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                                        index=False,
                                            #                                                        storage_options={
                                            #                                                            "key": secrets['AWS_SESSION_TOKEN'],
                                            #                                                            "secret": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                                            "token": secrets['Secret'],
                                            #                                                        },
                                            #                                                    )
                                            #                                                    print("Use Key='AWS_SESSION_TOKEN', Secret='AWS_SECRET_ACCESS_KEY', Token='Secret'")
                                            #                                                except Exception as e:
                                            #                                                    print(f"Key='AWS_SESSION_TOKEN', Secret='AWS_SECRET_ACCESS_KEY', Token='Secret' raised `{e}`")
                                            #                                                    try:
                                            #                                                        combined_df.to_parquet(
                                            #                                                            f"s3://{secrets['Bucket']}/nolcat/usage/test/{file_name}.parquet",
                                            #                                                            index=False,
                                            #                                                            storage_options={
                                            #                                                                "key": secrets['AWS_SESSION_TOKEN'],
                                            #                                                                "secret": secrets['AWS_SECRET_ACCESS_KEY'],
                                            #                                                                "token": secrets['AWS_ACCESS_KEY_ID'],
                                            #                                                            },
                                            #                                                        )
                                            #                                                        print("Use Key='AWS_SESSION_TOKEN', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_ACCESS_KEY_ID'")
                                            #                                                    except Exception as e:
                                            #                                                        print(f"Key='AWS_SESSION_TOKEN', Secret='AWS_SECRET_ACCESS_KEY', Token='AWS_ACCESS_KEY_ID' raised `{e}`")