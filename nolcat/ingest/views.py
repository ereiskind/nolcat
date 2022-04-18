


#Section: Updating Information
#Subsection: Adding Data
#ToDo: Create route to and page for adding non-COUNTER compliant usage
#ToDo: How should non-COUNTER usage be stored? As BLOB in MySQL, as files in the container, as a Docker volume, in some other manner?
#ToDo: Find all resources to which this applies with `SELECT AUCT_Statistics_Source, AUCT_Fiscal_Year FROM annualUsageCollectionTracking WHERE Usage_File_Path='true';`
# render_template('upload-historical-non-COUNTER-data.html')


#ToDo: Create route to and page for creating new records in `vendors`


#ToDo: Create route to and page for creating new records in `statisticsSources`


#Subsection: Updating and Displaying Data
#ToDo: Create route to and page for using methods StatisticsSources.add_access_start_date and StatisticsSources.remove_access_start_date


#ToDo: Create route to and page for `fiscalYears` from which all FiscalYears methods can be run


#ToDo: Create route to and page for `annualUsageCollectionTracking` which uses a variable route to filter just a single fiscal year and displays all the records for that fiscal year