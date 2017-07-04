#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Name : webapp.py
# Bottle template for busomatic web app
# Start standalone webserv if directly called (e.g python webapp.py)
# Version : 0.1.2

from bottle import route, run, template, static_file, response, get, default_app
from src import busquery, datetime, weather
import json
import sqlite3
import os

# Detect current path and add db location to it
current_dir = os.getcwd()
path_to_db = current_dir + '/static/db/busomatic-db.sq3'

# Default web page returned by bottle
@route('/')
def index():
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
	cur.execute('SELECT id_ligne, nom FROM lignes;')
	lineList = cur.fetchall()
        cur.close()
	weatherList = json.loads(weather.getWeather())
        condition = weatherList["meteo"]
        temp = weatherList["temp"]
        wind = weatherList["wind"]
	time = datetime.getTime()
	date = datetime.getDate()
	output = template('index',lineList=lineList,condition=condition,temp=temp, wind=wind,time=time, date=date)
	response.content_type = 'text/html;charset=utf8'
	return output

# Request direction list based on line choice
@get('/direction/<id_ligne>', method='GET')
def direction(id_ligne):
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
	cur.execute('SELECT id_direction, nom FROM directions WHERE id_ligne=(?)', (id_ligne,))
	dirList = cur.fetchall()
        cur.close()
	return template("""<option>Direction</option>\n
		% for id, name in dirList:\n 
		<option value="{{id}}">{{name}}</option>\n 
		%end""", dirList=dirList)

# Request stops based on direction choice
@get('/arret/<id_direction>', method='GET')
def arret (id_direction):
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
	cur.execute('SELECT numero, nom FROM arrets WHERE id_direction=(?)', (id_direction,))
	stopList = cur.fetchall()
        cur.close()
	response.content_type = 'text/html;charset=utf8'
	return template("""<option>Arrêt</option>\n
		% for id, name in stopList:\n 
		<option value="{{id}}">{{name}}</option>\n 
		%end""", stopList=stopList)

# Request schedule based on stop choice
@get('/horaire/<id_arret>', method='GET')
def horaires(id_arret):
	timeList = busquery.horaire(id_arret)
	return template("""
		<tr>\n
		</tr>\n
	% for linename, linedir, linetime in timeList:\n
		<tr>\n
			<td id="line_name">{{linename}}</td>\n
			<td id="line_direction">{{linedir}}</td>\n
			<td id="line_schedule">{{linetime}}</td>\n
		</tr>\n""",timeList=timeList)

@get('/time')
def heure():
	getTime = datetime.getTime()
	return template("{{time}}", time=getTime)

@get('/date')
def date():
	getDate = datetime.getDate()
	return template("{{date}}", date=getDate)

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
