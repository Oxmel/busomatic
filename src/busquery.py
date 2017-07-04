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
path_to_db = os.path.abspath(__file__ + '/../../static/db/busomatic-db.sq3')

# Generic function accepting either simple sql queries or queries with args
def generic(sqlQuery, *argparams):
    conn = sqlite3.connect(path_to_db)
    cur = conn.cursor()
    cur.execute(sqlQuery, argparams)
    testList = cur.fetchall()
    cur.close
    return testList

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
