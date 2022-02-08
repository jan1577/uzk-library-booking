import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def booking(url, day, first_seat, last_seat, start, end):
    # first/last: first/last seat to check, start/end: start/end time
    login(url)
    booked = False
    # book a space on most recent day || lesesaal 4 9-15, vwl bib 9-13, hwa 10-14
    # check all seats
    for current_seat in range(first_seat, last_seat):
        bookable = True
        # check if seat booked somewhere between start time and end time, every hour is own slot
        for hour in range(start, end):
            slot = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(hour), str(current_seat))
            if driver.find_element(By.XPATH, slot).get_attribute("title") != "buchbar":
                bookable = False

        if not bookable:
            print("Seat {} not available".format(current_seat))
        else:
            # all slots available for one seat -> book that seat
            # first hour to book
            # day || 1 = current day, 8 = last day
            # timeslot: start/end|| 3 = 9AM-10AM, 8= 2PM-3MP, 17= 11 pm-12 am
            # current_seat: table_id || last number(s) of table id
            xpath_start = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(start), str(current_seat))
            # last hour to book
            xpath_end = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(end - 1), str(current_seat))
            # select first hour + last hour to book rowspan from first to last hour
            driver.find_element(By.XPATH, xpath_start).click()
            time.sleep(3)
            driver.find_element(By.XPATH, xpath_end).click()

            try:
                # try: analyze message after trying to book
                message = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert') and "
                                                                "@data-notify='container']//span["
                                                                "@data-notify='message']"))).get_attribute(
                    "innerHTML")
                if "Max. Buchung" in message:
                    # already booked maximum hours for one day
                    print("Max. Buchungszeit! Keine Buchung möglich.")
                    break
                elif "Buchung war erfolgreich." in message:
                    # booking executed
                    print("Booking confirmed! Seat {}".format(current_seat))
                    print(datetime.datetime.now())
                    booked = True
                    break
                else:
                    # booking not possible, print message to get more information
                    print("Seat {} could not be booked. {}".format(current_seat, message))
            except:
                # except: no message
                # try: check if already booked hours for that day; verify slot owner returns boolean
                if url == url_l4:
                    already_booked = verify_slotowner(day, 3, 17, first_seat, last_seat)
                else:
                    already_booked = verify_slotowner(day, 3, 10, first_seat, last_seat)

                if already_booked:
                    print("You have already booked a seat for this day.")
                    driver.quit()
                    quit()
                else:
                    print("Seat {} could not be booked. Could not verify slot owner. Trying to cancel".format(
                        current_seat))
                    # except: try to cancel seat and continue with next seat
                    try:
                        driver.find_element(By.ID, "btn-cancel").click()
                        time.sleep(3)
                        print("Seat {} Canceled.".format(current_seat))
                    except:
                        print("Seat could not be booked. Could not cancel.")
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


def verify_slotowner(day, start_time, end_time, first_seat, last_seat):
    verify = False
    for seat in range(first_seat, last_seat):
        for hour in range(start_time, end_time + 1):
            xpath_hour = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(hour), str(seat))
            timeslot = driver.find_element(By.XPATH, xpath_hour)
            if timeslot.get_attribute("class") == "slot booked slotowner normal":
                verify = True
                break
    return verify


if __name__ == '__main__':
    # login credentials // website
    username = None
    password = None
    path = None
    # urls
    url_l4 = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/USBO1LS4"
    url_vwl = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOVWL"
    url_hwa = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/HWAEGLS"
    # path chromedriver exe file

    chrome_options = Options()
    # initialising driver
    driver = webdriver.Chrome(path, options=chrome_options)
    driver.maximize_window()

    print(datetime.datetime.now())
    print("Lesesaal 4:")
    if booking(url_l4, 8, 3, 51, 3, 9) == False:
        print("\nVWL:")
        if booking(url_vwl, 8, 5, 25, 3, 7) == False:
            # vwl: 5, 7, 8?, 9?
            print("\nHWA:")
            if booking(url_hwa, 8, 21, 36, 3, 7) == False:
                print("\nBooking not possible.")
        else:
            if booking(url_hwa, 8, 21, 36, 8, 11) == True:
                print("Additional Seat booked at HWA.")
            else:
                print("Could not book additional seat.")
    driver.quit()
