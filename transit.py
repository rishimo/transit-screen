import requests
from dotenv import load_dotenv
import os
import json
import pandas as pd
from datetime import datetime
from datetime import timezone
from dateutil import tz
import re

# function to load secrets
def secretFunc():
	load_dotenv()
	global transit_URL
	global transit_api_key
	global stopcodes
	global directions
	global operators
	global openweather_api_key
	global lat
	global long

	transit_URL = os.getenv('transit_URL')
	transit_api_key = os.getenv('transit_api_key')
	stopcodes = os.getenv('stopcodes')
	operators = os.getenv('operators')
	directions = os.getenv('directions')
	openweather_api_key = os.getenv('openweather_api_key')
	lat = os.getenv('lat')
	long = os.getenv('long')

	stopcodes = stopcodes.split(',')
	for i, stop in enumerate(stopcodes):
		stopcodes[i] = stop.strip()

	operators = operators.split(',')
	for i, operator in enumerate(operators):
		operators[i] = re.sub('[^a-zA-Z]+', '', operator)

	directions = directions.split(',')
	for i, dir in enumerate(directions):
		directions[i] = re.sub('[^a-zA-Z]+', '', dir)

	return()

# function to use 511org API to find next arrivals at each of the provided stopcodes
def getNextTransit(stopcodes, directions, operators):
	arrivals = list()
	for i, stop in enumerate(stopcodes):
		r = requests.get(f'{transit_URL}/StopMonitoring', 
						 params = {'agency': operators[i], 
								   'api_key': transit_api_key,
								   'stopcode': stop})
		
		content = json.loads(r.content)

		stopInfo = pd.DataFrame.from_records(content)
		stopInfo = stopInfo['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']

		for arrival in stopInfo:
			# Get arrivalTime from JSON content
			arrivalTime = arrival['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']

			# Convert arrivalTime into 12h Pacific time
			utc_datetime = datetime.fromisoformat(arrivalTime[:-1])

			# Define the timezones
			utc_tz = tz.gettz('UTC')
			pacific_tz = tz.gettz('America/Los_Angeles')
			currentTime = datetime.now(timezone.utc)

			# Set the UTC timezone for the datetime object
			utc_datetime = utc_datetime.replace(tzinfo = utc_tz)

			# Convert the datetime object to Pacific time
			pacific_datetime = utc_datetime.astimezone(pacific_tz)

			# Format the datetime object as a 12-hour time string
			time_str = pacific_datetime.strftime('%I:%M:%S %p')
			
			# Calculte timeToArrival
			timeToArrival = pacific_datetime - currentTime
			timeToArrival = divmod(timeToArrival.seconds, 60)
			timeToArrival = f"{timeToArrival[0]}:{timeToArrival[1]}"

			# Get destination from JSON content
			destination = arrival['MonitoredVehicleJourney']['MonitoredCall']['DestinationDisplay']

			# Append [code, direction, time]  to list
			arrivals.append([stop, directions[i], destination, time_str, timeToArrival])

	# Convert nested list to DataFrame
	arrivals = pd.DataFrame(arrivals, columns=['stopcode', 'direction', 'destination','arrivalTime', 'timeToArrival'])
	return(arrivals)


	''' 
	todo:
		- connect to RPLCD to print information
		- implement refreshment interval
	'''

# main function
if __name__ == '__main__':
	secretFunc()
	transitArrivals = getNextTransit(stopcodes, directions, operators)
	print(transitArrivals)  