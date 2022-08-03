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

The SUSHI API
*************

.. _using-selenium:
Using Selenium
==============
Some vendors provide SUSHI reports as JSON files that immediately begin downloading when the API call is made, so the data cannot be collected via any HTTP-related methods. For these resources, Selenium, with allows for automated interactions with web browsers, is employed. Using Selenium requires the installation of a driver to interface with the web browser (Chrome in this instance). To install the driver, ensure that Chrome is on the computer, then:

1. Check the version of Chrome by going to Settings > About Chrome
2. Go to https://sites.google.com/chromium.org/driver/downloads and select the appropriate ChromeDriver for the Chrome version
3. Download the zip file matching the operating system
4. Unzip the file into a location in PATH

.. The driver installation procedure may need to be done in the container, not on the host computer

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
