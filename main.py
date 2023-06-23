import requests
from dotenv import load_dotenv
import os
import json
import pandas as pd
from datetime import datetime
from dateutil import tz

# function to load secrets
def secretFunc():
    load_dotenv()
    global URL 
    global api_key
    global stopcodes # stopcodes define a direction already
    global operator
    URL = os.getenv('URL')
    api_key = os.getenv('api_key')
    stopcodes = os.getenv('stopcodes')
    operator = os.getenv('operator')

    stopcodes = stopcodes.split(',')
    for i in range(len(stopcodes)):
        stopcodes[i] = stopcodes[i].strip()
    
    return()

# function to use 511org API to find next arrivals
# at each of the provided stopcodes
def getNextTransit(stopcodes):
    arrivals = list()
    for stop in stopcodes:
        r = requests.get(f'{URL}/StopMonitoring', 
                         params = {'agency': operator, 
                                   'api_key': api_key,
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

            # Set the UTC timezone for the datetime object
            utc_datetime = utc_datetime.replace(tzinfo=utc_tz)

            # Convert the datetime object to Pacific time
            pacific_datetime = utc_datetime.astimezone(pacific_tz)

            # Format the datetime object as a 12-hour time string
            time_str = pacific_datetime.strftime('%I:%M:%S %p')

            # Get arrivalDirection from JSON content
            arrivalDirection = arrival['MonitoredVehicleJourney']['MonitoredCall']['DestinationDisplay']

            # Append [direction, time] pair to list
            arrivals.append([arrivalDirection, time_str])

            # UNIVERSAL time of next 3 projected arrivals for specified stop

    # Convert nested list to DataFrame
    arrivals = pd.DataFrame(arrivals, columns=['arrivalDirection','arrivalTime'])
    return(arrivals)


    ''' 
    todo:
        - connect to RPLCD to print information
        - implement refreshment interval
    '''
    return()

if __name__ == '__main__':
    secretFunc()
    transitArrivals = getNextTransit(stopcodes)
    print(transitArrivals)