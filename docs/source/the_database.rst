The Database
############

The database underlying this application is designed to facilitate holistic collections assessment, and has a number of unique and uncommon features designed to support this goal:
* The resources are deduplicated upon loading into the database, so looking up a resource will inherently retrieve all access and turnaway points
* A tool for tracking the collection of usage statistics for each fiscal year is included, and because the database can store data on non-COUNTER compliant resources, it can be used to track the manual collection of usage statistics for those resources requiring it
* Notes can be added to most records, enabling qualitative enhancement of quantitative usage data and the recording of institutional knowledge

Creating the Database
*********************

The database is designed to be loaded with the institution's vendors, sources of usage statistics, platforms providing resources, historical information about usage statistics collections in previous years, qualitative notes about the preceding data, historical COUNTER R4 reports, and a method to get institutional SUSHI credentials immediately after instantiation. The ``initialization`` blueprint serves as a wizard for uploading all of the above data to the database; the instructions for the wizard are on the pages of that blueprint, where they are needed to use the wizard, but not repeated here.