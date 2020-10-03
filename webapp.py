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
@get('/route/<line_id>', method='GET')
def route(line_id):
    directions = busquery.get_routes(line_id)
    return template('directions', directions=directions)

# Fetch all available stops for a given direction
@get('/stop/<route_id>', method='GET')
def stop (route_id):
    stops = busquery.get_stops(route_id)
    response.content_type = 'text/html;charset=utf8'
    return template('stop', stops=stops)

# Request schedule for a given stop
@get('/schedule/<stop_id>', method='GET')
def stops(stop_id):
    schedules = busquery.get_schedule(stop_id)
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
