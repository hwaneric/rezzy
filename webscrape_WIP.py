from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from emails import send_emails, send_error_notification
from datetime_helpers import convert_to_datetime, datetime_to_string, add_time, round_to_nearest_half_hour


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
# rezzy_date = {"day": 29, "month": 10, "year": 2024}
# rezzy_time must be a string in 24-hour format. Include padding zeros
# rezzy_time = "17:00"

BASE_OPENTABLE_URL = 'https://www.opentable.com'
# RESTAURANT_NAME = "House of Prime Rib"




def reservation_handler(driver, guests, date, opentable_url, ideal_time, earliest_time, latest_time, phone_number):
  driver.get(opentable_url)

  select_party_size(driver, guests)
  select_date(driver, date)
  times = get_valid_times(driver, earliest_time, latest_time)

  if not times:
    print("No reservations available")
    return {"status": 200, "message": "No reservations available", "reservation_success": False}

  # Sort times by proximity to ideal time
  times.sort(key=lambda x: abs(x - ideal_time))
  print(times)

  for time in times:
    if make_reservation(driver, time, phone_number, opentable_url):
      print("reservation made")
      sleep(10000)
      return {"status": 200, "message": "Reservations made!", "reservation_success": True}
  
  # send_emails(RESTAURANT_NAME, f"{date["month"]}/{date["day"]}/{date["year"]}", times, guests, opentable_url)
  return {"status": 200, "message": "No reservations available", "reservation_success": False}





def make_reservation(driver, time, phone_number, opentable_url):
  try:
    # Select time to ensure reservation time shows on screen
    select_time(driver, time)
    print(datetime_to_string(time))
    wait = WebDriverWait(driver, 10)
    button = wait.until(
      EC.visibility_of_element_located((By.XPATH, f"//a[contains(@class, 'vFX9z2MNdGY-') and text()='{datetime_to_string(time)}']"))
    )
    button.click()

    seating_options_header = driver.find_elements(By.XPATH, "//h1[contains(text(), 'Seating options')]")
    if seating_options_header:
      standard_seating_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test="seatingOption-default-button"]')
      standard_seating_button.click()

    
    phone_input = wait.until(
      EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Phone number']"))
    )
    # driver.find_element(By.XPATH, "//input[@aria-label='Phone number']")
    phone_input.send_keys(phone_number)

    email_opt_in_checkbox = driver.find_element(By.ID, "optInEmailRestaurant")

    driver.execute_script("arguments[0].scrollIntoView();", email_opt_in_checkbox)
    if email_opt_in_checkbox.is_selected():
      driver.execute_script("arguments[0].click();", email_opt_in_checkbox)
    
    required_fields = driver.find_elements(By.CLASS_NAME, "RPdaddsMSi4-")
    for field in required_fields:
      if not field.is_selected():
        driver.execute_script("arguments[0].click();", field)
        
    
    # TODO: Click button to make reservation!!!
    return True
  except Exception as e:
    print(e)
    if driver.current_url != opentable_url:
      driver.back()

    return False
 





  

def get_valid_times(driver, earliest_time, latest_time):
  # Pick time 2.5 hours after earliest time to optimally cover reservation window
  select_time(driver, add_time(earliest_time, hours=2.5))
  times = []

  try:
    wait = WebDriverWait(driver, 7)

    # Will raise exception if no reservation available message does not appear after 10 seconds
    no_reservations_msg = wait.until(
      EC.visibility_of_element_located((By.XPATH, '//span[starts-with(text(),"At the moment, there’s no online availability within 2.5 hours of")]'))
    )
  
  except:
    time_buttons = driver.find_elements(By.CLASS_NAME, 'vFX9z2MNdGY-')

    # Identify which times are available and in time range
    for button in time_buttons:
      time_text = button.text.rstrip("*")

      if time_text:
        print(time_text)
        dt = convert_to_datetime(time_text)

        if earliest_time <= dt <= latest_time:
          times.append(dt)

  finally:
    # Time window not fully covered in 5 hour range. Add another 5 hours to the range
    if add_time(earliest_time, hours=5) < latest_time:
      times.append.extend(get_valid_times(), add_time(earliest_time, hours=5), latest_time)

  return times




def get_opentable_url(driver, restaurant_name, geolocation):
  # Set location
  driver.execute_cdp_cmd("Emulation.setGeolocationOverride", geolocation)
  sleep(0.3) # Sleep to ensure location is set before loading page
  driver.get(BASE_OPENTABLE_URL)
  wait = WebDriverWait(driver, 10)

  # Update OpenTable location to user location
  location_setter = wait.until(EC.presence_of_element_located((By.XPATH, "//div[text()='Get current location']")))
  location_setter.click()
  driver.refresh()


  # Navigate to restaurant page
  restaurant_name_input = wait.until(EC.presence_of_element_located((By.ID, "home-page-autocomplete-input")))
  restaurant_name_input.clear()
  restaurant_name_input.send_keys(restaurant_name)

  submit_btn = driver.find_element(By.XPATH, "//button[text()=\"Let’s go\"]")
  submit_btn.click()

  try:
    restaurant_link = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "qCITanV81-Y-")))
    not_on_opentable_label = driver.find_elements(By.XPATH, "//p[contains(text(), 'Unfortunately, this restaurant is not on the OpenTable reservation network. To see if they take reservations and have availability, you will need to call the restaurant directly or visit their website.')]")
    
    if not_on_opentable_label:
      print("Restaurant not on OpenTable")
      # Should terminate AWS trigger if necessary here
      return ""

  except Exception as e:
    print(e)
    return ""
  
  return restaurant_link.get_attribute("href")




def select_party_size(driver, guests):
  # Resize window to make elements visible
  driver.set_window_size(750, 750)

  party_size_select = driver.find_element(By.XPATH, '//select[@aria-label="Party size selector"]')
  party_size = Select(party_size_select)
  party_size.select_by_value(str(guests))
  


def select_date(driver, date):
  calendar = driver.find_element(By.XPATH, "//div[@id='restProfileMainContentDtpDayPicker']")
  calendar.click()
  
  month_name = number_to_month[date["month"]]

  # Navigate to correct month
  while True:

    month_label = driver.find_element(By.ID, "react-day-picker-1").text # I believe this is stable? But be aware that the number at the end of the id may change
    
    target_month = month_name + " " + str(date["year"])
    if month_label == target_month:
      break

    next_button = driver.find_element(By.NAME, 'next-month')
    next_button.click()
    sleep(0.5) # Wait for next month to load on calendar

  # Get day of week corresponding to date
  day_of_week = datetime.date(
    date["year"], 
    date["month"], 
    date["day"]
  ).strftime("%A")

  aria_label = f"{day_of_week}, {month_name} {str(date["day"])}"
  day_button = driver.find_element(By.XPATH, f'//button[@aria-label="{aria_label}"]')
  day_button.click()


def select_time(driver, time_of_day):
  time_of_day = round_to_nearest_half_hour(time_of_day)
  time_of_day = datetime_to_string(time_of_day)

  wait = WebDriverWait(driver, 10)
  reservation_time_select = wait.until(
    EC.presence_of_element_located((By.XPATH, '//select[@aria-label="Time selector"]'))
  )

  # Wait until time buttons appear before selecting new time to ensure correct time are loaded
  _ = wait.until(
      EC.visibility_of_element_located((By.XPATH, f"//button[text()='Notify me']"))
    )

  reservation_time = Select(reservation_time_select)
  reservation_time.select_by_visible_text(time_of_day)
  



# Function to get the ordinal suffix for a day
def get_ordinal_suffix(day):
  if 11 <= day <= 13:
    return "th"
  else:
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
