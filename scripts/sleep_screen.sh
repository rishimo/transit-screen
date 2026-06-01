#!/bin/bash
uv run python -c "
import sys
sys.path.insert(0, '.')
from transit_screen.display import sleep_display
from transit_screen import config
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()
sleep_display(epd)
print('Display put to sleep')
"
