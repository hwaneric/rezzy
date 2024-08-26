from webscrape import reservation_handler, get_opentable_url
from lambda_function import lambda_handler, set_up_driver
from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

rule_name = 'trigger_lambda_every_minute'

@app.route("/reserve", methods=["POST"])
def reserve():
  data = request.json()

  # Phone number not currently required because it's not used in the lambda function
  # Email is required tho to send email
  required_fields = ["dates", "guest", "restaurant_name", "geolocation", "phone_number"]
  all_fields_present = all(field in data for field in required_fields)

  if not all_fields_present:
    return jsonify({"status": 400, "message": "Missing required fields"})

  response = lambda_handler(data, None)
  if response["reservation_success"]:
    return jsonify(response)
  

  # TODO: Set up aws lambda trigger
  # Initialize a session using Amazon Lambda
  client = boto3.client('events')
  lambda_client = boto3.client('lambda')

  # Define the CloudWatch Event Rule
  schedule_expression = 'rate(1 minute)'

  # Create or update the rule
  response = client.put_rule(
    Name=rule_name,
    ScheduleExpression=schedule_expression,
    State='ENABLED',
    Description='Triggers Lambda function every minute'
  )

  rule_arn = response['RuleArn']

  # Define the target for the rule
  lambda_function_name = 'rezzy_docker'
  lambda_arn = f'arn:aws:lambda:region:account-id:function:{lambda_function_name}'
  
  # Set up event data for the trigger
  event_json = {
    "dates": [{"day": 30, "month": 8, "year": 2024, "earliest_time": "5:00 PM", "latest_time": "7:30 PM", "ideal_time": "6:00 PM"}, {"day": 12, "month": 8, "year": 2024, "earliest_time": "11:00 AM", "latest_time": "1:00 PM", "ideal_time": "12:00 PM"}],
    "guests": 4,
    "restaurant_name": "Meso Modern Mediterranean",
    "geolocation": {
      "latitude": 42.3601,  # Boston latitude
      "longitude": -71.0589,  # Boston longitude
      "accuracy": 100
    },
    "phone_number": 1234567890
  }

  target = {
    'Id': '1',  # Identifier for the target. Could maybe use email? 
    'Arn': lambda_arn,
    'Input': json.dumps(event_json)  # Pass the static JSON event
  }

  # Add the Lambda function as the target of the rule
  client.put_targets(
    Rule=rule_name,
    Targets=[target]
  )

  # Add permission for the CloudWatch Events service to invoke your Lambda function
  lambda_client.add_permission(
    FunctionName=lambda_function_name,
    StatementId=f'{rule_name}-permission',
    Action='lambda:InvokeFunction',
    Principal='events.amazonaws.com',
    SourceArn=rule_arn
  )

  print(f"Trigger set up to invoke Lambda function '{lambda_function_name}' every minute.")


@app.route("/restaurant_info", methods=["GET"])
def restaurant_info():
  restaurant_name = request.args.get("restaurant_name")
  geolocation = request.args.get("geolocation")
  try:
    driver = set_up_driver()
    opentable_url = get_opentable_url(driver, restaurant_name, geolocation)
    driver.quit()
  except:
    return jsonify({"status": 400, "message": "Error fetching restaurant info"})
  
  return jsonify({"opentable_url": opentable_url})


# Cancel monitoring for a reservation at a specific restaurant
@app.route("/cancel_rezzy", methods=["DELETE"])
def cancel_rezzy():
  restaurant_name = request.args.get("restaurant_name")
  user_id = request.args.get("user_id")

  # Fetch the rule name and Ids from Supabase
  rule_name = "PLACEHOLDER"
  rule_ids = ["PLACEHOLDER1", "PLACEHOLDER2"]

  client = boto3.client('events')
  rule_name = f'trigger_lambda_every_minute_{restaurant_name}'
  try:
    client.remove_targets(Rule=rule_name, Ids=rule_ids)
    client.delete_rule(Name=rule_name)
  except:
    return jsonify({"status": 400, "message": "Error cancelling reservation monitoring"})

  return jsonify({"status": 200, "message": "Reservation monitoring cancelled"})



def test():
  # Initialize a session using Amazon Lambda
  client = boto3.client('events')
  lambda_client = boto3.client('lambda')

  # Define the CloudWatch Event Rule
  rule_name = 'trigger_lambda_every_minute'
  # schedule_expression = 'rate(1 minute)'

  # Create or update the rule
  # response = client.put_rule(
  #   Name=rule_name,
  #   ScheduleExpression=schedule_expression,
  #   State='ENABLED',
  #   Description='Triggers Lambda function every minute'
  # )

  rule_arn = client.describe_rule(Name=rule_name).get('Arn')

  # Define the target for the rule
  lambda_function_name = 'rezzy_docker'
  lambda_arn = 'arn:aws:lambda:us-east-2:339712894589:function:rezzy_docker'
  
  # Set up event data for the trigger
  event_json = {
    "dates": [{"day": 30, "month": 9, "year": 2024, "earliest_time": "5:00 PM", "latest_time": "7:30 PM", "ideal_time": "6:00 PM"}, {"day": 28, "month": 9, "year": 2024, "earliest_time": "11:00 AM", "latest_time": "1:00 PM", "ideal_time": "12:00 PM"}],
    "guests": 4,
    "restaurant_name": "House of Prime Rib",
    "geolocation": {
      "latitude": 42.3601,  # Boston latitude
      "longitude": -71.0589,  # Boston longitude
      "accuracy": 100
    },
    "phone_number": 1234567890
  }

  target = {
    'Id': '2',  # Identifier for the target
    'Arn': lambda_arn,
    'Input': json.dumps(event_json)  # Pass the static JSON event
  }

  # Add the Lambda function as the target of the rule
  client.put_targets(
    Rule=rule_name,
    Targets=[target]
  )

  # # Add permission for the CloudWatch Events service to invoke your Lambda function
  # lambda_client.add_permission(
  #   FunctionName=lambda_function_name,
  #   StatementId=f'{rule_name}-permission',
  #   Action='lambda:InvokeFunction',
  #   Principal='events.amazonaws.com',
  #   SourceArn=rule_arn
  # )

  print(f"Trigger set up to invoke Lambda function '{lambda_function_name}' every minute.")

def cancel_trigger():
  client = boto3.client('events')
  # rule_name = "trigger_lambda_every_minute"
  # Rule id will be user's email
  rule_ids = ["1"]

  try:
    client.remove_targets(Rule=rule_name, Ids=rule_ids)
    # client.delete_rule(Name=rule_name)
  except:
    print("Error cancelling reservation monitoring")

test()
# cancel_trigger()