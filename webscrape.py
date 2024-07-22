import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from emails import send_emails, send_error_notification
import traceback
from tempfile import mkdtemp




guests = 4
number_to_month = {
  1: "January",
  2: "February",
  3: "March",
  4: "April",
  5: "May",
  6: "June",
  7: "July",
  8: "August",
  9: "September",
  10: "October",
  11: "November",
  12: "December"
}

# rezzy_date values must all be integers. Do not add padding zeros. Year must be 4 digits
rezzy_date = {"day": 29, "month": 10, "year": 2024}
# rezzy_time must be a string in 24-hour format. Include padding zeros
rezzy_time = "17:00"

OPENTABLE_URL = 'https://www.opentable.com/restref/client/?restref=1779&corrid=05f5a50c-5839-4a47-85f8-9addf78bef1e'
RESTAURANT_NAME = "House of Prime Rib"

def check_availability(guests, date, time_of_day):
  try:
    # Set up the Chrome driver

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

    service = Service(
      executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
      service_log_path="/tmp/chromedriver.log"
    )


    print("Starting Chrome driver")
    driver = driver = webdriver.Chrome(
      service=service,
      options=chrome_options
    )
    print("Chrome driver started")

    driver.get(OPENTABLE_URL)
    # time.sleep(5)
    # driver.save_screenshot("screenshot.png")
    # time.sleep(10000)

    print("driver got url")

    select_party_size(driver, guests)
    select_date(driver, date)
    select_reservation_time(driver, time_of_day)

    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[data-auto="findATableButton"]')
    submit_button.click()

    try:
      wait = WebDriverWait(driver, 10)

      # Will raise exception if no reservation available message does not appear after 10 seconds
      no_reservations_msg = wait.until(
        EC.visibility_of_element_located((By.XPATH, '//p[@role="alert" and starts-with(text(),"At the moment, there’s no online availability within 2.5 hours of")]'))
      )
      print(f"No reservation available on {date} within 2.5 hours of {time_of_day}")

    except:
      # Locate all button elements within the time slots list
      time_buttons = driver.find_elements(By.XPATH, '//ul[@data-auto="timeSlots"]//button[@role="link"]')

      # Identify which times are available
      times = []
      for button in time_buttons:
        time_text = button.text
        if time_text:
          times.append(time_text)

      send_emails(RESTAURANT_NAME, f"{date["month"]}/{date["day"]}/{date["year"]}", times, guests, OPENTABLE_URL)
      raise
    finally:
      driver.quit()
  except Exception as e:
    print(f"Error: {e}")
    traceback_str = traceback.format_exc()
    send_error_notification(e, traceback_str)



def select_party_size(driver, guests):
  party_size_select = driver.find_element(By.XPATH, '//select[@aria-label="Party size"]')
  # party_size_select = WebDriverWait(driver, 10).until(
  #   EC.presence_of_element_located((By.XPATH, '//select[@aria-label="Party size"]'))
  # ) 
  party_size = Select(party_size_select)
  party_size.select_by_value(str(guests))
  


def select_date(driver, date):
  calendar = driver.find_element(By.XPATH, '//input[@data-auto="calendarDatePicker"]')
  calendar.click()
  WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, 'react-datepicker'))
  )

  month_name = number_to_month[date["month"]]

  # Navigate to correct month
  while True:

    month_label = driver.find_element(By.CLASS_NAME, "react-datepicker__current-month").text
    target_month = month_name + " " + str(date["year"])
    if month_label == target_month:
      break

    next_button = driver.find_element(By.CSS_SELECTOR, 'button.react-datepicker__navigation.react-datepicker__navigation--next')
    next_button.click()
    time.sleep(1) # Wait for next month to load on calendar

  # Get day of week corresponding to date
  day_of_week = datetime.date(
    date["year"], 
    date["month"], 
    date["day"]
  ).strftime("%A")

  ordinal_suffix = get_ordinal_suffix(date["day"])
  aria_label = f"Choose {day_of_week}, {month_name} {str(date["day"])}{ordinal_suffix}, {str(date['year'])}"
  day_button = driver.find_element(By.XPATH, f'//div[@aria-label="{aria_label}"]')
  day_button.click()


def select_reservation_time(driver, time_of_day):
  reservation_time_select = driver.find_element(By.XPATH, '//select[@aria-label="Reservation time"]')
  reservation_time = Select(reservation_time_select)
  reservation_time.select_by_value(time_of_day)
  



# Function to get the ordinal suffix for a day
def get_ordinal_suffix(day):
  if 11 <= day <= 13:
    return "th"
  else:
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
