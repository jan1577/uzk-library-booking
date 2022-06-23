# Library_Booking

This script can be used to automatically book seats at four different spots in the Library of Cologne University.
To add other places, some variables within the script may need to be changed (seat numbers, times). There is a maximum of four to six hours per day per spot. 

  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/USBO1LS4
  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOVWL
  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/HWAEGLS
  https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOSOZ

To execute the script, install Chromedriver, available at https://chromedriver.chromium.org/downloads

For logging in, create a second file "config.py" with your login credentials, wifi SSID and the chromedriver path to import these into the script.

To execute the booking at mitnight, use Windows Task Scheduler or Mac Automater. If needed, create and execute the bat-file, as seen in the repository, to start off the script.

