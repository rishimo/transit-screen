# transit-screen

A RasPi project to display next transit arrival times along with some other stuff. Originally intended to just display arrival time, but decided to succumb to feature creep. :)

This project is based heavily off of James Howard's [e_paper_weather_display project](https://github.com/AbnormalDistributions/e_paper_weather_display).

## Goals

Using an e-ink screen, display next transit arrival times at configured stops and configurable weather data (temp/feels-like, forecasts, AQI, etc.). The screen should update inbound and outbound forecasted transit arrival times once every 5 minutes or so, and fully refresh once or twice a day to maintain longevity.

_Future:_ Revamp display to include different forecast information from OpenWeatherMap's API 3.0

## Components

* [Raspberry Pi 0 W](https://www.amazon.com/Raspberry-Pi-Zero-Wireless-model/dp/B06XFZC3BX/)
* [waveshare 7.5" E-Ink Display](https://www.amazon.com/gp/product/B07Z25LWTS/)
* [RPi 0 W Starter Kit](https://www.amazon.com/gp/product/B08MVH2JJ1/)
* [Picture Frame](https://www.amazon.com/Langdon-House-Tabletop-Included-Collection/dp/B09CGSDSVH/)
