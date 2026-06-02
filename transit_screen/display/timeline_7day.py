"""7-day forecast timeline display rendering."""

from datetime import date
from datetime import datetime as dt

from PIL import Image

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
)


def render_7day_timeline(
    image: Image.Image, draw, fonts, forecast_data: list[dict], transit_data: list[dict]
) -> None:
    """Render 7-day forecast strip with today highlighted."""
    col_width = 800 // 7
    y_start = TOP_OFFSET + 15
    today = date.today()

    for i, day in enumerate(forecast_data):
        x = i * col_width
        day_dt = dt.fromtimestamp(day["time"]).date()
        day_str = day_dt.strftime("%a")

        is_today = day_dt == today

        # Highlight today's column header with inverted colors
        if is_today:
            draw.rectangle(
                (x + 1, y_start - 5, x + col_width - 1, y_start + 20), fill=BLACK
            )
            draw.text(
                (x + col_width // 2, y_start + 7),
                day_str,
                font=fonts[22],
                fill=WHITE,
                anchor="mm",
            )
        else:
            draw.text((x + 5, y_start), day_str, font=fonts[22], fill=BLACK)

        icon_code = day["icon"]
        icon_path = config.ASSETS_DIR / "icons" / f"{icon_code}.png"
        if icon_path.exists():
            icon = Image.open(icon_path)
            icon.thumbnail((85, 85))
            image.paste(icon, (x + 14, y_start + 28))

        high_str = f"↑ {day['temp_high']:.0f}°"
        low_str = f"↓ {day['temp_low']:.0f}°"

        draw.text((x + 5, y_start + 118), high_str, font=fonts[22], fill=BLACK)
        draw.text((x + 5, y_start + 150), low_str, font=fonts[22], fill=BLACK)

        # Precip with droplet icon
        draw_droplet(draw, x + 67, y_start + 148, size=3)
        draw.text(
            (x + 75, y_start + 135),
            f"{day['precip_prob']:.0f}%".rjust(3, " "),
            font=fonts[15],
            fill=BLACK,
        )

        if i < 6:
            draw.line(
                (x + col_width, y_start, x + col_width, y_start + 185), fill=BLACK
            )

    # Dotted separator line
    draw_dotted_line(draw, 0, SEPARATOR_Y, 800)

    # Transit section and updated box (aligned at same y)
    draw_transit_section(image, draw, fonts, transit_data, y_start=TRANSIT_Y_START)
    draw_updated_box(draw, fonts)
