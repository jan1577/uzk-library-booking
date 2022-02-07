
import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def booking(url, first, last, start, end):
    login(url)
    # first/last: first/last seat to check, start/end: start/end time
    booked = False
    # driver = login(username, password, url)
    # book a space on most recent day || lesesaal 4 9-15, vwl bib 9-13, hwa 10-14
    # check all seats
    for i in range(first, last):
        bookable = True
        # check if seat booked somewhere between 9 and 3, every hour is own slot
        for j in range(start, end):
            slot = "/html/body/div[1]/div[3]/div/div/div/div[8]/div/div/div[2]/table/tbody/tr[" + str(j) + "]/td[" + str(i) + "]"
            if driver.find_element(By.XPATH, slot).get_attribute("title") != "buchbar":
                bookable = False

        if bookable: # all slots available for one seat -> book that seat
            # first hour to book
            #                                                   day || 1 = current day, 8 = last day
            #                                                                                     timeslot || 3 = 9AM-10AM, 8= 2PM-3MP
            #                                                                                                  table_id || last number(s) of table id
            xpath_start = "/html/body/div[1]/div[3]/div/div/div/div[8]/div/div/div[2]/table/tbody/tr[" + str(start) + "]/td[" + str(i) + "]"
            # last hour to book (2-3 pm)
            xpath_end = "/html/body/div[1]/div[3]/div/div/div/div[8]/div/div/div[2]/table/tbody/tr[" + str(end - 1) + "]/td[" + str(i) + "]"
            # select first hour + last hour to book rowspan from first to last hour
            driver.find_element(By.XPATH, xpath_start).click()
            time.sleep(3)
            driver.find_element(By.XPATH, xpath_end).click()
            try:
                message = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert') and @data-notify='container']//span[@data-notify='message']"))).get_attribute("innerHTML")
                if "Max. Buchung" in message:
                    print("Max. Buchungszeit! Keine Buchung möglich.")
                    break
                elif "Buchung war erfolgreich." in message:
                    print("Booking confirmed! Seat {}".format(i))
                    print(datetime.datetime.now())
                    booked = True
                    break
                else:
                    print("Seat {} could not be booked. {}".format(i, message))
            except:
                try:
                    driver.find_element(By.ID, "btn-cancel").click()
                    time.sleep(3)
                    print("Seat {} Canceled.".format(i))
                    # can't recognize if booking for day exist which is not maximum booking time
                    # -> will cancel and try additional seats
                    # body > div.container-fluid.userpanel > div:nth-child(3) > div > div > div >
                    # div:nth-child(8) > div > div > div.daily-container-cell > table > tbody > tr:nth-child(8) > td.slot.booked.slotowner.normal
                    # -> use slotowner to verify if booking not successfull
                except:
                    print("Seat {} could not be booked [except].".format(i))
        else:
            print("Seat {} not available".format(i))
    return booked


def login(url):
    # opening the website in chrome
    driver.get(url)
    # find username field and insert username
    driver.find_element(By.NAME, "uid").send_keys(username)
    # find the password and insert password
    driver.find_element(By.NAME, "password").send_keys(password)
    # click on submit
    driver.find_element(By.ID, "btn-login").click()
    time.sleep(5)


if __name__ == '__main__':
    # login credentials // website
    username = None
    password = None
    # urls
    url_l4 = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/USBO1LS4"
    url_vwl = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOVWL"
    url_hwa = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/HWAEGLS"
    # path chromedriver exe file
    path = None

    chrome_options = Options()
    # initialising driver
    driver = webdriver.Chrome(path, options=chrome_options)
    driver.maximize_window()

    print(datetime.datetime.now())
    print("Lesesaal 4:")
    if booking(url_l4, 3, 51, 3, 9) == False:
        print("\nVWL:")
        if booking(url_vwl, 5, 25, 3, 7) == False:
            # vwl: 5, 7, 8?, 9?
            print("\nHWA:")
            if booking(url_hwa, 21, 36, 3, 7) == False:
                print("\nBooking not possible.")
        else:
            if booking(url_hwa, 21, 36, 8, 11) == True:
                print("Additional Seat booked at HWA.")
            else:
                print("Could not book additional seat.")
    driver.quit()
