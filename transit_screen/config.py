import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

TRANSIT_API_KEY: str = os.environ["TRANSIT_API_KEY"]
PIRATE_WEATHER_API_KEY: str = os.environ["PIRATE_WEATHER_API_KEY"]

config_path = Path(__file__).parent.parent / "config.yaml"
with open(config_path) as f:
    app_config = yaml.safe_load(f)

LAT: float = app_config["location"]["lat"]
LONG: float = app_config["location"]["long"]

STOPS: list[dict] = app_config["transit"]["stops"]

WEATHER_MODE: str = app_config["weather"]["mode"]
WEATHER_TIMELINE: str = app_config["weather"]["timeline"]

TRASH_ENABLED: bool = app_config["reminders"]["trash"]["enabled"]
_trash_days_names = app_config["reminders"]["trash"]["days"]
_day_map = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
TRASH_DAYS: list[int] = [_day_map[day.lower()] for day in _trash_days_names]

NIGHTLY_REFRESH_ENABLED: bool = app_config["display"]["nightly_refresh"]["enabled"]
NIGHTLY_REFRESH_HOURS: list[int] = app_config["display"]["nightly_refresh"]["hours"]

REFRESH_INTERVAL: int = 600
ERROR_RETRY_INTERVAL: int = 30
CSV_OPTION: bool = False

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LIB_DIR = Path(__file__).parent.parent / "lib"
