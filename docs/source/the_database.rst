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
1. Create a copy of "initialize_fiscalYear.csv"
2. For all previous fiscal years for which there is usage data, fill out a row in the CSV with the appropriate data (only the `Year`, `Start_Date`, and `End_Date` fields are required)
3. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Fiscal_Year_ID` field

2. Create the `vendors` Relation
================================
1. Create a copy of "initialize_vendors.csv"
2. In the `Vendor_Name` field, list all the sources which provide or have provided resources--publishers, aggregators, free sources, ect.
3. For all of the above values that have vendor codes in Alma, add those codes to the `Alma_Vendor_Code` field
4. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Vendor_ID` field

3. Create the `statisticsSources` Relation
==========================================
The most important data related to a statistics source--the SUSHI credentials--needs to be kept secure, so the database doesn't provide a place to store them. Instead, methods are provided to collect that data from one of two alternate sources: the Alma ILS API and a secure JSON file.

1. Create a copy of "initialize_statisticsSources.csv"
2. For each set of securely stored R5 SUSHI credentials, list the resource the the credentials are for in the `Statistics_Source_Name` field, the name of the vendor supplying the resource exactly how it appears in the `vendors` relation in the `REFERENCE Vendor_ID` field, and either the Alma interface name *check if these must be unique across all resources* or the secure JSON file ID for the credentials in the `Statistics_Source_Retrieval_Code` field
3. For all sites with administrator portals that don't provide R5 SUSHI credentials, add their names to the `Statistics_Source_Name` field and the name of the vendor supplying the resource exactly how it appears in the `vendors` relation in the `REFERENCE Vendor_ID` field
4. For all records in `vendors` not already in the CSV, add those values exactly how they appear in the `vendors` relation in the `REFERENCE Vendor_ID` field in one or more records for the domain or grouping under which usage statistics are collected if known or all existing domains if not known with the names going in the `Statistics_Source_Name` field
5. For all records, add a Boolean value to the `Current_Access` field indicating if we currently utilize the given source for resources
6. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Statistics_Source_ID` field

?. Initialize the Relations via CSV Upload
==========================================
1. Ensure all filled-out CSV copies are in the same folder
2. Copy the following `vlookup` functions into the designated cells, use autofill to copy the formula in all functions, then save the results in place as values

   * initialize_statisticsSources, cell F2: `=VLOOKUP(B2,initialize_vendors.csv!$A:$C,3,0)`

3. Delete the following columns:

   * initialize_statisticsSources: `REFERENCE Vendor_ID`

4. Upload <CSVs with relation data>

Naming Conventions in the Database and Source Code
**************************************************
For clarity, relations and fields have the same names in the database and the source code. To distinguish between the relations and fields of MySQL and the classes and attributes of SQLAlchemy, different stylistic conventions are used.

* MySQL relation names are written in camelCase; SQLAlchemy class names are written in PascalCase, also called UpperCamelCase.
* MySQL field names are written in Titlecase_with_Underscores; SQLAlchemy attribute names are written in lowercase_with_underscores.

The above styling is used in both the code and the documentation.