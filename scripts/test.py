#!/usr/bin/env python3
"""Integration test: verify weather/transit providers and render output."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from transit_screen.display import render_screen
from transit_screen.transit import get_next_transit
from transit_screen.weather import get_weather


def test_weather():
    """Fetch and validate weather data."""
    print("🌤️  Testing weather provider...")
    try:
        weather = get_weather()
        required_keys = [
            "temp",
            "feels_like",
            "humidity",
            "wind_speed",
            "description",
            "icon",
            "temp_max",
            "temp_min",
            "precip_prob",
        ]
        missing = [k for k in required_keys if k not in weather]
        if missing:
            print(f"  ❌ Missing keys: {missing}")
            return None
        for key in required_keys:
            val = weather[key]
            if val is None:
                print(f"  ❌ {key} is None")
                return None
        print("  ✓ Weather data:")
        print(f"    - Temp: {weather['temp']:.0f}°F (feels like {weather['feels_like']:.0f}°F)")
        print(f"    - {weather['description'].title()} | Precip: {weather['precip_prob']:.0f}%")
        print(f"    - High/Low: {weather['temp_max']:.0f}°F / {weather['temp_min']:.0f}°F")
        print(f"    - Icon: {weather['icon']}")
        return weather
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")
        return None


def test_transit():
    """Fetch transit data (non-critical if it fails)."""
    print("🚌 Testing transit provider...")
    try:
        transit = get_next_transit()
        print(f"  ✓ Got {len(transit)} transit arrivals")
        for i, arrival in enumerate(transit[:2], 1):
            print(f"    - {arrival.get('stop_name', 'N/A')}: {arrival.get('arrival_time', 'N/A')}")
        return transit
    except Exception as e:
        print(f"  ⚠️  Transit unavailable ({type(e).__name__}): {e}")
        print("  (proceeding with empty transit data)")
        return []


def test_render(weather, transit):
    """Render screen and save output."""
    print("🎨 Rendering output...")
    try:
        image = render_screen(weather, transit)
        output_dir = Path(__file__).parent.parent
        png_path = output_dir / "test_output.png"
        bmp_path = output_dir / "test_output.bmp"
        image.save(png_path)
        image.save(bmp_path)
        print(f"  ✓ Saved {png_path.name} and {bmp_path.name}")
        return True
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Transit Screen Integration Test")
    print("=" * 50)
    weather = test_weather()
    if weather is None:
        print("\n❌ Weather test failed. Aborting.")
        return 1
    print()
    transit = test_transit()
    print()
    if not test_render(weather, transit):
        print("\n❌ Render test failed.")
        return 1
    print("\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
