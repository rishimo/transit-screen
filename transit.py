import requests
from dotenv import load_dotenv
import os
import json
import pandas as pd
from datetime import datetime
from datetime import timezone
from dateutil import tz

# function to load secrets
def secretFunc():
	load_dotenv()
	global TRANSIT_URL
	global TRANSIT_API_KEY
	global STOPCODES
	global DIRECTIONS
	global OPERATORS
	global STOPNAMES
	global OPENWEATHER_API_KEY

	TRANSIT_URL = 'http://api.511.org/transit/StopMonitoring/'
	TRANSIT_API_KEY = os.environ['TRANSIT_API_KEY']
	OPENWEATHER_API_KEY = os.environ['OPENWEATHER_API_KEY']

	# update STOPCODES, OPERATORS, DIRECTIONS, STOPNAMES to add add'l stops

	STOPCODES = [13915, 13914, 14509, 14510]

	OPERATORS = ['SF','SF', 'SF', 'SF']

	DIRECTIONS = ['Inbound', 'Outbound', 'Inbound', 'Outbound']

	STOPNAMES = ['Stanyan', 'Stanyan', 'Folsom', 'Folsom']

	return()

# function to use 511org API to find next arrivals at each of the provided STOPCODES
def getNextTransit():
	secretFunc()
	arrivals = list()
	for i, stop in enumerate(STOPCODES):
		r = requests.get(TRANSIT_URL, 
						 params = {'agency': OPERATORS[i], 
								   'api_key': TRANSIT_API_KEY,
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
			time_str = pacific_datetime.strftime('%I:%M %p')
			
			# Calculte timeToArrival
			timeToArrival = pacific_datetime - currentTime
			timeToArrival = divmod(timeToArrival.seconds, 60)
			timeToArrival = f"{str(timeToArrival[0]).rjust(2,'0')}:{str(timeToArrival[1]).rjust(2,'0')}"

			# Get destination from JSON content
			destination = arrival['MonitoredVehicleJourney']['MonitoredCall']['DestinationDisplay']

			# Append [code, direction, time]  to list
			arrivals.append([STOPNAMES[i], DIRECTIONS[i], destination, time_str, timeToArrival, stop])

	# Convert nested list to DataFrame
	arrivals = pd.DataFrame(arrivals, columns=['stopnames', 'direction', 'destination','arrivalTime', 'timeToArrival', 'stopcode'])
	return(arrivals)


	''' 
	todo:
		- connect to RPLCD to print information
		- implement refreshment interval
	'''

# main function
if __name__ == '__main__':
	transitArrivals = getNextTransit()
	print(transitArrivals)