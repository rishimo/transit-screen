import requests

from . import config


def get_weather() -> dict:
    """Fetch current weather data from OpenWeatherMap API."""
    url = "http://api.openweathermap.org/data/2.5/onecall"
    params = {
        "lat": config.LAT,
        "lon": config.LONG,
        "units": "imperial",
        "appid": config.OPENWEATHER_API_KEY,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    current = data["current"]
    daily = data["daily"][0]

    return {
        "temp": current["temp"],
        "feels_like": current["feels_like"],
        "humidity": current["humidity"],
        "wind_speed": current["wind_speed"],
        "description": current["weather"][0]["description"],
        "icon": current["weather"][0]["icon"],
        "temp_max": daily["temp"]["max"],
        "temp_min": daily["temp"]["min"],
        "precip_prob": daily.get("pop", 0) * 100,
    }
