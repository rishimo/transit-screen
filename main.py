import requests
from dotenv import load_dotenv
import os
import json
import pandas as pd

# define secrets

def secretFunc():
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
    
    return()

# use 511org API to find next arrival at each of the provided stopcodes
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
            arrivalTime = arrival['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
            arrivalDirection = arrival['MonitoredVehicleJourney']['MonitoredCall']['DestinationDisplay']

            arrivals.append([arrivalDirection, arrivalTime])
            # UNIVERSAL time of next 3 projected arrivals for specified stop
    return(arrivals)


    ''' 
    todo:
        - save arrival times in some pd object
        - parse nextVehicle for each direction (est. time, etc.)
        - connect to RPLCD to print information
        - implement refreshment interval
        - multiple functions for multiple services? additional stops?
            - consider making more stop information easily addable
        - expansion: large e-ink screen with this info and weather and daily calendar    
    '''
    return()

if __name__ == '__main__':
    secretFunc()
    arrivals = getNextTransit(stopcodes)
    print(arrivals)