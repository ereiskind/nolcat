import os
from pathlib import Path
import re
import pandas as pd
from nolcat.raw_COUNTER_report import RawCOUNTERReport

def test_fixture():
    dataframes_to_concatenate = []
    for spreadsheet in os.listdir(Path('tests', 'bin', 'OpenRefine_exports')):
        statistics_source_ID = re.findall(r'(\d*)_\w{2}\d_\d{2}\-\d{2}\.xlsx', string=spreadsheet)[0]
        dataframe = pd.read_excel(
            Path('tests', 'bin', 'OpenRefine_exports', spreadsheet),
            engine='openpyxl',
            dtype={
                'Resource_Name': 'string',
                'Publisher': 'string',
                'Platform': 'string',
                'DOI': 'string',
                'Proprietary_ID': 'string',
                'ISBN': 'string',
                'Print_ISSN': 'string',
                'Online_ISSN': 'string',
                'Data_Type': 'string',
                'Metric_Type': 'string',
                # R4_Month is fine as default datetime64[ns]
                'R4_Count': 'int',
            },
        )
        dataframe['Statistics_Source_ID'] = statistics_source_ID
        dataframes_to_concatenate.append(dataframe)
    RawCOUNTERReport_fixture = pd.concat(
        dataframes_to_concatenate,
        ignore_index=True
    )
    print(f"the concatenated database:\n{RawCOUNTERReport_fixture}")
    yield_object = RawCOUNTERReport(RawCOUNTERReport_fixture)
    print(f"the yield object:\n{yield_object}")
    assert False
