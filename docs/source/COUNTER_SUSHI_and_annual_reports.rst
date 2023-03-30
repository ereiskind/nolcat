COUNTER, SUSHI, and Annual Reports
##################################

The COUNTER Standard
********************

Metric Types in R4 and R5
=========================
COUNTER underwent a paradigm shift from R4 to R5, so usage from the two generations of the standard shouldn't be directly compared; all COUNTER data, however, is stored in the same relation. Usage from the two generations is separated by the different metric types used. Per an extension as defined in section 11.4 of the Release 5.0 Code of Practice, custom metrics are allowed in customizable and custom reports, but these metrics aren't saved in NoLCAT.

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

Elements in R4 and R5
=====================
COUNTER refers to the fields in their reports as "elements." Not all elements are used in all reports. The names for the fields differ slightly from R4 to R5; when the difference is great enough that the match may be unclear, the R4 field name is added in quotation marks after the name of the report it's found in.

* Database (DB1, DB2, DR) -- Part of `resource_name` in NoLCAT
* Title (BR1, BR2, BR3, TR) -- Part of `resource_name` in NoLCAT
* Item (IR) -- Part of `resource_name` in NoLCAT
* Journal (JR1, JR2) -- Part of `resource_name` in NoLCAT
* Collection (MR1) -- Part of `resource_name` in NoLCAT
* Publisher (JR1, JR2, DB1, DB2, PR1, BR1, BR2, BR3, MR1 "Content Provider", DR, TR, IR)
* Publisher_ID (DR, TR, IR)
* Platform (JR1, JR2, DB1, DB2, PR1, BR1, BR2, BR3, MR1, PR, DR, TR, IR)
* Authors (IR)
* Publication_Date (IR)
* Article_Version (IR)
* DOI (JR1, JR2, BR1, BR2, BR3, TR, IR)
* Proprietary_ID (JR1, JR2, BR1, BR2, BR3, DR, TR, IR)
* ISBN (BR1, BR2, BR3, TR, IR)
* Print_ISSN (JR1, JR2, TR, IR)
* Online_ISSN (JR1, JR2, BR1 "ISSN", BR2 "ISSN", BR3 "ISSN", TR, IR)
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
* Metric_Type (JR2 "Access Denied Category", DB1 "User Activity", DB2 "Access Denied Category", PR1 "User Activity", BR3 "Access Denied Category", PR, DR, TR, IR)
* Reporting_Period_Total (JR1, JR2, DB1, DB2, PR1, BR1, BR2, BR3, MR1, PR, DR, TR, IR) -- Not preserved in NoLCAT
* Reporting Period HTML (JR1) -- Not preserved in NoLCAT
* Reporting Period PDF (JR1) -- Not preserved in NoLCAT

COUNTER 5.1 Proposals
=====================
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

Annual Usage Statistics
***********************
Each year, ARL and ACRL/IPEDS request data from libraries, including e-resource usage statistics, for the fiscal year. NoLCAT both compiles the requested information, which is described below, and saves it in the ``fiscalYears`` relation. That relation's class contains methods to calculate all of the metrics described below.

ACRL/IPEDS 60b. Initial Circulation: Digital/Electronic
=======================================================
"Report usage of digital/electronic titles whether viewed, downloaded, or streamed. Include usage for e-books, e-serials, and e-media titles even if they were purchased as part of a collection or database." The instructions say to use TR_B1 "unique title requests" for e-books and IR_M1 "total_item_requests" for e-media.

ACRL/IPEDS 63. E-Serials Usage: Digital/Electronic
==================================================
"Report usage of e-serial titles whether viewed, downloaded, or streamed. Include usage for e-serial titles only, even if the title was purchased as part of a database. Viewing a document is defined as having the full text of a digital document or electronic resource downloaded." The instructions say to use TR_J1 "unique item requests."

ARL 18. Number of successful full-text article requests (journals)
==================================================================
"The COUNTER 5 report that corresponds to Question 18 is TR_J3 Journal Usage by Access Type. The metric from this COUNTER 5 report is Unique Item Requests. In a footnote, please include the types of resources for which you are reporting data."

ARL 19. Number of regular searches (databases)
==============================================
"The COUNTER 5 report that corresponds to Question 19 is DR_D1 Database Search and Item Usage. The metric from this COUNTER 5 report is Searches_Regular....In a footnote, please include the types of resources for which you are reporting data. Please be sure to indicate whether you used DR_D1 or PR_P1. It is recommended that ONLY data that follow the COUNTER definitions be reported."

ARL 20. Number of federated searches (databases)
================================================
"The COUNTER 5 report that corresponds to Question 20 is DR_D1 Searches_Federated. Metric options include "Searches_Federated",...The goal is to capture the totality of federated searches. In a footnote, please include the types of resources for which you are reporting data, and please specify the COUNTER 5 metric used to report this value. It is recommended that ONLY data that follow the COUNTER definitions be reported."