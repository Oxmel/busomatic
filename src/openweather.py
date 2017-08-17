#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Get forecast from openweathermap.org

import urllib
import json

def getWeather():
	# Catching errors in case weather datas are not available
	try :
		# Open the file containing the api key in read only mode
		keyPath = open('src/weather-api-key', 'r')
		apiKey = keyPath.read().strip('\n')
		# Path to openweather api
		url = 'http://api.openweathermap.org/data/2.5/weather?'
		# Encode options to pass them later into the query string
		options = urllib.urlencode({'id': '3024635', 
			'units': 'metric', 'appid': apiKey, 'lang': 'fr'})
        # Gather current weather
		conn = urllib.urlopen(url + options)
        # Read output and format it in json
		weather = json.loads(conn.read())
        # Forecast
		meteo = weather["weather"][0]["description"]
        # Temperature
		temp = weather["main"]["temp"]
        # Wind speed in meters per second
		wind = weather["wind"]["speed"]
        # Convert wind speed from m/s to km/h and remove decimal
		wind = int((wind * 3600) / 1000)
	except IOError :
		meteo=temp=wind = 'n/a'
		print "Warning : Unable to fetch weather datas"
		print "Please check '/src/api-key-readme' for more informations"
		print

	currentWeather = ({'meteo': meteo, 'temp': temp, 'wind': wind})
	return json.dumps(currentWeather)
