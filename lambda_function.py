from webscrape import check_availability




# rezzy_date values must all be integers. Do not add padding zeros. Year must be 4 digits
rezzy_date = {"day": 29, "month": 10, "year": 2024}
# rezzy_time must be a string in 24-hour format. Include padding zeros
rezzy_time = "17:00"



          
  

dates = [{"day": 9, "month": 8, "year": 2024, "time": "17:00"}, {"day": 12, "month": 8, "year": 2024, "time": "17:00"}]
guests = 4 


def lambda_handler(event, context):
  for date in dates:
    day, month, year, time_of_day = date["day"], date["month"], date["year"], date["time"]
    check_availability(guests, {"day": day, "month": month, "year": year}, time_of_day)
  
  return {
    "status": 200,
    "message": "Success"
  }

  
  

lambda_handler(None, None)