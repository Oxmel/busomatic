#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Name : openweather.py
# Get forecast from openweathermap.org
# An api key is required, see 'api-key-readme' for more infos

import urllib
import json

def forecast():
    # Catching errors in case we can't fetch weather data
    try :
        # Open the file containing the api key in read only mode
        key_path = open('src/weather-api-key', 'r')
        api_key = key_path.read().strip('\n')
        # Path to openweather api
        url = 'http://api.openweathermap.org/data/2.5/weather?'
        # Encode options to pass them later into the query string
        options = urllib.urlencode({'id': '3024635', 'units': 'metric',
                                    'appid': api_key, 'lang': 'fr'})
        # Get current forecast
        conn = urllib.urlopen(url + options)
        forecast = json.loads(conn.read())
        # Weather
        weather = forecast["weather"][0]["description"]
        # Temperature
        temp = forecast["main"]["temp"]
        # Remove decimal in case the value returned is a float
        temp = int(temp)
        # Wind speed in meters per second
        wind = forecast["wind"]["speed"]
        # Convert wind speed from m/s to km/h and remove decimal
        wind = int((wind * 3600) / 1000)
    except IOError :
        weather=temp=wind = 'n/a'
        print "Warning : Unable to fetch weather data"
        print "Please check '/src/api-key-readme' for more informations"
        print

    forecast = ({'weather': weather, 'temp': temp, 'wind': wind})
    return forecast
