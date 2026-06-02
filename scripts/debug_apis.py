#!/usr/bin/env python3
"""Debug script to inspect API requests and responses."""
import json
import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).parent.parent))

from transit_screen import config
from transit_screen.weather import get_weather
from transit_screen.transit import get_next_transit


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print('='*80)


def debug_weather() -> None:
    """Fetch and inspect weather data."""
    print_section("PIRATE WEATHER API")

    print(f"\nRequest URL: https://api.pirateweather.net/forecast/{config.PIRATE_WEATHER_API_KEY}/{config.LAT},{config.LONG}")
    print(f"Parameters: units=us")

    try:
        weather_data = get_weather()

        print(f"\nResponse mode: {weather_data.get('mode')}")
        print(f"Response keys: {list(weather_data.keys())}")

        if weather_data.get('mode') == 'point-in-time':
            print("\n--- POINT-IN-TIME DATA ---")
            for key in ['temp', 'feels_like', 'temp_max', 'temp_min', 'humidity',
                       'wind_speed', 'description', 'icon', 'precip_prob']:
                print(f"  {key}: {weather_data.get(key)}")
        else:
            timeline = weather_data.get('timeline')
            print(f"\n--- TIMELINE DATA ({timeline}) ---")
            print(f"  Timeline: {timeline}")
            print(f"  Data points: {len(weather_data.get('data', []))}")

            # Show first and last data point
            data = weather_data.get('data', [])
            if data:
                print("\n  First forecast:")
                pprint(data[0], width=120)
                if len(data) > 1:
                    print("\n  Last forecast:")
                    pprint(data[-1], width=120)

        print("\n✓ Weather API successful")

    except Exception as e:
        print(f"\n✗ Weather API failed: {e}")
        import traceback
        traceback.print_exc()


def debug_transit() -> None:
    """Fetch and inspect transit data."""
    print_section("511.ORG TRANSIT API")

    print(f"\nConfigured stops ({len(config.STOPS)}):")
    for stop in config.STOPS:
        print(f"  - {stop['name']} ({stop['direction']}): ID={stop['id']}, operator={stop['operator']}")

    try:
        transit_data = get_next_transit()

        if not transit_data:
            print("\n⚠ No transit data returned")
            return

        print(f"\nResponse arrivals: {len(transit_data)}")
        print(f"Keys in first arrival: {list(transit_data[0].keys()) if transit_data else 'N/A'}")

        # Group by stop for inspection
        stops_seen = {}
        for arrival in transit_data:
            key = (arrival.get('stop_code'), arrival.get('direction'))
            if key not in stops_seen:
                stops_seen[key] = []
            stops_seen[key].append(arrival)

        print(f"\nArrivals by stop (grouped):")
        for (stop_code, direction), arrivals in sorted(stops_seen.items()):
            print(f"\n  Stop {stop_code} ({direction}): {len(arrivals)} arrivals")
            for i, arrival in enumerate(arrivals[:3]):  # Show first 3
                print(f"    [{i+1}]")
                for key, val in sorted(arrival.items()):
                    print(f"        {key}: {val}")

        print("\n✓ Transit API successful")

    except Exception as e:
        print(f"\n✗ Transit API failed: {e}")
        import traceback
        traceback.print_exc()


def debug_config() -> None:
    """Show current configuration."""
    print_section("CONFIGURATION")

    print(f"\nLocation: {config.LAT}, {config.LONG}")
    print(f"Weather mode: {config.WEATHER_MODE}")
    if config.WEATHER_MODE == 'timeline':
        print(f"Timeline: {config.WEATHER_TIMELINE}")
    print(f"Trash enabled: {config.TRASH_ENABLED}")
    if config.TRASH_ENABLED:
        print(f"Trash days: {config.TRASH_DAYS}")
    print(f"Nightly refresh: {config.NIGHTLY_REFRESH_ENABLED}")
    if config.NIGHTLY_REFRESH_ENABLED:
        print(f"Nightly refresh hours: {config.NIGHTLY_REFRESH_HOURS}")

    print(f"\nTransit stops ({len(config.STOPS)}):")
    for stop in config.STOPS:
        print(f"  - {stop['name']} ({stop['direction']})")
        print(f"      ID: {stop['id']}, operator: {stop['operator']}, arrivals: {stop['arrivals_shown']}")


if __name__ == "__main__":
    debug_config()
    debug_weather()
    debug_transit()
