#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Nom : Weather.py
# Version : 0.2.2
# Get weather forecast from openweathermap api

import requests
import json

keyPath = open('src/weather-api-key')
apiKey = keyPath.read().strip('\n')
url = 'http://api.openweathermap.org/data/2.5/weather?'
options = {'id': '3024635', 'units': 'metric', 'appid': apiKey, 'lang': 'fr'}

def getWeather():
    # Try/catch to prevent crashes if openweather is unreachable
    try :
        weather_req = json.loads(requests.get(url, params=options).text)
        # Weather condition
        meteo = weather_req["weather"][0]["description"]
        # Temperature
        temp = weather_req["main"]["temp"]
        # Wind speed in meters per second
        wind = weather_req["wind"]["speed"]
        # Convert wind speed from m/s to km/h and remove decimal
        wind = int((wind * 3600) / 1000)
    except KeyError :
        meteo=temp=wind = 'n/a'

    result = ({'meteo': meteo, 'temp': temp, 'wind': wind})
    return json.dumps(result)
