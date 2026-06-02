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

**Quick Setup (Raspberry Pi)**

```bash
git clone https://github.com/rishimo/transit-screen.git
cd transit-screen
cp .env.example .env          # Add your API keys
cp config.example.yaml config.yaml  # Customize your config
bash scripts/setup-pi.sh       # Install deps + systemd service
```

**Manual Setup**

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
   - `PIRATE_WEATHER_API_KEY` — from [Pirate Weather](https://pirate-weather.apiable.io)
   - `TRANSIT_API_KEY` — from [511.org](https://511.org/developer-resources/transit-api)

3. Create and customize `config.yaml`:
   ```bash
   cp config.example.yaml config.yaml
   nano config.yaml
   ```

4. Install dependencies (automatically fetches Pi-compatible wheels from piwheels.org):
   ```bash
   uv sync
   ```

5. Install systemd service (for auto-start on boot):
   ```bash
   sudo cp transit-screen.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable transit-screen
   ```

## Usage

### Start the display

```bash
scripts/start.sh
```

Automatically kills any existing instance and starts the main loop. Updates every 10 minutes (600s).

The display will:
- Fetch weather from Pirate Weather API
- Fetch transit arrivals from 511.org Transit API
- Render the current layout (point-in-time or timeline)
- Write to the e-ink display (or print to console if display unavailable)
- Retry on API errors every 30 seconds
- Clear display at nightly refresh hours (if enabled in config.yaml)

### Helper Scripts

```bash
# Stop the main loop
scripts/stop.sh

# Clear the display completely
scripts/reset.sh

# Put display into low-power sleep
scripts/sleep_screen.sh

# Trigger an immediate refresh (don't wait for next 10-min cycle)
scripts/force_refresh.sh
```

### Test Integration

Test the weather and transit API integration without running the full display loop:

```bash
# Use mock data to verify rendering pipeline
uv run scripts/test_layouts.py

# Use real APIs to verify data integration
uv run scripts/test_layouts.py --fetch
```

The test script outputs `test_output.png` in the project root. Use this to:
- Verify your config.yaml is correct
- Inspect all three layout modes before deploying to Pi
- Debug API integration without the display hardware
- Confirm your transit stops and weather mode are working

**Note:** Test renders all three modes (point-in-time, 7d, 24h) in a single image for easy comparison. On the actual display, only the configured mode appears.

## Configuration

All configuration is managed in `config.yaml`. Copy `config.example.yaml` to get started:

```bash
cp config.example.yaml config.yaml
```

Then edit `config.yaml` with your settings:

### Location
```yaml
location:
  lat: 37.77144        # Your latitude
  long: -122.43230     # Your longitude
```

### Transit Stops
```yaml
transit:
  stops:
    - id: 14448                      # 511.org stop ID
      operator: SF                   # Transit operator (e.g., SF, AC)
      direction: Inbound             # Inbound or Outbound
      name: Duboce & Church          # Display name
      arrivals_shown: 2              # Number of arrivals to display (1-3)
    - id: 14447
      operator: SF
      direction: Outbound
      name: Duboce & Church
      arrivals_shown: 2
```

**Stop ID** — Find your stop ID on [511.org](https://511.org). Search for your stop, then check the URL for the numeric ID, or use the [Transit API](https://511.org/developer-resources/transit-api) to look up by coordinates.

**Arrivals shown** — Controls how many departures appear per stop (1-3). More stops or higher values may require reducing `arrivals_shown` to fit in the transit zone.

**2-column layout** — When more than 2 stops are configured, the transit section automatically splits into 2 columns to fit more data. Fewer stops remain in a single column.

### Weather Display
```yaml
weather:
  mode: point-in-time     # point-in-time or timeline
  timeline: 24h           # Ignored if mode is point-in-time
                          # Options: 7d, 12h, or 24h
```

**Modes:**
- `point-in-time` — Current weather snapshot with large temperature, "feels like", high/low temps, weather icon, and precipitation %.
- `timeline` — Forecast strip; use `timeline` option below to choose between 7-day, 12-hour, or 24-hour.

**Timeline Options** (only used when mode is `timeline`):
- `7d` — 7-day forecast with daily high/low, precip%, and weather icons.
- `12h` — 12-hour forecast with temperature trend chart, hourly icons, temps, and precip%.
- `24h` — 24-hour forecast with temperature trend chart, hourly icons, temps, and precip%.

### Trash Reminder
```yaml
reminders:
  trash:
    enabled: true                    # true or false
    days: [monday, thursday]         # Days to remind (lowercase)
```

When enabled and matching the current day, a "TAKE OUT TRASH TODAY!" banner appears at the top of the display.

Valid days: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`.

### Nightly Refresh & Display Sleep
```yaml
display:
  nightly_refresh:
    enabled: true            # true or false
    hours: [3]               # Hours (24h format) to refresh/clear display
```

When enabled, the display clears and refreshes at the specified hours to prevent e-ink burn-in. For example, `hours: [3]` clears at 3 AM daily.

### Environment Variables

Create a `.env` file (copy from `.env.example`) with your API keys:

```bash
PIRATE_WEATHER_API_KEY=your_key_here
TRANSIT_API_KEY=your_key_here
```

- **PIRATE_WEATHER_API_KEY** — Get free key at [Pirate Weather](https://pirate-weather.apiable.io)
- **TRANSIT_API_KEY** — Get free key at [511.org Developer Resources](https://511.org/developer-resources/transit-api)

## Display Layout

The display is 800×480 pixels (Waveshare 7.5" V2). Layout depends on weather mode:

### Point-in-Time Mode
Current weather snapshot with detailed temperature breakdown.

```
+----------------------------------+-----+  ← Trash banner (if enabled today)
|                                  |     |
|  [Icon]  Description   Large°F   |     |
|          Precipitation%  Feels°F  |UPDA |
|                         Hi / Lo   |TED  |
|                                  | box |
+----------------------------------+-----+
|  IN  Stop Name:  ⬤N 3:42 PM | ⬤N 3:55 PM  |
|  OUT Stop Name:  ⬤43 3:48 PM | ⬤43 4:02 PM |
|  ...                                     |
+------------------------------------------+
```

**Weather section** (left of UPDATED box):
- Large current temperature (font 160) centered at top
- "Feels like" and high/low temps to the right
- Weather icon, description, and precipitation % to the right
- All within 52px from top through line at y=310

**Transit section** (left of UPDATED box):
- One row per configured stop
- Format: `DIR STOPNAME: ⬤ROUTE TIME | ⬤ROUTE TIME`
  - DIR = "IN" or "OUT" (inbound/outbound)
  - STOPNAME = configured stop name
  - ⬤ = Route glyph (black circle with white route number/letter)
  - Splits into 2 columns if more than 2 stops

**UPDATED box** (bottom-right, 170×170):
- Black background, white text
- "UPDATED" label + current time (HH:MM)

### 7-Day Timeline Mode
Full-width forecast strip, 7 columns (one per day).

```
+--+ +--+ +--+ +--+ +--+ +--+ +--+  +-----+
|Mo| |Tu| |We| |Th| |Fr| |Sa| |Su|  |UPDA |
|  | |  | |  | |  | |  | |  | |  |  |TED  |
|☀️ | |⛅| |☁️ | |☁️ | |🌧️ | |⛈️ | |☀️ |  | box |
|  | |  | |  | |  | |  | |  | |  |  |     |
|↑85°|↑82°|↑75°|↑73°|↑68°|↑70°|↑79°|  |     |
|↓60°|↓58°|↓52°|↓48°|↓45°|↓47°|↓55°|  |     |
| 0%| 10%|  5%| 35%| 90%| 80%|  0%|  |     |
+--+ +--+ +--+ +--+ +--+ +--+ +--+  +-----+
|  Transit section (full width)           |
+------------------------------------------+
```

- Today's column is highlighted (inverted header: white text on black background)
- Each column shows: day label, weather icon, high/low, precip%
- Vertical dividers between days

### 24h/12h Hourly Timeline Mode
Hourly forecast with temperature trend chart.

```
+--+--+--+--+--+--+--+--+--+--+--+--+-----+
|              Temperature Trend          |UPDA|
|                                      /╲ |TED |
|                            /╲  /╲  /  ╲ | box|
|                  /╲      /    ╲ ╱╲ ╱  ╲ |    |
|   ╱╲            ╱  ╲    ╱      ╲╱  ╲╱   | b. |
| ╱    ╲        ╱    ╲╱                   |    |
+--+--+--+--+--+--+--+--+--+--+--+--+-----+
|1a|3a|5a|7a|9a|11a|1p|3p|5p|7p|9p|11p|
| ☀️ | ☀️ | ⛅ | ⛅ | ☁️ | ☁️ | 🌧️ | 🌧️ | 🌧️ | ⛈️ | ⛈️ | 🌧️ |
|72°|70°|68°|75°|78°|80°|75°|72°|68°|65°|62°|63°|
| 0%| 0%| 0%| 5%| 0%|10%|40%|60%|80%|90%|85%|75%|
+--+--+--+--+--+--+--+--+--+--+--+--+-----+
|  Transit section (full width)           |
+------------------------------------------+
```

- Temperature chart at top spans full width (black line with data point markers)
- 12 hourly columns below chart
- Each column shows: time, weather icon, temperature, precip%
- Vertical dividers between hours

### Trash Banner
When enabled and matching the current day:
```
+--+ "TAKE OUT TRASH TODAY!" (white text on black) +--+
```
Reserved space at the top of all layouts (42px). If disabled, space shows as blank.

### Layout Constants (in `display/utils.py`)
- **BANNER_HEIGHT** = 42px — trash reminder banner
- **TOP_OFFSET** = 52px — start of weather content (below banner)
- **SEPARATOR_Y** = 310px — dotted line separating weather/transit
- **TRANSIT_Y_START** = 310px — start of transit section
- **UPDATED box** = 170×170px, bottom-right corner

## Running on Startup

### Option 1: systemd Service (Recommended)

Create a systemd service to automatically start on boot with auto-restart on failure:

1. Copy the service file to systemd:
   ```bash
   sudo cp transit-screen.service /etc/systemd/system/
   ```

2. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable transit-screen
   sudo systemctl start transit-screen
   ```

3. Check status:
   ```bash
   sudo systemctl status transit-screen
   ```

4. View logs:
   ```bash
   sudo journalctl -u transit-screen -f  # follow logs in real-time
   sudo journalctl -u transit-screen -n 50  # last 50 lines
   ```

5. Stop or restart:
   ```bash
   sudo systemctl stop transit-screen
   sudo systemctl restart transit-screen
   ```

**Notes:**
- Service automatically restarts if the process crashes (with 10s delay)
- Logs are written to systemd journal instead of a file
- Service runs as the `pi` user by default (change in `.service` file if needed)
- Requires `uv` to be installed in `~/.local/bin/` (standard for `uv` on Linux)

### Option 2: crontab

If you prefer crontab, add to your crontab:

```bash
crontab -e
```

Add the line:

```
@reboot /home/pi/transit-screen/scripts/start.sh
```

This is simpler but won't auto-restart if the process crashes.

## Project Structure

```
transit-screen/
├── transit_screen/          # Main package
│   ├── main.py              # Orchestration loop
│   ├── config.py            # Configuration loader (reads config.yaml)
│   ├── weather.py           # Pirate Weather API integration
│   ├── transit.py           # 511.org Transit API integration
│   └── display/             # Display rendering module
│       ├── __init__.py      # Main entry point (render_screen, display control)
│       ├── utils.py         # Shared utilities (layout constants, drawing helpers)
│       ├── point_in_time.py # Point-in-time weather snapshot rendering
│       ├── timeline_7day.py # 7-day forecast rendering
│       └── timeline_hourly.py # 12h/24h hourly forecast rendering
├── scripts/                 # Helper scripts
│   ├── start.sh             # Start the main loop
│   ├── stop.sh              # Stop the main loop
│   ├── reset.sh             # Clear the display
│   ├── force_refresh.sh     # Trigger immediate refresh
│   ├── sleep_screen.sh      # Put display to sleep
│   └── test_layouts.py      # Test script (renders all modes)
├── lib/                     # Waveshare display drivers
├── assets/
│   ├── font/                # TrueType font
│   └── icons/               # Pirate Weather icon PNGs
├── config.yaml              # Main configuration (location, stops, weather mode)
├── config.example.yaml      # Configuration template
├── .env                     # API keys (PIRATE_WEATHER_API_KEY, TRANSIT_API_KEY)
├── .env.example             # Environment template
└── pyproject.toml           # UV dependencies & project metadata
```

## Troubleshooting

### Display not updating
- Check that `scripts/start.sh` is running: `ps aux | grep main.py`
- Verify `.env` has valid API keys
- Check `config.yaml` has correct location coordinates and stop IDs
- Run `uv run scripts/test_layouts.py --fetch` to test APIs directly
- Monitor system logs for errors

### Weather or transit data missing
- Verify API keys in `.env` file (copy from `.env.example` if needed)
- Check `config.yaml` coordinates are valid (run `test_layouts.py --fetch`)
- For transit: verify stop IDs are correct (search on [511.org](https://511.org))
- Transit API may be unavailable; check [511.org status](https://511.org/status)

### Display showing old data
- Force immediate refresh: `scripts/force_refresh.sh`
- Stop and restart: `scripts/stop.sh && scripts/start.sh`
- Check refresh interval in main.py (default 600s / 10 min)

## Contributing

This project started as a fork of [James Howard's e_paper_weather_display](https://github.com/AbnormalDistributions/e_paper_weather_display) and has been significantly extended with:
- Pirate Weather API integration
- Modular display layout system
- YAML-based configuration
- Multi-stop transit support
- Test integration script

## Future Enhancements

- Web-based configurator for settings
- Additional display modes (calendar, air quality, etc.)
- Home Assistant integrations
- Historical weather tracking
- Multi-day transit alerts

## API References

- [Pirate Weather API](https://pirate-weather.apiable.io) — Weather data (free tier available)
- [511.org Transit API](https://511.org/developer-resources/transit-api) — Bay Area transit (SF, AC, etc.)
- [Waveshare 7.5" V2 Display Docs](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT)
- [PIL/Pillow](https://python-pillow.org/) — Image rendering library