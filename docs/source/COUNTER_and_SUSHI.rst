COUNTER and SUSHI
#################

The COUNTER Standard
********************

Metric Types in R4 and R5
=========================

COUNTER underwent a paradigm shift from R4 to R5, so usage from the two generations of the standard shouldn't be directly compared; all COUNTER data, however, is stored in the same relation. Usage from the two generations is separated by the  different metric types used.

R4 Metric Types
---------------
* Successful Title Requests (BR1)
* Successful Section Requests (BR2)
* Access denied: concurrent/simultaneous user license limit exceeded (BR3, DB2, JR2)
* Access denied: content item not licensed (BR3, DB2, JR2)
* Regular Searches (BR5, DB1, PR1)
* Searches-federated and automated (BR5, DB1, PR1)
* Result Clicks (DB1, PR1)
* Record Views (DB1, PR1)
* Successful Full-text Article Requests (JR1)
* Successful Content Unit Requests (MR1)

R5 Metric Types
---------------
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

Elements in R5
==============

COUNTER refers to the fields in their reports as "elements." Not all elements are used in all reports, and in some cases, different elements from different reports have been consolidated into a single field in NoLCAT.

* Database (DR) -- Part of `resource_name` in NoLCAT
* Title (TR) -- Part of `resource_name` in NoLCAT
* Item (IR) -- Part of `resource_name` in NoLCAT
* Publisher (DR, TR, IR)
* Publisher_ID (DR, TR, IR)
* Platform (PR, DR, TR, IR)
* Authors (IR)
* Publication_Date (IR)
* Article_Version (IR)
* DOI (TR, IR)
* Proprietary_ID (DR, TR, IR)
* ISBN (TR, IR)
* Print_ISSN (TR, IR)
* Online_ISSN (TR, IR)
* URI (TR, IR)
* Parent_Title (IR)
* Parent_Authors (IR)
* Parent_Publication_Date (IR)
* Parent_Article_Version (IR)
* Parent_Data_Type (IR)
* Parent_DOI (IR)
* Parent_Proprietary_ID (IR)
* Parent_ISBN (IR)
* Parent_Print_ISSN (IR)
* Parent_Online_ISSN (IR)
* Parent_URI (IR)
* Component_Title (IR) -- Not preserved in NoLCAT
* Component_Authors (IR) -- Not preserved in NoLCAT
* Component_Publication_Date (IR) -- Not preserved in NoLCAT
* Component_Data_Type (IR) -- Not preserved in NoLCAT
* Component_DOI (IR) -- Not preserved in NoLCAT
* Component_Proprietary_ID (IR) -- Not preserved in NoLCAT
* Component_ISBN (IR) -- Not preserved in NoLCAT
* Component_Print_ISSN (IR) -- Not preserved in NoLCAT
* Component_Online_ISSN (IR) -- Not preserved in NoLCAT
* Component_URI (IR) -- Not preserved in NoLCAT
* Data_Type (PR, DR, TR, IR)
* Section_Type (TR)
* YOP (TR, IR)
* Access_Type (TR, IR)
* Access_Method (PR, DR, TR, IR)
* Metric_Type (PR, DR, TR, IR)
* Reporting_Period_Total (PR, DR, TR, IR) -- Not preserved in NoLCAT

COUNTER 5.1 Proposals
*********************

* Many changes are designed to improve OA reporting
* Item is the unit of reporting

  * For books, chapter is the unit of reporting; full book download is an item request per chapter of book--item counts will increase but title metrics remain constant
  * `Section_Type` to be removed

* `Data_Types` fixed vocab list increasing for improved granularity (proposal has detailed descriptions)
* `Access_Type` changing

  * Access is the related to the access on the platform where it occurs
  * Access refers to the full text
  * `Open` means explicitly OA; `Free_To_Read` means free but not explicitly OA--deliberately avoiding models of OA controlled by other orgs
  * `Controlled` includes content that has no financial access requirements but requires registration to read

* **JSON structure may be changing**
* SUSHI

  * Dropping IP-based authentication
  * `/status` won't require credentials
  * `/reports` will include information on dates for which SUSHI cam provide data
  * Planning to add release number in URL path

* Optional global reports provide total usage for content--provide usage for OA sponsorships