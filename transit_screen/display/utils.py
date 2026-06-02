"""Shared display utilities and constants."""

import sys
from datetime import datetime

from PIL import Image, ImageFont

from .. import config

sys.path.insert(0, str(config.LIB_DIR))

# Color constants
BLACK = "rgb(0,0,0)"
WHITE = "rgb(255,255,255)"

# Layout constants
BANNER_HEIGHT = 42
BANNER_MARGIN = 10
TOP_OFFSET = BANNER_HEIGHT + BANNER_MARGIN  # 52px

# Consistent spacing for all layouts
TRANSIT_Y_START = 310
BOX_HEIGHT = 170
BOX_Y_START = TRANSIT_Y_START
BOX_Y_END = 480
SEPARATOR_Y = 310


def get_fonts() -> dict:
    """Load fonts at various sizes."""
    font_path = config.ASSETS_DIR / "font" / "Font.ttc"
    return dict(
        [(size, ImageFont.truetype(str(font_path), size)) for size in range(1, 200)]
    )


def draw_dotted_line(
    draw, x1: int, y: int, x2: int, dash_width: int = 2, gap_width: int = 2
) -> None:
    """Draw a dotted horizontal line."""
    x = x1
    while x < x2:
        draw.line((x, y, min(x + dash_width, x2), y), fill=BLACK)
        x += dash_width + gap_width


def draw_droplet(draw, x: int, y: int, size: int = 4) -> None:
    """Draw a small droplet circle icon."""
    draw.ellipse((x - size, y - size - 7, x + size, y + size), fill=BLACK)


def draw_route_glyph(draw, cx: int, cy: int, route: str, font) -> None:
    """Draw a filled black circle with white route text centered."""
    radius = 14
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=BLACK)
    draw.text((cx, cy), route, font=font, fill=WHITE, anchor="mm")


def draw_temp_chart(
    draw, forecast_data: list[dict], y_start: int = 5, y_end: int = 80
) -> None:
    """Draw temperature trend line chart with data points."""
    if len(forecast_data) < 2:
        return

    temps = [h["temp"] for h in forecast_data]
    temp_min = min(temps)
    temp_max = max(temps)
    temp_range = max(1, temp_max - temp_min)

    # Calculate points
    points = []
    for i, hour in enumerate(forecast_data):
        x = (i / (len(forecast_data) - 1)) * 800
        y = y_end - ((hour["temp"] - temp_min) / temp_range) * (y_end - y_start)
        points.append((x, y))

    # Draw line connecting points
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=BLACK, width=1)

    # Draw data points at each hour
    for x, y in points:
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=BLACK)


def draw_updated_box(draw, fonts, y_start: int = BOX_Y_START) -> None:
    """Draw the updated timestamp box (170x170 square, bottom flush with screen)."""
    draw.rectangle((630, y_start, 800, BOX_Y_END), fill=BLACK)

    # Center text vertically and horizontally in the box
    box_center_x = 715
    box_center_y = y_start + 85

    draw.text(
        (box_center_x, box_center_y - 45),
        "UPDATED",
        font=fonts[30],
        fill=WHITE,
        anchor="mm",
    )
    current_time = datetime.now().strftime("%H:%M")
    draw.text(
        (box_center_x, box_center_y + 25),
        current_time,
        font=fonts[60],
        fill=WHITE,
        anchor="mm",
    )


def draw_stop_row(
    draw, fonts, x_start: int, y: int, stop: dict, arrivals: list[dict]
) -> None:
    """Draw a single transit stop row with header and arrivals."""
    font_22 = fonts[22]

    # Draw header with direction abbreviation and stop name
    dir_abbr = "IN" if stop["direction"].lower() == "inbound" else "OUT"
    header = f"{dir_abbr} {stop['name']}"
    draw.text((x_start, y), header, font=font_22, fill=BLACK)

    # Draw arrivals below header with more spacing
    y += 30
    x = x_start

    for i, arrival in enumerate(arrivals):
        if i > 0:
            draw.text((x, y), " | ", font=font_22, fill=BLACK)
            x += 20

        route = arrival["route_name"]
        time_str = arrival["arrival_time"]

        # Draw glyph centered at this y position
        glyph_x = x + 15
        draw_route_glyph(draw, glyph_x, y + 11, route, font_22)
        x += 35

        # Draw time, vertically centered with glyph
        draw.text((x, y + 11), time_str, font=font_22, fill=BLACK, anchor="lm")
        x += 90


def draw_transit_section(
    image: Image.Image,
    draw,
    fonts,
    transit_data: list[dict],
    y_start: int = TRANSIT_Y_START,
) -> None:
    """Draw transit stops with departures under headers (2 columns if more than 2 stops)."""
    if not transit_data:
        return

    # Create lookup of arrivals by stop code and direction
    arrivals_by_key = {}
    for arrival in transit_data:
        key = (arrival["stop_code"], arrival["direction"])
        arrivals_by_key.setdefault(key, []).append(arrival)

    # Determine if we need 2 columns
    stops_with_arrivals = [
        stop
        for stop in config.STOPS
        if (stop["id"], stop["direction"]) in arrivals_by_key
    ]
    use_two_columns = len(stops_with_arrivals) > 2

    if use_two_columns:
        # Split stops across two columns
        col1_stops = stops_with_arrivals[: (len(stops_with_arrivals) + 1) // 2]
        col2_stops = stops_with_arrivals[(len(stops_with_arrivals) + 1) // 2 :]

        # Column 1 (left)
        y = y_start + 20
        for stop in col1_stops:
            key = (stop["id"], stop["direction"])
            arrivals = arrivals_by_key[key]

            draw_stop_row(draw, fonts, 25, y, stop, arrivals)
            y += 67

        # Column 2 (right)
        y = y_start + 20
        for stop in col2_stops:
            key = (stop["id"], stop["direction"])
            arrivals = arrivals_by_key[key]

            draw_stop_row(draw, fonts, 325, y, stop, arrivals)
            y += 67
    else:
        # Single column layout
        y = y_start
        for stop in stops_with_arrivals:
            key = (stop["id"], stop["direction"])
            arrivals = arrivals_by_key[key]

            draw_stop_row(draw, fonts, 10, y, stop, arrivals)
            y += 48
