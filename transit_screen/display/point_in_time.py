"""Point-in-time weather display rendering."""

from datetime import datetime

from PIL import Image, ImageDraw

from .. import config
from .utils import (
    BLACK,
    SEPARATOR_Y,
    TOP_OFFSET,
    TRANSIT_Y_START,
    WHITE,
    draw_dotted_line,
    draw_droplet,
    draw_transit_section,
    draw_updated_box,
    get_fonts,
)


def render_point_in_time_screen(
    weather_data: dict, transit_data: list[dict]
) -> Image.Image:
    """Render current weather snapshot with 2-column layout."""
    fonts = get_fonts()
    image = Image.new("1", (800, 480), 255)
    draw = ImageDraw.Draw(image)

    # Trash banner (full width, centered)
    if config.TRASH_ENABLED:
        weekday = datetime.today().weekday()
        if weekday in config.TRASH_DAYS:
            draw.rectangle((0, 0, 800, 42), fill=BLACK)
            draw.text(
                (400, 21),
                "TAKE OUT TRASH TODAY!",
                font=fonts[22],
                fill=WHITE,
                anchor="mm",
            )

    # LEFT COLUMN: Large temperature (centered) with feels-like below
    y_temp = TOP_OFFSET + 100
    temp_str = f"{weather_data['temp']:.0f}°F"
    draw.text((200, y_temp), temp_str, font=fonts[160], fill=BLACK, anchor="mm")

    # Feels-like centered below temp
    y_feels = y_temp + 100
    feel_str = f"Feels like: {weather_data['feels_like']:.0f}°F"
    draw.text((200, y_feels), feel_str, font=fonts[30], fill=BLACK, anchor="mm")

    # RIGHT OF TEMP: High / Low (top-right and bottom-right of big number)
    x_hi_lo = 420
    high_str = f"↑ {weather_data['temp_max']:.0f}°F"
    low_str = f"↓ {weather_data['temp_min']:.0f}°F"
    draw.text((x_hi_lo, y_temp - 50), high_str, font=fonts[30], fill=BLACK, anchor="mm")
    draw.text((x_hi_lo, y_temp + 80), low_str, font=fonts[30], fill=BLACK, anchor="mm")

    # Precip with droplet icon (aligned with description)
    precip_pct = weather_data["precip_prob"]
    y_precip = y_temp
    draw_droplet(draw, x_hi_lo - 20, y_precip + 18, size=4)
    draw.text(
        (x_hi_lo - 10, y_precip + 15),
        f"{precip_pct:.0f}%",
        font=fonts[22],
        fill=BLACK,
        anchor="lm",
    )

    # RIGHT COLUMN: Weather icon, description, precip
    x_right = 600
    icon_code = weather_data["icon"]
    icon_path = config.ASSETS_DIR / "icons" / f"{icon_code}.png"
    if icon_path.exists():
        icon = Image.open(icon_path)
        icon.thumbnail((110, 110))
        image.paste(icon, (x_right + 15, TOP_OFFSET + 35))

    # Description
    description = weather_data["description"]
    draw.text(
        (x_right, y_temp + 40), f"{description.title()}", font=fonts[22], fill=BLACK
    )

    # Dotted separator line
    draw_dotted_line(draw, 0, SEPARATOR_Y, 800)

    # Transit section and updated box (aligned at same y)
    draw_transit_section(image, draw, fonts, transit_data, y_start=TRANSIT_Y_START)
    draw_updated_box(draw, fonts)

    return image
