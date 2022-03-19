import time
import datetime
from datetime import datetime as dt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# import login credentials
import config
import subprocess


def booking(url, day, first_seat, last_seat, start, end):
    """
    Book a seat for a given day and time.
    :param url: where to book, tuple (name, link)
    :param day: when to book, integer; 1 = today, 8 = last day
    :param first_seat: seats to check, integer; loops from first to last
    :param last_seat: see above
    :param start: time to start booking, integer; first hour = 3 (9-10 / 10-11)
    :param end: time to end booking, integer; last hour = 10 for HWA/ VWL, 17 for L4
    :return: True if booking done, False if not possible (No seats available or max time for a day reached.)
    """
    login(url[1])  # website login
    # print requested location, time and date to book
    if url == url_l4 or url == url_vwl:
        get_requested_date(url[0], day, start, end, 6)
    else:
        get_requested_date(url[0], day, start, end, 7)

    booked = False
    # check for all seats if bookable for given time span
    for seat_id in range(first_seat, last_seat):
        bookable = True
        # check if seat booked somewhere between start time and end time, every hour is own slot
        for hour in range(start, end):
            slot = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(hour), str(seat_id))
            if driver.find_element(By.XPATH, slot).get_attribute("title") != "buchbar":
                bookable = False

        if not bookable:
            print("Seat {} not available".format(seat_id))
        else:
            # all slots available for one seat -> book that seat
            # first hour to book
            xpath_start = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(start), str(seat_id))
            # last hour to book
            xpath_end = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(end - 1), str(seat_id))
            # select first hour + last hour to book rowspan from first to last hour
            driver.find_element(By.XPATH, xpath_start).click()
            time.sleep(3)
            driver.find_element(By.XPATH, xpath_end).click()

            try:
                # analyze message after trying to book
                message = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert') and "
                                                                "@data-notify='container']//span["
                                                                "@data-notify='message']"))).get_attribute(
                    "innerHTML")
                if "Max. Buchung" in message:
                    print("Max. Buchungszeit! Keine Buchung möglich.")
                    if url[1] == url_l4[1]:
                        verify_slotowner(url, day, 3, 17, first_seat, last_seat)
                    else:
                        verify_slotowner(url, day, 3, 10, first_seat, last_seat)
                    break
                elif "Buchung war erfolgreich." in message:
                    print("Booking confirmed! Seat {}".format(seat_id))
                    end_time_script = datetime.datetime.now()
                    print(end_time_script.replace(microsecond=0))
                    print("Time to book: {}".format(end_time_script - start_time_script))
                    booked = True
                    break
                else:
                    print("Seat {} could not be booked. {}".format(seat_id, message))
            except:
                # except: no message
                # check if already booked hours for that day; verify slot owner returns boolean
                if url[1] == url_l4[1]:
                    already_booked = verify_slotowner(url[1], day, 3, 17, first_seat, last_seat)[0]
                else:
                    already_booked = verify_slotowner(url[1], day, 3, 10, first_seat, last_seat)[0]

                if already_booked:
                    break
                else:
                    print("Seat {} could not be booked. Could not verify slot owner. Trying to cancel".format(
                        seat_id))
                    try:
                        driver.find_element(By.ID, "btn-cancel").click()
                        time.sleep(3)
                        print("Seat {} Canceled.".format(seat_id))
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
    try:
        driver.get(url)
    except Exception as ex:
        ex_message = str(ex.args)
        if "ERR_INTERNET_DISCONNECTED" in ex_message:
            print("No internet connection, trying to reconnect.")
            # connecting to wifi
            cmd = "netsh wlan connect name={0} ssid={0}".format(wifi_SSID)
            k = subprocess.run(cmd, capture_output=True, text=True).stdout
            time.sleep(5)
            try:
                driver.get(url)
                print("Reconnected succesfully.")
            except:
                print("Not able to reconnect.")
        else:
            print(ex_message)
    # find username field and insert username
    driver.find_element(By.NAME, "uid").send_keys(username)
    # find the password and insert password
    driver.find_element(By.NAME, "password").send_keys(password)
    # click on submit
    driver.find_element(By.ID, "btn-login").click()
    time.sleep(5)


def get_requested_date(url, day, start_time, end_time, time_shift):
    """
    Get's requested date given input day (1-8); prints location, date and time of current booking request
    :param url: String, where to book
    :param day: int from 1-8; today = 1, 7 days ahead = 8
    :param start_time: int, start time of booking request
    :param end_time: int, end time of booking request
    :param time_shift: int; value used to convert integer used for booking to 24h time
    :return: no return value
    """
    today = dt.today()
    requested = datetime.timedelta(days=day - 1)
    requested_day = today + requested
    print("\nChecking {0} from {1} to {2} on {3}, {4}:".format(
        url, start_time + time_shift, end_time + time_shift, requested_day.strftime("%A"),
        requested_day.strftime("%d.%m.%Y").split()[0]))


def verify_slotowner(url, day, start_time, end_time, first_seat, last_seat):
    """
    Verifies if a seat is already booked for current day. Only called if seat available, but booking not possible.
    :param url: link, where to book
    :param day: when to book, integer; 1 = today, 8 = last day
    :param start_time: time to start booking, integer; first hour = 3 (9-10 / 10-11)
    :param end_time: time to end booking, integer; last hour = 10 for HWA/ VWL, 17 for L4
    :param first_seat: seats to check, integer; loops from first to last
    :param last_seat: see above
    :return: returns list, [False] if no seat booked, [True, booked_seat, booked_start (time), day] if seat booked
    """
    verified = False
    for seat in range(first_seat, last_seat):
        for hour in range(start_time, end_time + 1):
            xpath_hour = "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                str(day), str(hour), str(seat))
            timeslot = driver.find_element(By.XPATH, xpath_hour)
            if timeslot.get_attribute("class") == "slot booked slotowner normal":
                duration = int(timeslot.get_attribute("rowspan"))
                if url == url_l4[1] or url_vwl[1]:
                    print("Already booked seat {0}, from {1} to {2}.".format(seat, hour + 6, hour + 6 + duration))
                else:  # hwa
                    print("Already booked seat {0}, from {1} to {2}.".format(seat, hour + 7, hour + 7 + duration))
                verified, booked_seat, booked_start = True, seat, hour
                return [verified, booked_seat, booked_start, day]
    return [verified]


def verify_cancel(url, day):
    """
    cancel a booking on website on given day
    :param url: link, where seat is booked
    :param day: int, day when seat is booked
    :return: No return value
    """
    login(url)
    if url == url_l4[1]:
        verified = verify_slotowner(url, day, 3, 17, 1, 50)
    elif url == url_vwl[1]:
        verified = verify_slotowner(url, day, 3, 10, 1, 25)
    else:  # hwa
        verified = verify_slotowner(url, day, 3, 10, 1, 36)
    if verified[0]:
        verified_cancel(verified)
    else:
        print("No seat booked.")


def verified_cancel(verified):
    verified_seat = driver.find_element(By.XPATH,
                                        "/html/body/div[1]/div[3]/div/div/div/div[{0}]/div/div/div[2]/table/tbody/tr[{1}]/td[{2}]".format(
                                            verified[3], verified[2], verified[1]))
    verified_seat.click()
    # click cancel button
    cancel_button_xpath = "/html/body/div[1]/div[2]/div/div/ul/li[3]/button"
    driver.find_element(By.XPATH, cancel_button_xpath).click()
    # confirm cancelling
    time.sleep(3)
    confirm_xpath = "/html/body/div[2]/div/div/div[3]/button[1]"
    driver.find_element(By.XPATH, confirm_xpath).click()
    # check message
    message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert') and "
                                                    "@data-notify='container']//span["
                                                    "@data-notify='message']"))).get_attribute(
        "innerHTML")
    if "Die Buchung wurde erfolgreich gelöscht" in message:
        print("Booking cancelled successfully!")
    else:
        print(message)
    time.sleep(3)
    driver.quit()


if __name__ == '__main__':
    # login credentials & chromedriver.exe path
    username = config.username
    password = config.password
    path = config.path
    # only used if no internet connection
    wifi_SSID = config.wifi_SSID
    # urls for booking
    url_l4 = ("Lesesaal 4", "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/USBO1LS4")
    url_vwl = ("VWL", "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/wiso/WISOVWL")
    url_hwa = ("HWA", "https://raumbuchung.ub.uni-koeln.de/raumbelegung/gar/export/index/rooms/HWAEGLS")
    # initialising driver
    chrome_options = Options()
    driver = webdriver.Chrome(path, options=chrome_options)
    driver.maximize_window()

    start_time_script = datetime.datetime.now()
    print(start_time_script.replace(microsecond=0))

    # can be used to cancel a seat at certain day and certain url
    # verify_cancel(url_hwa[1], 1)

    # check l4 for booking, last day, 9AM - 1PM
    if booking(url_l4, 8, 1, 51, 3, 7):
        # if l4 booked, book hwa from 2PM-6PM
        booking(url_hwa, 8, 21, 36, 7, 11)
    else:
        # check VWL, last day, 9AM - 1PM
        if not booking(url_vwl, 8, 5, 25, 3, 7):
            # check HWA, 10AM - 2PM
            if not booking(url_hwa, 8, 21, 36, 3, 7):
                end_time_script = datetime.datetime.now()
                print("\nBooking not possible. Execution time: {}".format(end_time_script - start_time_script))
            # if hwa booked from 10am - 2pm, try l4 and vwl from 3-6PM
            elif not booking(url_l4, 8, 1, 51, 8, 12):
                booking(url_vwl, 8, 5, 25, 8, 12)
        # if VWL booked, try HWA from 2PM - 6PM
        else:
            if booking(url_hwa, 8, 21, 36, 6, 11):
                print("Additional Seat booked at HWA.")
            else:
                print("Could not book additional seat.")
    driver.quit()
