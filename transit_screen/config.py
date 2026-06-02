import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TRANSIT_API_KEY: str = os.environ["TRANSIT_API_KEY"]
PIRATE_WEATHER_API_KEY: str = os.environ["PIRATE_WEATHER_API_KEY"]
LAT: str = os.environ["LAT"]
LONG: str = os.environ["LONG"]

STOP_CODES: list[int] = [13915, 13914, 14509, 14510]
OPERATORS: list[str] = ["SF", "SF", "SF", "SF"]
DIRECTIONS: list[str] = ["Inbound", "Outbound", "Inbound", "Outbound"]
STOP_NAMES: list[str] = ["Stanyan", "Stanyan", "Folsom", "Folsom"]

REFRESH_INTERVAL: int = 600  # seconds between display updates
ERROR_RETRY_INTERVAL: int = 30
CSV_OPTION: bool = False

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LIB_DIR = Path(__file__).parent.parent / "lib"
