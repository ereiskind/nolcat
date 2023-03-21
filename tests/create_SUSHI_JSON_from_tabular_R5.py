"""Transform Excel worksheet produced by "tests\\data\\create_JSON_base.json" into a JSON."""

import logging
import pathlib

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

absolute_path_to_tests_directory = pathlib.Path(__file__).parent.resolve()
directory_with_final_JSONs = absolute_path_to_tests_directory / 'data' / 'COUNTER_JSONs_for_tests'