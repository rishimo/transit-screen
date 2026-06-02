import requests

from . import config


def get_weather() -> dict:
    """Fetch current weather data from Pirate Weather API."""
    url = f"https://api.pirateweather.net/forecast/{config.PIRATE_WEATHER_API_KEY}/{config.LAT},{config.LONG}"
    params = {
        "units": "us",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    current = data["currently"]
    daily = data["daily"]["data"][0]

    return {
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
