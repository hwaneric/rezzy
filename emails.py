import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

def send_emails(restaurant_name, date, times, party_size, url):
  load_dotenv()

  # Email details
  sender_email = os.getenv("SEND_EMAIL")
  receiver_email_list = os.getenv("RECEIVER_EMAILS").split(",")
  password = os.getenv("SMTP_APP_PASSWORD")

  subject = f"REZZY ALERT: {restaurant_name} Reservation Available"
  body = f"A reservation for {party_size} is available at {restaurant_name} on {date} at {times}. Click here to book: {url}"

  # Create a multipart message and set headers
  message = MIMEMultipart()
  message["From"] = sender_email
  message["Subject"] = subject
  message.attach(MIMEText(body, "plain"))

  for receiver_email in receiver_email_list:
    message["To"] = receiver_email
   
    # Connect to the server and send the email
    try:
      server = smtplib.SMTP("smtp.gmail.com", 587)
      server.ehlo() 
      server.starttls()  # Secure the connection
      server.ehlo()  
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message.as_string())
      server.quit()

      # Only send one email to avoid being flagged as spam
      break
    except Exception as e:
      print(f"Error: {e}")


def send_error_notification(exception, traceback):
  load_dotenv()

  # Email details
  sender_email = os.getenv("SEND_EMAIL")
  receiver_email = os.getenv("DEV_EMAIL")
  password = os.getenv("SMTP_APP_PASSWORD")

  subject = f"REZZY IS BROKEN"
  body = f"There was an error with Rezzy. \n\nException: {exception} \n\nTraceback: {traceback}"

  # Create a multipart message and set headers
  message = MIMEMultipart()
  message["From"] = sender_email
  message["Subject"] = subject
  message.attach(MIMEText(body, "plain"))

  message["To"] = receiver_email
  
  # Connect to the server and send the email
  try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo() 
    server.starttls()  # Secure the connection
    server.ehlo()  
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
  except Exception as e:
    print(f"Error: {e}")