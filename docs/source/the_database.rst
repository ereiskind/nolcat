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
2. In the `Vendor_Name` field, list all the sources which provide resources--publishers, aggregators, free sources, ect.
3. For all of the above values that have vendor codes in Alma, add those codes to the `Alma_Vendor_Code` field
4. Add sequential integer numbering starting at `1` and incrementing by one to all records in the `Vendor_ID` field

?. Initialize the Relations via CSV Upload
==========================================
1. <perform vlookups to get foreign keys>
2. <save FK vlookup results as values>
3. Delete the following columns:

   * <columns with the data referenced to create FK/represented by FK in RBDMS>

4. Upload <CSVs with relation data>

Naming Conventions in the Database and Source Code
**************************************************
For clarity, relations and fields have the same names in the database and the source code. To distinguish between the relations and fields of MySQL and the classes and attributes of SQLAlchemy, different stylistic conventions are used.

* MySQL relation names are written in camelCase; SQLAlchemy class names are written in PascalCase, also called UpperCamelCase.
* MySQL field names are written in Titlecase_with_Underscores; SQLAlchemy attribute names are written in lowercase_with_underscores.

The above styling is used in both the code and the documentation.