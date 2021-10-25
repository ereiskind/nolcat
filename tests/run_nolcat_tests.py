"""Recreate a Dockerfile and its image"""

from datetime import datetime
import subprocess
import os

#Section: Dockerfile inputs
branch_name = input("What's the name of the branch being tested? ")
test_script_name = input("If only one test script is being run, put the full name of the test script here; to run all scripts, press enter without entering any text. ")
log_level = input("Enter `debug` or `info` for the log level. ")

if test_script_name != "":
    test_script_name = f" tests/{test_script_name}"


#Section: Create Image
#Subsection: Create New Dockerfile
logfile_timestamp = datetime.now().strftime('%Y-%m-%dT%H.%M.%S%z')
dockerfile_text = f"""
FROM python:3.8
WORKDIR ./

RUN git clone https://github.com/ereiskind/nolcat.git -b {branch_name} ./nolcat/

RUN pip install --no-cache-dir -r nolcat/requirements.txt

WORKDIR ./nolcat/
CMD python -m pytest -s --log-cli-level="{log_level}" -p pytest_session2file --session2file=logfile_{logfile_timestamp}.txt{test_script_name}
"""
with open('Dockerfile', 'w') as dockerfile:
    dockerfile.write(dockerfile_text)

#Subsection: Build New Image
subprocess.call("docker build -t nolcat-image --no-cache .")


#Section: Create Container, Running Tests and Generating Logs
subprocess.call("docker run -itd --name nolcat-container nolcat-image")
subprocess.call(f"docker cp nolcat-container:nolcat/logfile_{logfile_timestamp}.txt ./tests/logs/logfile_{logfile_timestamp}.txt")


#Section: Remove Docker Objects
subprocess.call("docker rm -f nolcat-container")
subprocess.call("docker image rm nolcat-image")
os.remove('Dockerfile')