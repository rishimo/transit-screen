import csv
import sys
import time
from datetime import datetime
from pathlib import Path

from . import config
from .display import clear_display, render_screen, show_error, write_to_display
from .transit import get_next_transit
from .weather import get_weather

sys.path.insert(0, str(config.LIB_DIR))
try:
    from waveshare_epd import epd7in5_V2
except (OSError, ImportError):
    epd7in5_V2 = None


def main():
    if epd7in5_V2 is None:
        print("Warning: Display driver not available (running in test mode)")
        epd = None
    else:
        epd = epd7in5_V2.EPD()

    if epd is not None:
        print("Initializing and clearing screen.")
        epd.init()
        epd.Clear()
    else:
        print("Display not available - running in test mode")

    records_file = Path(__file__).parent.parent / "records.csv"

    while True:
        try:
            print("Attempting to fetch weather...")
            weather_data = get_weather()
            print("Weather fetch successful.")

            try:
                print("Attempting to fetch transit data...")
                transit_data = get_next_transit()
                print(f"Transit fetch successful ({len(transit_data)} arrivals).")
            except Exception as e:
                print(f"Transit fetch failed: {e}")
                transit_data = []

            image = render_screen(weather_data, transit_data)
            write_to_display(epd, image)

            if config.CSV_OPTION:
                with open(records_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            datetime.now().strftime("%Y"),
                            datetime.now().strftime("%m"),
                            datetime.now().strftime("%d"),
                            datetime.now().strftime("%H:%M"),
                            "San Francisco, CA",
                            weather_data["temp"],
                            weather_data["feels_like"],
                            weather_data["temp_max"],
                            weather_data["temp_min"],
                            weather_data["humidity"],
                            weather_data["precip_prob"],
                            weather_data["wind_speed"],
                        ]
                    )
                print("Weather data appended to CSV.")

            current_hour = int(datetime.now().strftime("%H"))
            if config.NIGHTLY_REFRESH_ENABLED and current_hour in config.NIGHTLY_REFRESH_HOURS:
                print("Clearing screen to avoid burn-in.")
                clear_display(epd)
                time.sleep(3600)
            else:
                print(f"Sleeping for {config.REFRESH_INTERVAL} seconds.")
                if Path("/tmp/transit_screen_refresh").exists():
                    Path("/tmp/transit_screen_refresh").unlink()
                    print("Force refresh requested, skipping sleep.")
                else:
                    time.sleep(config.REFRESH_INTERVAL)

        except KeyboardInterrupt:
            print("Shutting down...")
            if epd is not None:
                epd.sleep()
            break
        except Exception as e:
            print(f"Error: {e}")
            try:
                show_error(epd, "CONNECTION" if "requests" in str(type(e)) else "HTTP")
                time.sleep(config.ERROR_RETRY_INTERVAL)
            except Exception:
                time.sleep(config.ERROR_RETRY_INTERVAL)


if __name__ == "__main__":
    main()
