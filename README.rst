NoLCAT
######

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

To-Do List
**********
Last updated: 2023-01-24

TaDS Assistance Required
========================

To Make NoLCAT Viable with Command Line SQL
===========================================

To Complete NoLCAT
==================
