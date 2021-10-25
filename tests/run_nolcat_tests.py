"""Recreate a Dockerfile and its image"""

import sys
import subprocess
import os

#Section: Dockerfile inputs
branch_name = sys.argv[1]
log_level = sys.argv[2]
test_script_name = sys.argv[3]

if test_script_name != "":
    test_script_name = f" tests/{test_script_name}"


#Section: Create Image
#Subsection: Create New Dockerfile
dockerfile_text = f"""
FROM python:3.8
WORKDIR ./

RUN git clone https://github.com/ereiskind/nolcat.git -b {branch_name} ./nolcat/

RUN pip install --no-cache-dir -r nolcat/requirements.txt

WORKDIR ./nolcat/
CMD python -m pytest -s --log-cli-level="{log_level}"{test_script_name}
"""
with open('Dockerfile', 'w') as dockerfile:
    dockerfile.write(dockerfile_text)

#Subsection: Build New Image
subprocess.call("docker build -t nolcat-image --no-cache .")


#Section: Run Tests by Instantiating Container with Tests
subprocess.call("docker run -it --rm nolcat-image")


#Section: Remove Docker Objects
subprocess.call("docker image rm nolcat-image")
os.remove('Dockerfile')