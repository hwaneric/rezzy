import datetime

def convert_to_datetime(time_str):
  return datetime.datetime.strptime(time_str, '%I:%M %p')

def datetime_to_string(dt):
  return dt.strftime('%I:%M %p').lstrip("0")

def add_time(dt, hours=0, minutes=0):
  return dt + datetime.timedelta(hours=hours, minutes=minutes)

def round_to_nearest_half_hour(dt):
  # Calculate the number of minutes past the hour
  minutes = dt.minute
  seconds = dt.second
  
  # Determine the total number of minutes to add to the hour to round to the nearest half hour
  if minutes < 15 or (minutes == 15 and seconds == 0):
      rounded_minutes = 0
  elif minutes < 45 or (minutes == 45 and seconds == 0):
      rounded_minutes = 30
  else:
      rounded_minutes = 0
      dt += datetime.timedelta(hours=1)  # Add one hour if rounding up from the second half hour

  # Create the rounded datetime
  rounded_dt = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
  return rounded_dt