The Database
############

The database underlying this application is designed to facilitate holistic collections assessment, and has a number of unique and uncommon features designed to support this goal:
* The resources are deduplicated upon loading into the database, so looking up a resource will inherently retrieve all access and turnaway points
* A tool for tracking the collection of usage statistics for each fiscal year is included, and because the database can store data on non-COUNTER compliant resources, it can be used to track the manual collection of usage statistics for those resources requiring it
* Notes can be added to most records, enabling qualitative enhancement of quantitative usage data and the recording of institutional knowledge

Creating the Database
*********************

The database is designed to be loaded with certain data immediately after instantiation.

1. Initialize the Fiscal_Year Relation with Historical Years
============================================================
1. Create a copy of "initialize_fiscalYear.csv"
2. For all previous fiscal years for which there is usage data, fill out a row in the CSV with the appropriate data (only the `Year`, `Start_Date`, and `End_Date` fields are required)
3. Upload the CSV

Naming Conventions in the Database and Source Code
**************************************************
For clarity, relations and fields have the same names in the database and the source code. To distinguish between the relations and fields of MySQL and the classes and attributes of SQLAlchemy, different stylistic conventions are used.

* MySQL relation names are written in camelCase; SQLAlchemy class names are written in PascalCase, also called UpperCamelCase.
* MySQL field names are written in Titlecase_with_Underscores; SQLAlchemy attribute names are written in lowercase_with_underscores.

The above styling is used in both the code and the documentation.