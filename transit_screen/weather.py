import requests

from . import config


def get_weather() -> dict:
    """Fetch weather data from Pirate Weather API."""
    url = f"https://api.pirateweather.net/forecast/{config.PIRATE_WEATHER_API_KEY}/{config.LAT},{config.LONG}"
    params = {"units": "us"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if config.WEATHER_MODE == "point-in-time":
        return _get_point_in_time(data)
    elif config.WEATHER_MODE == "timeline":
        return _get_timeline(data)
    else:
        raise ValueError(
            f"Unknown weather mode: {config.WEATHER_MODE!r}\n"
            f"Valid modes: 'point-in-time' or 'timeline'\n"
            f"Check config.yaml: weather.mode"
        )


def _get_point_in_time(data: dict) -> dict:
    """Format point-in-time weather (current + today's forecast)."""
    current = data["currently"]
    daily = data["daily"]["data"][0]

    return {
        "mode": "point-in-time",
        "temp": current["temperature"],
        "feels_like": current["apparentTemperature"],
        "humidity": current["humidity"] * 100,
        "wind_speed": current["windSpeed"],
        "description": current["summary"],
        "icon": current["icon"],
        "temp_max": daily["temperatureHigh"],
        "temp_min": daily["temperatureLow"],
        "precip_prob": daily["precipProbability"] * 100,
    }


def _get_timeline(data: dict) -> dict:
    """Format timeline weather (forecast strip)."""
    timeline = config.WEATHER_TIMELINE

    if timeline == "7d":
        forecast_data = data["daily"]["data"][:7]
        return {
            "mode": "timeline",
            "timeline": "7d",
            "data": [
                {
                    "time": item["time"],
                    "temp_high": item["temperatureHigh"],
                    "temp_low": item["temperatureLow"],
                    "icon": item["icon"],
                    "precip_prob": item["precipProbability"] * 100,
                }
                for item in forecast_data
            ],
        }
    else:
        hours = int(timeline.rstrip("h"))
        forecast_data = data["hourly"]["data"][:hours]
        return {
            "mode": "timeline",
            "timeline": timeline,
            "data": [
                {
                    "time": item["time"],
                    "temp": item["temperature"],
                    "icon": item["icon"],
                    "precip_prob": item["precipProbability"] * 100,
                }
                for item in forecast_data
            ],
        }
