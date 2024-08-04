from webscrape import reservation_handler, get_opentable_url
from selenium import webdriver
from datetime_helpers import convert_to_datetime




boston_geolocation = {
  "latitude": 42.3601,  # Boston latitude
  "longitude": -71.0589,  # Boston longitude
  "accuracy": 100
}
          
event = {
  "dates": [{"day": 30, "month": 8, "year": 2024, "earliest_time": "5:00 PM", "latest_time": "7:30 PM", "ideal_time": "6:00 PM"}, {"day": 12, "month": 8, "year": 2024, "earliest_time": "11:00 AM", "latest_time": "12:00 PM", "ideal_time": "1:00 PM"}],
  "guests": 4,
  "restaurant_name": "Mare",
  "geolocation": boston_geolocation,
  "phone_number": 1234567890
}




def lambda_handler(event, context):
  driver = set_up_driver()
  dates = event.get("dates", [])
  guests = event.get("guests", 2)
  restaurant_name = event.get("restaurant_name", "")
  geolocation = event.get("geolocation", boston_geolocation)
  phone_number = event.get("phone_number", 0000000000)



  opentable_url = get_opentable_url(driver, restaurant_name, geolocation)
  print(opentable_url)
  if not opentable_url:
    raise Exception("Opentable URL not found")

  # Fetch restaurant name, dates, guests, etc. from the context
  for date in dates:
    day, month, year = date["day"], date["month"], date["year"]
    latest = convert_to_datetime(date["latest_time"])
    earliest = convert_to_datetime(date["earliest_time"])
    ideal = convert_to_datetime(date["ideal_time"])
    print(day, month, year)

    reservation_handler(
      driver, 
      guests, 
      {"day": day, "month": month, "year": year}, 
      opentable_url, 
      ideal, 
      earliest, 
      latest, 
      phone_number
    )
  
  driver.quit()
  return {
    "status": 200,
    "message": "Success"
  }


def set_up_driver():
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
    return driver

  
  
lambda_handler(event, None)
