COUNTER and SUSHI
#################

The COUNTER Standard
********************

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