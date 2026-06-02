#!/usr/bin/env python3
"""Inspect raw 511.org transit API response to find short route codes."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from transit_screen import config


def inspect_transit_response():
    """Fetch raw transit API response for first stop and inspect all available fields."""
    if not config.STOPS:
        print("No stops configured in config.yaml")
        return

    stop = config.STOPS[0]
    print(f"\nFetching transit data for: {stop['name']} ({stop['direction']})")
    print(f"Stop ID: {stop['id']}, Operator: {stop['operator']}\n")

    r = requests.get(
        "http://api.511.org/transit/StopMonitoring/",
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

    if not stop_visits:
        print("No arrivals found")
        return

    print(f"Found {len(stop_visits)} arrivals\n")

    # Inspect first arrival in detail
    visit = stop_visits[0]
    journey = visit["MonitoredVehicleJourney"]
    call = journey["MonitoredCall"]

    print("="*80)
    print("FIRST ARRIVAL - Full MonitoredVehicleJourney object:")
    print("="*80)
    print(json.dumps(journey, indent=2)[:2000])  # First 2000 chars

    print("\n" + "="*80)
    print("KEY FIELDS TO CONSIDER FOR ROUTE CODE:")
    print("="*80)

    # Try different fields that might contain the route code
    fields_to_check = [
        "PublishedLineName",
        "LineRef",
        "OperatorRef",
        "VehicleRef",
        "CourseOfJourneyRef",
        "DatedVehicleJourneyRef",
    ]

    for field in fields_to_check:
        value = journey.get(field)
        if value:
            print(f"  {field}: {value}")

    # Check MonitoredCall fields too
    print("\nMonitoredCall fields:")
    call_fields_to_check = [
        "StopPointRef",
        "DestinationDisplay",
        "ArrivalProximityText",
    ]
    for field in call_fields_to_check:
        value = call.get(field)
        if value:
            print(f"  {field}: {value}")

    # Show all arrivals and their PublishedLineName values
    print("\n" + "="*80)
    print("ALL ARRIVALS - PublishedLineName and LineRef:")
    print("="*80)
    for i, visit in enumerate(stop_visits[:5]):  # Show first 5
        journey = visit["MonitoredVehicleJourney"]
        published = journey.get("PublishedLineName", "N/A")
        lineref = journey.get("LineRef", "N/A")
        call = journey["MonitoredCall"]
        dest = call.get("DestinationDisplay", "?")
        print(f"\n  [{i+1}] {published} → {dest}")
        print(f"       LineRef: {lineref}")


if __name__ == "__main__":
    inspect_transit_response()
