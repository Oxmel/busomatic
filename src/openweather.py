#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Nom : weather.py
# Get forecast from openweathermap.org

import urllib
import json

# Open the file containing the api key in read only mode
keyPath = open('src/weather-api-key', 'r')
# Extract the key and remove the auto added newline
apiKey = keyPath.read().strip('\n')
# Path to openweather api
url = 'http://api.openweathermap.org/data/2.5/weather?'
# Encode options to pass them later into the query string
options = urllib.urlencode({'id': '3024635', 'units': 'metric', 'appid': apiKey, 'lang': 'fr'})

def getWeather():
    # Try/catch to prevent crashes if openweather is unreachable
    try :
        # Gather current weather
        conn = urllib.urlopen(url + options)
        # Read output and format it in json
        weather_req = json.loads(conn.read())
        # Forecast
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

getWeather()
