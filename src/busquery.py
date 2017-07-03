#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Name : BusQuery.py
# Version : 0.1.2
import os
import sqlite3
import urllib
from bs4 import BeautifulSoup

# Climb up to parent folder
# Needed since folder containing db is not a child of py scripts folder
# http://stackoverflow.com/questions/2817264/how-to-get-the-parent-dir-location
working_dir = os.path.abspath(__file__ + '/../../')
db_dir = '/static/db/busomatic-db.sq3'
path_to_db = working_dir + db_dir

# Connect to database
conn = sqlite3.connect(path_to_db)
cur = conn.cursor()

# Fetch all available lines from database
def ligne():
	# Look for all id / line name in database
	cur.execute('SELECT id_ligne, nom FROM lignes;')
	# Put all matching entries in a list
	lineList = cur.fetchall()
	cur.close
	return lineList

# Get available directions for selected line
def direction(id_ligne):
	# stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
	cur.execute("""SELECT id_direction, 
			nom FROM directions WHERE id_ligne=(?)""", (id_ligne,))
	dirList = cur.fetchall()
	cur.close
	return dirList

# Get available stops for selected direction
def arret(id_direction):
	cur.execute('SELECT numero, nom FROM arrets WHERE id_direction=(?)',(id_direction,))
	stopList = cur.fetchall()
	cur.close
	return stopList

# Gather schedule for selected line
def horaire(id_arret):
	url = ('http://qr.t2c.fr/qrcode?_stop_id=' + id_arret)
	readfile = urllib.urlopen(url)
	soup = BeautifulSoup(readfile, from_encoding='utf-8')
	timeList=[]
	# For each item in <tr> excepted the first one (junk)
	for item in soup.find_all('tr')[1:]:
		# For each item in <td> excepted the third
		lineInfo = item.find_all('td')[:3]
		# Get line name
		lineName = lineInfo[0].get_text().strip()
		# Get line direction
		lineDir = lineInfo[1].get_text().strip()
		# Get line schedule at specific stop
		lineTime = lineInfo[2].get_text().strip()
		# Create tuple with name, direction, schedule and add it in list
		timeList.append((lineName,lineDir,lineTime))
	readfile.close()
	return timeList
