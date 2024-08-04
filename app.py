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
from webscrape import get_opentable_url, make_reservation
import requests



def reserve_or_poll(guests, date, time_of_day, restaurant_name, opentable_url=None):
  try:
    # Set up the Chrome driver
    # chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-dev-tools")
    # chrome_options.add_argument("--no-zygote")
    # chrome_options.add_argument("--single-process")
    # chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    # chrome_options.add_argument(f"--data-path={mkdtemp()}")
    # chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    # chrome_options.add_argument("--remote-debugging-pipe")
    # chrome_options.add_argument("--verbose")
    # chrome_options.add_argument("--log-path=/tmp")
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

    # service = Service(
    #   executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
    #   service_log_path="/tmp/chromedriver.log"
    # )

    # print("Starting Chrome driver")
    # driver = webdriver.Chrome(
    #   service=service,
    #   options=chrome_options
    # )
    # print("Chrome driver started")

    driver = webdriver.Chrome()

    if not opentable_url:
      opentable_url = get_opentable_url(driver, restaurant_name, {
        "latitude": 37.7749,  # San Francisco latitude
        "longitude": -122.4194,  # San Francisco longitude
        "accuracy": 100
      })

      if not opentable_url:
        raise Exception("Restaurant not found on OpenTable")
    
    res = make_reservation(driver, guests, date, time_of_day, opentable_url)

    if res["reservation_success"]:
      print("Reservation made!")
      return
    
    print("Reservation not available. Polling for availability")
    # TODO: set up AWS Lambda trigger to poll for availability

    
    
  except Exception as e:
    print(f"Error: {e}")
    traceback_str = traceback.format_exc()
    send_error_notification(e, traceback_str)
    raise
