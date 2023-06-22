import requests
from dotenv import load_dotenv
import os
import json
import pandas as pd
import datetime

load_dotenv()
global URL 
global api_key
global stopcodes # stopcodes intrinsically defines the destination as SF-bound
global operator
URL = os.getenv('URL')
api_key = os.getenv('api_key')
stopcodes = os.getenv('stopcodes')
operator = os.getenv('operator')

stopcodes = stopcodes.split(',')
for i in range(len(stopcodes)):
    stopcodes[i] = stopcodes[i].strip()
    print(stopcodes)
    
for stop in stopcodes:
    r = requests.get(f'{URL}/StopMonitoring', 
                        params = {'agency': operator, 
                                'api_key': api_key,
                                'stopcode': stop})
    
    content = json.loads(r.content)
    stopinfo = pd.DataFrame.from_records(content)
    stopinfo = stopinfo['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']

    for arrival in stopinfo:
        print(arrival['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime'], arrival['MonitoredVehicleJourney']['MonitoredCall']['DestinationDisplay']) # standard time of next 3 projected arrivals for specified stop