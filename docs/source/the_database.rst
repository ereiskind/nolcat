The Database
############

The database underlying this application is designed to facilitate holistic collections assessment, and has a number of unique and uncommon features designed to support this goal:
* The resources are deduplicated upon loading into the database, so looking up a resource will inherently retrieve all access and turnaway points
* A tool for tracking the collection of usage statistics for each fiscal year is included, and because the database can store data on non-COUNTER compliant resources, it can be used to track the manual collection of usage statistics for those resources requiring it
* Notes can be added to most records, enabling qualitative enhancement of quantitative usage data and the recording of institutional knowledge

Creating the Database
*********************

The database is designed to be loaded with certain data immediately after instantiation.

1. Create the `fiscalYears` Relation with Historical Years
==========================================================
1. Create a copy of "initialize_fiscalYear.csv" in a given folder
2. For all previous fiscal years for which there is usage data, fill out a row in the CSV with the appropriate data (only the `Year`, `Start_Date`, and `End_Date` fields are required)
3. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Fiscal_Year_ID` field

2. Create the `vendors` Relation
================================
1. Create a copy of "initialize_vendors.csv" in the same folder as the copy of "initialize_fiscalYear.csv"
2. In the `Vendor_Name` field, list all the sources which provide or have provided resources--publishers, aggregators, free sources, ect.
3. For all of the above values that have vendor codes in Alma, add those codes to the `Alma_Vendor_Code` field
4. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Vendor_ID` field

3. Create the `statisticsSources` Relation
==========================================
The most important data related to a statistics source--the SUSHI credentials--needs to be kept secure, so the database doesn't provide a place to store them. Instead, methods are provided to collect that data from one of two alternate sources: the Alma ILS API and a secure JSON file.

1. Create a copy of "initialize_statisticsSources.csv" in the same folder as "initialize_fiscalYear.csv" and "initialize_vendors.csv"
2. For each set of securely stored R5 SUSHI credentials, list the resource the the credentials are for in the `Statistics_Source_Name` field, the name of the vendor supplying the resource exactly how it appears in the `vendors` relation in the `REFERENCE Vendor_ID` field, and either the Alma interface name *check if these must be unique across all resources* or the secure JSON file ID for the credentials in the `Statistics_Source_Retrieval_Code` field
3. For all sites with administrator portals that don't provide R5 SUSHI credentials, add their names to the `Statistics_Source_Name` field and the name of the vendor supplying the resource exactly how it appears in the `vendors` relation in the `REFERENCE Vendor_ID` field
4. For all records in `vendors` not already in the CSV, add those values exactly how they appear in the `vendors` relation in the `REFERENCE Vendor_ID` field in one or more records for the domain or grouping under which usage statistics are collected if known or all existing domains if not known with the names going in the `Statistics_Source_Name` field
5. For all records, add a Boolean value to the `Current_Access` field indicating if we currently utilize the given source for resources
6. Copy `=VLOOKUP(B2,initialize_vendors.csv!$A:$C,3,0)` into cell F2, use autofill to copy the formula in all records, then save the results in place as values
7. Delete column B with the field `REFERENCE Vendor_ID`
8. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Statistics_Source_ID` field

4. Create the `annualUsageCollectionTracking` Relation
========================================================
1. Upload the copies of "initialize_fiscalYear.csv", "initialize_vendors.csv", and "initialize_statisticsSources.csv" from their given folder
2. Download "initialize_annualUsageCollectionTracking.csv" from the next page in the web app
3. Save a copy of the CSV and fill it out from existing documentation

   * For statistics sources/interfaces not requiring usage collection, set `Usage_Is_Being_Collected` to false and choose the appropriate `Collection_Status`
   * For statistics sources which had manually collected non-COUNTER compliant usage (including COUNTER R3 and earlier), set `Usage_Is_Being_Collected` and `Manual_Collection_Required` to true, `Is_COUNTER_Compliant` to false, choose the appropriate `Collection_Status`, and if a file with the usage exists, put "true" in `Usage_File_Path`
   * For statistics sources with manually collected COUNTER R4 reports, set `Usage_Is_Being_Collected`, `Manual_Collection_Required`, and `Is_COUNTER_Compliant` to true, choose the appropriate `Collection_Status`, then, if applicable, prepare the R4 reports:

     1. Load each R4 report into OpenRefine, ignoring the first seven (7) lines at the beginning of the file and naming the project `<Statistics_Source_ID>_<report type>_<fiscal year in "yy-yy" format>`

        * Gale reports needed to be copied and pasted as values with the paste special dialog box to work in OpenRefine

     2. Apply the JSON appropriate for the report type
     3. Export the OpenRefine project as an Excel file (this preserves the encoding) into a folder just for these files

   * For statistics sources with R5 SUSHI, set `Usage_Is_Being_Collected` and `Is_COUNTER_Compliant` to true and `Collection_Status` to "Collection not started"
   * For statistics sources not falling into any of the above categories, make selections as appropriate

4. Delete the columns with the `statisticsSources.Statistics_Source_Name` and `fiscalYears.Year` fields
5. Upload the CSV
6. On the next web app page, for all pages where a file with usage is being saved, upload the file/add the path to the file

5. Upload and Dedupe Historical R4 Usage
========================================
1. In the file selector on the next web app page, select all the transformed R4 CSVs
2. On the next web app page, <this is the page for confirming matches--write instructions from this point on when pages and forms are established>

Naming Conventions in the Database and Source Code
**************************************************
For clarity, relations and fields have the same names in the database and the source code. To distinguish between the relations and fields of MySQL and the classes and attributes of SQLAlchemy, different stylistic conventions are used.

* MySQL relation names are written in camelCase; SQLAlchemy class names are written in PascalCase, also called UpperCamelCase.
* MySQL field names are written in Titlecase_with_Underscores; SQLAlchemy attribute names are written in lowercase_with_underscores.

The above styling is used in both the code and the documentation.

Metric Types in R4 and R5
*************************
COUNTER underwent a paradigm shift from R4 to R5, so usage from the two generations of the standard shouldn't be directly compared; all COUNTER data, however, is stored in the same relation. Usage from the two generations is separated by the  different metric types used.

R4 Metric Types
===============
* Successful Title Requests (BR1)
* Successful Section Requests (BR2)
* Access denied: concurrent/simultaneous user license limit exceeded (BR3)
* Access denied: content item not licensed (BR3)

R5 Metric Types
===============
* Searches_Regular
* Searches_Automated
* Searches_Federated
* Searches_Platform
* Total_Item_investigations
* Unique_Item_Investigations
* Unique_Title_Investigations
* Total_Item_Requests
* Unique_Item_Requests
* Unique_Title_Requests
* No_License
* Limit_Exceeded