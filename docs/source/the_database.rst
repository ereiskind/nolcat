The Database
############

The database underlying this application is designed to facilitate holistic collections assessment, and has a number of unique and uncommon features designed to support this goal:
* The resources are deduplicated upon loading into the database, so looking up a resource will inherently retrieve all access and turnaway points
* A tool for tracking the collection of usage statistics for each fiscal year is included, and because the database can store data on non-COUNTER compliant resources, it can be used to track the manual collection of usage statistics for those resources requiring it
* Notes can be added to most records, enabling qualitative enhancement of quantitative usage data and the recording of institutional knowledge

Creating the Database
*********************

The database is designed to be loaded with certain data immediately after instantiation.

1. Create the ``fiscalYears`` Relation with Historical Years
============================================================
1. Create a copy of "initialize_fiscalYear.csv".
2. For all previous fiscal years for which there is usage data, fill out a row in the CSV with the appropriate data (only the ``Year``, ``Start_Date``, and ``End_Date`` fields are required).
3. Add sequential integer numbering starting at ``1`` and incrementing by one to all records in the ``Fiscal_Year_ID`` field.

2. Create the ``vendors`` and ``vendorNotes`` Relations
=======================================================
1. Create a copy of "initialize_vendors.csv".
2. In the ``Vendor_Name`` field, list all the organizations which provide or have provided resources--publishers, aggregators, free sources, ect.
3. For all of the above values that have vendor codes in Alma, add those codes to the ``Alma_Vendor_Code`` field.
4. Add sequential integer numbering starting at ``1`` and incrementing by one to all records in the ``Vendor_ID`` field.
5. Create a copy of "initialize_vendorNotes.csv".
6. For every note on a vendor that needs to be added, in the ``REFERENCE Vendor_ID`` field, put the name of the vendor exactly how it appears in the ``vendors`` relation.
7. For all records, fill out the ``Note``, ``Written_By``, and ``Date_Written`` fields.
8. Copy ``=VLOOKUP(A2,initialize_vendors.csv!$A:$C,3,0)`` into cell E2, use autofill to copy the formula in all records, then save the results in place as values.
9. Delete column A with the field ``REFERENCE Vendor_ID``.

3. Create the ``statisticsSources``, ``statisticsSourceNotes``, ``resourceSources``, ``resourceSourceNotes``, and ``statisticsResourceSources`` Relations
=========================================================================================================================================================
In handling usage statistics for electronic resources, there are two information sources to consider--the resource source, also called the platform and often equivalent to a HTTP domain, which is the source of the e-resource content, and the statistics source, where the usage statistics come from. There's a complex, many-to-many relationship between these two sources with situations/use cases that include

* a single statistics source providing usage for multiple resource sources from a single vendor (e.g. Oxford),
* a single statistics source providing usage for multiple resource sources from different vendors (e.g. HighWire),
* multiple resource sources being moved to a single statistics source (e.g. Peterson's Prep),
* resource sources that shared a statistics source being split apart on the backend (e.g. UN/OECD iLibrary),
* a new publisher leaving a resource source as is but moving the usage to the publisher's existing statistics source (e.g. Nature), and
* a hosting service change that doesn't include any changes to the resource source UI (e.g. Company of Biologists).

To handle this complexity, three relations in a junction table-like relationship are employed: the ``resourceSources`` relation contains records for sources of e-resource content, including if that content is still available to patrons; the ``statisticsSources`` relation contains records for all the different usage statistics sources and a field for linking to externally stored SUSHI R5 credentials; and the ``statisticsResourceSources`` relation is a junction table for the other two relations with an additional field to indicate if the given statistics source currently provides usage for the given resource source. This model can integrate with other e-resource management tools through the ``resourceSources`` relation and track changes to system backends that don't cause frontend changes.

1. Create copies of "initialize_resourceSources.csv", "initialize_statisticsSources.csv", "initialize_resourceSourceNotes.csv", and "initialize_statisticsSourceNotes.csv".
2. Create a spreadsheet with all the field names from the resourceSources and statisticsSources CSVs, replacing all the ones that include "Vendor_ID" with ``Resource Vendor`` and ``Stats Vendor`` and adding ``Current_Statistics_Source``.
3. Create the list of statistics sources and resource sources pairings in the above spreadsheet, adding to the notes CSVs whenever appropriate. This is a comprehensive listing, so the best methods to use will depend on how much data is already gathered and what form it is in. Below are some ideas that form a potential procedure.

   * For all securely stored R5 SUSHI credentials, give the credentials a name in the ``Statistics_Source_Name`` field and put either the Alma interface name or the secure JSON file ID for the credentials in the ``Statistics_Source_Retrieval_Code`` field, then fill in the ``Resource Vendor`` field, the fields for the resource source, and the ``Current_Statistics_Source`` field; repeat for each resource source the SUSHI credentials serve, using the same ``Statistics_Source_ID`` for all the records.
   * For all the administrator portals not providing SUSHI, give the credentials a name in the ``Statistics_Source_Name`` field, then fill in the ``Stats Vendor`` field, the fields for the resource source, and the ``Current_Statistics_Source`` field; repeat for each resource source which has its usage provided by the given administrator portal, using the same ``Statistics_Source_ID`` for all the records.
   * For resource sources that have changed statistics sources at any point since the beginning of the desired collection period, fill out all the resource source fields identically in as many records as there are statistics sources, then fill each record's  ``Statistics_Source_Name`` and ``Stats Vendor`` field for the different statistics sources, putting ``TRUE`` in ``Current_Statistics_Source`` for the current statistics source for the given resource source and filling that field in with ``FALSE`` for all other records.
   * For all vendors in the list of vendors not connected to a statistics source or resource source, determine what statistics source(s) and/or resource source(s) come from the vendor and add the relevant record(s).

4. If numbers weren't added to ``Statistics_Source_ID`` and ``Resource_Source_ID`` in all records as the spreadsheet was being filled in, finish adding sequential numbering to those fields (any records that have duplicates or a note should already have an ID number).
5. Copy the values in the spreadsheet columns into the columns with the same field labels in "initialize_resourceSources.csv" and "initialize_statisticsSources.csv", including copying the ``Resource Vendor`` and ``Stats Vendor`` columns into the ``REFERENCE Vendor_ID`` fields in the appropriate CSV.
6. Remove duplicate records in "initialize_resourceSources.csv" and "initialize_statisticsSources.csv", then double check that there are no duplicated values in ``Resource_Source_ID`` or ``Statistics_Source_ID``; if there are duplicates, return to the spreadsheet and determine where the error is, then redo steps five and six.
7. In "initialize_resourceSources.csv", copy ``=VLOOKUP(D2,initialize_vendors.csv!$A:$C,3,0)`` into cell E2, use autofill to copy the formula in all records, save the results in place as values, and delete column D (field ``REFERENCE Vendor_ID``).
8. In "initialize_statisticsSources.csv", copy ``=VLOOKUP(C2,initialize_vendors.csv!$A:$C,3,0)`` into cell D2, use autofill to copy the formula in all records, save the results in place as values, and delete column C (field ``REFERENCE Vendor_ID``).
9. Create a new CSV file and name it "initialize_statisticsResourceSources.csv".
10. Copy the ``Statistics_Source_ID``, ``Resource_Source_ID``, and ``Current_Statistics_Source`` columns from the spreadsheet into "initialize_statisticsResourceSources.csv".
11. In "initialize_statisticsResourceSources.csv", change ``Statistics_Source_ID`` to ``SRS_Statistics_Source`` and ``Resource_Source_ID`` to ``SRS_Resource_Source``.

4. Create the `annualUsageCollectionTracking` Relation
========================================================
1. Upload the copies of "initialize_fiscalYear.csv", "initialize_vendors.csv", "initialize_vendorNotes.csv", "initialize_statisticsSources.csv", "initialize_statisticsSourceNotes.csv", "initialize_statisticsResourceSources.csv", "initialize_resourceSources.csv", and "initialize_resourceSourceNotes.csv".
2. Download "initialize_annualUsageCollectionTracking.csv" from the next page in the web app
3. Save a copy of the CSV and fill it out from existing documentation

   * For statistics sources/interfaces not requiring usage collection, set ``Usage_Is_Being_Collected`` to false and choose the appropriate ``Collection_Status``
   * For statistics sources which had manually collected non-COUNTER compliant usage (including COUNTER R3 and earlier), set ``Usage_Is_Being_Collected`` and ``Manual_Collection_Required`` to true, ``Is_COUNTER_Compliant`` to false, choose the appropriate ``Collection_Status``, and if a file with the usage exists, put "true" in ``Usage_File_Path``
   * For statistics sources with manually collected COUNTER R4 reports, set ``Usage_Is_Being_Collected``, ``Manual_Collection_Required``, and ``Is_COUNTER_Compliant`` to true, choose the appropriate ``Collection_Status``, then prepare the R4 reports:

     1. Load each R4 report into OpenRefine, ignoring the first seven (7) lines at the beginning of the file and naming the project ``<Statistics_Source_ID>_<report type>_<ending year of fiscal year in "yyyy" format>``

        * Gale reports needed to be copied and pasted as values with the paste special dialog box to work in OpenRefine
        * iG Press/BEP reports have multiple ISBNs and ISSNs in the fields for those values

     2. Apply the JSON appropriate for the report type
     3. Export the OpenRefine project as a CSV file into a folder just for these files

   * For statistics sources with R5 SUSHI, set ``Usage_Is_Being_Collected`` to true, ``Manual_Collection_Required`` to false, and ``Collection_Status`` to "Collection not started"
   * For statistics sources not falling into any of the above categories, make selections as appropriate

4. Delete the columns with the ``statisticsSources.Statistics_Source_Name`` and ``fiscalYears.Year`` fields
5. Upload the CSV

5. Upload and Dedupe Historical R4 Usage
========================================
Initializing the database with the historical R4 data not only ensures that all the historical COUNTER data is preserved, it also provides a foundation for the deduplication of resources collected via SUSHI.

1. In the file selector on the next web app page, select all the transformed R4 CSVs; if all the files are in a single folder and that folder contains no other items, navigate to that folder, then use ``Ctrl + a`` to select all the files in the folder
2. On the next web app page, <this is the page for confirming matches--write instructions from this point on when pages and forms are established>

6. Upload Historical R5 Usage
=============================
1. Run ``FiscalYears.collect_fiscal_year_usage`` for all the fiscal years including and after calendar year 2019