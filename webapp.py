#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Bottle template for busomatic web app
# Version : 0.2.5

from bottle import route, run, template, static_file, response, get, default_app
from src import busquery, openweather

busquery = busquery.BusQuery()
journey = busquery.journey

# Default page returned when calling the base url
@route('/')
def index():
    busquery.update_feed_thread()
    lines = busquery.get_lines()
    forecast = openweather.forecast()
    weather = forecast["weather"]
    temp = forecast["temp"]
    wind = forecast["wind"]
    response.content_type = 'text/html;charset=utf8'
    return template('index', lines=lines, weather=weather,
                    temp=temp, wind=wind, is_realtime='')

# Fetch all available directions for a given line
@get('/direction/<id_ligne>')
def direction(id_ligne):
    busquery.update_journey(route_id=id_ligne)
    directions = busquery.get_directions(journey)
    return template('directions', directions=directions)

# Fetch all available stops for a given direction
@get('/arret/<id_direction>')
def arret (id_direction):
    busquery.update_journey(direction_id=id_direction)
    stops = busquery.get_stops(journey)
    response.content_type = 'text/html;charset=utf8'
    return template('stop', stops=stops)

# Request schedule for a given stop
@get('/horaire/<id_arret>')
def horaires(id_arret):
    busquery.update_journey(stop_id=id_arret)
    select_schedule = busquery.select_schedule(journey, id_arret)
    schedules = select_schedule['schedule']
    is_realtime = select_schedule['is_realtime']
    if schedules:
        return template('schedule', schedules=schedules, is_realtime=is_realtime)
    else:
        return '<h3 style="padding-top:20px;text-align:center;">Aucun passage prévu</h3>'

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
