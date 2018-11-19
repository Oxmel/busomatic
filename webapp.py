#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Bottle template for busomatic web app
# Start standalone webserv if directly called (e.g python webapp.py)
# Version : 0.2.5

from bottle import route, run, template, static_file, response, get, default_app
from src import busquery, openweather
import json

# Default web page returned by bottle
@route('/')
def index():
    lines = busquery.database('SELECT id_ligne, nom FROM lignes')
    forecast = json.loads(openweather.forecast())
    weather = forecast["weather"]
    temp = forecast["temp"]
    wind = forecast["wind"]
    response.content_type = 'text/html;charset=utf8'
    return template('index', lines=lines, weather=weather,
                    temp=temp, wind=wind)

# Request direction list based on line choice
@get('/direction/<id_ligne>', method='GET')
def direction(id_ligne):
    directions = busquery.database("""SELECT id_direction,
            nom FROM directions WHERE id_ligne=?""", id_ligne)
    return template('directions', directions=directions)

# Request stops based on direction choice
@get('/arret/<id_direction>', method='GET')
def arret (id_direction):
    stops = busquery.database("""SELECT numero,
            nom FROM arrets WHERE id_direction=?""", id_direction)
    response.content_type = 'text/html;charset=utf8'
    return template('stop', stops=stops)

# Request schedule based on stop choice
@get('/horaire/<id_arret>', method='GET')
def horaires(id_arret):
    schedules = busquery.horaire(id_arret)
    return template('schedule', schedules=schedules)

# Paths to static files (scripts, images, stylesheet,...)
@get('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')


# Start integrated webserv if called directly
if __name__ == '__main__':
    run(host='0.0.0.0', port=8080, reloader=True)
# Or launch bottle in application mode wich is interfacing with uwsgi
else:
    app = application = default_app()
