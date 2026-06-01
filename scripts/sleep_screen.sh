#!/bin/bash
uv run python << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transit_screen.display import sleep_display
from transit_screen import config
from waveshare_epd import epd7in5_V2

epd = epd7in5_V2.EPD()
sleep_display(epd)
print('Display put to sleep')
EOF
