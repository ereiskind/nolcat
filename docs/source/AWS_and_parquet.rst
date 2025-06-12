Using AWS and Parquet
#####################
MySQL and the Flask server are struggling to store and process multiple years of COUNTER data. To solve this issue, COUNTER data is being saved in Parquet files and much of the processing power of NoLCAT is being moved into AWS.

AWS
***

AWS Products
============

Glue
----
Glue is an ETL service with jobs that can work like programming functions. The data download and processing code should be saved here.

* Jobs are written as coding scripts, which are saved to a designated folder in S3; the IAM role to write the scripts needs to have edit permission for the given S3 location
* Complete job download is a JSON, featuring configs and the complete code using newline characters
* Jobs can be pushed to and pulled from GitHub repos with the creation of a personal access token 

  * Instructions at https://github.com/settings/personal-access-tokens
  * Tokens aren't saved--they must be reentered at every session or there's an error with the pull request
  * GitHub tokens can't be viewed again after initial issuing, but reissued tokens will work
  * Every time data is pulled from the repo, the "Load common analytics libraries" option in the "Job details" tab is selected again and must be deselected before saving

* Be aware of the "Data processing units" setting under "Job details"

  * For testing, use 1/16 DPU (0.5 vCPU, 1 GiB Memory)
  * For production, use 1 DPU (4 vCPU, 16 GiB Memory)

* Data I/O

  * Data comes into jobs in JSON format, generally via step functions
  * ``awsglue.utils.getResolvedOptions(sys.argv, ["input_key"])`` is used to retrieve the data from the JSON

    * ``input_key`` represents the variable names, which are the key values in the input JSON
    * The function returns a list

  * Output JSON, which can go to step functions, is metadata; code is designed for ETL and *must* contain a load to storage, frequently S3
  * Functions and classes in other Glue jobs can be called, but the S3 URI(s) of the other job(s) must be added to the ``pythonPath``, ``referencedPath``, and ``additionalPythonModules`` config fields in a comma-delineated list; as above, values cannot be returned through code

* Testing

  * "Actions" > "Run with parameters" runs the code in the job with the given parameters as input
  * In the run parameters dialog, select "Continuous logging" under "Monitoring options" and add the parameters as key-value pairs under "Job parameters" 

* "Connectors" connect jobs to other data sources
* Multiple jobs can run simultaneously

S3
---
Simple Storage Service (S3) stores all types of data.

* S3 files are stored in buckets
* S3 buckets don't have folders, but file names contain segments separated by slashes; these can be managed similarly to file paths

Step Functions
--------------
Step Functions create workflows among other AWS services.

* Step Functions objects/workflows are called state machines; the individual steps are called states
* State machine triggers are ???
* State machine output is determined by the last step in the state machine; this can be email via SNS, an API call, ect.
* Testing

  * 
  * To test the AWS Step Function, click the Execute button and paste in the parameters that will be sent into the Glue ETL Job as JSON. An example of this can be found in the step-functions-test-parameters.json attached file.
  * When a test starts, the state machine's logging output is brought up; links to logging for any states that have it are included in the text log

* State machine construction define input parameters and imported libraries for Glue jobs
#######

* 
* Start triggered by Flask sending input, which is taken in as JSON




#######

SNS
---
Simple Notification Service (SNS) sends messages from applications to other applications and people.

* SNS is organized by topics, which define the message being sent, and subscriptions, which are nested under topics and define where the message is sent

Moving Data to AWS
==================

1. Create S3 Locations
----------------------

2. Create Glue Jobs
-------------------

3. Create SNS Topic
-------------------

Parquet
*******
Parquet is a columnar data format designed to handle large volumes of data. Unlike relational databases, parquet performance doesn't degrade as the amount of data increases, making it a much more sustainable way to store COUNTER data.

Parquet Files
=============
Parquet files inherently contain schema/structure metadata in addition to the data (unlike relational databases, where a `CREATE TABLE` statement has the schema metadata and `INSERT INTO` statement(s) contain the data). As a result, parquet data can be read from and written to files directly, without an intermediary program like a RDBMS.