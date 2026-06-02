import sys
import time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from . import config

sys.path.insert(0, str(config.LIB_DIR))
try:
    from waveshare_epd import epd7in5_V2
except (OSError, ImportError):
    epd7in5_V2 = None

BLACK = "rgb(0,0,0)"
WHITE = "rgb(255,255,255)"


def _get_fonts():
    """Load fonts at various sizes."""
    font_path = config.ASSETS_DIR / "font" / "Font.ttc"
    return {
        22: ImageFont.truetype(str(font_path), 22),
        30: ImageFont.truetype(str(font_path), 30),
        35: ImageFont.truetype(str(font_path), 35),
        50: ImageFont.truetype(str(font_path), 50),
        60: ImageFont.truetype(str(font_path), 60),
        100: ImageFont.truetype(str(font_path), 100),
        160: ImageFont.truetype(str(font_path), 160),
    }


def render_screen(weather_data: dict, transit_data: list[dict]) -> Image.Image:
    """Render weather and transit data to PIL Image."""
    if weather_data["mode"] == "timeline":
        return render_timeline_screen(weather_data, transit_data)
    else:
        return render_point_in_time_screen(weather_data, transit_data)


def render_point_in_time_screen(weather_data: dict, transit_data: list[dict]) -> Image.Image:
    """Render current weather snapshot."""
    fonts = _get_fonts()
    template = Image.open(config.ASSETS_DIR / "template.png")
    draw = ImageDraw.Draw(template)

    icon_code = weather_data["icon"]
    icon_path = config.ASSETS_DIR / "icons" / f"{icon_code}.png"
    if icon_path.exists():
        icon = Image.open(icon_path)
        template.paste(icon, (40, 15))

    draw.rectangle((25, 20, 225, 180), outline=BLACK)

    description = weather_data["description"]
    precip_pct = weather_data["precip_prob"]
    draw.text((30, 200), f"Now: {description.title()}", font=fonts[22], fill=BLACK)
    draw.text((30, 240), f"Precip: {precip_pct:.0f}%", font=fonts[30], fill=BLACK)

    temp_str = f"{weather_data['temp']:.0f}°F"
    draw.text((375, 35), temp_str, font=fonts[160], fill=BLACK)
    feel_str = f"Feels like: {weather_data['feels_like']:.0f}°F"
    draw.text((350, 210), feel_str, font=fonts[50], fill=BLACK)

    high_str = f"High: {weather_data['temp_max']:.0f}°F"
    draw.text((35, 325), high_str, font=fonts[50], fill=BLACK)
    draw.rectangle((170, 385, 265, 387), fill=BLACK)
    low_str = f"Low:  {weather_data['temp_min']:.0f}°F"
    draw.text((35, 390), low_str, font=fonts[50], fill=BLACK)

    if len(transit_data) > 0:
        t1 = f" City: {transit_data[0]['arrival_time']}"
    else:
        t1 = " City: No arrivals"
    if len(transit_data) > 1:
        t2 = f"Next: {transit_data[1]['arrival_time']}"
    else:
        t2 = "Next: No arrivals"

    draw.text((345, 340), t1, font=fonts[30], fill=BLACK)
    draw.text((345, 400), t2, font=fonts[30], fill=BLACK)

    draw.text((627, 330), "UPDATED", font=fonts[35], fill=WHITE)
    current_time = datetime.now().strftime("%H:%M")
    draw.text((627, 375), current_time, font=fonts[60], fill=WHITE)

    if config.TRASH_ENABLED:
        weekday = datetime.today().weekday()
        if weekday in config.TRASH_DAYS:
            draw.rectangle((345, 13, 705, 55), fill=BLACK)
            draw.text((355, 15), "TAKE OUT TRASH TODAY!", font=fonts[30], fill=WHITE)

    return template


def render_timeline_screen(weather_data: dict, transit_data: list[dict]) -> Image.Image:
    """Render forecast timeline strip."""
    fonts = _get_fonts()
    image = Image.new("1", (800, 480), 255)
    draw = ImageDraw.Draw(image)

    timeline = weather_data["timeline"]
    forecast_data = weather_data["data"]

    if timeline == "7d":
        _render_7day_timeline(image, draw, fonts, forecast_data, transit_data)
    else:
        _render_hourly_timeline(image, draw, fonts, timeline, forecast_data, transit_data)

    return image


def _render_7day_timeline(
    image: Image.Image, draw, fonts, forecast_data: list[dict], transit_data: list[dict]
) -> None:
    """Render 7-day forecast strip."""
    from datetime import datetime as dt

    col_width = 800 // 7
    y_start = 20

    for i, day in enumerate(forecast_data):
        x = i * col_width
        day_dt = dt.fromtimestamp(day["time"])
        day_str = day_dt.strftime("%a")

        draw.text((x + 5, y_start), day_str, font=fonts[22], fill=BLACK)

        icon_code = day["icon"]
        icon_path = config.ASSETS_DIR / "icons" / f"{icon_code}.png"
        if icon_path.exists():
            icon = Image.open(icon_path)
            icon.thumbnail((col_width - 10, 100))
            image.paste(icon, (x + 5, y_start + 25))

        high_str = f"{day['temp_high']:.0f}°"
        low_str = f"{day['temp_low']:.0f}°"
        precip_str = f"{day['precip_prob']:.0f}%"

        draw.text((x + 5, y_start + 130), high_str, font=fonts[22], fill=BLACK)
        draw.text((x + 5, y_start + 155), low_str, font=fonts[22], fill=BLACK)
        draw.text((x + 5, y_start + 180), precip_str, font=fonts[22], fill=BLACK)

        if i < 6:
            draw.line((x + col_width, y_start, x + col_width, y_start + 200), fill=BLACK)

    draw.rectangle((0, 220, 800, 222), fill=BLACK)

    if len(transit_data) > 0:
        t1 = f"Next: {transit_data[0]['arrival_time']}"
    else:
        t1 = "Next: No arrivals"

    draw.text((20, 240), t1, font=fonts[30], fill=BLACK)

    current_time = dt.now().strftime("%H:%M")
    draw.text((600, 400), f"Updated: {current_time}", font=fonts[22], fill=BLACK)


def _render_hourly_timeline(
    image: Image.Image, draw, fonts, timeline: str, forecast_data: list[dict],
    transit_data: list[dict]
) -> None:
    """Render hourly forecast strip (12h or 24h)."""
    from datetime import datetime as dt

    hours = int(timeline.rstrip("h"))
    step = max(1, hours // 12)
    col_width = 800 // 12
    y_start = 20

    col_idx = 0
    for i in range(0, len(forecast_data), step):
        if col_idx >= 12:
            break
        hour = forecast_data[i]
        x = col_idx * col_width

        hour_dt = dt.fromtimestamp(hour["time"])
        hour_str = hour_dt.strftime("%I%p").lstrip("0")

        draw.text((x + 2, y_start), hour_str, font=fonts[22], fill=BLACK)

        icon_code = hour["icon"]
        icon_path = config.ASSETS_DIR / "icons" / f"{icon_code}.png"
        if icon_path.exists():
            icon = Image.open(icon_path)
            icon.thumbnail((col_width - 4, 80))
            image.paste(icon, (x + 2, y_start + 25))

        temp_str = f"{hour['temp']:.0f}°"
        precip_str = f"{hour['precip_prob']:.0f}%"

        draw.text((x + 2, y_start + 110), temp_str, font=fonts[22], fill=BLACK)
        draw.text((x + 2, y_start + 135), precip_str, font=fonts[22], fill=BLACK)

        if col_idx < 11:
            draw.line((x + col_width, y_start, x + col_width, y_start + 160), fill=BLACK)

        col_idx += 1

    draw.rectangle((0, 200, 800, 202), fill=BLACK)

    if len(transit_data) > 0:
        t1 = f"Next: {transit_data[0]['arrival_time']}"
    else:
        t1 = "Next: No arrivals"

    draw.text((20, 220), t1, font=fonts[30], fill=BLACK)

    current_time = dt.now().strftime("%H:%M")
    draw.text((600, 400), f"Updated: {current_time}", font=fonts[22], fill=BLACK)


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
    fonts = _get_fonts()
    error_image = Image.new("1", (800, 480), 255)
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), f"{error_type} ERROR", font=fonts[50], fill=BLACK)
    draw.text((100, 300), "Retrying in 30 seconds", font=fonts[22], fill=BLACK)
    current_time = datetime.now().strftime("%H:%M")
    draw.text((300, 365), f"Last Refresh: {current_time}", font=fonts[50], fill=BLACK)
    write_to_display(epd, error_image)
