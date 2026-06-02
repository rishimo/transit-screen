"""Display rendering module for transit screen."""
import sys
import time
from datetime import datetime

from PIL import Image, ImageDraw

from .point_in_time import render_point_in_time_screen
from .timeline_7day import render_7day_timeline
from .timeline_hourly import render_hourly_timeline
from .utils import get_fonts

try:
    from waveshare_epd import epd7in5_V2
except (OSError, ImportError):
    epd7in5_V2 = None


def render_screen(weather_data: dict, transit_data: list[dict]) -> Image.Image:
    """Render weather and transit data to PIL Image."""
    if weather_data["mode"] == "timeline":
        return render_timeline_screen(weather_data, transit_data)
    else:
        return render_point_in_time_screen(weather_data, transit_data)


def render_timeline_screen(weather_data: dict, transit_data: list[dict]) -> Image.Image:
    """Render forecast timeline strip."""
    fonts = get_fonts()
    image = Image.new("1", (800, 480), 255)
    draw = ImageDraw.Draw(image)

    timeline = weather_data["timeline"]
    forecast_data = weather_data["data"]

    if timeline == "7d":
        render_7day_timeline(image, draw, fonts, forecast_data, transit_data)
    else:
        render_hourly_timeline(image, draw, fonts, timeline, forecast_data, transit_data)

    return image


def write_to_display(epd, image: Image.Image) -> None:
    """Initialize display and write image to it."""
    if epd is None:
        print("(Display unavailable - would show image)")
        return
    epd.init()
    epd.display(epd.getbuffer(image))
    time.sleep(2)
    epd.sleep()


def clear_display(epd) -> None:
    """Clear the display completely."""
    if epd is None:
        print("(Display unavailable - would clear)")
        return
    epd.init()
    epd.Clear()
    epd.sleep()


def sleep_display(epd) -> None:
    """Put display into deep sleep mode."""
    if epd is None:
        print("(Display unavailable - would sleep)")
        return
    epd.sleep()


def show_error(epd, error_type: str) -> None:
    """Display error message on screen."""
    fonts = get_fonts()
    error_image = Image.new("1", (800, 480), 255)
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), f"{error_type} ERROR", font=fonts[50], fill=0)
    draw.text((100, 300), "Retrying in 30 seconds", font=fonts[22], fill=0)
    current_time = datetime.now().strftime("%H:%M")
    draw.text((300, 365), f"Last Refresh: {current_time}", font=fonts[50], fill=0)
    write_to_display(epd, error_image)
