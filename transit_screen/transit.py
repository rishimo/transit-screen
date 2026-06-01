import json
import requests
from datetime import datetime, timezone
from dateutil import tz

from . import config

TRANSIT_URL = "http://api.511.org/transit/StopMonitoring/"


def get_next_transit() -> list[dict]:
    """Fetch next arrivals for all configured stops. Returns list of arrival dicts."""
    arrivals = []
    pacific_tz = tz.gettz("America/Los_Angeles")
    utc_tz = tz.gettz("UTC")

    for i, stop in enumerate(config.STOP_CODES):
        r = requests.get(
            TRANSIT_URL,
            params={
                "agency": config.OPERATORS[i],
                "api_key": config.TRANSIT_API_KEY,
                "stopcode": stop,
            },
        )
        content = json.loads(r.content)
        stop_visits = (
            content["ServiceDelivery"]["StopMonitoringDelivery"]["MonitoredStopVisit"]
        )

        for visit in stop_visits:
            call = visit["MonitoredVehicleJourney"]["MonitoredCall"]
            arrival_iso = call["ExpectedArrivalTime"]

            utc_dt = datetime.fromisoformat(arrival_iso.rstrip("Z")).replace(tzinfo=utc_tz)
            pacific_dt = utc_dt.astimezone(pacific_tz)
            now_utc = datetime.now(timezone.utc)

            time_str = pacific_dt.strftime("%I:%M %p")
            delta = pacific_dt - now_utc
            mins, secs = divmod(max(0, int(delta.total_seconds())), 60)
            time_to_arrival = f"{str(mins).rjust(2, '0')}:{str(secs).rjust(2, '0')}"

            arrivals.append(
                {
                    "stop_name": config.STOP_NAMES[i],
                    "direction": config.DIRECTIONS[i],
                    "destination": call["DestinationDisplay"],
                    "arrival_time": time_str,
                    "time_to_arrival": time_to_arrival,
                    "stop_code": stop,
                }
            )

    return arrivals
