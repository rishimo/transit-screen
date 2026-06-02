"""Hourly (12h/24h) forecast timeline display rendering."""

from .. import config

from datetime import datetime as dt

from PIL import Image

from .utils import (
    SEPARATOR_Y,
    TOP_OFFSET,
    TRANSIT_Y_START,
    draw_dotted_line,
    draw_droplet,
    draw_temp_chart,
    draw_transit_section,
    draw_updated_box,
)


def render_hourly_timeline(
    image: Image.Image,
    draw,
    fonts,
    timeline: str,
    forecast_data: list[dict],
    transit_data: list[dict],
) -> None:
    """Render hourly forecast strip with temperature chart."""
    # Draw temperature chart
    draw_temp_chart(draw, forecast_data, y_start=TOP_OFFSET + 5, y_end=TOP_OFFSET + 75)

    hours = int(timeline.rstrip("h"))
    step = max(1, hours // 12)
    col_width = 800 // 12
    y_start = TOP_OFFSET + 95

    col_idx = 0
    for i in range(0, len(forecast_data), step):
        if col_idx >= 12:
            break
        hour = forecast_data[i]
        x = col_idx * col_width
        col_center = x + col_width // 2

        hour_dt = dt.fromtimestamp(hour["time"])
        hour_str = hour_dt.strftime("%I%p").lstrip("0")

        draw.text(
            (col_center, y_start + 10), hour_str, font=fonts[22], fill=0, anchor="mm"
        )

        icon_code = hour["icon"]
        icon_path = config.ASSETS_DIR / "icons" / f"{icon_code}.png"
        if icon_path.exists():
            icon = Image.open(icon_path)
            icon.thumbnail((50, 50))
            icon_x = col_center - 25
            image.paste(icon, (icon_x, y_start + 25))

        # Temperature: right-align the number so degree symbol doesn't affect alignment
        temp_val = f"{hour['temp']:.0f}"
        draw.text(
            (col_center + 7, y_start + 86),
            temp_val,
            font=fonts[22],
            fill=0,
            anchor="rm",
        )
        draw.text(
            (col_center + 7, y_start + 86), "°", font=fonts[22], fill=0, anchor="lm"
        )

        # Precip with droplet icon
        draw_droplet(draw, col_center - 22, y_start + 119, size=2)
        draw.text(
            (col_center - 15, y_start + 115),
            f"{hour['precip_prob']:.0f}%".rjust(3, " "),
            font=fonts[17],
            fill=0,
            anchor="lm",
        )

        if col_idx < 11:
            draw.line((x + col_width, y_start, x + col_width, y_start + 120), fill=0)

        col_idx += 1

    # Dotted separator line
    draw_dotted_line(draw, 0, SEPARATOR_Y, 800)

    # Transit section and updated box (aligned at same y)
    draw_transit_section(image, draw, fonts, transit_data, y_start=TRANSIT_Y_START)
    draw_updated_box(draw, fonts)
