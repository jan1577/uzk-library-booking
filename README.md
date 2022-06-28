# uzk-ibrary-booking

A script to automatically book seats in different Libraries at Cologne University.

## Introduction

The scripts can be used to book seats at various places using chromedriver. There is a limit of 4 to 6 hours per day and per place - for detailed information
check out the websites provided below. As booking is enabled at midnight, booking automatically guarantees a place booked at the time and 
place you want without having to stay up until midnight.

  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/USBO1LS4 - Main Library  
  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOVWL - Economics Library  
  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/HWAEGLS - Human Science Faculty Library  
  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOSOZ - Sociology Library  

## Setup

To run this project, install Chromedriver, available at https://chromedriver.chromium.org/downloads
Make sure to use the version matching your Chrome version (Settings -> About Chrome).
If Chrome is updated, make sure to download the new version of Chromedriver.

### Packages to install:

Install the following package using pip:
```
pip install -U selenium
```
To pass your login data, create a second file "config.py" with your login credentials, wifi SSID and the chromedriver path to import these into the script.
The config.py file should look like this:
```
username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
path = r"C:\Users\...\chromedriver_win32\chromedriver.exe"

wifi_SSID = "YOUR_WIFI_SSID" (to be found at the back of your router)
```

To execute the booking at mitnight, use Windows Task Scheduler or Mac Automater. 
If needed, create and execute the bat-file, as seen in the repository, to start off the script.

## Other Information

To add other libraries, usually only the seat numbers must be changed. The start parameter is always 3 for the first hour that can be booked,
you may want to adjust the end parameter depending on the given limit.

Edit (06/2022):
At the moment, booking a spot in only necessary in the Sociology Library.

