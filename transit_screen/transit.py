import json
from datetime import datetime, timezone

import requests
from dateutil import tz

from . import config

TRANSIT_URL = "http://api.511.org/transit/StopMonitoring/"


def get_next_transit() -> list[dict]:
    """Fetch next arrivals for all configured stops. Returns list of arrival dicts."""
    arrivals = []
    pacific_tz = tz.gettz("America/Los_Angeles")
    utc_tz = tz.gettz("UTC")

    for stop in config.STOPS:
        r = requests.get(
            TRANSIT_URL,
            params={
                "agency": stop["operator"],
                "api_key": config.TRANSIT_API_KEY,
                "stopcode": stop["id"],
            },
        )
        content = json.loads(r.content)
        stop_visits = (
            content["ServiceDelivery"]["StopMonitoringDelivery"]["MonitoredStopVisit"]
        )

        for visit in stop_visits[: stop["arrivals_shown"]]:
            journey = visit["MonitoredVehicleJourney"]
            call = journey["MonitoredCall"]
            arrival_iso = call["ExpectedArrivalTime"]

            utc_dt = datetime.fromisoformat(arrival_iso.rstrip("Z")).replace(tzinfo=utc_tz)
            pacific_dt = utc_dt.astimezone(pacific_tz)
            now_utc = datetime.now(timezone.utc)

            time_str = pacific_dt.strftime("%I:%M %p")
            delta = pacific_dt - now_utc
            mins, secs = divmod(max(0, int(delta.total_seconds())), 60)
            time_to_arrival = f"{str(mins).rjust(2, '0')}:{str(secs).rjust(2, '0')}"

            route_name = journey.get("PublishedLineName") or journey.get("LineRef", "?")

            arrivals.append(
                {
                    "stop_name": stop["name"],
                    "direction": stop["direction"],
                    "destination": call["DestinationDisplay"],
                    "arrival_time": time_str,
                    "time_to_arrival": time_to_arrival,
                    "stop_code": stop["id"],
                    "route_name": route_name,
                }
            )

    return arrivals
