# Transit Screen

Display real-time transit arrivals and weather on a Waveshare 7.5" e-ink display.

This project is based on James Howard's [e_paper_weather_display](https://github.com/AbnormalDistributions/e_paper_weather_display) project.

## Hardware

- Raspberry Pi Zero W
- Waveshare 7.5" V2 e-paper display (800×480, black & white)
- Picture frame with mounting hardware

## Setup

### Prerequisites

- Python 3.13+
- `uv` package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rishimo/transit-screen.git
   cd transit-screen
   ```

2. Create a `.env` file with your API keys (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add:
   - `OPENWEATHER_API_KEY` — from [OpenWeatherMap](https://openweathermap.org/api)
   - `TRANSIT_API_KEY` — from [511.org](https://511.org/developer-resources/transit-api)
   - `LAT`, `LONG` — your coordinates (defaults: San Francisco)

3. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

### Start the display

```bash
scripts/start.sh
```

Automatically kills any existing instance and starts the main loop. Updates every 10 minutes.

### Helper Scripts

```bash
# Stop the display
scripts/stop.sh

# Clear the display
scripts/reset.sh

# Put display to sleep (low power)
scripts/sleep_screen.sh

# Force an immediate refresh (don't wait 10 min)
scripts/force_refresh.sh
```

## Configuration

Edit `transit_screen/config.py` to customize:

- **Stop codes** — which transit stops to monitor (`STOP_CODES`)
- **Operators** — transit agencies (`OPERATORS`)
- **Directions** — inbound/outbound (`DIRECTIONS`)
- **Stop names** — display labels (`STOP_NAMES`)
- **Refresh interval** — seconds between updates (default: 600)
- **CSV logging** — log weather data to `records.csv` (default: off)

## Display Layout

The e-ink display shows:

- **Top-left**: Weather icon + description + precipitation %
- **Top-right**: Large current temperature + "feels like"
- **Bottom-left**: High/low temperatures
- **Bottom-middle**: Next 2 transit arrivals
- **Bottom-right**: "UPDATED" timestamp (white on black)
- **Top bar** (Mon/Thu): "TAKE OUT TRASH TODAY!" reminder

Auto-clears screen at 3 AM daily to prevent burn-in.

## Running on Startup

Add to crontab on the Pi:

```bash
crontab -e
```

Add the line:

```
@reboot /home/pi/transit-screen/scripts/start.sh
```

Replace path as needed.

## Project Structure

```
transit-screen/
├── transit_screen/          # Main package
│   ├── main.py              # Orchestration loop
│   ├── config.py            # Configuration
│   ├── weather.py           # OpenWeatherMap API
│   ├── transit.py           # 511.org transit API
│   └── display.py           # Rendering & display control
├── scripts/                 # Helper scripts
├── lib/                     # Waveshare display drivers
├── assets/
│   ├── font/                # Fonts
│   ├── icons/               # Weather icons
│   └── template.png         # Base display template
└── records.csv              # Optional weather log
```

## Future Enhancements

- Web-based configurator for tile layout
- Additional tiles: calendar, clock, QOTD, Home Assistant integrations
- Configurable stop codes via web UI
- Historical weather tracking

## API References

- [OpenWeatherMap One Call API](https://openweathermap.org/api/one-call-api)
- [511.org Transit API](https://511.org/developer-resources/transit-api)
- [Waveshare 7.5" Display Docs](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT)