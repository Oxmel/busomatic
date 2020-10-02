#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Bottle template for busomatic web app
# Version : 0.2.5

from bottle import route, run, template, static_file, response, get, default_app
from src import busquery, openweather

# Default page returned when calling the base url
@route('/')
def index():
    lines = busquery.get_lines()
    forecast = openweather.forecast()
    weather = forecast["weather"]
    temp = forecast["temp"]
    wind = forecast["wind"]
    response.content_type = 'text/html;charset=utf8'
    return template('index', lines=lines, weather=weather,
                    temp=temp, wind=wind)

# Fetch all available directions for a given line
@get('/direction/<id_ligne>', method='GET')
def direction(id_ligne):
    directions = busquery.get_routes(id_ligne)
    return template('directions', directions=directions)

# Fetch all available stops for a given direction
@get('/arret/<id_direction>', method='GET')
def arret (id_direction):
    stops = busquery.get_stops(id_direction)
    response.content_type = 'text/html;charset=utf8'
    return template('stop', stops=stops)

# Request schedule for a given stop
@get('/horaire/<id_arret>', method='GET')
def horaires(id_arret):
    schedules = busquery.get_schedule(id_arret)
    return template('schedule', schedules=schedules)

# Paths to static files (scripts, images, stylesheet,...)
@get('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')


# Starts integrated web server if directly called (e.g 'python webapp.py')
# But remember to NOT use it in production, this is only for testing purposes
if __name__ == '__main__':
    run(host='0.0.0.0', port=8080, reloader=True)
# Or launch bottle in application mode wich is interfacing with uwsgi
else:
    app = application = default_app()
