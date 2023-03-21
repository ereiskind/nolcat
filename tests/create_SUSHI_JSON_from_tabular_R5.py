"""Transform Excel worksheet produced by "tests\\data\\create_JSON_base.json" into a JSON."""

import logging
import pathlib
from openpyxl import load_workbook

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

absolute_path_to_tests_directory = pathlib.Path(__file__).parent.resolve()
directory_with_final_JSONs = absolute_path_to_tests_directory / 'data' / 'COUNTER_JSONs_for_tests'


#Section: Load the Workbook(s)
file_path = input("Enter the complete file path for the Excel workbook output from OpenRefine: ")
file_path = pathlib.Path(file_path)
file = load_workbook(filename=file_path, read_only=True)
report_name = file_path.stem
report_type = report_name.split("_")[1]
sheet = file[report_name]
logging.info(f"Creating JSON from report {report_name} for a {report_type}.")