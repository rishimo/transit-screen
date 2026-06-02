#!/usr/bin/env python
"""Test all display layouts with mock or real data."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from transit_screen import config
from transit_screen.display import render_screen

output_dir = Path(__file__).parent.parent


def get_mock_weather_point_in_time() -> dict:
    """Generate realistic mock point-in-time weather data."""
    return {
        "mode": "point-in-time",
        "temp": 72.5,
        "feels_like": 71.0,
        "humidity": 65.0,
        "wind_speed": 8.5,
        "description": "Partly Cloudy",
        "icon": "partly-cloudy-day",
        "temp_max": 82.0,
        "temp_min": 58.0,
        "precip_prob": 15.0,
    }


def get_mock_weather_7d() -> dict:
    """Generate realistic mock 7-day forecast data."""
    return {
        "mode": "timeline",
        "timeline": "7d",
        "data": [
            {
                "time": 1717357200 + i * 86400,
                "temp_high": 82 - i,
                "temp_low": 62 - i,
                "icon": ("clear-day" if i % 3 == 0 else
                        "partly-cloudy-day" if i % 3 == 1 else "rain"),
                "precip_prob": (i * 10) % 80,
            }
            for i in range(7)
        ],
    }


def get_mock_weather_24h() -> dict:
    """Generate realistic mock 24-hour forecast data."""
    return {
        "mode": "timeline",
        "timeline": "24h",
        "data": [
            {
                "time": 1717330800 + i * 3600,
                "temp": 70 + ((i * 2) % 15),
                "icon": "clear-day" if i % 4 == 0 else "partly-cloudy-day",
                "precip_prob": (i * 5) % 40,
            }
            for i in range(24)
        ],
    }


def get_mock_transit() -> list[dict]:
    """Generate realistic mock transit data with 4 stops (tests 2-column layout)."""
    return [
        {
            "stop_name": "Duboce & Church",
            "direction": "Inbound",
            "destination": "Embarcadero",
            "arrival_time": "3:42 PM",
            "time_to_arrival": "05:30",
            "stop_code": 14448,
            "route_name": "N",
        },
        {
            "stop_name": "Duboce & Church",
            "direction": "Inbound",
            "destination": "Embarcadero",
            "arrival_time": "3:55 PM",
            "time_to_arrival": "18:45",
            "stop_code": 14448,
            "route_name": "N",
        },
        {
            "stop_name": "Duboce & Church",
            "direction": "Outbound",
            "destination": "Forest Hill",
            "arrival_time": "3:48 PM",
            "time_to_arrival": "11:15",
            "stop_code": 14447,
            "route_name": "43",
        },
        {
            "stop_name": "Duboce & Church",
            "direction": "Outbound",
            "destination": "Forest Hill",
            "arrival_time": "4:02 PM",
            "time_to_arrival": "25:30",
            "stop_code": 14447,
            "route_name": "43",
        },
        {
            "stop_name": "Church",
            "direction": "Inbound",
            "destination": "Embarcadero",
            "arrival_time": "4:10 PM",
            "time_to_arrival": "33:20",
            "stop_code": 15726,
            "route_name": "N",
        },
        {
            "stop_name": "Church",
            "direction": "Inbound",
            "destination": "Embarcadero",
            "arrival_time": "4:25 PM",
            "time_to_arrival": "48:15",
            "stop_code": 15726,
            "route_name": "N",
        },
        {
            "stop_name": "Church",
            "direction": "Outbound",
            "destination": "Forest Hill",
            "arrival_time": "4:15 PM",
            "time_to_arrival": "38:45",
            "stop_code": 15661,
            "route_name": "43",
        },
        {
            "stop_name": "Church",
            "direction": "Outbound",
            "destination": "Forest Hill",
            "arrival_time": "4:30 PM",
            "time_to_arrival": "53:30",
            "stop_code": 15661,
            "route_name": "43",
        },
    ]


def get_real_data() -> tuple[dict, list]:
    """Fetch real data from APIs."""
    from transit_screen.weather import get_weather
    from transit_screen.transit import get_next_transit

    print("Fetching real weather data...")
    weather = get_weather()
    print(f"  ✓ Weather: {weather.get('description', 'unknown')}")
    print(f"    Mode: {weather.get('mode')}")
    if weather.get("mode") == "point-in-time":
        print(f"    Temp: {weather.get('temp')}°F")
    elif weather.get("mode") == "timeline":
        print(f"    Timeline: {weather.get('timeline')}")

    print("Fetching real transit data...")
    transit_data = get_next_transit()
    print(f"  ✓ Got {len(transit_data)} arrivals")

    return weather, transit_data


def test_layout(name: str, weather: dict, transit_data: list) -> bool:
    """Test a layout and save output."""
    try:
        img = render_screen(weather, transit_data)
        output_path = output_dir / f"test_layout_{name}.png"
        img.save(output_path)
        print(f"  ✓ {name:20s} rendered → {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ {name:20s} failed: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test transit-screen display layouts")
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch real data from APIs instead of using mock data",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Transit Screen Layout Tests")
    print("=" * 60)
    print()

    # Get data
    if args.fetch:
        try:
            weather, transit_data = get_real_data()
        except Exception as e:
            print(f"✗ Failed to fetch real data: {e}")
            print(
                "\nTo use real data, ensure:")
            print("  - PIRATE_WEATHER_API_KEY is set in .env")
            print("  - TRANSIT_API_KEY is set in .env")
            print("  - config.yaml is properly configured")
            print("\nRunning with mock data instead...")
            weather = None
            transit_data = get_mock_transit()
    else:
        print("Using mock data (use --fetch to test with real APIs)")
        print()
        weather = None
        transit_data = get_mock_transit()

    print()

    # Test all three layouts
    results = []

    if weather is None:
        # Mock mode: always test all three layouts
        print("Testing Point-in-Time Layout:")
        results.append(
            (
                "Point-in-Time",
                test_layout("point_in_time", get_mock_weather_point_in_time(), transit_data),
            )
        )

        print("\nTesting 7-Day Timeline:")
        results.append(
            (
                "7-Day Timeline",
                test_layout("7day", get_mock_weather_7d(), transit_data),
            )
        )

        print("\nTesting 24-Hour Timeline:")
        results.append(
            (
                "24-Hour Timeline",
                test_layout("24h", get_mock_weather_24h(), transit_data),
            )
        )

    else:
        # Real data mode: test based on configured weather mode
        mode = weather.get("mode", "point-in-time")

        if mode == "point-in-time":
            print("Testing Point-in-Time Layout (configured):")
            results.append(("Point-in-Time", test_layout("point_in_time_real", weather, transit_data)))

            print("\nTesting 7-Day Timeline (synthetic):")
            results.append(("7-Day Timeline", test_layout("7day_real", get_mock_weather_7d(), transit_data)))

            print("\nTesting 24-Hour Timeline (synthetic):")
            results.append(
                ("24-Hour Timeline", test_layout("24h_real", get_mock_weather_24h(), transit_data))
            )

        else:  # timeline mode
            timeline = weather.get("timeline", "24h")

            print(f"Testing {timeline.upper()} Timeline (configured):")
            results.append((f"{timeline}-Hour", test_layout(f"{timeline}h_real", weather, transit_data)))

            if timeline != "7d":
                print("\nTesting 7-Day Timeline (synthetic):")
                results.append(("7-Day Timeline", test_layout("7day_real", get_mock_weather_7d(), transit_data)))

            if timeline != "24h":
                print("\nTesting 24-Hour Timeline (synthetic):")
                results.append(
                    ("24-Hour Timeline", test_layout("24h_real", get_mock_weather_24h(), transit_data))
                )

    print()
    print("=" * 60)
    print("Results:")
    print("=" * 60)
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")

    print()
    if all(r for _, r in results):
        print("✓ All layouts rendered successfully!")
        sys.exit(0)
    else:
        print("✗ Some layouts failed")
        sys.exit(1)
