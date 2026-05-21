NoLCAT
######
Noles Collection Assessment Tool (NoLCAT) is a combined database and web application designed to facilitate collections assessment. Its features include

* Lists of all past and present sources of resources, sources of usage statistics, and vendors supplying resources and/or usage statistics
* Separate listings for sources of resources and sources of usage statistics to handle both those instances where multiple resource sources have a single statistics source (e.g. SAGE/CQ Press) and when a resource source has multiple statistics sources for historical purposes (e.g. migrating from Allen Press/Pinnacle Hosting to an independent platform)
* A listing of fiscal years and every statistics source that must be accounted for for that fiscal year, creating a single location for tracking the status of usage statistics collection
* The ability to add notes about the vendors, statistics sources, resource sources, and annual usage statistics collection elements
* A single database relation containing all COUNTER R4 and R5 data
* The ability to ingest COUNTER data through both uploads of Excel files with tabular layouts and SUSHI
* The ability to store files containing non-COUNTER compliant usage data for later download
* A wizard for the initial data entry of the vendors, statistics sources, resource sources, historical usage collection tracking information, and historical usage

NoLCAT Simplification
*********************
At this time, the environment is unable to support the matching and deduplication needed for the distinct identification of all the resources included in the COUNTER reports, which enabled most of NoLCAT's more advanced features. As a result, COUNTER data from uploaded tabular R4 reports, uploaded tabular R5 reports, and R5 SUSHI calls will be loaded into a single relation without further processing.

About This Repo
***************

The Hosting Instance
====================
NoLCAT is a containerized application: it exists within a Docker container which is built on an AWS EC2 instance. The host instance, a Linux-based t3.2xlarge, contains files with Docker build instructions and private information that cannot be committed to GitHub.

Working with the Web Server
---------------------------
NoLCAT is a web application, meaning the program is accessed through the internet and controlled through a web browser. It uses Flask as the web framework, Gunicorn as the WSGI (web service gateway interface), and nginx as the web server. Gunicorn and nginx are added to the instance as part of the Docker build process and connect to the overall codebase through the "nolcat/wsgi.py" file, which contains an instantiated Flask object.
The public IP address used to access the web app is ultimately that of the instance.

Working with MySQL
------------------
The instance can access the external MySQL database server, which serves as the RDBMS for NoLCAT. The MySQL command line can be accessed from the instance command line.

Encodings and File Types
========================
E-resources involves working with scholarly content in a wide variety of languages, requiring the use of Unicode to accommodate multiple alphabets/character sets. NoLCAT uses the UTF-8 encoding for a variety of reasons, including its ubiquity, backwards compatibility, and inclusion as a requirement of the COUNTER 5 Code of Practice. Since Microsoft Excel can explicitly save files as CSV files with an UTF-8 encoding, NoLCAT will use the CSV format for plain text file uploads and downloads.

File Paths
==========
NoLCAT defaults to using absolute file paths created through the pathlib module. The constant `nolcat.app.TOP_NOLCAT_DIRECTORY` creates an absolute path to the repo's outer `nolcat` folder with `pathlib.Path(__file__)` and bases that path upon the file in which the code is located, rather than the more common `pathlib.Path.cwd()`, which returns the folder from which the code is being run. An absolute path to any file or folder in the repo can be created by calling `nolcat.app.TOP_NOLCAT_DIRECTORY` and following it with the remaining folder and file names, combined either within a `Path()` constructor or through the pathlib slash operator (`/`).