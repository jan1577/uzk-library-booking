import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# import login credentials
import config


def booking(url, day, first_seat, last_seat, start, end):
    """
    Book a seat for a given day and time.
    :param url: where to book, link
    :param day: when to book, integer; 1 = today, 8 = last day
    :param first_seat: seats to check, integer; loops from first to last
    :param last_seat: see above
    :param start: time to start booking, integer; first hour = 3 (9-10 / 10-11)
    :param end: time to end booking, integer; last hour = 10 for HWA/ VWL, 17 for L4
    :return: True if booking done, False if not possible (No seats available or max time for a day reached.)
    """
    login(url)
    booked = False
    # check for all seats if bookable for given time span
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
                    print(datetime.datetime.now().replace(microsecond=0))
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
                    break
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
    """
    passes login credentials and executes login
    :param url: link for website (where to book)
    :return: no return value
    """
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
    """
    Verifies if a seat is already booked for current day. Only called if seat available, but booking not possible.
    :params: see booking()
    :return: True if a seat is already booked, False if not
    """
    verify = False
    for seat in range(first_seat, last_seat):
        for hour in range(start_time, end_time + 1):
            xpath_hour = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(hour), str(seat))
            timeslot = driver.find_element(By.XPATH, xpath_hour)
            if timeslot.get_attribute("class") == "slot booked slotowner normal":
                duration = int(timeslot.get_attribute("rowspan"))
                print("Already booked seat {0}.".format(seat))
                # todo: add time where seat is booked # differs depending on url
                verify = True
                break
    return verify


if __name__ == '__main__':
    # login credentials & chromedriver.exe path
    username = config.username
    password = config.password
    path = config.path
    # urls for booking
    url_l4 = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/USBO1LS4"
    url_vwl = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOVWL"
    url_hwa = "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/HWAEGLS"
    chrome_options = Options()
    # initialising driver
    driver = webdriver.Chrome(path, options=chrome_options)
    driver.maximize_window()

    print(datetime.datetime.now().replace(microsecond=0))
    print("Lesesaal 4:")

    # check l4 for booking, last day, 9AM - 3PM
    if booking(url_l4, 8, 3, 51, 3, 9) == False:
        print("\nVWL:")
        # check VWL, last day, 9AM - 1PM
        if booking(url_vwl, 8, 5, 25, 3, 7) == False:
            # vwl: 5, 7, 8?, 9?
            print("\nHWA:")
            # check HWA, 10AM - 2PM
            if booking(url_hwa, 8, 21, 36, 3, 7) == False:
                print("\nBooking not possible.")
        # if VWL booked, try HWA from 3PM - 6PM
        else:
            if booking(url_hwa, 8, 21, 36, 8, 11) == True:
                print("Additional Seat booked at HWA.")
            else:
                print("Could not book additional seat.")
    driver.quit()